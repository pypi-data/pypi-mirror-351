# Copyright (C) 2022 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher

import numpy as np
from cosmic_toolbox import logger
from scipy.optimize import minimize
from scipy.stats import gaussian_kde
from tqdm.auto import trange

LOGGER = logger.get_logger(__name__)


def get_bestfit(samples, lnprobs=None, bestfit_method="mode"):
    """
    Get the best fit value each parameter of the sample.

    :param samples: rec array with samples
    :param lnprobs: array with log probabilities of the samples
        (optional, default: None)
    :param bestfit_method: method to use for best fit, options:
        mode: mode of the distribution (default)
        mean: mean of the distribution
        median: median of the distribution
        best_sample: sample with the highest log probability
    :return: best fit value for each parameter
    """
    if bestfit_method == "mode":
        lim = [np.min(samples), np.max(samples)]
        return mode(samples, lim)
    elif bestfit_method == "mean":
        return np.mean(samples)
    elif bestfit_method == "median":
        return np.median(samples)
    elif bestfit_method == "best_sample":
        if lnprobs is not None:
            return best_sample(samples, lnprobs)
        else:
            LOGGER.error(
                "best_sample cannot be computed without logprobability of"
                "the samples."
            )
            LOGGER.info("mode is used instead")
            lim = [np.min(samples), np.max(samples)]
            return mode(samples, lim)
    else:
        LOGGER.error(f"{bestfit_method} is not known")
        LOGGER.info("mode is used instead")
        lim = [np.min(samples), np.max(samples)]
        return mode(samples, lim)


def best_sample(samples, lnprobs):
    """
    Get the sample with the highest log probability.

    :param samples: rec array with samples
    :param lnprobs: array with log probabilities of the samples
    :return: sample with the highest log probability
    """

    return samples[np.argmax(lnprobs)]


def get_means_and_medians(samples):
    """
    Get the mean and median of each parameter of the sample.

    :param samples: rec array with samples
    :return: mean and median of each parameter
    """
    names = samples.dtype.names
    means = np.empty(1, dtype=samples.dtype)
    medians = np.empty(1, dtype=samples.dtype)
    for n in names:
        means[n] = np.mean(samples[n]).item()
        medians[n] = np.median(samples[n]).item()
    return means, medians


def get_best_likelihood(
    params_chain,
    lnprobs,
    emu,
    cl_fid,
    inv_C,
    ells,
    lims,
    prior_ind=[],
    gauss_mean=[],
    gauss_sigma=[],
    use_best_n=1,
):
    """
    Get the best likelihood value of the chain by minimizing the chi2.

    :param params_chain: rec array with samples
    :param lnprobs: array with log probabilities of the samples
    :param emu: emulator of the power spectrum
    :param cl_fid: fiducial power spectrum
    :param inv_C: inverse covariance matrix
    :param ells: ell values
    :param lims: limits of the parameters
    :param prior_ind: indices of the parameters with a gaussian prior
    :param gauss_mean: mean of the gaussian prior
    :param gauss_sigma: sigma of the gaussian prior
    :param use_best_n: number of best samples to use for the minimization
    :return: bool if successful minimization, best likelihood value and best lnprob
    """
    if use_best_n == 1:
        bl = params_chain[np.argmax(lnprobs)]
    else:
        sorted_indices = np.unique(-lnprobs, return_index=True)[1][:use_best_n]
        bl = params_chain[sorted_indices]

    def chi2(cosmo_p, cl_fid, inv_C, ells, lims):
        for i, p in enumerate(cosmo_p):
            if (p < lims[i, 0]) or (p > lims[i, 1]):
                return np.inf
        cl = emu(cosmo_p.reshape(1, -1), ell=ells).flatten()

        def log_gauss(x, mu, sigma):
            return (
                -0.5 * (x - mu) ** 2 / sigma**2
            )  # + np.log(1.0/(np.sqrt(2*np.pi)*sigma))

        gaussian_add = 0
        for i, p in enumerate(prior_ind):
            gaussian_add += log_gauss(cosmo_p[p], gauss_mean[i], gauss_sigma[i])
        diff = cl - cl_fid
        return 0.5 * (diff.dot(inv_C) * diff).sum() - gaussian_add

    if use_best_n == 1:
        x0 = np.zeros(len(bl))
        for i, p in enumerate(bl):
            x0[i] = p
        best_l = np.empty(1, dtype=params_chain.dtype)
        res = minimize(
            chi2,
            x0,
            args=(cl_fid, inv_C, ells, lims),
            method="Nelder-Mead",
            options={"maxiter": 5000},
        )
        best_l = np.empty(1, dtype=params_chain.dtype)
        if res.success:
            for i, p in enumerate(params_chain.dtype.names):
                best_l[p] = res.x[i]
            return True, best_l, -res.fun
        else:
            best_l[0] = params_chain[np.argmax(lnprobs)]
            return False, best_l, np.max(lnprobs)
    else:
        success = True
        best_l = np.empty(use_best_n, dtype=params_chain.dtype)
        for ii in trange(use_best_n):
            x0 = np.zeros(len(bl[ii]))
            for i, p in enumerate(bl[ii]):
                x0[i] = p
            res = minimize(
                chi2,
                x0,
                args=(cl_fid, inv_C, ells, lims),
                method="Nelder-Mead",
            )  # options={'maxiter':5000})
            if res.success:
                for i, p in enumerate(params_chain.dtype.names):
                    best_l[ii][p] = res.x[i]
            else:
                success = False
                best_l[ii] = params_chain[np.argmax(lnprobs)]
        return success, get_means_and_medians(best_l)[1], np.max(lnprobs)


