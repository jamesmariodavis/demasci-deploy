from typing import (
    Collection,
    Any,
    Dict,
)
from dataclasses import dataclass
import collections
import numpy as np
import pytest
import pandas as pd
from tests.base_test_case import BaseTestCase
from app_lib.utils.appx_hash import AppxHash


@dataclass(frozen=False)
class GenericDataClass:
    a: Dict[Any, Any]
    b: float


class TestAppxHash(BaseTestCase):
    def _assert_hashes_are_unique(self, list_of_objects: Collection[Any]) -> None:
        list_of_hashes = [AppxHash.get_appx_hash(input_object=i) for i in list_of_objects]
        self.assertEqual(len(list_of_hashes), len(set(list_of_hashes)))

    def _assert_hashes_match(self, list_of_objects: Collection[Any]) -> None:
        list_of_hashes = [AppxHash.get_appx_hash(input_object=i) for i in list_of_objects]
        self.assertEqual(len(set(list_of_hashes)), 1)

    def test_collections_basic(self) -> None:
        list_of_objects = [
            [1, 2],
            [2, 3],
            (1, 2),
            (2, 3),
            {1, 2},
            {2, 3},
            frozenset([1, 2]),
            frozenset([2, 3]),
        ]
        self._assert_hashes_are_unique(list_of_objects)

    def test_dict_basic(self) -> None:
        odict1 = collections.OrderedDict()
        odict1[1] = 2
        odict1[3] = 4

        odict2 = collections.OrderedDict()
        odict2[1] = 2
        odict2[3] = 5
        list_of_objects = [
            {
                1: 2,
                3: 4,
            },
            {
                1: 2,
                3: 5,
            },
            odict1,
            odict2,
        ]
        self._assert_hashes_are_unique(list_of_objects)

        list_of_objects = [
            {
                1: 2,
                3: 4,
            },
            {
                3: 4,
                1: 2,
            },
        ]
        self._assert_hashes_match(list_of_objects)

    def test_float_basic(self) -> None:
        list_of_objects = [
            1.2,
            1.3,
            np.float64(1.4),
            np.float64(1.5),
        ]
        self._assert_hashes_are_unique(list_of_objects)

        list_of_objects = [
            1.2,
            1.20000000001,
            np.float64(1.2),
            np.float32(1.2),
            np.float64(1.200000000001),
        ]
        self._assert_hashes_match(list_of_objects)

    def test_nested_objects(self) -> None:
        list_of_objects = [
            [1, 2, {3, 4}, {
                1: 2,
                3: 4
            }],
            (1, 2, {3, 4}, {
                1: 2,
                3: 4
            }),
            [1, 2, {3, 4}, {
                1: 2,
                3: 5
            }],
        ]
        self._assert_hashes_are_unique(list_of_objects)

        list_of_objects = [
            [1, 2, {3, 4}, {
                1: 2,
                3: 4,
            }],
            [1, 2, {4, 3}, {
                3: 4,
                1: 2,
            }],
        ]
        self._assert_hashes_match(list_of_objects)

    def test_dataframe_basic(self) -> None:
        frame1 = pd.DataFrame({
            'a': [1.0, 2.0],
            'b': ['a', 'b'],
            'c': pd.to_datetime(['2021-01-01', '2021-01-01']),
        })
        frame2 = pd.DataFrame({
            'a': [1.1, 2.0],
            'b': ['a', 'b'],
            'c': pd.to_datetime(['2021-01-01', '2021-01-01']),
        })
        frame3 = pd.DataFrame({
            'a': [1.0, 2.0],
            'b': ['a', 'c'],
            'c': pd.to_datetime(['2021-01-01', '2021-01-01']),
        })
        frame4 = pd.DataFrame({
            'a': [1.0, 2.0],
            'b': ['a', 'b'],
            'c': pd.to_datetime(['2021-01-01', '2021-01-02']),
        })
        frame4 = pd.DataFrame({
            'a': [1, 2],
            'b': ['a', 'b'],
            'c': pd.to_datetime(['2021-01-01', '2021-01-01']),
        })
        list_of_objects = [
            frame1,
            frame2,
            frame3,
            frame4,
        ]
        self._assert_hashes_are_unique(list_of_objects)

        frame5 = pd.DataFrame({
            'a': [1.0, 2.00000000000001],
            'b': ['a', 'b'],
            'c': pd.to_datetime(['2021-01-01', '2021-01-01']),
        })
        list_of_objects = [
            frame1,
            frame5,
        ]
        self._assert_hashes_match(list_of_objects)

    def test_dataclass_basic(self) -> None:
        list_of_objects = [
            GenericDataClass(
                a={
                    1: 2,
                    3: 4,
                },
                b=2,
            ),
            GenericDataClass(
                a={
                    1: 2,
                    3: 5,
                },
                b=2,
            ),
        ]
        self._assert_hashes_are_unique(list_of_objects)

        list_of_objects = [
            GenericDataClass(
                a={
                    1: 2,
                    3: 4,
                },
                b=2,
            ),
            GenericDataClass(
                a={
                    3: 4,
                    1: 2,
                },
                b=2,
            ),
        ]
        self._assert_hashes_match(list_of_objects)


if __name__ == '__main__':
    pytest.main([__file__])
