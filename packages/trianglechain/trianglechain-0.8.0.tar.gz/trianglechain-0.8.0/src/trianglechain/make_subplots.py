# Copyright (C) 2022 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Tomasz Kacprzak, Silvan Fischbacher

import warnings

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from scipy.interpolate import griddata

from trianglechain.density_estimation import (
    get_confidence_levels,
    get_density_grid_1D,
    get_density_grid_2D,
)
from trianglechain.utils_plots import (
    compute_plot_limits,
    find_alpha,
    get_best_lims,
    get_old_lims,
    get_values,
)


def plot_1d(
    axc,
    column,
    param_label,
    data,
    prob,
    ranges,
    current_ranges,
    hist_binedges,
    hist_bincenters,
    de_kwargs,
    hist_kwargs,
    empty_columns,
    show_values=False,
    label=None,
    density_estimation_method="smoothing",
    density=True,
    color_hist="k",
    alpha1D=1,
    fill=False,
    lnprobs=None,
    levels_method="hdi",
    bestfit_method="mean",
    credible_interval=0.68,
    sigma_one_tail=3,
    bestfit_fontsize=12,
):
    """
    Plot 1D histogram and density estimation.

    :param axc: matplotlib axis
        axis of the plot
    :param column: str
        name of the parameter in data that is plotted
    :param param_label: str
        name of the parameter that should be plotted in case
        bestfit and uncertainty are shown
    :param data: numpy struct array
        the data that should be plotted with column data
    :param prob: None or array
        if not None, then probability attached to the samples,
        in that case samples are treated as grid not a chain
    :param ranges: dict
        dictionary with the ranges of of the plot for each parameter
    :param current_ranges: dict
        dictionary with the current ranges of of the plot for each parameter
    :param hist_binedges: array
        edges of the histogram for the plot
    :param hist_bincenters: array
        centers of the histogram for the plot
    :param de_kwargs: dict
        additional kwargs for density estimation, passed to get_density_grid
    :param hist_kwargs: dict
        additional kwargs for the histogram plot, passed to plt.plot()
    :param empty_columns: list
        list with the indices of empty columns
    :param show_values: bool
        if values of bestfit and uncertainty should be plotted
    :param label: str
        label of the plot
    :param density_estimation_method: {"gaussian_mixture", "smoothing",
        "median_filter", "kde", "hist"}
        method how to estimate the density
    :param density: bool
        if histogram should be normalized
    :param color_hist: color
        color of the histogram
    :param alpha1D: float in [0, 1]
        alpha value of the histogram
    :param fill: bool
        use filled histograms
    :param lnprobs: array
        logprobabilites used for the bestfit and uncertainty finding
    :param levels_method: {"hdi", "percentile", "PJ_HPD"}
        method how to compute the uncertainty
    :param bestfit_method: {"mode", "mean", "median", "best_sample"}
        method how to compute the bestfit
    :param credible_interval: float in [0, 1]
        credible interval of the uncertainty bar
    :param sigma_one_tail: how many sigma should be used to decide if one tailed
        credible interval should be used
        defaults to 3
    :param best_fontsize: int or float
        fontsize of the label of the bestfit parameters
    """

    try:
        d = data[column]
    except Exception:
        return

    prob1D = get_density_grid_1D(
        data=d,
        prob=prob,
        lims=current_ranges[column],
        binedges=hist_binedges[column],
        bincenters=hist_bincenters[column],
        method=density_estimation_method,
        de_kwargs=de_kwargs,
    )
    if not density:
        prob1D *= len(d)
    old_xlims, old_ylims = get_old_lims(axc)
    axc.plot(
        hist_bincenters[column],
        prob1D,
        "-",
        color=color_hist,
        alpha=find_alpha(column, empty_columns, alpha1D),
        label=label,
        **hist_kwargs,
    )
    if fill:
        axc.fill_between(
            hist_bincenters[column],
            np.zeros_like(prob1D),
            prob1D,
            alpha=0.1 * find_alpha(column, empty_columns, alpha1D),
            color=color_hist,
        )
    try:
        xlims = ranges[column]
    except Exception:
        xlims = get_best_lims(
            current_ranges[column],
            current_ranges[column],
            old_xlims,
            old_ylims,
        )[0]
    if np.isfinite(xlims[0]):
        axc.set_xlim(xlims)
    new_ylim = compute_plot_limits(prob1D)[1]
    upper = np.nanmax([old_ylims[1], new_ylim])
    if np.isnan(upper):
        # probably no data
        upper = 1.0
    axc.set_ylim(0, upper)
    if show_values:
        add_values(
            axc,
            column,
            data,
            lnprobs,
            label=param_label,
            levels_method=levels_method,
            bestfit_method=bestfit_method,
            credible_interval=credible_interval,
            sigma_one_tail=sigma_one_tail,
            bestfit_fontsize=bestfit_fontsize,
        )


