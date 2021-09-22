from typing import (
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
import functools
import os
import inspect
import json
import pickle
import pandas as pd
from app_lib.utils.appx_hash import AppxHash

DEFAULT_USE_CACHE_KWARG = 'use_cache'
DEFAULT_CACHE_VALIDITY_HOURS = 24 * 7
DATETIME_FORMAT_STR = '%Y-%m-%d %H:%M:%S'

TMetaData = TypeVar('TMetaData', bound='MetaData')


class LocalCacheException(Exception):
    pass


def _get_canonical_file_prefix(
    function_source_hash: str,
    kwargs_hash: str,
) -> str:
    file_prefix_str = '{}-{}'.format(function_source_hash, kwargs_hash)
    return file_prefix_str


@dataclass(frozen=True)
class MetaData:
    write_datetime_str: str
    canonical_file_prefix: str
    cache_handler_name: str
    function_source_hash: str
    kwargs_hash: str
    function_name: str
    function_file_location: str

    def write_to_disk(
        self,
        cache_dir: str,
    ) -> None:
        meta_data_dict = self.__dict__
        file_path = MetaData._get_meta_data_file_path(
            canonical_file_prefix=self.canonical_file_prefix,
            cache_dir=cache_dir,
        )
        with open(file_path, 'w', encoding='utf8') as f:
            json.dump(meta_data_dict, f, indent=0)

    @classmethod
    def from_disk(
        cls: Type[TMetaData],
        canonical_file_prefix: str,
        cache_dir: str,
    ) -> TMetaData:
        file_path = cls._get_meta_data_file_path(
            canonical_file_prefix=canonical_file_prefix,
            cache_dir=cache_dir,
        )
        with open(file_path, 'r', encoding='utf8') as f:
            meta_data = cls(**json.load(f))
        return meta_data

    @staticmethod
    def cache_is_valid(
        cache_validity_hours: int,
        canonical_file_prefix: str,
        cache_dir: str,
    ) -> bool:
        # if file does not exist there is no cache
        meta_data_file_path = MetaData._get_meta_data_file_path(
            canonical_file_prefix=canonical_file_prefix,
            cache_dir=cache_dir,
        )
        if not os.path.exists(meta_data_file_path):
            return False
        cache_meta_data = MetaData.from_disk(
            canonical_file_prefix=canonical_file_prefix,
            cache_dir=cache_dir,
        )

        # check that cache is not stale
        cache_time = datetime.datetime.strptime(
            cache_meta_data.write_datetime_str,
            DATETIME_FORMAT_STR,
        )
        current_time = datetime.datetime.now()
        cache_time_delta = current_time - cache_time
        if cache_time_delta < datetime.timedelta(seconds=0):
            err_str = 'cache time {} prior to current time {}'.format(cache_time, current_time)
            raise LocalCacheException(err_str)
        if cache_time_delta > datetime.timedelta(hours=cache_validity_hours):
            return False

        return True

    @staticmethod
    def _get_meta_data_file_path(
        canonical_file_prefix: str,
        cache_dir: str,
    ) -> str:
        file_name = '{}-meta.json'.format(canonical_file_prefix)
        file_path = os.path.join(cache_dir, file_name)
        return file_path

    def delete_meta_data(
        self,
        cache_dir: str,
    ) -> None:
        meta_data_file_path = self._get_meta_data_file_path(
            canonical_file_prefix=self.canonical_file_prefix,
            cache_dir=cache_dir,
        )
        os.remove(meta_data_file_path)


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

    @staticmethod
    def get_file_path(
        canonical_file_prefix: str,
        file_suffix: str,
        cache_dir: str,
    ) -> str:
        file_name = '{}.{}'.format(canonical_file_prefix, file_suffix)
        file_path = os.path.join(cache_dir, file_name)
        return file_path

    @staticmethod
    def serialize_to_disk(
        cachable_object: Any,
        meta_data: MetaData,
        cache_dir: str,
    ) -> None:
        file_path = ObjectCacheHandler.get_file_path(
            canonical_file_prefix=meta_data.canonical_file_prefix,
            file_suffix='pkl',
            cache_dir=cache_dir,
        )
        with open(file_path, 'wb') as f:
            pickle.dump(obj=cachable_object, file=f)

    @staticmethod
    def deserialize_from_disk(
        meta_data: MetaData,
        cache_dir: str,
    ) -> Any:
        file_path = ObjectCacheHandler.get_file_path(
            canonical_file_prefix=meta_data.canonical_file_prefix,
            file_suffix='pkl',
            cache_dir=cache_dir,
        )
        with open(file_path, 'rb') as f:
            return_object = pickle.load(file=f)
        return return_object

    @staticmethod
    def delete_cache(
        meta_data: MetaData,
        cache_dir: str,
    ) -> None:
        file_path = ObjectCacheHandler.get_file_path(
            canonical_file_prefix=meta_data.canonical_file_prefix,
            file_suffix='pkl',
            cache_dir=cache_dir,
        )
        os.remove(file_path)


class DataFrameCacheHandler(ObjectCacheHandler):
    CACHE_HANDLER_NAME = 'DataFrame'
    CACHE_HANDLER_TYPES = (pd.DataFrame, )

    @classmethod
    def serialize_to_disk(
        cls,
        cachable_object: Any,
        meta_data: MetaData,
        cache_dir: str,
    ) -> None:
        if isinstance(cachable_object, pd.DataFrame):
            file_path = cls.get_file_path(
                canonical_file_prefix=meta_data.canonical_file_prefix,
                file_suffix='csv',
                cache_dir=cache_dir,
            )
            cachable_object.to_csv(path_or_buf=file_path, index=False)
        else:
            cls.raise_type_error()

    @staticmethod
    def deserialize_from_disk(
        meta_data: MetaData,
        cache_dir: str,
    ) -> Any:
        file_path = DataFrameCacheHandler.get_file_path(
            canonical_file_prefix=meta_data.canonical_file_prefix,
            file_suffix='csv',
            cache_dir=cache_dir,
        )
        frame = pd.read_csv(filepath_or_buffer=file_path)
        return frame

    @staticmethod
    def delete_cache(
        meta_data: MetaData,
        cache_dir: str,
    ) -> None:
        file_path = DataFrameCacheHandler.get_file_path(
            canonical_file_prefix=meta_data.canonical_file_prefix,
            file_suffix='csv',
            cache_dir=cache_dir,
        )
        os.remove(file_path)


class LocalCacher:
    AVAILABLE_CACHE_HANDLERS = [
        DataFrameCacheHandler,
        ObjectCacheHandler,
    ]

    def __init__(
        self,
        cache_dir: str,
        unhashable_kwargs: Optional[Collection[Any]] = None,
        use_cache_kwarg: str = DEFAULT_USE_CACHE_KWARG,
        cache_validity_hours: int = DEFAULT_CACHE_VALIDITY_HOURS,
        disable_cache: bool = False,
    ):
        self.unhashable_kwargs = unhashable_kwargs
        self.use_cache_kwarg = use_cache_kwarg
        self.cache_dir = cache_dir
        self.cache_validity_hours = cache_validity_hours
        self.disable_cache = disable_cache

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # get full kwargs to use in function call
            full_kwargs = LocalCacher._get_full_kwargs(
                func=func,
                passed_args=args,
                passed_kwargs=kwargs,
            )
            if self.use_cache_kwarg in full_kwargs and not self.disable_cache:
                call_signature_hash = self._get_call_signature_hash(
                    func=func,
                    passed_args=args,
                    passed_kwargs=kwargs,
                    use_cache_kwarg=self.use_cache_kwarg,
                    unhashable_kwargs=self.unhashable_kwargs,
                )

                function_source_hash = LocalCacher._get_function_source_hash(func=func)

                # full hash is combination of func hash and kwarg hash
                canonical_file_prefix = LocalCacher._get_file_prefix(
                    func=func,
                    passed_args=args,
                    passed_kwargs=kwargs,
                    use_cache_kwarg=self.use_cache_kwarg,
                    unhashable_kwargs=self.unhashable_kwargs,
                )

                # check if cache is valid
                cache_is_valid = MetaData.cache_is_valid(
                    cache_validity_hours=self.cache_validity_hours,
                    canonical_file_prefix=canonical_file_prefix,
                    cache_dir=self.cache_dir,
                )

                use_cache = full_kwargs[self.use_cache_kwarg]
                if use_cache and cache_is_valid:
                    # recover from disk
                    meta_data = MetaData.from_disk(
                        canonical_file_prefix=canonical_file_prefix,
                        cache_dir=self.cache_dir,
                    )
                    cache_handler = LocalCacher._get_cache_handler_from_meta_data(meta_data=meta_data)
                    return_object = cache_handler.deserialize_from_disk(
                        meta_data=meta_data,
                        cache_dir=self.cache_dir,
                    )
                else:
                    # execute function
                    return_object = func(**full_kwargs)
                    cache_handler = LocalCacher._get_cache_handler_from_object(return_object=return_object)
                    # get meta data and write to disk
                    meta_data = MetaData(
                        write_datetime_str=datetime.datetime.now().strftime(DATETIME_FORMAT_STR),
                        canonical_file_prefix=canonical_file_prefix,
                        cache_handler_name=cache_handler.CACHE_HANDLER_NAME,
                        function_source_hash=function_source_hash,
                        kwargs_hash=call_signature_hash,
                        function_name=func.__name__,
                        function_file_location=inspect.getfile(func),
                    )
                    meta_data.write_to_disk(cache_dir=self.cache_dir)
                    # cache object
                    cache_handler.serialize_to_disk(
                        cachable_object=return_object,
                        meta_data=meta_data,
                        cache_dir=self.cache_dir,
                    )
            else:
                # if use_cache_kwarg is not present do not use cache at all
                return_object = func(**full_kwargs)
            return return_object

        return wrapper

    @staticmethod
    def _get_file_prefix(
        func: Callable[..., Any],
        passed_args: Tuple[Any, ...],
        passed_kwargs: Dict[str, Any],
        use_cache_kwarg: Optional[str],
        unhashable_kwargs: Optional[Collection[str]],
    ) -> str:
        call_signature_hash = LocalCacher._get_call_signature_hash(
            func=func,
            passed_args=passed_args,
            passed_kwargs=passed_kwargs,
            use_cache_kwarg=use_cache_kwarg,
            unhashable_kwargs=unhashable_kwargs,
        )
        function_source_hash = LocalCacher._get_function_source_hash(func=func)
        file_prefix = _get_canonical_file_prefix(
            function_source_hash=function_source_hash,
            kwargs_hash=call_signature_hash,
        )
        return file_prefix

    @staticmethod
    def _get_full_kwargs(
        func: Callable[..., Any],
        passed_args: Tuple[Any, ...],
        passed_kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        # https://docs.python.org/3/library/inspect.html#inspect.Parameter
        default_kwargs = {
            k: v.default
            for k, v in inspect.signature(func).parameters.items() if v.default != inspect.Parameter.empty
        }
        # turns args into kwargs
        kawrg_names_in_order = [
            param_properties.name for param, param_properties in inspect.signature(func).parameters.items()
        ]
        args_as_kwargs = dict(zip(kawrg_names_in_order, passed_args))
        full_kwargs = default_kwargs.copy()
        full_kwargs.update(passed_kwargs)
        full_kwargs.update(args_as_kwargs)
        return full_kwargs

    @staticmethod
    def _get_call_signature_hash(
        func: Callable[..., Any],
        passed_args: Tuple[Any, ...],
        passed_kwargs: Dict[str, Any],
        use_cache_kwarg: Optional[str],
        unhashable_kwargs: Optional[Collection[str]],
    ) -> str:
        # represent function call as exhaustive list of kwargs
        full_kwargs = LocalCacher._get_full_kwargs(
            func=func,
            passed_args=passed_args,
            passed_kwargs=passed_kwargs,
        )
        # remove use_cache_kwarg from hash to prevent thrashing loops
        if use_cache_kwarg:
            _ = full_kwargs.pop(use_cache_kwarg)

        # sort input kwarg keys to maintain unique hashes
        sorted_kwarg_keys = sorted(full_kwargs.keys())
        sorted_kwarg_values = []

        for k in sorted_kwarg_keys:
            if unhashable_kwargs and k in unhashable_kwargs:
                continue
            kwarg_value: Any = full_kwargs[k]
            sorted_kwarg_values.append(kwarg_value)

        # build call signature
        args_call_signature = (
            sorted_kwarg_keys,
            sorted_kwarg_values,
        )
        # hash call signature
        call_signature_hash = AppxHash.get_appx_hash(input_object=args_call_signature)
        return call_signature_hash

    @staticmethod
    def _get_function_source_hash(func: Callable[..., Any]) -> str:
        # get function source signature
        func_source_str = inspect.getsource(func)
        # hash function source
        function_source_hash = AppxHash.get_appx_hash(func_source_str)
        return function_source_hash

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

    @staticmethod
    def clear_cache(
        cache_dir: str,
        cache_validity_hours: int = 0,
    ) -> None:
        meta_data_files = [
            f for f in os.listdir(cache_dir) if (os.path.isfile(os.path.join(cache_dir, f)) and '-meta.json' in f)
        ]
        for f in meta_data_files:
            canonical_file_prefix = f.split('-meta.json')[0]
            meta_data = MetaData.from_disk(
                canonical_file_prefix=canonical_file_prefix,
                cache_dir=cache_dir,
            )
            write_datetime = datetime.datetime.strptime(meta_data.write_datetime_str, DATETIME_FORMAT_STR)
            days_since_write = (datetime.datetime.now() - write_datetime).days
            seconds_since_write = (datetime.datetime.now() - write_datetime).seconds
            hours_since_write = (seconds_since_write / (60 * 60)) + (days_since_write * 24)
            # if cache is fresh break loop
            if hours_since_write < cache_validity_hours:
                continue
            cache_handler = LocalCacher._get_cache_handler_from_meta_data(meta_data=meta_data)
            # delete files
            cache_handler.delete_cache(
                meta_data=meta_data,
                cache_dir=cache_dir,
            )
            meta_data.delete_meta_data(cache_dir=cache_dir)