def get_best_likelihood_from_MCMC(params_chain, lnprobs):
    """
    Get the best likelihood value of the chain by maximizing the log probability.

    :param params_chain: rec array with samples
    :param lnprobs: array with log probabilities of the samples
    :return: best likelihood value
    """
    bl = np.empty(1, dtype=params_chain.dtype)
    bl[0] = params_chain[np.argmax(lnprobs)]
    return bl, np.max(lnprobs)


def mode(sample, lim):
    """
    Get the mode of a sample.

    :param sample: 1D array with samples
    :param lim: limits of the parameter
    :return: mode of the sample
    """
    x = np.linspace(lim[0], lim[1])
    kde = gaussian_kde(sample)
    func = lambda x: -kde(x)  # noqa
    res = minimize(func, x[np.argmax(kde(x))])
    assert -res.fun >= np.max(kde(x)), "Finding mode failed"
    return res.x[0]


def get_mode(samples, lims):
    """
    Get the mode of the sample for each parameter.

    :param samples: rec array with samples
    :param lims: limits of the parameters
    :return: mode of the sample
    """
    names = samples.dtype.names
    modes = np.empty(1, dtype=samples.dtype)
    for i, n in enumerate(names):
        modes[n] = mode(samples[n], lims[i, :])
    return modes


def get_mean_median_best_likelihood_from_MCMC(params_chain, lnprobs):
    """
    Get the mean and median best likelihood of the samples of the chain.

    :param params_chain: rec array with samples
    :param lnprobs: array with log probabilities of the samples
    :return: mean and median value of the 10 best likelihood samples
    """
    sorted_indices = np.unique(-lnprobs, return_index=True)[1][:10]
    samples = params_chain[sorted_indices]
    return get_means_and_medians(samples)


