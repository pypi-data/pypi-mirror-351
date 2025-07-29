# Copyright (C) 2022 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_array_equal

from trianglechain.params import (
    add_derived,
    check_if_names_is_used_correctly,
    ensure_rec,
)


@pytest.fixture
def data():
    return np.array([[1, 2], [3, 4]])


@pytest.fixture
def data_dict():
    return {"a": np.array([1, 2]), "b": np.array([3, 4])}


@pytest.fixture
def data_names():
    return np.array([[1, 2], [3, 4]])


@pytest.fixture
def data_prefix():
    return np.array([[1, 2], [3, 4]])


@pytest.fixture
def df():
    return pd.DataFrame({"a": [1, 2], "b": [3, 4]})


@pytest.fixture
def expected_rec():
    return np.rec.array([(1, 2), (3, 4)], dtype=[("0", "<i8"), ("1", "<i8")])


@pytest.fixture
def expected_rec_dict():
    return np.rec.array([(1, 3), (2, 4)], dtype=[("a", "<i8"), ("b", "<i8")])


@pytest.fixture
def expected_rec_names():
    return np.rec.array([(1, 2), (3, 4)], dtype=[("x", "<i8"), ("y", "<i8")])


@pytest.fixture
def expected_rec_prefix():
    return np.rec.array([(1, 2), (3, 4)], dtype=[("data_0", "<i8"), ("data_1", "<i8")])


def test_ensure_rec_numpy(data, expected_rec):
    rec = ensure_rec(data)
    assert_array_equal(rec, expected_rec)


def test_ensure_rec_dict(data_dict, expected_rec_dict):
    rec_dict = ensure_rec(data_dict)
    assert_array_equal(rec_dict, expected_rec_dict)


def test_ensure_rec_names(data_names, expected_rec_names):
    rec_names = ensure_rec(data_names, names=["x", "y"])
    assert_array_equal(rec_names, expected_rec_names)


def test_ensure_rec_prefix(data_prefix, expected_rec_prefix):
    rec_prefix = ensure_rec(data_prefix, column_prefix="data_")
    assert_array_equal(rec_prefix, expected_rec_prefix)


def test_ensure_rec_dataframe(df, expected_rec_dict):
    rec_df = ensure_rec(df)
    assert_array_equal(rec_df, expected_rec_dict)


def test_add_derived_numpy():
    # Test adding derived parameter to numpy recarray
    data = np.rec.array([(1, 2), (3, 4)], names=["x", "y"])
    new_param = "z"
    derived = data["x"] + data["y"]
    result = add_derived(data, new_param, derived)
    assert np.array_equal(result[new_param], np.array([3, 7]))


def test_add_derived_pandas():
    # Test adding derived parameter to pandas DataFrame
    data = pd.DataFrame({"x": [1, 3], "y": [2, 4]})
    new_param = "z"
    derived = data["x"] + data["y"]
    result = add_derived(data, new_param, derived)
    assert np.array_equal(result[new_param], np.array([3, 7]))


def test_add_derived_numpy_arr():
    # Test adding derived parameter to numpy rarray
    data = np.array([[1, 2], [3, 4]])
    new_param = "z"
    derived = np.array([3, 7])
    result = add_derived(data, new_param, derived, names=["x", "y"])
    assert np.array_equal(result[new_param], np.array([3, 7]))
    assert np.array_equal(result["x"], np.array([1, 3]))


def test_check_names(data, data_dict, expected_rec):
    names = ["col0", "col1"]
    assert check_if_names_is_used_correctly(names, data) == names
    assert check_if_names_is_used_correctly(names, data_dict) is None
    assert check_if_names_is_used_correctly(names, expected_rec) is None
