# Copyright (C) 2022 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher

import numpy as np
import pytest
from cosmic_toolbox import arraytools as at
from matplotlib import pyplot as plt

from trianglechain import TriangleChain
from trianglechain.make_subplots import scatter_density
from trianglechain.params import get_samples


def test_basic_plot():
    samples1 = get_samples()
    samples2 = get_samples()
    tri = TriangleChain(density_estimation_method="smoothing")
    tri.contour_cl(samples1, color="r")
    tri.contour_cl(samples2, color="b")

    tri = TriangleChain(fill=True)
    tri.contour_cl(
        samples1, color="r", plot_histograms_1D=False, line_kwargs={"zorder": 2}
    )
    plt.close("all")


def test_density_image():
    samples1 = get_samples()
    tri = TriangleChain(density_estimation_method="smoothing", n_bins=100)
    tri.density_image(samples1, cmap="inferno")
    tri.contour_cl(samples1, color="skyblue")
    plt.close("all")


def test_scatter_density():
    samples = get_samples()
    tri = TriangleChain(density_estimation_method="smoothing", n_bins=100)
    tri.scatter_density(samples, cmap="viridis")

    fig, ax = plt.subplots()
    x = np.random.normal(size=1000)
    y = np.random.normal(size=1000)
    scatter_density(ax, x, y)
    plt.close("all")


def test_n_points_scatter():
    samples = get_samples(10000)
    prob = np.ones(len(samples))
    tri = TriangleChain()
    tri.scatter(samples, n_points_scatter=10)
    tri.scatter_density(samples, n_points_scatter=10)
    tri.scatter_prob(samples, prob=prob, n_points_scatter=10)
    plt.close("all")


def test_scatter_prob():
    samples = np.random.rand(1000, 5)
    prob = (10 * samples[:, 0] - 0.1) ** 3

    tri = TriangleChain(colorbar=True, colorbar_label="normalized prob")
    tri.scatter_prob(samples, prob=prob, normalize_prob2D=True, normalize_prob1D=True)
    tri.scatter_prob(samples, prob=prob, normalize_prob2D=False, normalize_prob1D=True)
    prob = np.random.rand(1000)
    tri.scatter_prob(samples, prob=prob, normalize_prob2D=False, normalize_prob1D=False)
    plt.close("all")


def test_scatter():
    samples = get_samples()
    tri = TriangleChain(scatter_kwargs={"s": 1}, hist_kwargs={"lw": 10})
    tri.scatter(samples, color="pink")
    individual_color = ["pink" for _ in range(len(samples))]
    tri.scatter(samples, color=individual_color)
    plt.close("all")


def test_grouping_and_double_tri():
    samples1 = get_samples(n_dims=6)
    samples2 = get_samples(n_dims=6)
    kwargs = {
        "n_ticks": 3,
        "de_kwargs": {"smoothing_parameter2D": 0.3},
        "grouping_kwargs": {"n_per_group": (4, 2), "empty_ratio": 0.2},
        "fill": True,
        "grid": True,
    }

    # lower first
    tri = TriangleChain(labels=samples1.dtype.names, **kwargs)
    tri.contour_cl(samples1, color="r", label="sample1")
    tri.contour_cl(samples2, color="b", label="sample2", tri="upper", show_legend=True)

    # upper first
    tri = TriangleChain(density_estimation_method="smoothing", n_bins=100, **kwargs)
    tri.contour_cl(samples1, color="r", label="sample1", tri="upper")
    tri.contour_cl(samples2, color="b", label="sample2", show_legend=True)

    # lower, upper, first
    tri = TriangleChain(density_estimation_method="smoothing", n_bins=100, **kwargs)
    tri.contour_cl(samples1, color="r", label="sample1")
    tri.contour_cl(samples2, color="b", label="sample2", tri="upper")
    tri.contour_cl(samples1, color="r", label="sample1", tri="lower", show_legend=True)

    plt.close("all")


def test_upper_lower():
    samples1 = get_samples(n_dims=6)
    samples2 = get_samples(n_dims=6)

    tri = TriangleChain()
    tri.contour_cl(samples1, color="r", tri="upper")
    tri.contour_cl(samples2, color="b", tri="lower")

    tri = TriangleChain()
    tri.contour_cl(samples1, color="r", tri="lower")
    tri.contour_cl(samples2, color="b", tri="upper")

    plt.close("all")


