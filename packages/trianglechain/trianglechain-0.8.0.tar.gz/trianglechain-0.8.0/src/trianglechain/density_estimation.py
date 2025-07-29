# Copyright (C) 2022 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Tomasz Kacprzak, Silvan Fischbacher


import numpy as np
import scipy

from trianglechain.utils_plots import (
    get_smoothing_sigma,
    normalise,
    pixel_coords,
    safe_normalise,
)


def get_density_grid_1D(
    data,
    binedges,
    bincenters,
    lims,
    prob=None,
    method="smoothing",
    de_kwargs={},
):
    """
    Get density estimation for 1D data

    :param data: data to estimate density from
    :param binedges: bin edges for the histogram
    :param bincenters: bin centers for the histogram
    :param lims: limits for the histogram
    :param prob: weights for the data
    :param method: Method for density estimation. Valid options are:
        - 'smoothing': First create a histogram of samples, and then smooth it
        with a Gaussian kernel corresponding to the variance of the 20% of the
        smallest eigenvalue of the 2D distribution (smoothing scale can be adapted
        using the smoothing_scale parameter).
        - 'gaussian_mixture': Fit a Gaussian mixture model to the data.
        - 'median_filter': Use a median filter to smooth the histogram.
        - 'kde': Use a kernel density estimation to estimate the density.
        - 'hist': Use a histogram to estimate the density.
    :param de_kwargs: keyword arguments for the density estimation method
    :return: density estimation
    """

    if method == "gaussian_mixture":
        if prob is not None:
            ind = np.random.choice(
                a=len(prob), size=10000, p=safe_normalise(prob), replace=True
            )
            data_ = data[ind][:, np.newaxis]
        else:
            data_ = data[:, np.newaxis]

        from cosmic_toolbox.TransformedGaussianMixture import TransformedGaussianMixture

        clf = TransformedGaussianMixture(
            param_bounds=[lims], n_components=20, covariance_type="full"
        )
        clf.fit(data_)
        logL = clf.score_samples(bincenters[:, np.newaxis])

        de = np.exp(logL - np.max(logL))
        de = normalise(de, bincenters)

    elif method == "smoothing":
        from scipy import ndimage, signal

        prob1D = histogram_1D(data=data, prob=prob, binedges=binedges)
        data_pixel = pixel_coords(
            data, [[binedges[0], binedges[-1]]], n_pix_img=len(bincenters)
        )
        if prob is not None:
            ind = np.random.choice(prob.shape[0], p=prob, size=1000)
            data_pixel = data_pixel[0, ind]

        sig_pix = (
            get_smoothing_sigma(data_pixel, prob1D.shape[0])
            * de_kwargs["smoothing_parameter1D"]
        )
        n_pix = max(3, int(np.ceil(sig_pix * 10)))  # 10 sigma smoothing
        kernel = signal.windows.gaussian(n_pix, sig_pix)
        de = scipy.ndimage.convolve(prob1D, kernel, mode="reflect")
        de = normalise(de, bincenters)

        # de = np.convolve(a=prob1D, v=np.ones(5), mode='same')
        # de = signal.convolve2d(prob2d, kernel, mode='same', boundary='wrap')

    elif method == "median_filter":
        from scipy import ndimage

        prob1D = histogram_1D(data=data, prob=prob, binedges=binedges)
        de = ndimage.median_filter(prob1D, int(prob1D.shape[0] / 10))

    elif method == "kde":
        from KDEpy import TreeKDE

        de = (
            TreeKDE(kernel="gaussian", bw="ISJ")
            .fit(data, weights=prob)
            .evaluate(bincenters)
        )

    elif method == "hist":
        de = histogram_1D(data=data, prob=prob, binedges=binedges)

    else:
        raise Exception("unknown density estimation method {}".format(method))

    return de


def histogram_1D(data, prob, binedges):
    """
    Create a histogram of the data

    :param data: data to create histogram from
    :param prob: weights for the data
    :param binedges: bin edges for the histogram
    :return: histogram
    """
    if prob is None:
        prob1D, _ = np.histogram(data, bins=binedges)

    else:
        assert prob.shape[0] == data.shape[0]

        prob1D, _ = np.histogram(data, bins=binedges, weights=prob)

    prob1D = safe_normalise(prob1D)
    prob1D = np.ma.array(prob1D, mask=prob1D == 0)
    return prob1D


