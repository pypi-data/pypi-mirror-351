# Copyright (C) 2022 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher

import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import root_scalar


def interpolate(sample, bins=1000):
    """
    Interpolate a histogram of the sample.

    :param sample: The sample to interpolate.
    :param bins: The number of bins to use for the histogram.
    :return: A function that can be used to evaluate the interpolated histogram.
    """
    hist, bin_edges = np.histogram(sample, bins=bins, density=True)
    central_values = (bin_edges[:-1] + bin_edges[1:]) / 2
    return interp1d(central_values, hist, fill_value=0, bounds_error=False)


def sort_according_to_lnprobs(samples, lnprobs):
    """
    Sort the samples according to the log-probabilities.

    :param samples: The samples.
    :param lnprobs: The log-probabilities of the samples.
    :return: The sorted samples.
    """
    return samples[np.argsort(-lnprobs)]


def update_interval(p, p_min, p_max):
    """
    Update the interval.

    :param p: The new value.
    :param p_min: The current minimum.
    :param p_max: The current maximum.
    :return: The new minimum, maximum, and a flag indicating if the minimum or
        maximum changed.
    """
    changed = False
    if p < p_min:
        p_min = p
        changed = 1
    elif p > p_max:
        p_max = p
        changed = 2
    return p_min, p_max, changed


def check_threshold(func, p_min, p_max, threshold):
    """
    Check if the integral of the function over the interval is above the
    threshold.

    :param func: The function to integrate.
    :param p_min: The minimum of the interval.
    :param p_max: The maximum of the interval.
    :param threshold: The threshold.
    :return: True if the integral is above the threshold, False otherwise.
    """
    # return quad(func, p_min, p_max)[0] > threshold
    p = np.linspace(p_min, p_max, 1000)
    return np.trapz(func(p), p) > threshold


def find_threshold_param(func, p_min, p_max, which_changed, credible_interval=0.68):
    """
    Find the parameter value at which the integral of the function over the
    interval is above the threshold.

    :param func: The function to integrate.
    :param p_min: The minimum of the interval.
    :param p_max: The maximum of the interval.
    :param which_changed: A flag indicating if the minimum or maximum changed.
    :param credible_interval: The credible interval.
    :return: The parameter value at which the integral is above the threshold.
    """
    assert which_changed in [1, 2], "which_changed must be 1 or 2"
    if which_changed == 1:

        def f(p):
            x = np.linspace(p, p_max, 1000)
            return np.trapz(func(x), x) - credible_interval

        res = root_scalar(f, x0=p_min, x1=p_max)
        return res.root, p_max

    # which_changed == 2:
    def f(p):
        x = np.linspace(p_min, p, 1000)
        return np.trapz(func(x), x) - credible_interval

    res = root_scalar(f, x0=p_min, x1=p_max)
    return p_min, res.root
