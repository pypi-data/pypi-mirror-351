# Copyright (C) 2023 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher


import os

import numpy as np
import pytest

from trianglechain.bestfit import (
    get_all_bl_estimates,
    get_all_bl_estimates_except_mode,
    get_best_likelihood,
    get_bestfit,
)


def _get_abspath(filename):
    return os.path.join(os.path.dirname(__file__), filename)


@pytest.fixture
def samples():
    # samples that have best fit at (1, 1, 1)
    return np.load(_get_abspath("best_fit_data/mcmc_samples.npy"))


@pytest.fixture
def lnprobs():
    return np.load(_get_abspath("best_fit_data/lnprobs.npy"))


def dummy_emu(params, ell=None):
    # like emulator input with ell as dummy input
    x_values = np.arange(1, 11)
    return (
        params[:, 0, None] * x_values**3
        + params[:, 1, None] * x_values**2
        + params[:, 2, None] * x_values
    )


@pytest.fixture
def inv_c():
    covariance_matrix = np.diag((np.arange(1, 11)) ** 2)
    return np.linalg.inv(covariance_matrix)


@pytest.fixture
def mock_obs():
    return dummy_emu(np.array([[1, 1, 1]]))


def test_get_bestfit():
    np.random.seed(0)
    samples = np.random.normal(10, 1, 10000)
    lnprobs = -((samples - 10) ** 2)

    mean = get_bestfit(samples, bestfit_method="mean")
    median = get_bestfit(samples, bestfit_method="median")
    mode = get_bestfit(samples, bestfit_method="mode")
    best_sample = get_bestfit(samples, lnprobs, "best_sample")

    assert np.isclose(mean, 10, atol=0.1)
    assert np.isclose(median, 10, atol=0.1)
    assert np.isclose(mode, 10, atol=0.1)
    assert np.isclose(best_sample, 10, atol=0.1)


def test_errors():
    np.random.seed(0)
    samples = np.random.normal(10, 1, 10000)
    mode = get_bestfit(samples, bestfit_method="mode")
    no_lnprobs = get_bestfit(samples, bestfit_method="best_sample")
    assert mode == no_lnprobs
    unknown_method = get_bestfit(samples, bestfit_method="unknown")
    assert mode == unknown_method


def test_get_all_bl_estimates(samples, lnprobs, mock_obs, inv_c):
    lims = np.array([[-10, 10], [-10, 10], [-10, 10]])
    bl, names = get_all_bl_estimates(
        samples,
        lnprobs,
        dummy_emu,
        mock_obs,
        inv_c,
        ells=None,
        lims=lims,
        prior_ind=[],
        gauss_mean=[],
        gauss_sigma=[],
        just_names=False,
        use_best_n=1,
        both_minimization=True,
        flat_chi2minimization=True,
    )
    just_names = get_all_bl_estimates(
        samples,
        lnprobs,
        dummy_emu,
        mock_obs,
        inv_c,
        ells=None,
        lims=lims,
        prior_ind=[],
        gauss_mean=[],
        gauss_sigma=[],
        just_names=True,
        use_best_n=1,
        both_minimization=True,
        flat_chi2minimization=True,
    )
    assert len(bl) == len(names)
    assert names == just_names
    for b in bl:
        for n in b.dtype.names:
            if n == "a":
                assert np.isclose(b[n][0], 1, atol=0.1)
            elif n == "b":
                assert np.isclose(b[n][0], 1, atol=0.5)
            else:
                assert np.isclose(b[n][0], 1, atol=1)
    bl_prior, names = get_all_bl_estimates(
        samples,
        lnprobs,
        dummy_emu,
        mock_obs,
        inv_c,
        ells=None,
        lims=lims,
        prior_ind=[2],
        gauss_mean=[3],
        gauss_sigma=[0.1],
        just_names=False,
        use_best_n=1,
        both_minimization=True,
        flat_chi2minimization=True,
    )
    for i in range(len(bl_prior)):
        if (names[i] != "chi2minimization") & (names[i] != "improved chi2minimization"):
            assert bl_prior[i]["c"] == bl[i]["c"]
        else:
            assert np.isclose(bl_prior[i]["c"][0], 3, atol=0.5)


