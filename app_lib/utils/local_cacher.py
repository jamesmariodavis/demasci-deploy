from typing import (
    List,
    Optional,
    Collection,
    Callable,
    Dict,
    Any,
    Tuple,
    TypeVar,
    Type,
)
from dataclasses import dataclass
import datetime
import os
import inspect
import json
import pickle
import pandas as pd
from app_lib.app_paths import LOCAL_CACHE_DIR, ROOT_DIR
from app_lib import AppxHash

DEFAULT_USE_CACHE_KWARG = 'use_cache'
DEFAULT_INVALIDITY_HOURS = 24 * 7
DATETIME_FORMAT_STR = '%Y-%m-%d--%H-%M'

TMetaData = TypeVar('TMetaData', bound='MetaData')


@dataclass(frozen=True)
class MetaData:
    datetime_string: str
    cache_handler_name: str
    hash_string: str

    def write_to_disk(
        self,
        file_path: str,
    ) -> None:
        meta_data_dict = self.__dict__
        with open(file_path, 'w', encoding='utf8') as f:
            json.dump(meta_data_dict, f)

    @classmethod
    def from_disk(
        cls: Type[TMetaData],
        file_path: str,
    ) -> TMetaData:
        with open(file_path, 'r', encoding='utf8') as f:
            meta_data = cls(**json.load(f))
        return meta_data


class LocalCacheException(Exception):
    pass


class ObjectCacheHandler:
    CACHE_HANDLER_NAME = 'Generic'
    CACHE_HANDLER_TYPES: Tuple[Any, ...] = ()

    @classmethod
    def raise_type_error(cls) -> None:
        err_str = 'cache handler {} can only be used in types {}'.format(
            cls.CACHE_HANDLER_NAME,
            cls.CACHE_HANDLER_TYPES,
        )
        raise LocalCacheException(err_str)

    @classmethod
    def get_file_path(cls, file_hash_prefix: str, cache_dir: str, file_suffix: str) -> str:
        file_name = '{}.{}'.format(file_hash_prefix, file_suffix)
        file_path = os.path.join(cache_dir, file_name)
        return file_path

    @classmethod
    def serialize_to_disk(
        cls,
        cachable_object: Any,
        file_hash_prefix: str,
        cache_dir: str,
    ) -> None:
        file_path = cls.get_file_path(
            file_hash_prefix=file_hash_prefix,
            cache_dir=cache_dir,
            file_suffix='pkl',
        )
        with open(file_path, 'wb') as f:
            pickle.dump(obj=cachable_object, file=f)

    @classmethod
    def deserialize_from_disk(
        cls,
        file_hash_prefix: str,
        cache_dir: str,
    ) -> Any:
        file_path = cls.get_file_path(
            file_hash_prefix=file_hash_prefix,
            cache_dir=cache_dir,
            file_suffix='pkl',
        )
        with open(file_path, 'rb') as f:
            return_object = pickle.load(file=f)
        return return_object


class DataFrameCacheHandler(ObjectCacheHandler):
    CACHE_HANDLER_NAME = 'DataFrame'
    CACHE_HANDLER_TYPES = (pd.DataFrame, )

    @classmethod
    def serialize_to_disk(
        cls,
        cachable_object: Any,
        file_hash_prefix: str,
        cache_dir: str,
    ) -> None:
        if isinstance(cachable_object, pd.DataFrame):
            file_path = cls.get_file_path(
                file_hash_prefix=file_hash_prefix,
                cache_dir=cache_dir,
                file_suffix='csv',
            )
            cachable_object.to_csv(path_or_buf=file_path, index=False)
        else:
            cls.raise_type_error()

    @classmethod
    def deserialize_from_disk(
        cls,
        file_hash_prefix: str,
        cache_dir: str,
    ) -> Any:
        file_path = cls.get_file_path(
            file_hash_prefix=file_hash_prefix,
            cache_dir=cache_dir,
            file_suffix='csv',
        )
        frame = pd.read_csv(filepath_or_buffer=file_path)
        return frame