def add_values(
    axc,
    column,
    data,
    lnprobs,
    label,
    levels_method="hdi",
    bestfit_method="mean",
    credible_interval=0.68,
    sigma_one_tail=3,
    bestfit_fontsize=12,
):
    """
    Add values of bestfit and uncertainty to the plot.

    :param axc: matplotlib axis
        axis of the plot
    :param column: str
        name of the parameter in data that is plotted
    :param data: numpy struct array
        the data that should be plotted with column data
    :param lnprobs: array
        logprobabilites used for the bestfit and uncertainty finding
    :param label: str
        label of the plot
    :param levels_method: {"hdi", "percentile", "PJ_HPD"}
        method how to compute the uncertainty, default is hdi
    :param bestfit_method: {"mode", "mean", "median", "best_sample"}
        method how to compute the bestfit, default is mean
    :param credible_interval: float in [0, 1]
        credible interval of the uncertainty bar, default is 0.68
    :param sigma_one_tail: how many sigma should be used to decide if one tailed
        credible interval should be used
        defaults to 3
    :param bestfit_fontsize: int or float
        fontsize of the label of the parameters, default is 12
    """
    two_tail, str_bf, up, low = get_values(
        column,
        data,
        lnprobs,
        levels_method=levels_method,
        bestfit_method=bestfit_method,
        credible_interval=credible_interval,
        sigma_one_tail=sigma_one_tail,
    )
    if two_tail:
        axc.set_title(
            r"{} $= {}^{{{} }}_{{{} }}$".format(label, str_bf, up, low),
            fontsize=bestfit_fontsize,
        )
    else:
        side = str_bf
        limit = up
        if side[0] == "l":
            axc.set_title(
                r"{} $> {}$".format(label, limit),
                fontsize=bestfit_fontsize,
            )
        else:
            axc.set_title(
                r"{} $< {}$".format(label, limit),
                fontsize=bestfit_fontsize,
            )


