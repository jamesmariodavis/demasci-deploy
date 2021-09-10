from typing import Dict
import os
import datetime
import pickle
import pytest
import pandas as pd
from tests.base_test_case import BaseTestCase
from app_lib.utils.local_cacher import (
    LocalCacher,
    MetaData,
    DATETIME_FORMAT_STR,
    ObjectCacheHandler,
    DataFrameCacheHandler,
)
from app_lib.app_paths import LOCAL_CACHE_DIR

BASIC_F_HASH = '8218a314-b144-5c20-84b5-69cbc7c16942-f51eece0-641e-5b32-90cc-db915563f359'
BASIC_F_META_DATA_FILE = '8218a314-b144-5c20-84b5-69cbc7c16942-f51eece0-641e-5b32-90cc-db915563f359-meta.json'
BASIC_F_META_DATA_FILE_PATH = os.path.join(LOCAL_CACHE_DIR, BASIC_F_META_DATA_FILE)
BASIC_F_CACHE_FILE = '8218a314-b144-5c20-84b5-69cbc7c16942-f51eece0-641e-5b32-90cc-db915563f359.pkl'
BASIC_F_CACHE_FILE_PATH = os.path.join(LOCAL_CACHE_DIR, BASIC_F_CACHE_FILE)

DATAFRAME_F_HASH = '75b27c67-4dfb-5c5e-a0f5-bf67933b4a3b-f51eece0-641e-5b32-90cc-db915563f359'
DATAFRAME_F_META_DATA_FILE = '75b27c67-4dfb-5c5e-a0f5-bf67933b4a3b-f51eece0-641e-5b32-90cc-db915563f359-meta.json'
DATAFRAME_F_META_DATA_FILE_PATH = os.path.join(LOCAL_CACHE_DIR, DATAFRAME_F_META_DATA_FILE)
DATAFRAME_F_CACHE_FILE = '75b27c67-4dfb-5c5e-a0f5-bf67933b4a3b-f51eece0-641e-5b32-90cc-db915563f359.csv'
DATAFRAME_F_CACHE_FILE_PATH = os.path.join(LOCAL_CACHE_DIR, DATAFRAME_F_CACHE_FILE)


@LocalCacher(use_cache_kwarg='use_cache')
def basic_f(
        x: int,
        y: str,
        use_cache: bool,  # pylint: disable=unused-argument
) -> Dict[int, str]:
    return {x: y}


@LocalCacher(use_cache_kwarg='use_cache')
def dataframe_f(
        x: int,
        y: str,
        use_cache: bool,  # pylint: disable=unused-argument
) -> pd.DataFrame:
    frame = pd.DataFrame({
        'a': [x] * 5,
        'b': [y] * 5,
    })
    return frame


class TestLocalCacher(BaseTestCase):
    def setUp(self) -> None:
        # write fake meta data files
        fake_meta_data_basic = MetaData(
            datetime_string=datetime.datetime.now().strftime(DATETIME_FORMAT_STR),
            hash_string=BASIC_F_HASH,
            cache_handler_name=ObjectCacheHandler.CACHE_HANDLER_NAME,
        )
        fake_meta_data_basic.write_to_disk(file_path=BASIC_F_META_DATA_FILE_PATH)

        fake_meta_data_dataframe = MetaData(
            datetime_string=datetime.datetime.now().strftime(DATETIME_FORMAT_STR),
            hash_string=DATAFRAME_F_HASH,
            cache_handler_name=DataFrameCacheHandler.CACHE_HANDLER_NAME,
        )
        fake_meta_data_dataframe.write_to_disk(file_path=DATAFRAME_F_META_DATA_FILE_PATH)

        # write fake cache files
        self.fake_obj = (1, 2, 3, 4)
        with open(BASIC_F_CACHE_FILE_PATH, 'wb') as f:
            pickle.dump(self.fake_obj, f)

        self.fake_frame = pd.DataFrame({
            'a': [1.3],
            'b': [2.7],
        })
        self.fake_frame.to_csv(DATAFRAME_F_CACHE_FILE_PATH, index=False)

    def tearDown(self) -> None:
        files_to_remove = [
            BASIC_F_META_DATA_FILE_PATH,
            BASIC_F_CACHE_FILE_PATH,
            DATAFRAME_F_META_DATA_FILE_PATH,
            DATAFRAME_F_CACHE_FILE_PATH,
        ]
        for file in files_to_remove:
            os.remove(file)

    def test_cache_recovery(self) -> None:
        return_value = basic_f(x=1, y='a', use_cache=True)
        self.assertEqual(return_value, self.fake_obj)

    def test_ignore_cache(self) -> None:
        return_value = basic_f(x=1, y='a', use_cache=False)
        self.assertEqual(return_value, {1: 'a'})

        return_value = basic_f(x=1, y='a', use_cache=True)
        self.assertEqual(return_value, {1: 'a'})

    def test_dataframe_handler(self) -> None:
        return_value = dataframe_f(x=1, y='a', use_cache=True)
        self.assertFramesEqual(return_value, self.fake_frame)


if __name__ == '__main__':
    pytest.main([__file__])
