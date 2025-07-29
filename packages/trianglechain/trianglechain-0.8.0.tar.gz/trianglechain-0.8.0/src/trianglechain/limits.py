# Copyright (C) 2022 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher


import arviz
import numpy as np
from cosmic_toolbox.logger import get_logger
from scipy.stats import norm

from trianglechain import utils_pj_hpd

LOGGER = get_logger(__file__)


def get_levels(
    samples, lnprob=None, levels_method="hdi", credible_interval=0.68, sigma_one_tail=3
):
    """
    Get the upper and lower level of the credible interval.
    If the credible interval is two tailed, the upper and lower level are
    returned. If the credible interval is one tailed, only the lower/upper level is
    returned.

    :param samples: np.ndarray with the given samples
    :param lnprob: logprobability of the samples, used for some methods,
        defaults to None
    :param levels_method: method how to compute the levels,
        options: "hdi", "percentile", "PJ_HPD",
        defaults to "hdi"
    :param credible_interval: which credible interval should be used, defaults to 0.68
    :param sigma_one_tail: how many sigma should be used to decide if one tailed
        credible interval should be used
        defaults to 3
    :return: upper and lower limit (or only lower/upper limit if one tailed)
    """

    two_tail, side = check_if_two_tailed(samples, credible_interval, sigma_one_tail)
    if two_tail:
        return (
            get_two_tailed_levels(samples, lnprob, levels_method, credible_interval),
            two_tail,
            side,
        )
    else:
        return get_one_tailed_levels(samples, credible_interval, side), two_tail, side


def check_if_two_tailed(samples, credible_interval, sigma_one_tail):
    """
    Check if the credible interval is two tailed or one tailed.

    :param samples: np.ndarray with the given samples
    :param credible_interval: which credible interval should be used, defaults to 0.68
    :param sigma_one_tail: how many sigma should be used to decide if one tailed
        credible interval should be used
        defaults to 3
    :return: True if two tailed, False if one tailed; if one tailed, if upper or lower
    """
    hdi_of_sample = arviz.hdi(samples, hdi_prob=credible_interval)

    if cdf(samples, hdi_of_sample[0]) < sigma_to_cdf(sigma_one_tail, side="right"):
        return False, "upper"
    elif cdf(samples, hdi_of_sample[1]) > sigma_to_cdf(sigma_one_tail, side="left"):
        return False, "lower"
    else:
        return True, None


def sigma_to_cdf(sigma, side="left"):
    """
    Convert sigma to CDF for a standard normal distribution.

    :param sigma: sigma value
    :param side: "left" for left-tailed CDF, "right" for right-tailed CDF
    :return: CDF value
    """
    if side == "left":
        return norm.cdf(sigma)
    elif side == "right":
        return 1 - norm.cdf(sigma)
    else:
        raise ValueError(
            "Invalid value for 'side' argument. Expected 'left' or 'right'."
        )


def get_two_tailed_levels(
    samples, lnprob=None, levels_method="hdi", credible_interval=0.68
):
    """
    Get the upper and lower level of the credible interval.

    :param samples: np.ndarray with the given samples
    :param lnprob: logprobability of the samples, used for some methods,
        defaults to None
    :param levels_method: method how to compute the levels,
        options: "hdi", "percentile", "PJ_HPD",
        defaults to "hdi"
    :param credible_interval: which credible interval should be used, defaults to 0.68
    :return: upper and lower limit
    """
    if levels_method == "hdi":
        return hdi(samples, credible_interval)
    elif levels_method == "percentile":
        return percentile(samples, credible_interval)
    elif levels_method == "PJ_HPD":
        if lnprob is not None:
            return PJ_HPD(samples, lnprob, credible_interval)
        else:
            LOGGER.error(
                "PJ_HPD cannot be computed without probability of the samples."
            )
            LOGGER.info("hdi is used instead")
            return hdi(samples, credible_interval)
    else:
        LOGGER.error(f"{levels_method} is not known")
        LOGGER.info("hdi is used instead")
        return hdi(samples, credible_interval)


def get_one_tailed_levels(samples, credible_interval=0.68, side="upper"):
    """
    Get the upper or lower level of the credible interval.

    :param samples: np.ndarray with the given samples
    :param credible_interval: which credible interval should be used, defaults to 0.68
    :param side: "upper" or "lower" side of the credible interval
    :return: upper or lower limit
    """
    if side == "upper":
        return np.percentile(samples, 100 * credible_interval)
    elif side == "lower":
        return np.percentile(samples, 100 * (1 - credible_interval))
    else:
        raise ValueError(
            "Invalid value for 'side' argument. Expected 'upper' or 'lower'."
        )


def percentile(samples, credible_interval=0.68):
    """
    Returns the upper and lower percentile.

    :param samples: np.ndarray with the given samples
    :param credible_interval: which credible interval should be used, defaults to 0.68
    :return: upper and lower limit
    """
    s = 100 * (1 - credible_interval) / 2
    lower = np.percentile(samples, s)
    upper = np.percentile(samples, 100 - s)
    return lower, upper


def hdi(samples, credible_interval=0.68):
    """
    Returns the upper and lower limit using highest density interval

    :param samples: np.ndarray with the given samples
    :param credible_interval: which credible interval should be used, defaults to 0.68
    :return: upper and lower limit
    """
    lower, upper = arviz.hdi(samples, hdi_prob=credible_interval)
    return lower, upper


def PJ_HPD(
    samples,
    lnprobs,
    credible_interval=0.68,
    interpolator=utils_pj_hpd.interpolate,
    **interp_kwargs,
):
    """
    Returns the upper and lower limit using projected joint highest posterior density.
    see arXiv:2007.01844

    :param samples: np.ndarray with the given samples
    :param lnprobs: logprobability of the samples
    :param credible_interval: which credible interval should be used, defaults to 0.68
    :param interpolator: interpolation function, defaults to utils_pj_hpd.interpolate
    :param interp_kwargs: kwargs for the interpolation function
    :return: upper and lower limit
    """
    post_1D = interpolator(samples, **interp_kwargs)
    sorted_chain = utils_pj_hpd.sort_according_to_lnprobs(samples, lnprobs)
    p_min = sorted_chain[0]
    p_max = sorted_chain[0]
    for par in sorted_chain:
        p_min_new, p_max_new, changed = utils_pj_hpd.update_interval(par, p_min, p_max)
        if changed and utils_pj_hpd.check_threshold(
            post_1D, p_min_new, p_max_new, credible_interval
        ):
            p_min, p_max = utils_pj_hpd.find_threshold_param(
                post_1D, p_min_new, p_max_new, changed, credible_interval
            )
            break
        p_min = p_min_new
        p_max = p_max_new
    return p_min, p_max


def get_uncertainty_band(lower, upper):
    """
    Get the uncertainty band.

    :param lower: lower limit
    :param upper: upper limit
    :return: uncertainty band
    """
    return (upper - lower) / 2


def uncertainty(samples, model, **model_kwargs):
    """
    Get the uncertainty of the samples.

    :param samples: np.ndarray with the given samples
    :param model: model function to compute uncertainty
    :return: uncertainty
    """
    lower, upper = model(samples, **model_kwargs)
    return get_uncertainty_band(lower, upper)


def cdf(samples, value):
    """
    Get the cumulative distribution function.

    :param samples: np.ndarray with the given samples
    :param value: value to compute the cdf
    :return: cdf
    """
    return np.sum(samples < value) / len(samples)