def density_image(
    axc,
    data,
    ranges,
    columns,
    i,
    j,
    cmap,
    de_kwargs={},
    vmin=None,
    vmax=None,
    prob=None,
    density_estimation_method="smoothing",
    label=None,
    alpha=1,
    alpha_for_low_density=False,
    alpha_threshold=0,
):
    """
    Plot the density of the data in the given axis as a density image.

    :param axc: matplotlib axis
        axis of the plot
    :param data: numpy struct array
        the data that should be plotted with column data
    :param ranges: dict
        dictionary with the ranges of of the plot for each parameter
    :param columns: list
        list of all parameters
    :param i: int
        index of the first column to plot
    :param j: int
        index of the second column to plot
    :param cmap: matplotlib colormap
        colormap that is used
    :param de_kwargs: dict
        dict with kde settings, has to have n_points, n_levels_check, levels
    :param vmin: None or float
        minimum value for the density (default=None)
    :param vmax: float
        maximum value for the density (default=None),
        if None, the maximum in each subplot will be chosen as vmax
    :param prob: None or array
        if not None, then probability attached to the samples,
        in that case samples are treated as grid not a chain
    :param density_estimation_method:
        {"gaussian_mixture", "smoothing", "median_filter", "kde", "hist"}
        method how to estimate the density
    :param label: str
        label of the plot
    :param alpha: float
        alpha value of the density image. If alpha_for_low_density is True, then
        alpha is the maximum alpha value.
    :param alpha_for_low_density: bool
        if low density should fade out using alpha values
    :param alpha_treshold: float in [0, 1]
        fraction of sample where alpha value should reach 1
        0 means alpha is 1 everywhere
        1 means linear decrease of alpha from 0 to 1 over the whole range
    """
    if vmin is None:
        vmin = 0

    kde, x_grid, y_grid = get_density_grid_2D(
        data=data,
        ranges=ranges,
        columns=columns,
        i=i,
        j=j,
        de_kwargs=de_kwargs,
        prob=prob,
        method=density_estimation_method,
    )

    if alpha_for_low_density | (alpha != 1):
        # get the color levels for chosen cmap (typically 256)
        cmap_plt = plt.get_cmap(cmap)
        my_cmap = cmap_plt(np.arange(cmap_plt.N))
        # find the index of value closest to alpha_threshold
        cmap_threshold = int(cmap_plt.N * alpha_threshold)
        # all values below alpha_threshold are linearly increased from 0 to alpha
        my_cmap[:cmap_threshold, -1] = np.linspace(0, alpha, cmap_threshold)
        # all values above alpha_threshold are set to alpha
        my_cmap[cmap_threshold:, -1] = alpha
        cmap = ListedColormap(my_cmap)

    axc.pcolormesh(
        x_grid,
        y_grid,
        kde,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        label=label,
        # shading="auto",
        # alpha=alpha,
    )


def contour_cl(
    axc,
    data,
    ranges,
    columns,
    i,
    j,
    fill,
    color,
    de_kwargs={},
    line_kwargs={},
    prob=None,
    density_estimation_method="smoothing",
    label=None,
    alpha=1,
):
    """
    Plot the density of the data in the given axis as a contour plot.

    :param axc: matplotlib axis
        axis of the plot
    :param data: numpy struct array
        the data that should be plotted with column data
    :param ranges: dict
        dictionary with the ranges of of the plot for each parameter
    :param columns: list
        list of all parameters
    :param i: int
        index of the first column to plot
    :param j: int
        index of the second column to plot
    :param fill: bool
        if the contour should be filled
    :param color: str
        color of the contour
    :param de_kwargs: dict
        dict with kde settings, has to have n_points, n_levels_check, levels
    :param line_kwargs: dict
        dict with line settings, has to have linewidth, linestyle
    :param prob: None or array
        if not None, then probability attached to the samples,
        in that case samples are treated as grid not a chain
    :param density_estimation_method:
        {"gaussian_mixture", "smoothing", "median_filter", "kde", "hist"}
        method how to estimate the density
    :param label: str
        label of the plot
    :param alpha: float
        alpha value of the contour
    """

    def _get_paler_colors(color_rgb, n_levels, pale_factor=None):
        """
        Get a list of colors that are paler than the given color.

        :param color_rgb: str
            color in rgb format
        :param n_levels: int
            number of levels
        :param pale_factor: float
            pale factor
        :return: list
            list of colors
        """

        solid_contour_palefactor = 0.6

        # convert a color into an array of colors for used in contours
        color = matplotlib.colors.colorConverter.to_rgb(color_rgb)
        pale_factor = pale_factor or solid_contour_palefactor
        cols = [color]
        for _ in range(1, n_levels):
            cols = [[c * (1 - pale_factor) + pale_factor for c in cols[0]]] + cols
        return cols

    de, x_grid, y_grid = get_density_grid_2D(
        i=i,
        j=j,
        data=data,
        prob=prob,
        ranges=ranges,
        columns=columns,
        method=density_estimation_method,
        de_kwargs=de_kwargs,
    )

    levels_contour = get_confidence_levels(
        de=de,
        levels=de_kwargs["levels"],
        n_levels_check=de_kwargs["n_levels_check"],
    )
    with warnings.catch_warnings():
        # this will suppress all warnings in this block
        warnings.simplefilter("ignore")
        colors = _get_paler_colors(color_rgb=color, n_levels=len(de_kwargs["levels"]))

        for l_i, lvl in enumerate(levels_contour):
            if fill:
                axc.contourf(
                    x_grid,
                    y_grid,
                    de,
                    levels=[lvl, np.inf],
                    colors=[colors[l_i]],
                    alpha=0.85 * alpha,
                    **line_kwargs,
                )
                if "zorder" not in line_kwargs:
                    line_kwargs["zorder"] = 299
                    delete_later = True
                else:
                    delete_later = False
                axc.contour(
                    x_grid,
                    y_grid,
                    de,
                    levels=[lvl, np.inf],
                    colors=[color],
                    alpha=alpha,
                    **line_kwargs,
                )
                if delete_later:
                    del line_kwargs["zorder"]
            else:
                axc.contour(
                    x_grid,
                    y_grid,
                    de,
                    levels=[lvl, np.inf],
                    colors=[color],
                    alpha=alpha,
                    **line_kwargs,
                )
    # dummy plot to get legend
    axc.plot(data[columns[i]][0], data[columns[j]][0], label=label, color=color)