def test_get_all_bl_estimates_except_mode(samples, lnprobs, mock_obs, inv_c):
    lims = np.array([[-10, 10], [-10, 10], [-10, 10]])
    bl, names = get_all_bl_estimates_except_mode(
        samples,
        lnprobs,
        dummy_emu,
        mock_obs,
        inv_c,
        ells=None,
        lims=lims,
        prior_ind=[],
        gauss_mean=[],
        gauss_sigma=[],
        just_names=False,
        use_best_n=1,
        both_minimization=True,
        flat_chi2minimization=True,
    )
    just_names = get_all_bl_estimates_except_mode(
        samples,
        lnprobs,
        dummy_emu,
        mock_obs,
        inv_c,
        ells=None,
        lims=lims,
        prior_ind=[],
        gauss_mean=[],
        gauss_sigma=[],
        just_names=True,
        use_best_n=1,
        both_minimization=True,
        flat_chi2minimization=True,
    )
    assert len(bl) == len(names)
    assert names == just_names
    for b in bl:
        for n in b.dtype.names:
            if n == "a":
                assert np.isclose(b[n][0], 1, atol=0.1)
            elif n == "b":
                assert np.isclose(b[n][0], 1, atol=0.5)
            else:
                assert np.isclose(b[n][0], 1, atol=1)
    bl_prior, names = get_all_bl_estimates_except_mode(
        samples,
        lnprobs,
        dummy_emu,
        mock_obs,
        inv_c,
        ells=None,
        lims=lims,
        prior_ind=[2],
        gauss_mean=[3],
        gauss_sigma=[0.1],
        just_names=False,
        use_best_n=1,
        both_minimization=True,
        flat_chi2minimization=True,
    )
    for i in range(len(bl_prior)):
        if (names[i] != "chi2minimization") & (names[i] != "improved chi2minimization"):
            assert bl_prior[i]["c"] == bl[i]["c"]
        else:
            assert np.isclose(bl_prior[i]["c"][0], 3, atol=0.5)


def test_get_best_likelihood(samples, lnprobs, mock_obs, inv_c):
    lims = np.array([[-10, 10], [-10, 10], [-10, 10]])
    success, bestfit, bestfit_lnprob = get_best_likelihood(
        samples, lnprobs, dummy_emu, mock_obs, inv_c, ells=None, lims=lims
    )
    assert success

    success, bestfit, bestfit_lnprob = get_best_likelihood(
        samples,
        lnprobs,
        dummy_emu,
        mock_obs,
        inv_c,
        ells=None,
        lims=lims,
        use_best_n=10,
    )
    assert success
    lims = np.array([[100, 200], [-10, 10], [-10, 10]])
    success, bestfit, bestfit_lnprob = get_best_likelihood(
        samples,
        lnprobs,
        dummy_emu,
        mock_obs,
        inv_c,
        ells=None,
        lims=lims,
        prior_ind=[0],
        gauss_mean=[-100],
        gauss_sigma=[0.01],
    )
    assert not success
    assert bestfit == samples[np.argmax(lnprobs)]

    lims = np.array([[100, 200], [-10, 10], [-10, 10]])
    success, bestfit, bestfit_lnprob = get_best_likelihood(
        samples,
        lnprobs,
        dummy_emu,
        mock_obs,
        inv_c,
        ells=None,
        lims=lims,
        prior_ind=[0],
        gauss_mean=[-100],
        gauss_sigma=[0.01],
        use_best_n=10,
    )
    assert not success


