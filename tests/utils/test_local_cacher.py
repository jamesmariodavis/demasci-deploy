# pylint: disable=protected-access
from typing import (
    Dict,
    Union,
)
import os
import datetime
import pickle
import inspect
import pytest
import pandas as pd
from tests.base_test_case import BaseTestCase
from tests.fixtures.simple_function import some_f as other_some_f
from app_lib.utils.local_cacher import (
    LocalCacher,
    MetaData,
    DATETIME_FORMAT_STR,
    ObjectCacheHandler,
    DataFrameCacheHandler,
)
from app_lib.app_paths import LOCAL_CACHE_DIR

CUSTOM_USE_CACHE_KWARG = 'use_cache_a_lache'


def some_f(
    x: int,
    y: str,
    use_cache_a_lache: bool,  # pylint: disable=unused-argument
    z: int = 4,
) -> Dict[int, Union[int, str]]:
    return {x: y, z: z}


def some_g(
    x: int,
    y: str,
    use_cache_a_lache: bool,  # pylint: disable=unused-argument
    z: int = 4,
) -> Dict[int, Union[int, str]]:
    return {x: y, z: z}


@LocalCacher(cache_dir=LOCAL_CACHE_DIR, use_cache_kwarg=CUSTOM_USE_CACHE_KWARG, cache_validity_hours=1)
def cached_f(
    x: int,
    y: str,
    use_cache_a_lache: bool,  # pylint: disable=unused-argument
    z: int = 4,
) -> Dict[int, Union[int, str]]:
    return {x: y, z: z}


@LocalCacher(
    cache_dir=LOCAL_CACHE_DIR,
    use_cache_kwarg=CUSTOM_USE_CACHE_KWARG,
    cache_validity_hours=1,
    disable_cache=True,
)
def disabled_cached_f(
    x: int,
    y: str,
    use_cache_a_lache: bool,  # pylint: disable=unused-argument
    z: int = 4,
) -> Dict[int, Union[int, str]]:
    return {x: y, z: z}


@LocalCacher(cache_dir=LOCAL_CACHE_DIR, use_cache_kwarg=CUSTOM_USE_CACHE_KWARG, cache_validity_hours=1)
def no_cache_kwarg_cached_f(
    x: int,
    y: str,
    z: int = 4,
) -> Dict[int, Union[int, str]]:
    return {x: y, z: z}


@LocalCacher(cache_dir=LOCAL_CACHE_DIR, use_cache_kwarg=CUSTOM_USE_CACHE_KWARG)
def cached_g(
    x: int,
    y: str,
    use_cache_a_lache: bool,  # pylint: disable=unused-argument
    z: int = 4,
) -> Dict[int, Union[int, str]]:
    return {x: y, z: z}


@LocalCacher(cache_dir=LOCAL_CACHE_DIR, use_cache_kwarg=CUSTOM_USE_CACHE_KWARG)
def cached_frame_f(
        x: int,
        use_cache_a_lache: bool = True,  # pylint: disable=unused-argument
) -> pd.DataFrame:
    frame = pd.DataFrame({
        'b': [x] * 2,
        'c': ['a', 'b'],
    })
    return frame