def scatter_density(
    axc,
    points1,
    points2,
    n_bins=50,
    lim1=None,
    lim2=None,
    n_points_scatter=-1,
    label=None,
    alpha=1,
    **kwargs,
):
    """
    Plot the density of the data in the given axis as a scatter plot. The color of
    the scatter points is determined by the density of the points.

    :param axc: matplotlib axis
        axis of the plot
    :param points1: numpy array
        array of the first parameter
    :param points2: numpy array
        array of the second parameter
    :param n_bins: int
        number of bins
    :param lim1: tuple
        limits of the first parameter
    :param lim2: tuple
        limits of the second parameter
    :param n_points_scatter: int
        number of points to plot
    :param label: str
        label of the plot
    :param alpha: float
        alpha value of the scatter points
    :param kwargs: dict
        dict with kwargs for the scatter plot
    """

    if lim1 is None:
        min1 = np.min(points1)
        max1 = np.max(points1)
    else:
        min1 = lim1[0]
        max1 = lim1[1]
    if lim2 is None:
        min2 = np.min(points2)
        max2 = np.max(points2)
    else:
        min2 = lim2[0]
        max2 = lim2[1]

    bins_edges1 = np.linspace(min1, max1, n_bins)
    bins_edges2 = np.linspace(min2, max2, n_bins)

    hv, _, _ = np.histogram2d(
        points1, points2, bins=[bins_edges1, bins_edges2], density=True
    )

    bins_centers1 = (bins_edges1 - (bins_edges1[1] - bins_edges1[0]) / 2)[1:]
    bins_centers2 = (bins_edges2 - (bins_edges2[1] - bins_edges2[0]) / 2)[1:]

    select_box = (
        (points1 < max1) & (points1 > min1) & (points2 < max2) & (points2 > min2)
    )
    points1_box, points2_box = points1[select_box], points2[select_box]

    x1, x2 = np.meshgrid(bins_centers1, bins_centers2)
    points = np.concatenate(
        [x1.flatten()[:, np.newaxis], x2.flatten()[:, np.newaxis]], axis=1
    )
    xi = np.concatenate(
        [points1_box[:, np.newaxis], points2_box[:, np.newaxis]], axis=1
    )

    if lim1 is not None:
        axc.set_xlim(lim1)
    if lim2 is not None:
        axc.set_ylim(lim2)

    if n_points_scatter > 0:
        select = np.random.choice(len(points1_box), n_points_scatter)
        c = griddata(
            points,
            hv.T.flatten(),
            xi[select, :],
            method="linear",
            rescale=True,
            fill_value=np.min(hv),
        )
        axc.scatter(
            points1_box[select],
            points2_box[select],
            c=c,
            label=label,
            alpha=alpha,
            **kwargs,
        )
    else:
        c = griddata(
            points,
            hv.T.flatten(),
            xi,
            method="linear",
            rescale=True,
            fill_value=np.min(hv),
        )
        sorting = np.argsort(c)
        axc.scatter(
            points1_box[sorting],
            points2_box[sorting],
            c=c[sorting],
            label=label,
            alpha=alpha,
            **kwargs,
        )
