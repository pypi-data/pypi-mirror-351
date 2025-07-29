# Copyright (C) 2023 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher

import itertools
from copy import deepcopy

import matplotlib.pyplot as plt
import numpy as np
from cosmic_toolbox import logger

from trianglechain.BaseChain import BaseChain
from trianglechain.make_subplots import contour_cl, density_image, scatter_density
from trianglechain.params import ensure_rec
from trianglechain.utils_plots import (
    add_colorbar,
    delete_all_ticks,
    get_labels,
    get_lines_and_labels,
    get_n_points_for_scatter,
    get_old_lims,
    rasterize_density_images,
    set_limits,
    update_current_ranges,
    update_current_ticks,
)

LOGGER = logger.get_logger(__file__)


class RectangleChain(BaseChain):
    """
    Class to produce reactangular plots
    Parameters defined for this class are used for all plots that are added to the
    figure. If you want to change the parameters for a specific plot, you can do so
    by passing the parameters to the plotting function.

    :param fig: matplotlib figure, default: None
    :param size: size of the panels, if one number is given, the panels are rectangular
        with the y axis being 70% of the x axis, if two numbers are given, the first
        number is the width of the panels and the second number is the height of the
        panels, default: 4
    :param params_x: parameters to plot on the x axis
    :param params_y: parameters to plot on the y axis
    :param names: names of parameters (when data is np array), default: None
    :param ranges: dictionary with the ranges for the parameters
    :param labels_x: list of labels (e.g. latex style) for the parameters for the
        plot on the x axis
    :param labels_y: list of labels (e.g. latex style) for the parameters for the
        plot on the y axis
    :param fill: if the contours should be filled, default: False
    :param grid: if the grid should be plotted, default: False
    :param n_ticks: number of ticks on the axes, default: 3
    :param ticks: dict specifying the ticks for a parameter
    :param tick_length: length of the ticks, default: 3
    :param n_bins: number of bins for the 1D histograms, default: 100
    :param density_estimation_method: method for density estimation. Available options:

        - smoothing (default):
            First create a histogram of samples and then smooth it with a Gaussian kernel
            corresponding to the variance of the 20% of the smallest eigenvalue of the 2D distribution
            (smoothing scale can be adapted using the smoothing parameter in de_kwargs).
        - gaussian_mixture:
            Use Gaussian mixture to fit the 2D samples.
        - median_filter:
            Use median filter on the 2D histogram.
        - kde:
            Use TreeKDE, may be slow.
        - hist:
            Simple 2D histogram.

    :param cmap: colormap, default: "viridis"
    :param colorbar: if a colorbar should be plotted, default: False
    :param colorbar_label: label for the colorbar, default: None
    :param colorbar_ax: axis for the colorbar, default: [0.735, 0.5, 0.03, 0.25]
    :param cmap_vmin: minimum value for the colormap, default: 0
    :param cmap_vmax: maximum value for the colormap, default: None
    :param show_legend: if a legend should be shown, default: False
    :param alpha: alpha for the 2D histograms, default: 1
    :param alpha_for_low_density: if low density areas should fade to transparent
    :param alpha_threshold: threshold from where the fading to transparent should
        start, default: 0
    :param n_points_scatter: number of points to use for scatter plots,
        default: -1 (all)
    :param label_fontsize: fontsize of the labels, default: 24
    :param de_kwargs: density estimation kwargs, dictionary with keys:

        - n_points:
            number of bins for 2d histograms used to create contours etc., default: n_bins
        - levels:
            density levels for contours, the contours will enclose this
            level of probability, default: [0.68, 0.95]
        - n_levels_check:
            number of levels to check when looking for density levels
            More levels is more accurate, but slower, default: 2000
        - smoothing_parameter1D:
            smoothing scale for the 1D histograms, default: 0.1
        - smoothing_parameter2D:
            smoothing scale for the 2D histograms, default: 0.2

    :param grid_kwargs: kwargs for ax.grid, passed to ax.grid
    :param labels_kwargs: kwargs for the x and y labels, passed to ax.set_xlabel and
    :param line_kwargs: kwargs for the lines, passed to plt.contour and plt.contourf
    :param ticks_kwargs: kwargs for the ticks, passed to ax.set_xticklabels
    :param scatter_kwargs: kwargs for the scatter plot, passed to plt.scatter
    :param subplots_kwargs: kwargs for the subplots, passed to plt.subplots
    :param axlines_kwargs: kwargs for the axlines, passed to ax.axhline and ax.axvline

    Basic usage::

        rec = RectangleChain(params_x=["par1", "par2"], params_y=["par2", "par3"])
        # plot contours at given confidence levels
        rec.contour_cl(samples)
        # plot PDF density image
        rec.density_image(samples)
        # simple scatter plot
        rec.scatter(samples)
        # scatter plot, with probability for each sample provided
        rec.scatter_prob(samples, prob=prob)
        # scatter plot, color corresponds to probability
        rec.scatter_density(samples)

    """

    def __init__(self, params_x, params_y, fig=None, size=4, **kwargs):
        if "colorbar_ax" not in kwargs:
            kwargs["colorbar_ax"] = [0.93, 0.1, 0.03, 0.8]
        super().__init__(fig=fig, size=size, **kwargs)
        self.params_x = params_x
        self.params_y = params_y
        self.add_plotting_functions(self.add_plot)

    def add_plot(
        self,
        data,
        plottype,
        prob=None,
        color=None,
        label=None,
        **kwargs,
    ):
        """
        Plotting function for the line chain class. Parameters that are passed to
        this function are overwriting the default parameters of the class.

        :param data: data to plot, can be recarray, array, pandas dataframe or dict
        :param prob: probability for each sample, default: None
        :param color: color for the plot, default: None
        :param label: label for the plot, default: None
        :param names: list of names of the parameters, only used when input is
            unstructured array
        :param fill: if the contours should be filled, default: False
        :param grid: if the grid should be plotted, default: False
        :param n_bins: number of bins for the 1D histograms, default: 100
        :param density_estimation_method: method for density estimation. Available
            options:

            - smoothing (default):
                First create a histogram of samples and then smooth it with a Gaussian kernel
                corresponding to the variance of the 20% of the smallest eigenvalue of the 2D distribution
                (smoothing scale can be adapted using the smoothing parameter in de_kwargs).
            - gaussian_mixture:
                Use Gaussian mixture to fit the 2D samples.
            - median_filter:
                Use median filter on the 2D histogram.
            - kde:
                Use TreeKDE, may be slow.
            - hist:
                Simple 2D histogram.

        :param cmap: colormap, default: "viridis"
        :param colorbar: if a colorbar should be plotted, default: False
        :param colorbar_label: label for the colorbar, default: None
        :param colorbar_ax: axis for the colorbar, default: [0.735, 0.5, 0.03, 0.25]
        :param cmap_vmin: minimum value for the colormap, default: 0
        :param cmap_vmax: maximum value for the colormap, default: None
        :param show_legend: if a legend should be shown, default: False
        :param alpha: alpha for the 2D histograms, default: 1
        :param normalize_prob2D: if the 2D histograms should be normalized for
            scatter_prob, default: True
        :param alpha_for_low_density: if low density areas should fade to transparent
        :param alpha_threshold: threshold from where the fading to transparent should
            start, default: 0
        :param n_points_scatter: number of points to use for scatter plots,
            default: -1 (all)
        :param de_kwargs: density estimation kwargs, dictionary with keys:

            - n_points:
                number of bins for 2d histograms used to create contours etc., default: n_bins
            - levels:
                density levels for contours, the contours will enclose this
                level of probability, default: [0.68, 0.95]
            - n_levels_check:
                number of levels to check when looking for density levels
                More levels is more accurate, but slower, default: 2000
            - smoothing_parameter1D:
                smoothing scale for the 1D histograms, default: 0.1
            - smoothing_parameter2D:
                smoothing scale for the 2D histograms, default: 0.2

        :param grid_kwargs: kwargs for ax.grid, passed to ax.grid
        :param ticks_kwargs: kwargs for the ticks, passed to ax.set_xticklabels
        :param labels_kwargs: kwargs for the x and y labels, passed to ax.set_xlabel and
        :param line_kwargs: kwargs for the lines, passed to plt.contour and plt.contourf
        :param scatter_kwargs: kwargs for the scatter plot, passed to plt.scatter
        :param subplots_kwargs: kwargs for the subplots, passed to plt.subplots
        """

        # check if all kwargs are valid trianglechain arguments
        self._check_unexpected_kwargs(kwargs)

        kwargs_copy = deepcopy(self.kwargs)
        kwargs_copy.update(kwargs)

        if (plottype == "scatter_prob") & (prob is None):
            raise ValueError("prob needs to be defined for scatter_prob")

        color = self.setup_color(color)
        self.fig = plot_rec_marginals(
            params_x=self.params_x,
            params_y=self.params_y,
            fig=self.fig,
            size=self.size,
            func=plottype,
            data=data,
            prob=prob,
            color=color,
            label=label,
            **kwargs_copy,
        )

        return self.fig