class TestLocalCacher(BaseTestCase):
    def test_get_full_kwargs(self) -> None:
        # check that identical calls return identical results
        expected_result = {
            'x': 1,
            'y': 'a',
            CUSTOM_USE_CACHE_KWARG: True,
            'z': 4,
        }
        args_list = [
            (),
            (1, ),
            (1, 'a'),
            (1, 'a', True),
            (1, 'a', True, 4),
        ]
        kwargs_list = [
            {
                'x': 1,
                'y': 'a',
                CUSTOM_USE_CACHE_KWARG: True
            },
            {
                'y': 'a',
                CUSTOM_USE_CACHE_KWARG: True,
                'z': 4
            },
            {
                CUSTOM_USE_CACHE_KWARG: True,
            },
            {},
            {},
        ]
        function_results = [some_f(*args, **kwargs) for args, kwargs in zip(args_list, kwargs_list)]  # type: ignore
        full_kwargs_results = [
            LocalCacher._get_full_kwargs(func=some_f, passed_args=args, passed_kwargs=kwargs)  # type: ignore
            for args, kwargs in zip(args_list, kwargs_list)
        ]
        # assert all elements are the same
        assert function_results.count(function_results[0]) == len(function_results)
        assert full_kwargs_results.count(full_kwargs_results[0]) == len(full_kwargs_results)
        self.assertEqual(full_kwargs_results[0], expected_result)

    def test_get_call_signature_hash(self) -> None:
        call_signature_hash_1 = LocalCacher._get_call_signature_hash(
            func=some_f,
            passed_args=(),
            passed_kwargs={
                'x': 1,
                'y': 'a',
                CUSTOM_USE_CACHE_KWARG: True,
                'z': 4
            },
            use_cache_kwarg=CUSTOM_USE_CACHE_KWARG,
            unhashable_kwargs=[],
        )
        call_signature_hash_2 = LocalCacher._get_call_signature_hash(
            func=some_f,
            passed_args=(1, 'a'),
            passed_kwargs={
                CUSTOM_USE_CACHE_KWARG: True,
            },
            use_cache_kwarg=CUSTOM_USE_CACHE_KWARG,
            unhashable_kwargs=[],
        )
        # test use_cache param value has no impact
        call_signature_hash_3 = LocalCacher._get_call_signature_hash(
            func=some_f,
            passed_args=(1, 'a'),
            passed_kwargs={
                CUSTOM_USE_CACHE_KWARG: False,
            },
            use_cache_kwarg=CUSTOM_USE_CACHE_KWARG,
            unhashable_kwargs=[],
        )
        self.assertEqual(call_signature_hash_1, call_signature_hash_2)
        self.assertEqual(call_signature_hash_1, call_signature_hash_3)

        # test unhashable_kwargs respected
        call_signature_hash_4 = LocalCacher._get_call_signature_hash(
            func=some_f,
            passed_args=(),
            passed_kwargs={
                'x': 1,
                'y': 'a',
                CUSTOM_USE_CACHE_KWARG: True,
                'z': 3
            },
            use_cache_kwarg=CUSTOM_USE_CACHE_KWARG,
            unhashable_kwargs=['z'],
        )

        call_signature_hash_5 = LocalCacher._get_call_signature_hash(
            func=some_f,
            passed_args=(),
            passed_kwargs={
                'x': 1,
                'y': 'a',
                CUSTOM_USE_CACHE_KWARG: True,
                'z': 4
            },
            use_cache_kwarg=CUSTOM_USE_CACHE_KWARG,
            unhashable_kwargs=['z'],
        )
        self.assertEqual(call_signature_hash_4, call_signature_hash_5)

    def test_get_function_source_hash(self) -> None:
        some_f_source = inspect.getsource(some_f)
        other_some_f_source = inspect.getsource(other_some_f)
        self.assertEqual(some_f_source, other_some_f_source)

        some_f_hash = LocalCacher._get_function_source_hash(func=some_f)
        other_some_f_hash = LocalCacher._get_function_source_hash(func=other_some_f)
        self.assertEqual(some_f_hash, other_some_f_hash)

        some_g_hash = LocalCacher._get_function_source_hash(func=some_g)
        self.assertNotEqual(some_f_hash, some_g_hash)

        cached_f_hash = LocalCacher._get_function_source_hash(func=cached_f)
        cached_g_hash = LocalCacher._get_function_source_hash(func=cached_g)
        self.assertNotEqual(cached_f_hash, cached_g_hash)

    # pylint: disable=too-many-locals
    def test_cache_retreival(self) -> None:
        # can't retreive hash of function or kwargs because decorator returns wrapper
        # use hard coded values instead
        kwargs = {
            'x': 1,
            'y': 'a',
            CUSTOM_USE_CACHE_KWARG: True,
            'z': 5,
        }
        real_result = {1: 'a', 5: 5}
        fake_result = 'winner!'

        file_prefix = LocalCacher._get_file_prefix(
            func=cached_f,
            passed_args=(),
            passed_kwargs=kwargs,
            use_cache_kwarg=CUSTOM_USE_CACHE_KWARG,
            unhashable_kwargs=[],
        )
        meta_data_file = '{}-meta.json'.format(file_prefix)
        meta_data_file_path = os.path.join(LOCAL_CACHE_DIR, meta_data_file)
        meta_data = MetaData(
            write_datetime_str=datetime.datetime.now().strftime(DATETIME_FORMAT_STR),
            canonical_file_prefix=file_prefix,
            cache_handler_name=ObjectCacheHandler.CACHE_HANDLER_NAME,
            function_source_hash='',
            kwargs_hash='',
            function_name='',
            function_file_location='',
        )

        pickle_file_path = ObjectCacheHandler.get_file_path(
            canonical_file_prefix=file_prefix,
            file_suffix='pkl',
            cache_dir=LOCAL_CACHE_DIR,
        )
        # delete cache
        files_paths_to_clear = [
            pickle_file_path,
            meta_data_file_path,
        ]
        for file_path in files_paths_to_clear:
            if os.path.exists(file_path):
                os.remove(file_path)

        # write fake cache
        meta_data.write_to_disk(cache_dir=LOCAL_CACHE_DIR)
        with open(pickle_file_path, 'wb') as f:
            pickle.dump(fake_result, f)

        # returned result should be fake cached object
        returned_result = cached_f(**kwargs)
        self.assertEqual(returned_result, fake_result)

        # delete cache
        for file_path in files_paths_to_clear:
            if os.path.exists(file_path):
                os.remove(file_path)

        # # verify cache is written
        returned_result = cached_f(**kwargs)
        self.assertEqual(returned_result, real_result)
        for file_path in files_paths_to_clear:
            assert os.path.exists(file_path)

        # verify cache is retreived
        returned_result = cached_f(**kwargs)
        self.assertEqual(returned_result, real_result)

        # delete cache
        for file_path in files_paths_to_clear:
            if os.path.exists(file_path):
                os.remove(file_path)

        # test old cache is invalid
        old_datetime = datetime.datetime.now() - datetime.timedelta(hours=5)
        old_meta_data = MetaData(
            write_datetime_str=old_datetime.strftime(DATETIME_FORMAT_STR),
            canonical_file_prefix=file_prefix,
            cache_handler_name=ObjectCacheHandler.CACHE_HANDLER_NAME,
            function_source_hash='',
            kwargs_hash='',
            function_name='',
            function_file_location='',
        )
        # write fake cache
        old_meta_data.write_to_disk(cache_dir=LOCAL_CACHE_DIR)
        with open(pickle_file_path, 'wb') as f:
            pickle.dump(fake_result, f)

        # returned result should not be fake cached object
        returned_result = cached_f(**kwargs)
        self.assertEqual(returned_result, real_result)

        # delete cache
        for file_path in files_paths_to_clear:
            if os.path.exists(file_path):
                os.remove(file_path)

        # test use cache kwarg is respected
        # write fake cache
        old_meta_data.write_to_disk(cache_dir=LOCAL_CACHE_DIR)
        with open(pickle_file_path, 'wb') as f:
            pickle.dump(fake_result, f)

        kwargs_with_no_cache = kwargs.copy()
        kwargs_with_no_cache[CUSTOM_USE_CACHE_KWARG] = False

        # verify cache is not read
        returned_result = cached_f(**kwargs)
        self.assertEqual(returned_result, real_result)

        # delete cache
        for file_path in files_paths_to_clear:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_dataframe_handler(self) -> None:
        kwargs = {'x': 1}
        fake_result = pd.DataFrame({'a': [1, 2]})
        real_result = pd.DataFrame({
            'b': [1] * 2,
            'c': ['a', 'b'],
        })

        file_prefix = LocalCacher._get_file_prefix(
            func=cached_frame_f,
            passed_args=(),
            passed_kwargs=kwargs,
            use_cache_kwarg=CUSTOM_USE_CACHE_KWARG,
            unhashable_kwargs=[],
        )
        meta_data_file = '{}-meta.json'.format(file_prefix)
        meta_data_file_path = os.path.join(LOCAL_CACHE_DIR, meta_data_file)
        meta_data = MetaData(
            write_datetime_str=datetime.datetime.now().strftime(DATETIME_FORMAT_STR),
            canonical_file_prefix=file_prefix,
            cache_handler_name=DataFrameCacheHandler.CACHE_HANDLER_NAME,
            function_source_hash='',
            kwargs_hash='',
            function_name='',
            function_file_location='',
        )

        csv_file_path = DataFrameCacheHandler.get_file_path(
            canonical_file_prefix=file_prefix,
            file_suffix='csv',
            cache_dir=LOCAL_CACHE_DIR,
        )
        # delete cache
        files_paths_to_clear = [
            csv_file_path,
            meta_data_file_path,
        ]
        for file_path in files_paths_to_clear:
            if os.path.exists(file_path):
                os.remove(file_path)

        # write fake cache
        meta_data.write_to_disk(cache_dir=LOCAL_CACHE_DIR)
        fake_result.to_csv(csv_file_path, index=False)

        # verify fake result is retrieved
        returned_result = cached_frame_f(**kwargs)
        expected_result = fake_result
        self.assertFramesEqual(returned_result, expected_result)

        # delete cache
        for file_path in files_paths_to_clear:
            if os.path.exists(file_path):
                os.remove(file_path)

        # verify cache is written
        returned_result = cached_frame_f(**kwargs)
        self.assertFramesEqual(returned_result, real_result)
        for file_path in files_paths_to_clear:
            assert os.path.exists(file_path)

        # verify cache is retreived
        returned_result = cached_frame_f(**kwargs)
        self.assertFramesEqual(returned_result, real_result)

        # delete cache
        for file_path in files_paths_to_clear:
            if os.path.exists(file_path):
                os.remove(file_path)

    @staticmethod
    def test_alternate_pattern() -> None:
        local_cacher_instance = LocalCacher(cache_dir=LOCAL_CACHE_DIR, use_cache_kwarg=CUSTOM_USE_CACHE_KWARG)

        @local_cacher_instance
        def alt_f(
                x: int,
                use_cache_a_lache: bool,  # pylint: disable=unused-argument
        ) -> int:
            return 2 * x

        kwargs = {'x': 2, CUSTOM_USE_CACHE_KWARG: True}

        file_prefix = LocalCacher._get_file_prefix(
            func=alt_f,
            passed_args=(),
            passed_kwargs=kwargs,
            use_cache_kwarg=CUSTOM_USE_CACHE_KWARG,
            unhashable_kwargs=[],
        )
        meta_data_file = '{}-meta.json'.format(file_prefix)
        meta_data_file_path = os.path.join(LOCAL_CACHE_DIR, meta_data_file)
        pickle_file_path = ObjectCacheHandler.get_file_path(
            canonical_file_prefix=file_prefix,
            file_suffix='pkl',
            cache_dir=LOCAL_CACHE_DIR,
        )

        cached_files = [
            meta_data_file_path,
            pickle_file_path,
        ]

        # check that cache is written
        # delete cache
        alt_f(**kwargs)

        for file_path in cached_files:
            assert os.path.exists(file_path)
            os.remove(file_path)

    @staticmethod
    def test_clear_cache() -> None:
        kwargs = {
            'x': 1,
            'y': 'a',
            CUSTOM_USE_CACHE_KWARG: True,
        }
        file_prefix = LocalCacher._get_file_prefix(
            func=cached_f,
            passed_args=(),
            passed_kwargs=kwargs,
            use_cache_kwarg=CUSTOM_USE_CACHE_KWARG,
            unhashable_kwargs=[],
        )
        meta_data_file = '{}-meta.json'.format(file_prefix)
        meta_data_file_path = os.path.join(LOCAL_CACHE_DIR, meta_data_file)
        pickle_file_path = ObjectCacheHandler.get_file_path(
            canonical_file_prefix=file_prefix,
            file_suffix='pkl',
            cache_dir=LOCAL_CACHE_DIR,
        )

        cached_file_paths = [
            meta_data_file_path,
            pickle_file_path,
        ]

        # eval function to write cache
        _ = cached_f(**kwargs)

        # check files created
        for file_path in cached_file_paths:
            assert os.path.exists(file_path)

        # overwrite meta data with very old meta data
        lots_of_hours = 500000
        very_old_date = datetime.datetime.now() - datetime.timedelta(hours=lots_of_hours)
        old_meta_data = MetaData(
            write_datetime_str=very_old_date.strftime(DATETIME_FORMAT_STR),
            canonical_file_prefix=file_prefix,
            cache_handler_name=ObjectCacheHandler.CACHE_HANDLER_NAME,
            function_source_hash='',
            kwargs_hash='',
            function_name='',
            function_file_location='',
        )
        old_meta_data.write_to_disk(cache_dir=LOCAL_CACHE_DIR)

        # delete cached data using old date as filter
        LocalCacher.clear_cache(
            cache_dir=LOCAL_CACHE_DIR,
            cache_validity_hours=(lots_of_hours - 1),
        )

        # check files deleted
        for file_path in cached_file_paths:
            assert not os.path.exists(file_path)

    @staticmethod
    def test_disable_cache_modes() -> None:
        kwargs = {
            'x': 1,
            'y': 'a',
            CUSTOM_USE_CACHE_KWARG: True,
        }
        file_prefix = LocalCacher._get_file_prefix(
            func=disabled_cached_f,
            passed_args=(),
            passed_kwargs=kwargs,
            use_cache_kwarg=CUSTOM_USE_CACHE_KWARG,
            unhashable_kwargs=[],
        )
        meta_data_file = '{}-meta.json'.format(file_prefix)
        meta_data_file_path = os.path.join(LOCAL_CACHE_DIR, meta_data_file)
        pickle_file_path = ObjectCacheHandler.get_file_path(
            canonical_file_prefix=file_prefix,
            file_suffix='pkl',
            cache_dir=LOCAL_CACHE_DIR,
        )

        cached_file_paths = [
            meta_data_file_path,
            pickle_file_path,
        ]

        # execute method
        _ = disabled_cached_f(**kwargs)

        # check cache not written
        for file_path in cached_file_paths:
            assert not os.path.exists(file_path)

        kwargs = {
            'x': 1,
            'y': 'a',
        }
        file_prefix = LocalCacher._get_file_prefix(
            func=no_cache_kwarg_cached_f,
            passed_args=(),
            passed_kwargs=kwargs,
            use_cache_kwarg=None,
            unhashable_kwargs=[],
        )
        meta_data_file = '{}-meta.json'.format(file_prefix)
        meta_data_file_path = os.path.join(LOCAL_CACHE_DIR, meta_data_file)
        pickle_file_path = ObjectCacheHandler.get_file_path(
            canonical_file_prefix=file_prefix,
            file_suffix='pkl',
            cache_dir=LOCAL_CACHE_DIR,
        )

        cached_file_paths = [
            meta_data_file_path,
            pickle_file_path,
        ]

        # execute method
        _ = no_cache_kwarg_cached_f(**kwargs)

        for file_path in cached_file_paths:
            assert not os.path.exists(file_path)


if __name__ == '__main__':
    pytest.main([__file__])
