# Copyright (C) 2023 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Tomasz Kacprzak, Silvan Fischbacher

import numpy as np
import pandas as pd
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import logger

LOGGER = logger.get_logger(__file__)


def ensure_rec(data, names=None, column_prefix=""):
    """
    Ensure that the input data is a numpy record array (recarray).
    If the input is already a recarray, it is returned as-is.
    If it is a 2D numpy array, a pandas dataframe, or a dictionary of arrays,
    it is converted to a recarray with automatically generated field names.

    :param data: The input data to ensure is a recarray.
        If a 2D numpy array, a pandas dataframe, or a dictionary of arrays,
        it will be converted to a recarray with automatically generated field names.
    :type data: numpy.ndarray or dict or pandas.DataFrame

    :param names: A list of field names to use if the input data is a 2D numpy array.
        The length of this list should match the number of columns in the array.
        If not provided, field names will be automatically generated.
    :type names: list of str, optional

    :param column_prefix: A prefix to add to the automatically generated field names
        for the input data. This can be useful for distinguishing between multiple
        rec arrays with similar fields.
    :type column_prefix: str, optional

    :return: The input data as a recarray.
    :rtype: numpy.recarray

    Example usage:
        >>> data = np.array([[1, 2], [3, 4]])
        >>> rec = ensure_rec(data)
        >>> print(rec)
        [(1, 2) (3, 4)]

        >>> data_dict = {'a': [1, 2], 'b': [3, 4]}
        >>> rec_dict = ensure_rec(data_dict)
        >>> print(rec_dict)
        [(1, 3) (2, 4)]

        >>> data_names = np.array([[1, 2], [3, 4]])
        >>> rec_names = ensure_rec(data_names, names=['x', 'y'])
        >>> print(rec_names)
        [(1, 2) (3, 4)]

        >>> data_prefix = np.array([[1, 2], [3, 4]])
        >>> rec_prefix = ensure_rec(data_prefix, column_prefix='data_')
        >>> print(rec_prefix)
        [(1, 2) (3, 4)]

        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        >>> rec_df = ensure_rec(df)
        >>> print(rec_df)
        [(1, 3) (2, 4)]
    """
    if isinstance(data, pd.DataFrame):
        data = data.to_records(index=False)

    if (names is not None) and (isinstance(data, np.ndarray)):
        assert (
            len(names) == data.shape[1]
        ), "number of names does not match the number of parameters"
        data = at.arr2rec(data, names)

    if isinstance(data, dict):
        return at.dict2rec(data)

    if data.dtype.names is not None:
        # already recarray, but maybe without lenght
        return np.atleast_1d(data)

    else:
        n_rows, n_cols = data.shape
        dtype = np.dtype(
            dict(
                formats=[data.dtype] * n_cols,
                names=[f"{column_prefix}{i}" for i in range(n_cols)],
            )
        )
        rec = np.empty(n_rows, dtype=dtype)
        for i in range(n_cols):
            rec[f"{column_prefix}{i}"] = data[:, i]
        return rec


def add_derived(data, new_param, derived, names=None):
    """
    Adds a new derived parameter to the input data.

    :param data: The input data to add the derived parameter to.
        If a 2D numpy array, a pandas dataframe, or a dictionary of arrays,
        it will be converted to a recarray with automatically generated field names.
    :type data: numpy.ndarray or dict or pandas.DataFrame

    :param new_param: The name of the new derived parameter to add.
    :type new_param: str

    :param derived: The derived value of the new parameter.
    :type derived: np.ndarray or list or float

    :param names: A list of field names to use if the input data is a 2D numpy array.
        The length of this list should match the number of columns in the array.
        If not provided, field names will be automatically generated.
    :type names: list of str, optional

    :return: The input data with the new derived parameter added.
    :rtype: numpy.recarray

    Example usage:

        >>> data = add_derived(data, "S8", data["sigma8"] * np.sqrt(data["omega_m"]/0.3))

    """
    # Make a rec array out of it
    data = ensure_rec(data, names=names)

    # Add new column to data
    data = at.add_cols(data, [new_param])

    # Set values of new column to the derived value
    data[new_param] = derived

    return data


def check_if_names_is_used_correctly(names, data):
    """
    Check if the names argument is used correctly.

    :param names: A list of field names to use if the input data is a 2D numpy array.
    :param data: The input data to check.
    :return: corrected names
    """

    is_ndarray = isinstance(data, np.ndarray) and not isinstance(data, np.recarray)
    if (names is not None) and (not is_ndarray):
        LOGGER.warning(
            "The names argument is only used if data is a non-structured numpy array. "
            "Probably you want to use the params argument instead. "
            "The names argument will be ignored."
        )
        names = None
    return names


def get_samples(
    n_samples=100000,
    n_dims=None,
    names=None,
    column_prefix="col",
    covmat=None,
    mean=None,
):
    """
    Get a random set of samples from a multivariate Gaussian distribution.

    :param n_samples: The number of samples to generate.
    :param n_dims: The number of dimensions of the samples.
    :param names: A list of field names to use if the input data is a 2D numpy array.
        The length of this list should match the number of columns in the array.
        If not provided, field names will be automatically generated.
    :param column_prefix: A prefix to add to the automatically generated field names
        for the input data.
    :param covmat: The covariance matrix of the distribution.
    :param mean: The mean of of each parameter in the distribution.
    :return: The samples.
    """
    # Get dimension from default or from input data
    if n_dims is None:
        if (names is None) & (covmat is None) & (mean is None):
            n_dims = 4
        else:
            if names is not None:
                n_dims = len(names)
            elif mean is not None:
                n_dims = len(mean)
            else:
                n_dims = np.shape(covmat)[0]

    if covmat is None:
        covmat = np.random.normal(size=(n_dims, n_dims))
        covmat = np.dot(covmat.T, covmat)
    if mean is None:
        mean = np.random.uniform(size=(n_dims))
    samples = np.random.multivariate_normal(mean=mean, cov=covmat, size=(n_samples))
    samples = ensure_rec(samples, names, column_prefix)
    return samples