class LocalCacher:
    AVAILABLE_CACHE_HANDLERS = (
        DataFrameCacheHandler,
        ObjectCacheHandler,
    )

    def __init__(
        self,
        unhashable_kwargs: Optional[Collection[Any]] = None,
        use_cache_kwarg: str = DEFAULT_USE_CACHE_KWARG,
    ):
        self.unhashable_kwargs = unhashable_kwargs
        self.use_cache_kwarg = use_cache_kwarg

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:
            if self.use_cache_kwarg in kwargs:
                # remove use_cache_kwarg from hash
                use_cache = kwargs.pop(self.use_cache_kwarg)

                # sort input kwarg keys to maintain unique hashes
                sorted_kwarg_keys = sorted(kwargs.keys())
                sorted_kwarg_values = []

                for k in sorted_kwarg_keys:
                    if self.unhashable_kwargs and k in self.unhashable_kwargs:
                        continue
                    kwarg_value: Any = kwargs[k]
                    sorted_kwarg_values.append(kwarg_value)

                # add use_cache_kwarg for valid function call
                kwargs[self.use_cache_kwarg] = use_cache

                # build call signature
                args_call_signature = (
                    sorted_kwarg_keys,
                    sorted_kwarg_values,
                )
                # hash call signature
                args_hash_value = AppxHash.get_appx_hash(input_object=args_call_signature)

                # get function signature
                func_file_path = inspect.getfile(func)
                relative_function_file_path = os.path.relpath(path=func_file_path, start=ROOT_DIR)
                full_func_str = '{}-{}'.format(relative_function_file_path, func.__name__)
                # hash function signature
                func_hash_value = AppxHash.get_appx_hash(full_func_str)

                # full hash is combination of both hashes
                hash_string = '{}-{}'.format(func_hash_value, args_hash_value)

                meta_data_file = '{}-meta.json'.format(hash_string)
                meta_data_file_path = os.path.join(LOCAL_CACHE_DIR, meta_data_file)
                if use_cache and os.path.exists(meta_data_file_path):
                    # recover from disk
                    meta_data = MetaData.from_disk(file_path=meta_data_file_path)
                    cache_handler = LocalCacher._get_cache_handler_from_meta_data(meta_data=meta_data)
                    return_object = cache_handler.deserialize_from_disk(
                        file_hash_prefix=hash_string,
                        cache_dir=LOCAL_CACHE_DIR,
                    )
                else:
                    # execute function
                    return_object = func(*args, **kwargs)
                    cache_handler = LocalCacher._get_cache_handler_from_object(return_object=return_object)
                    # get meta data and write to disk
                    meta_data = LocalCacher._get_meta_data(
                        cache_handler=cache_handler,
                        hash_string=hash_string,
                    )
                    meta_data.write_to_disk(file_path=meta_data_file_path)
                    # cache object
                    cache_handler.serialize_to_disk(
                        cachable_object=return_object,
                        file_hash_prefix=hash_string,
                        cache_dir=LOCAL_CACHE_DIR,
                    )
            else:
                # if use_cache_kwarg is not present do not use cache at all
                return_object = func(*args, **kwargs)
            return return_object

        return wrapper

    @staticmethod
    def _get_meta_data(
        cache_handler: ObjectCacheHandler,
        hash_string: str,
    ) -> MetaData:
        meta_data = MetaData(
            datetime_string=datetime.datetime.now().strftime(DATETIME_FORMAT_STR),
            cache_handler_name=cache_handler.CACHE_HANDLER_NAME,
            hash_string=hash_string,
        )
        return meta_data

    @staticmethod
    def _get_cache_handler_from_object(return_object: Any) -> ObjectCacheHandler:
        object_type = type(return_object)
        for handler in LocalCacher.AVAILABLE_CACHE_HANDLERS:
            if object_type in handler.CACHE_HANDLER_TYPES:
                return handler()
        return ObjectCacheHandler()

    @staticmethod
    def _get_cache_handler_from_meta_data(meta_data: MetaData) -> ObjectCacheHandler:
        cache_handler_name = meta_data.cache_handler_name
        for handler in LocalCacher.AVAILABLE_CACHE_HANDLERS:
            if cache_handler_name == handler.CACHE_HANDLER_NAME:
                return handler()
        err_str = 'could not find cache handler {}'.format(cache_handler_name)
        raise LocalCacheException(err_str)