def test_get_all_bl_estimates_wo_both_min_and_flat(samples, lnprobs, mock_obs, inv_c):
    lims = np.array([[-10, 10], [-10, 10], [-10, 10]])
    bl, names = get_all_bl_estimates(
        samples,
        lnprobs,
        dummy_emu,
        mock_obs,
        inv_c,
        ells=None,
        lims=lims,
        prior_ind=[],
        gauss_mean=[],
        gauss_sigma=[],
        just_names=False,
        use_best_n=1,
        both_minimization=False,
        flat_chi2minimization=False,
    )
    just_names = get_all_bl_estimates(
        samples,
        lnprobs,
        dummy_emu,
        mock_obs,
        inv_c,
        ells=None,
        lims=lims,
        prior_ind=[],
        gauss_mean=[],
        gauss_sigma=[],
        just_names=True,
        use_best_n=1,
        both_minimization=False,
        flat_chi2minimization=False,
    )
    assert len(bl) == len(names)
    assert names == just_names
    for b in bl:
        for n in b.dtype.names:
            if n == "a":
                assert np.isclose(b[n][0], 1, atol=0.1)
            elif n == "b":
                assert np.isclose(b[n][0], 1, atol=0.5)
            else:
                assert np.isclose(b[n][0], 1, atol=1)
    bl_prior, names = get_all_bl_estimates(
        samples,
        lnprobs,
        dummy_emu,
        mock_obs,
        inv_c,
        ells=None,
        lims=lims,
        prior_ind=[2],
        gauss_mean=[3],
        gauss_sigma=[0.1],
        just_names=False,
        use_best_n=1,
        both_minimization=False,
        flat_chi2minimization=False,
    )
    for i in range(len(bl_prior)):
        if (names[i] != "chi2minimization") & (names[i] != "improved chi2minimization"):
            assert bl_prior[i]["c"] == bl[i]["c"]
        else:
            assert np.isclose(bl_prior[i]["c"][0], 3, atol=0.5)


def test_get_all_bl_estimates_except_mode_wo_both_min_and_flat(
    samples, lnprobs, mock_obs, inv_c
):
    lims = np.array([[-10, 10], [-10, 10], [-10, 10]])
    bl, names = get_all_bl_estimates_except_mode(
        samples,
        lnprobs,
        dummy_emu,
        mock_obs,
        inv_c,
        ells=None,
        lims=lims,
        prior_ind=[],
        gauss_mean=[],
        gauss_sigma=[],
        just_names=False,
        use_best_n=1,
        both_minimization=False,
        flat_chi2minimization=False,
    )
    just_names = get_all_bl_estimates_except_mode(
        samples,
        lnprobs,
        dummy_emu,
        mock_obs,
        inv_c,
        ells=None,
        lims=lims,
        prior_ind=[],
        gauss_mean=[],
        gauss_sigma=[],
        just_names=True,
        use_best_n=1,
        both_minimization=False,
        flat_chi2minimization=False,
    )
    assert len(bl) == len(names)
    assert names == just_names
    for b in bl:
        for n in b.dtype.names:
            if n == "a":
                assert np.isclose(b[n][0], 1, atol=0.1)
            elif n == "b":
                assert np.isclose(b[n][0], 1, atol=0.5)
            else:
                assert np.isclose(b[n][0], 1, atol=1)
    bl_prior, names = get_all_bl_estimates_except_mode(
        samples,
        lnprobs,
        dummy_emu,
        mock_obs,
        inv_c,
        ells=None,
        lims=lims,
        prior_ind=[2],
        gauss_mean=[3],
        gauss_sigma=[0.1],
        just_names=False,
        use_best_n=1,
        both_minimization=False,
        flat_chi2minimization=False,
    )
    for i in range(len(bl_prior)):
        if (names[i] != "chi2minimization") & (names[i] != "improved chi2minimization"):
            assert bl_prior[i]["c"] == bl[i]["c"]
        else:
            assert np.isclose(bl_prior[i]["c"][0], 3, atol=0.5)