def plot_rec_marginals(
    params_x,
    params_y,
    data,
    prob=None,
    func="contour_cl",
    color="#0063B9",
    label=None,
    fig=None,
    size=4,
    ranges={},
    labels_x=None,
    labels_y=None,
    names=None,
    fill=False,
    grid=False,
    n_ticks=3,
    ticks={},
    tick_length=3,
    n_bins=100,
    density_estimation_method="smoothing",
    cmap=plt.cm.viridis,
    cmap_vmin=0,
    cmap_vmax=None,
    colorbar=False,
    colorbar_label=None,
    colorbar_ax=[0.735, 0.5, 0.03, 0.25],
    show_legend=False,
    normalize_prob2D=True,
    alpha=None,
    alpha2D=1,
    alpha_for_low_density=False,
    alpha_threshold=0,
    n_points_scatter=-1,
    label_fontsize=24,
    tick_fontsize=14,
    legend_fontsize=24,
    de_kwargs={},
    grid_kwargs={},
    labels_kwargs={},
    line_kwargs={},
    scatter_kwargs={},
    subplots_kwargs={},
    axlines_kwargs={},
    ticks_kwargs={},
    **kwargs,
):
    """
    Plot line plots of chains.

    :param data: rec array, array, dict or pd dataframe
        data to plot
    :param prob: probability for each sample
    :param names: names of parameters (when data is np array), default: None
    :param func: function to use for plotting
        options: contour_cl, density_image, scatter_density, scatter_prob, scatter, axlines
        default: contour_cl
    :param color: color of the plot, default: "#0063B9"
    :param cmap: colormap for 2D plots, default: plt.cm.viridis
    :param cmap_vmin: minimum value for colormap, default: 0
    :param cmap_vmax: maximum value for colormap, default: None
    :param colorbar: show colorbar, default: False
    :param colorbar_label: label for colorbar, default: None
    :param colorbar_ax: position of colorbar, default: [0.735, 0.5, 0.03, 0.25]
    :param ranges: dictionary with ranges for each parameter, default: {}
    :param ticks: dictionary with ticks for each parameter, default: {}
    :param n_ticks: number of ticks for each parameter, default: 3
    :param tick_length: length of ticks, default: 3
    :param n_bins: number of bins for histograms, default: 20
    :param fig: figure to plot on, default: None
    :param size: size of the figure, default: 4
    :param fill: fill the area of the contours, default: True
    :param grid: show grid, default: False
    :param labels: labels for each parameter, default: None
        if None, labels are taken from the parameter names
    :param label: label for the plot, default: None
    :param label_fontsize: fontsize of the label, default: 24
    :param tick_fontsize: fontsize of the ticks, default: 14
    :param legend_fontsize: fontsize of the legend, default: 24
    :param show_legend: show legend, default: False
    :param density_estimation_method: method to use for density estimation
        options: smoothing, histo, kde, gaussian_mixture, median_filter
        default: smoothing
    :param normalize_prob2D: normalize probability for 2D plots, default: True
    :param alpha: alpha value for the plot, default: None
    :param alpha2D: alpha value for 2D plots, default: 1
    :param alpha_for_low_density: use alpha for low density regions, default: False
    :param alpha_threshold: threshold for alpha, default: 0
    :param subplots_kwargs: kwargs for plt.subplots, default: {}
    :param de_kwargs: kwargs for density estimation, default: {}
    :param labels_kwargs: kwargs for labels, default: {}
    :param grid_kwargs: kwargs for grid, default: {}
    :param line_kwargs: kwargs for line plots, default: {}
    :param scatter_kwargs: kwargs for scatter plots, default: {}
    :param normalize_prob2D: normalize probability for 2D plots, default: True
    :param n_points_scatter: number of points for scatter plots, default: -1 (all)
    :param axlines_kwargs: kwargs for axlines, default: {}
    :param ticks_kwargs: kwargs for ticks, default: {}
    :param kwargs: additional kwargs for the plot function
    :return: fig, axes
    """
    if alpha is not None:
        if alpha2D != 1:
            LOGGER.warning("parameters alpha and alpha2D are both set, using alpha")
    else:
        if alpha2D != 1:
            alpha = alpha2D
        else:
            alpha = 1
    ###############################
    # prepare data and setup plot #
    ###############################
    data = ensure_rec(data, names=names)

    # needed for plotting chains with different automatic limits
    current_ranges = {}
    current_ticks = {}

    labels_x = get_labels(labels_x, params_x)
    labels_y = get_labels(labels_y, params_y)

    columns = params_x + params_y

    # Setup the probabilities for possible plots
    prob_label = None
    if prob is not None:
        if np.min(prob) < 0:
            prob_offset = -np.min(prob)
        else:
            prob_offset = 0
        if normalize_prob2D:
            prob2D = (prob + prob_offset) / np.sum(prob + prob_offset)
        else:
            # for example to plot an additional parameter in parameter space
            prob_label = prob
            prob2D = None

    # Setup the figure orientation
    n_cols = len(params_x)
    n_rows = len(params_y)

    # Setup the figure size
    if isinstance(size, (list, tuple)):
        x_size = size[0]
        y_size = size[1]
    else:
        x_size = size
        y_size = size * 0.7

    # Setup the figure
    if fig is None:
        fig, _ = plt.subplots(
            nrows=n_rows,
            ncols=n_cols,
            figsize=(n_cols * x_size, n_rows * y_size),
            **subplots_kwargs,
        )
        ax = np.array(fig.get_axes()).ravel().reshape(n_rows, n_cols)
    else:
        ax = np.array(fig.get_axes()).ravel().reshape(n_rows, n_cols)
    # get ranges for each parameter (if not specified, max/min of data is used)
    update_current_ranges(current_ranges, ranges, columns, data)

    def get_current_ax(ax, i, j):
        axc = ax[i, j]
        return axc

    #################
    # 2D histograms #
    #################
    for i, j in itertools.product(range(n_rows), range(n_cols)):
        # j corresponds to x axis
        j_rec = j
        i_rec = i + n_cols

        axc = get_current_ax(ax, i, j)
        old_xlims, old_ylims = get_old_lims(axc)
        if func == "contour_cl":
            contour_cl(
                axc,
                data=data,
                ranges=current_ranges,
                columns=columns,
                i=i_rec,
                j=j_rec,
                fill=fill,
                color=color,
                de_kwargs=de_kwargs,
                line_kwargs=line_kwargs,
                prob=prob,
                density_estimation_method=density_estimation_method,
                label=label,
                alpha=alpha,
            )

        if func == "density_image":
            density_image(
                axc,
                data=data,
                ranges=current_ranges,
                columns=columns,
                i=i_rec,
                j=j_rec,
                cmap=cmap,
                de_kwargs=de_kwargs,
                vmin=cmap_vmin,
                vmax=cmap_vmax,
                prob=prob,
                density_estimation_method=density_estimation_method,
                label=label,
                alpha=alpha,
                alpha_for_low_density=alpha_for_low_density,
                alpha_threshold=alpha_threshold,
            )

        elif func == "scatter":
            x, y = get_n_points_for_scatter(
                data[columns[j_rec]],
                data[columns[i_rec]],
                n_points_scatter=n_points_scatter,
            )
            axc.scatter(
                x,
                y,
                c=color,
                label=label,
                alpha=alpha,
                **scatter_kwargs,
            )

        elif func == "scatter_prob":
            if normalize_prob2D:
                _prob = prob2D
            else:
                _prob = prob_label
            x, y, _prob = get_n_points_for_scatter(
                data[columns[j_rec]],
                data[columns[i_rec]],
                prob=_prob,
                n_points_scatter=n_points_scatter,
            )
            sorting = np.argsort(_prob)
            axc.scatter(
                x[sorting],
                y[sorting],
                c=_prob[sorting],
                label=label,
                cmap=cmap,
                alpha=alpha,
                **scatter_kwargs,
            )

        elif func == "scatter_density":
            scatter_density(
                axc,
                points1=data[columns[j_rec]],
                points2=data[columns[i_rec]],
                n_bins=n_bins,
                lim1=current_ranges[columns[j_rec]],
                lim2=current_ranges[columns[i_rec]],
                n_points_scatter=n_points_scatter,
                cmap=cmap,
                vmin=cmap_vmin,
                vmax=cmap_vmax,
                label=label,
                alpha=alpha,
            )
        elif func == "axlines":
            if len(data[columns[i_rec]]) > 1:
                raise ValueError(
                    "axlines can only be used with one point, not with {} points".format(
                        len(data[columns[i_rec]])
                    )
                )

            axc.axhline(
                y=data[columns[i_rec]],
                color=color,
                label=label,
                alpha=alpha,
                **axlines_kwargs,
            )
            axc.axvline(
                x=data[columns[j_rec]],
                color=color,
                label=label,
                alpha=alpha,
                **axlines_kwargs,
            )
        set_limits(
            axc,
            ranges,
            current_ranges,
            columns[i_rec],
            columns[j_rec],
            old_xlims,
            old_ylims,
        )
    # grid
    if grid:
        for axc in ax.flatten():
            axc.grid(zorder=0, **grid_kwargs)

    #########
    # ticks #
    #########
    def get_ticks(i):
        try:
            return ticks[columns[i]]
        except Exception:
            return current_ticks[columns[i]]

    def plot_yticks(axc, i, length=10, direction="in"):
        axc.yaxis.set_ticks_position("both")
        axc.set_yticks(get_ticks(i))
        axc.tick_params(direction=direction, length=length)

    def plot_xticks(axc, i, length=10, direction="in"):
        axc.xaxis.set_ticks_position("both")
        axc.set_xticks(get_ticks(i))
        axc.tick_params(direction=direction, length=length)

    delete_all_ticks(ax)
    update_current_ticks(current_ticks, columns, ranges, current_ranges, n_ticks)
    for i, j in itertools.product(range(n_rows), range(n_cols)):
        axc = get_current_ax(ax, i, j)
        plot_xticks(axc, j, tick_length)
        plot_yticks(axc, i + n_cols, tick_length)

    def plot_tick_labels(axc, xy, i, ticks_kwargs):
        ticklabels = [t for t in get_ticks(i)]
        if xy == "y":
            axc.set_yticklabels(
                ticklabels,
                rotation=0,
                fontsize=tick_fontsize,
                **ticks_kwargs,
            )
        else:
            # xy == "x":
            axc.set_xticklabels(
                ticklabels,
                rotation=90,
                fontsize=tick_fontsize,
                **ticks_kwargs,
            )

    for i, j in itertools.product(range(n_rows), range(n_cols)):
        axc = get_current_ax(ax, i, j)
        if i == n_rows - 1:
            plot_tick_labels(axc, "x", j, ticks_kwargs)
        if j == 0:
            plot_tick_labels(axc, "y", i + n_cols, ticks_kwargs)

    # legends
    legend_lines, legend_labels = get_lines_and_labels(ax)
    for i, j in itertools.product(range(n_rows), range(n_cols)):
        labelpad = 10
        axc = get_current_ax(ax, i, j)
        if j == 0:
            axc.set_ylabel(
                labels_y[i],
                **labels_kwargs,
                rotation=90,
                labelpad=labelpad,
                fontsize=label_fontsize,
            )
            axc.yaxis.set_label_position("left")
        if i == n_rows - 1:
            axc.set_xlabel(
                labels_x[j],
                **labels_kwargs,
                rotation=0,
                labelpad=labelpad,
                fontsize=label_fontsize,
            )
            axc.xaxis.set_label_position("bottom")
        if legend_lines and show_legend:
            # only print legend when there are labels for it
            fig.legend(
                legend_lines,
                legend_labels,
                bbox_to_anchor=(1, 1),
                bbox_transform=ax[0, -1].transAxes,
                fontsize=legend_fontsize,
            )

    if colorbar:
        add_colorbar(
            fig,
            cmap_vmin,
            cmap_vmax,
            cmap,
            colorbar_ax,
            colorbar_label,
            legend_fontsize,
            tick_fontsize,
            prob_label,
        )
    rasterize_density_images(ax)
    plt.subplots_adjust(hspace=0, wspace=0)
    fig.align_ylabels()
    fig.align_xlabels()
    return fig