def get_density_grid_2D(
    data, ranges, columns, i, j, prob=None, method="smoothing", de_kwargs={}
):
    """
    Get density estimation for 2D data

    :param data: data to estimate density from
    :param ranges: ranges for the data
    :param columns: columns to use for the data
    :param i: index of the first column
    :param j: index of the second column
    :param prob: weights for the data
    :param method: Method for density estimation. Valid options are:
        - 'smoothing': First create a histogram of samples, and then smooth it
        with a Gaussian kernel corresponding to the variance of the 20% of the
        smallest eigenvalue of the 2D distribution (smoothing scale can be adapted
        using the smoothing_scale parameter).
        - 'gaussian_mixture': Fit a Gaussian mixture model to the data.
        - 'median_filter': Use a median filter to smooth the histogram.
        - 'kde': Use a kernel density estimation to estimate the density.
        - 'hist': Use a histogram to estimate the density.
    :param de_kwargs: keyword arguments for the density estimation method
    :return: density estimation
    """

    data_panel = np.vstack((data[columns[j]], data[columns[i]]))
    x_ls = np.linspace(*ranges[columns[j]], num=de_kwargs["n_points"])
    y_ls = np.linspace(*ranges[columns[i]], num=de_kwargs["n_points"])
    x_grid, y_grid = np.meshgrid(x_ls, y_ls)
    gridpoints = np.vstack([x_grid.ravel(), y_grid.ravel()])
    bins_x = np.linspace(x_ls[0], x_ls[-1], num=de_kwargs["n_points"] + 1)
    bins_y = np.linspace(y_ls[0], y_ls[-1], num=de_kwargs["n_points"] + 1)
    bins_x_centers = (bins_x[1:] + bins_x[:-1]) / 2.0
    bins_y_centers = (bins_y[1:] + bins_y[:-1]) / 2.0
    x_grid_centers, y_grid_centers = np.meshgrid(bins_x_centers, bins_y_centers)

    if method == "gaussian_mixture":
        if prob is not None:
            ind = np.random.choice(
                a=len(prob), size=10000, p=safe_normalise(prob), replace=True
            )
            data_panel = data_panel[:, ind]

        bounds = [ranges[columns[j]], ranges[columns[i]]]

        from cosmic_toolbox.TransformedGaussianMixture import TransformedGaussianMixture

        clf = TransformedGaussianMixture(
            param_bounds=bounds, n_components=10, covariance_type="full"
        )
        clf.fit(data_panel.T)
        logL = clf.score_samples(gridpoints.T)

        de = np.exp(logL - np.max(logL)).reshape(x_grid.shape)
        de = safe_normalise(de)

    elif method == "smoothing":
        prob2d = histogram_2D(data_panel, prob, bins_x, bins_y)
        prob2d = safe_normalise(prob2d)

        data_panel_pixel = pixel_coords(
            data_panel,
            [ranges[columns[j]], ranges[columns[i]]],
            n_pix_img=de_kwargs["n_points"],
        )
        if prob is not None:
            ids = np.random.choice(a=len(prob), p=prob, size=1000, replace=True)
            data_panel_pixel = data_panel_pixel[:, ids]

        sig_pix = (
            get_smoothing_sigma(data_panel_pixel) * de_kwargs["smoothing_parameter2D"]
        )
        n_pix = int(np.ceil(sig_pix * 5))

        from scipy.ndimage import gaussian_filter

        de = gaussian_filter(prob2d, sigma=sig_pix)

    elif method == "median_filter":
        from scipy import ndimage

        prob2d = histogram_2D(data_panel, prob, bins_x, bins_y)
        prob2d = safe_normalise(prob2d)
        n_pix = int(prob2d.shape[0] / 5)
        de = ndimage.median_filter(prob2d, n_pix)

    elif method == "kde":
        from KDEpy import TreeKDE

        de = (
            TreeKDE(kernel="gaussian")
            .fit(data_panel.T)
            .evaluate(gridpoints.T)
            .reshape(x_grid.shape)
        )

    elif method == "hist":
        de = histogram_2D(data_panel, prob, bins_x, bins_y)

    else:
        raise Exception("unknown density estimation method {}".format(method))

    de[~np.isfinite(de)] = 0
    de = safe_normalise(de)
    return de, x_grid_centers, y_grid_centers


def histogram_2D(data_panel, prob, bins_x, bins_y):
    """
    Create a 2D histogram

    :param data_panel: data to create histogram from
    :param prob: weights for the data
    :param bins_x: bins for the first dimension
    :param bins_y: bins for the second dimension
    :return: 2D histogram
    """

    if prob is None:
        prob2d = np.histogram2d(*data_panel, bins=(bins_x, bins_y))[0].T.astype(
            np.float32
        )

    else:
        assert prob.shape[0] == data_panel[0].shape[0]
        prob2d = np.histogram2d(*data_panel, weights=prob, bins=(bins_x, bins_y))[
            0
        ].T.astype(np.float32)

    if np.sum(prob2d) > 0:
        prob2d = prob2d / np.sum(prob2d)

    return prob2d


def get_confidence_levels(de, levels, n_levels_check):
    """
    Get the confidence levels for a given density estimation

    :param de: density estimation
    :param levels: confidence levels
    :param n_levels_check: number of levels to check
    :return: confidence levels
    """

    lvl_max = 0.99
    levels_check = np.linspace(0, np.amax(de) * lvl_max, n_levels_check)
    frac_levels = np.zeros_like(levels_check)

    for il, vl in enumerate(levels_check):
        pixels_above_level = de > vl
        frac_levels[il] = np.sum(pixels_above_level * de)

    levels_contour = [
        levels_check[np.argmin(np.fabs(frac_levels - level))] for level in levels
    ][::-1]
    # print('levels_contour', levels_contour/np.amax(de)/lvl_max)
    # if np.any(levels_contour==levels_check[-1]):
    # boundary level = levels_contour/np.amax(de)/lvl_max
    # print(f'contour hitting the boundary level {str(boundary_level))}'
    return levels_contour