def get_all_bl_estimates(
    params_chain,
    lnprobs,
    emu,
    cl_fid,
    inv_C,
    ells,
    lims,
    prior_ind=[],
    gauss_mean=[],
    gauss_sigma=[],
    just_names=False,
    use_best_n=1,
    both_minimization=False,
    flat_chi2minimization=False,
):
    """
    Get all the best likelihood estimates.

    :param params_chain: rec array with samples
    :param lnprobs: array with log probabilities of the samples
    :param emu: emulator (or any function that returns the observable)
    :param cl_fid: fiducial power spectrum
    :param inv_C: inverse covariance matrix
    :param ells: array with multipoles
    :param lims: limits of the parameters
    :param prior_ind: indices of the parameters with priors
    :param gauss_mean: mean of the Gaussian priors
    :param gauss_sigma: standard deviation of the Gaussian priors
    :param just_names: if True, only return the names of the best likelihood estimates
    :param use_best_n: number of best likelihood samples to use
    :param both_minimization: if True, use both minimizations
    :param flat_chi2minimization: if True, use chi2 minimization without Gaussian priors
    :return: array with best likelihood estimates
    """
    names = [
        "means",
        "medians",
        "blMCMC",
        "blmeanMCMC",
        "blmedianMCMC",
        "mode",
        "chi2minimization",
    ]
    if both_minimization:
        names.append("improved chi2minimization")
    if flat_chi2minimization:
        names.append("flat_chi2minimization")
    if just_names:
        return names
    bl = []

    mean, median = get_means_and_medians(params_chain)
    bl.append(mean)
    bl.append(median)

    bl.append(get_best_likelihood_from_MCMC(params_chain, lnprobs)[0])

    mean, median = get_mean_median_best_likelihood_from_MCMC(params_chain, lnprobs)
    bl.append(mean)
    bl.append(median)

    bl.append(get_mode(params_chain, lims))

    if both_minimization:
        bl.append(
            get_best_likelihood(
                params_chain,
                lnprobs,
                emu,
                cl_fid,
                inv_C,
                ells,
                lims,
                prior_ind,
                gauss_mean,
                gauss_sigma,
                use_best_n=1,
            )[1]
        )
    bl.append(
        get_best_likelihood(
            params_chain,
            lnprobs,
            emu,
            cl_fid,
            inv_C,
            ells,
            lims,
            prior_ind,
            gauss_mean,
            gauss_sigma,
            use_best_n=use_best_n,
        )[1]
    )
    if flat_chi2minimization:
        bl.append(
            get_best_likelihood(
                params_chain,
                lnprobs,
                emu,
                cl_fid,
                inv_C,
                ells,
                lims,
                prior_ind=[],
            )[1]
        )
    return bl, names


def get_all_bl_estimates_except_mode(
    params_chain,
    lnprobs,
    emu,
    cl_fid,
    inv_C,
    ells,
    lims,
    prior_ind=[],
    gauss_mean=[],
    gauss_sigma=[],
    just_names=False,
    use_best_n=1,
    both_minimization=False,
    flat_chi2minimization=False,
):
    """
    Get all the best likelihood estimates except the mode.

    :param params_chain: rec array with samples
    :param lnprobs: array with log probabilities of the samples
    :param emu: emulator
    :param cl_fid: fiducial power spectrum
    :param inv_C: inverse covariance matrix
    :param ells: array with multipoles
    :param lims: limits of the parameters
    :param prior_ind: indices of the parameters with priors
    :param gauss_mean: mean of the Gaussian priors
    :param gauss_sigma: standard deviation of the Gaussian priors
    :param just_names: if True, only return the names of the best likelihood estimates
    :param use_best_n: number of best likelihood samples to use
    :param both_minimization: if True, use both minimizations
    :param flat_chi2minimization: if True, use chi2 minimization without Gaussian priors
    :return: array with best likelihood estimates
    """
    names = [
        "means",
        "medians",
        "blMCMC",
        "blmeanMCMC",
        "blmedianMCMC",
        "chi2minimization",
    ]
    if both_minimization:
        names.append("improved chi2minimization")
    if flat_chi2minimization:
        names.append("flat_chi2minimization")
    if just_names:
        return names
    bl = []

    mean, median = get_means_and_medians(params_chain)
    bl.append(mean)
    bl.append(median)

    bl.append(get_best_likelihood_from_MCMC(params_chain, lnprobs)[0])

    mean, median = get_mean_median_best_likelihood_from_MCMC(params_chain, lnprobs)
    bl.append(mean)
    bl.append(median)

    if both_minimization:
        bl.append(
            get_best_likelihood(
                params_chain,
                lnprobs,
                emu,
                cl_fid,
                inv_C,
                ells,
                lims,
                prior_ind,
                gauss_mean,
                gauss_sigma,
                use_best_n=1,
            )[1]
        )
    bl.append(
        get_best_likelihood(
            params_chain,
            lnprobs,
            emu,
            cl_fid,
            inv_C,
            ells,
            lims,
            prior_ind,
            gauss_mean,
            gauss_sigma,
            use_best_n=use_best_n,
        )[1]
    )
    if flat_chi2minimization:
        bl.append(
            get_best_likelihood(
                params_chain,
                lnprobs,
                emu,
                cl_fid,
                inv_C,
                ells,
                lims,
                prior_ind=[],
            )[1]
        )
    return bl, names