def test_alpha():
    samples1 = get_samples()
    samples2 = get_samples(n_dims=6)
    tri = TriangleChain(add_empty_plots_like=samples2)
    tri.contour_cl(samples1, color="r", alpha1D=0.5)
    tri.contour_cl(samples2, color="b", alpha2D=0.2)

    tri = TriangleChain(alpha=0.1)
    tri.contour_cl(samples1)

    tri = TriangleChain(alpha=0.1, alpha2D=0.2, alpha1D=0.3)
    tri.contour_cl(samples1)

    tri = TriangleChain()
    tri.contour_cl(samples1, alpha=0.1)

    plt.close("all")


def test_not_all_params():
    n_dims = 6
    samples1 = get_samples(n_samples=20000, n_dims=n_dims)
    samples2 = get_samples(n_samples=20000, n_dims=n_dims)

    tri = TriangleChain(params=["col0", "col2", "col5"])
    tri.contour_cl(samples1, color="r")
    tri.contour_cl(samples2, color="b")

    tri = TriangleChain(size=1, params=["col0", "col2", "col5"], params_from=samples1)
    tri.contour_cl(samples1, color="r")
    tri.contour_cl(samples2, color="b")
    x, y = tri.fig.get_size_inches()
    assert x == y == 3

    sample1 = get_samples(names=["a", "b"])
    sample2 = get_samples(names=["b", "c"])
    ranges = {"a": (-10, 10)}

    tri = TriangleChain(params_from=[sample1, sample2], ranges=ranges)
    tri.contour_cl(sample1)
    tri.contour_cl(sample2)

    tri = TriangleChain(params_from=sample1, ranges=ranges)
    tri.contour_cl(sample1)
    tri.contour_cl(sample2)

    plt.close("all")


def test_density_image_with_alpha():
    samples1 = get_samples(mean=np.ones(5))
    kwargs = {"alpha_for_low_density": True, "alpha_threshold": 0.1}
    tri = TriangleChain(**kwargs)
    tri.density_image(samples1, cmap="jet")
    tri.contour_cl(samples1, color="skyblue")

    plt.close("all")


def test_vline():
    samples1 = get_samples(covmat=np.eye(5))
    kwargs = {"scatter_kwargs": {"s": 500, "marker": "*", "zorder": 299}}
    tri = TriangleChain(density_estimation_method="smoothing", **kwargs)
    tri.contour_cl(samples1)
    tri.scatter(
        samples1[0],
        plot_histograms_1D=False,
        scatter_vline_1D=True,
    )
    tri.scatter(
        samples1[1:5],
        plot_histograms_1D=False,
        scatter_vline_1D=True,
    )

    plt.close("all")


def test_credible_intervals():
    samples = np.random.multivariate_normal(
        mean=np.zeros(3), cov=np.eye(3), size=100000
    )
    samples = at.arr2rec(samples, names=["a", "b", "c"])
    tri = TriangleChain(labels=["$a$", "$b$", "$c$"])
    tri.contour_cl(samples, show_values=True, credible_interval=0.5)

    tri = TriangleChain(labels=["$a$", "$b$", "$c$"])
    tri.contour_cl(samples[samples["a"] < -0.5], show_values=True)

    tri = TriangleChain(labels=["$a$", "$b$", "$c$"])
    tri.contour_cl(samples[samples["a"] > 0.5], show_values=True)

    plt.close("all")


def test_density_estimation_methods():
    samples = get_samples(n_samples=10000)
    tri = TriangleChain()
    tri.contour_cl(samples, density_estimation_method="smoothing")
    tri.contour_cl(samples, density_estimation_method="hist")
    tri.contour_cl(samples, density_estimation_method="kde")
    tri.contour_cl(samples, density_estimation_method="median_filter")
    tri.contour_cl(samples, density_estimation_method="gaussian_mixture")

    with pytest.raises(Exception):
        tri.contour_cl(samples, density_estimation_method="by_eye")

    with pytest.raises(Exception):
        tri.contour_cl(
            samples, density_estimation_method="by_eye", plot_histograms_1D=False
        )

    plt.close("all")


