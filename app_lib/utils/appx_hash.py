from typing import Any, Tuple
import dataclasses
import uuid
import collections
import pandas as pd
import pandas.api.types as pandas_types
import numpy as np

# all floats will be rounded to DIGITS_OF_PRECISION before hashing
DIGITS_OF_PRECISION = 8
# hashes may appear in file names. forbid charachters that make invalid file names
FORBIDDEN_STRING_CHARS = ('?', '/', '\\', '<', '>', '*', '|', '"', ':')


def _hash_function(object_to_hash: Any) -> str:
    hash_str = uuid.uuid5(namespace=uuid.NAMESPACE_URL, name=object_to_hash.__str__()).__str__()
    return hash_str


class AppxHashException(Exception):
    pass


class ObjectHashHandler:
    HANDLER_OBJECT_TYPES: Tuple[Any, ...] = ()

    @classmethod
    def raise_type_exception(cls, input_object: Any) -> None:
        err_str = 'expected types {} in hash handler {}\npassed type:{}'.format(
            cls.HANDLER_OBJECT_TYPES,
            cls,
            type(input_object),
        )
        raise AppxHashException(err_str)

    @classmethod
    def get_appx_object_hash(cls, input_object: Any) -> str:
        return _hash_function(object_to_hash=input_object)


class StringHashHandler(ObjectHashHandler):
    HANDLER_OBJECT_TYPES = (str, )

    @classmethod
    def get_appx_object_hash(cls, input_object: Any) -> str:
        if isinstance(input_object, str):
            return_object = input_object
            # if forbidden char exists use hash instead
            for charachter in FORBIDDEN_STRING_CHARS:
                if charachter in input_object:
                    return_object = _hash_function(object_to_hash=input_object)
        else:
            cls.raise_type_exception(input_object=input_object)
        return return_object


class FloatHashHandler(ObjectHashHandler):
    HANDLER_OBJECT_TYPES = (
        float,
        np.floating,
    )

    @classmethod
    def get_appx_object_hash(cls, input_object: Any) -> str:
        if isinstance(input_object, float) or isinstance(input_object, np.floating):
            hashable_object = np.round(input_object, DIGITS_OF_PRECISION)
        else:
            cls.raise_type_exception(input_object=input_object)
        return str(hashable_object)


class CollectionHashHandler(ObjectHashHandler):
    HANDLER_OBJECT_TYPES = (
        list,
        set,
        tuple,
        frozenset,
    )

    @classmethod
    def get_appx_object_hash(cls, input_object: Any) -> str:
        # homogenize all objects to tuples
        # identify between types by using a co-hash when we execute final hash
        if isinstance(input_object, list):
            co_hash = '23'
            hashable_object = tuple(input_object)
        elif isinstance(input_object, set):
            co_hash = '43'
            hashable_object = tuple(sorted(list(input_object)))
        elif isinstance(input_object, tuple):
            co_hash = '89'
            hashable_object = input_object
        elif isinstance(input_object, frozenset):
            co_hash = '02'
            hashable_object = tuple(input_object)
        else:
            cls.raise_type_exception(input_object=input_object)

        # try to hash object to detect if hashable
        try:
            # we use standard hash method to determine hashability
            # if hashable make no changes
            _ = hash(hashable_object)
        except TypeError:
            # some member of collection may not be hashable
            # convert unhashable objects in collection to hashes
            hashable_object = tuple([AppxHash.get_appx_hash(i) for i in hashable_object])
        return_hash = _hash_function(object_to_hash=(hashable_object, co_hash))
        return return_hash


class DictHashHandler(ObjectHashHandler):
    HANDLER_OBJECT_TYPES = (
        dict,
        collections.OrderedDict,
    )

    @classmethod
    def get_appx_object_hash(cls, input_object: Any) -> str:
        if isinstance(input_object, collections.OrderedDict):
            # we do not need to sort in this case
            sorted_hashable_tuples = [(AppxHash.get_appx_hash(i), AppxHash.get_appx_hash(j))
                                      for i, j in input_object.items()]
            co_hash = '48'
        elif isinstance(input_object, dict):
            hashable_dict = {AppxHash.get_appx_hash(i): AppxHash.get_appx_hash(j) for i, j in input_object.items()}
            # sort dictionary for uniqueness
            sorted_hashable_tuples = sorted([i for i in hashable_dict.items()])
            # to distinguish dict from tuple of tuples hash a tuple with identifier
            co_hash = '73'
        else:
            cls.raise_type_exception(input_object=input_object)
        hashable_object = (tuple(sorted_hashable_tuples), co_hash)
        return _hash_function(object_to_hash=hashable_object)


class DataClassHashHandler(ObjectHashHandler):
    HANDLER_OBJECT_TYPES = ()

    @classmethod
    def get_appx_object_hash(cls, input_object: Any) -> str:
        if dataclasses.is_dataclass(input_object):
            dict_repr = input_object.__dict__
            co_hash = '12'
            dict_hash = DictHashHandler.get_appx_object_hash(input_object=dict_repr)
            return_hash = _hash_function(object_to_hash=(dict_hash, co_hash))
        else:
            cls.raise_type_exception(input_object=input_object)
        return return_hash


class DataFrameHashHandler(ObjectHashHandler):
    HANDLER_OBJECT_TYPES = (pd.DataFrame, )

    @classmethod
    def get_appx_object_hash(cls, input_object: Any) -> str:
        if isinstance(input_object, pd.DataFrame):
            frame = input_object.copy()
            frame_cols = sorted(list(frame.columns))
            # convert types and round data
            for col in frame_cols:
                col_type = frame[col].dtype
                if pandas_types.is_float_dtype(col_type):
                    frame[col] = frame[col].round(DIGITS_OF_PRECISION)
                elif pandas_types.is_datetime64_dtype(col_type):
                    frame[col] = frame[col].astype('datetime64[ms]')
            # sort list by columns and rows
            frame = frame.sort_values(frame_cols).reset_index(drop=True)
            hash_series = pd.util.hash_pandas_object(obj=frame)
            hashable_object = tuple(hash_series)
        else:
            cls.raise_type_exception(input_object=input_object)
        return _hash_function(object_to_hash=hashable_object)


class AppxHash:
    HASH_HANDLERS = (
        ObjectHashHandler,
        DictHashHandler,
        CollectionHashHandler,
        DataFrameHashHandler,
        FloatHashHandler,
        StringHashHandler,
    )

    @classmethod
    def get_appx_hash(cls, input_object: Any) -> str:
        # initialize with default object handler
        target_hash_handler = ObjectHashHandler
        # search for appropriate object handler, if any
        for hash_handler in cls.HASH_HANDLERS:
            hash_handler_matches = [isinstance(input_object, i) for i in hash_handler.HANDLER_OBJECT_TYPES]
            if sum(hash_handler_matches) > 0:
                target_hash_handler = hash_handler
        # dataclass is a special case
        if dataclasses.is_dataclass(input_object):
            target_hash_handler = DataClassHashHandler
        # get object appx hash
        hash_safe_arg = target_hash_handler.get_appx_object_hash(input_object=input_object)
        return hash_safe_arg