def test_prob():
    n_dims = 3
    n_samples = 10000

    # Initalize grid
    samples = np.random.uniform(-5, 5, size=(n_samples, n_dims))

    # loglikelihood
    def loglike(x, mean, covmat):
        return -0.5 * np.dot(np.dot((x - mean).T, np.linalg.inv(covmat)), (x - mean))

    # Generate the covariance matrix
    covmat = np.random.normal(size=(n_dims, n_dims))
    covmat = np.identity(n_dims)

    # Generate the mean vector
    mean = np.zeros(n_dims)

    # Compute the probability for each generated sample
    prob = np.zeros(n_samples)
    for i in range(n_samples):
        prob[i] = loglike(samples[i], mean, covmat)

    # Transform and normalize to probabilites
    prob = np.exp(prob)
    prob /= sum(prob)

    tri = TriangleChain()
    tri.contour_cl(samples, prob=prob, density_estimation_method="smoothing")
    tri.contour_cl(samples, prob=prob, density_estimation_method="hist")
    tri.contour_cl(samples, prob=prob, density_estimation_method="kde")
    tri.contour_cl(samples, prob=prob, density_estimation_method="median_filter")
    tri.contour_cl(samples, prob=prob, density_estimation_method="gaussian_mixture")

    plt.close("all")


def test_errors():
    samples = get_samples()

    with pytest.raises(TypeError):
        tri = TriangleChain(samples, wrong_argument="wrong_argument")

    tri = TriangleChain()
    with pytest.raises(ValueError):
        tri.scatter_prob(samples)

    with pytest.raises(ValueError):
        tri.contour_cl(samples, tri="somewhere_in_the_middle")

    with pytest.raises(TypeError):
        tri.contour_cl(samples, wrong_argument="wrong_argument")

    plt.close("all")


def test_figure_size():
    samples = get_samples()

    tri = TriangleChain(size=4)
    tri.contour_cl(samples)
    x, y = tri.fig.get_size_inches()
    assert x == y
    assert x == 4 * len(samples.dtype.names)

    tri = TriangleChain(size=(4, 5))
    tri.contour_cl(samples)
    x, y = tri.fig.get_size_inches()
    assert x == 4 * len(samples.dtype.names)
    assert y == 5 * len(samples.dtype.names)
    assert y > x

    tri = TriangleChain(size=[4, 5])
    tri.contour_cl(samples)
    x, y = tri.fig.get_size_inches()
    assert x == 4 * len(samples.dtype.names)
    assert y == 5 * len(samples.dtype.names)
    assert y > x

    plt.close("all")


def test_histograms_1D_density_false():
    samples = get_samples()
    tri = TriangleChain(histograms_1D_density=False)
    tri.contour_cl(samples)
    plt.close("all")


def test_axlines():
    samples = get_samples(1000)
    tri = TriangleChain()
    tri.contour_cl(samples)
    tri.axlines(samples[0])

    with pytest.raises(ValueError):
        tri.axlines(samples[:10])

    plt.close("all")


def test_axlines_with_grouping():
    samples = get_samples(1000)
    tri = TriangleChain(grouping_kwargs={"n_per_group": (2, 1)})
    tri.contour_cl(samples)
    tri.axlines(samples[0])
    plt.close("all")


def test_axvlines_backwards_compatibility():
    samples = get_samples()
    tri = TriangleChain(axvline_kwargs={"color": "r", "linestyle": "--"})
    tri.contour_cl(samples)
    plt.close("all")


def test_legend_fontsize():
    tri = TriangleChain(label_fontsize=32)
    assert tri.kwargs["legend_fontsize"] == 32

    tri = TriangleChain(label_fontsize=32, legend_fontsize=16)
    assert tri.kwargs["legend_fontsize"] == 16


def test_empty_plots():
    samples = {"a": np.random.uniform(0, 1, 1000), "b": np.random.uniform(0, 1, 1000)}

    tri = TriangleChain(ranges={"a": [-10, -9], "b": [-10, -9]})
    tri.contour_cl(samples)
    plt.close("all")
