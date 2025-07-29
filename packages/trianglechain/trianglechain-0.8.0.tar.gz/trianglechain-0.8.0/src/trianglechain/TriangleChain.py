# Copyright (C) 2022 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Tomasz Kacprzak, Silvan Fischbacher

from copy import deepcopy

import matplotlib.pyplot as plt
import numpy as np
from cosmic_toolbox.logger import get_logger
from tqdm.auto import tqdm, trange

from trianglechain.BaseChain import BaseChain
from trianglechain.make_subplots import (
    contour_cl,
    density_image,
    plot_1d,
    scatter_density,
)
from trianglechain.params import check_if_names_is_used_correctly, ensure_rec
from trianglechain.utils_plots import (
    add_colorbar,
    add_vline,
    delete_all_ticks,
    find_alpha,
    get_best_old_lims,
    get_hw_ratios,
    get_labels,
    get_lines_and_labels,
    get_n_points_for_scatter,
    get_old_lims,
    prepare_columns,
    rasterize_density_images,
    set_limits,
    setup_figure,
    setup_grouping,
    update_current_ranges,
    update_current_ticks,
)

LOGGER = get_logger(__file__)


class TriangleChain(BaseChain):
    """
    Class to produce triangle plots.
    Parameters defined for this class are used for all plots that are added to the
    figure. If you want to change the parameters for a specific plot, you can do so
    by passing the parameters to the plotting function.

    :param fig: matplotlib figure, default: None
    :param size: size of the panels, if one number is given, the panels are square,
        if two numbers are given, the figure is rectangular, default: 4
    :param params: list of parameters to plot, default: "all"
    :param params_from: sample or list of samples from which the parameters should
        be taken, default: None
    :param ranges: dictionary with the ranges for the parameters
    :param names: list of names of the parameters, only used when input data is
        unstructured array
    :param labels: list of labels (e.g. latex style) for the parameters for the
        plot
    :param fill: if the contours should be filled, default: False
    :param grid: if the grid should be plotted, default: False
    :param tri: if upper or lower triangle should be plotted, default: "lower"
    :param plot_histograms_1D: if the 1D histograms should be plotted, default: True
    :param histograms_1D_density: if the 1D histograms should be normalized to 1, default: True
    :param n_ticks: number of ticks on the axes, default: 3
    :param ticks: dict specifying the ticks for a parameter
    :param tick_length: length of the ticks, default: 3
    :param show_values: if best-fit and uncertainty should be given, default: False
    :param bestfit_method: method for the best_fit,
        options: "mode", "mean", "median", "best_sample" (requires lnprobs),
        default: "mode"
    :param levels_method: method to compute the uncertainty bands,
        options: "hdi", "percentile", "PJ-HPD" (requires lnprobs),
        default: "hdi"
    :param credible_interval: credible interval for the uncertainty, default: 0.68
    :param n_sigma_for_one_sided_tail: number of sigma for the one-sided tail,
        default: 3
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
    :param progress_bar: if a progress bar should be shown, default: True
    :param alpha: alpha for the plots, overwrite alpha1D and alpha2D, default: None
    :param alpha1D: alpha for the 1D histograms, default: 1
    :param alpha2D: alpha for the 2D histograms, default: 1
    :param normalize_prob1D: if the 1D histograms should be normalized for
        scatter_prob, default: True
    :param normalize_prob2D: if the 2D histograms should be normalized for
        scatter_prob, default: True
    :param scatter_vline_1D: if a vertical line should be plotted in the 1D
        histograms for each point when using scatter, default: False
    :param alpha_for_low_density: if low density areas should fade to transparent
    :param alpha_threshold: threshold from where the fading to transparent should
        start, default: 0
    :param n_points_scatter: number of points to use for scatter plots,
        default: -1 (all)
    :param label_fontsize: fontsize of the labels, default: 24
    :param tick_fontsize: fontsize of the ticks, default: 14
    :param legend_fontsize: fontsize of the legend, default: 24
    :param bestfit_fontsize: fontsize of the bestfit, default: 14
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

    :param grid_kwargs: kwargs for ax.grid, passed to ax.grid function
    :param hist_kwargs: kwargs for the 1D histograms, passed to plt.hist function
    :param labels_kwargs: kwargs for the x and y labels, passed to ax.set_xlabel (and y)
    :param line_kwargs: kwargs for the lines, passed to plt.contour and plt.contourf
    :param scatter_kwargs: kwargs for the scatter plot, passed to plt.scatter
    :param ticks_kwargs: kwargs for the ticks, passed to ax.set_xticklabels
    :param axvline_kwargs: kwargs for the vertical lines in the 1D histograms,
        passed to plt.axvline
    :param subplots_kwargs: kwargs for the subplots, passed to plt.subplots
    :param grouping_kwargs: kwargs for grouping parameters in the plot with options:

        - n_per_group:
            how many parameters are grouped together (e.g. (3, 4, 5) for grouping the
            parameters accordingly), default: None
        - empty_ratio:
            fraction of a whole plot that is left empty for separation, default: 0.2

    Basic usage::

        tri = TriangleChain()
        # plot contours at given confidence levels
        tri.contour_cl(samples)
        # plot PDF density image
        tri.density_image(samples)
        # simple scatter plot
        tri.scatter(samples)
        # scatter plot, with probability for each sample provided
        tri.scatter_prob(samples, prob=prob)
        # scatter plot, color corresponds to probability
        tri.scatter_density(samples)

    """

    def __init__(self, fig=None, size=4, **kwargs):
        super().__init__(fig=fig, size=size, **kwargs)

        self.add_plotting_functions(self.add_plot)

    def add_plot(
        self,
        data,
        plottype,
        prob=None,
        color=None,
        label=None,
        lnprobs=None,
        **kwargs,
    ):
        """
        Plotting function for the triangle chain class. Parameters that are passed to
        this function are overwriting the default parameters of the class.

        :param data: data to plot, can be recarray, array, pandas dataframe or dict
        :param prob: probability for each sample, default: None
        :param color: color for the plot, default: None
        :param label: label for the plot, default: None
        :param lnprobs: lnprob for each sample (used for some best-fit methods),
            default: None
        :param names: list of names of the parameters, only used when input is
            unstructured array
        :param fill: if the contours should be filled, default: False
        :param grid: if the grid should be plotted, default: False
        :param tri: if upper or lower triangle should be plotted, default: "lower"
        :param plot_histograms_1D: if 1D histograms should be plotted, default: True
        :param show_values: if best-fit and uncertainty should be given, default: False
        :param bestfit_method: method for the best_fit,
            options: "mode", "mean", "median", "best_sample" (requires lnprobs),
            default: "mode"
        :param levels_method: method to compute the uncertainty bands, default:
            options: "hdi", "percentile", "PJ-HPD" (requires lnprobs),
            default: "hdi"
        :param credible_interval: credible interval for the uncertainty, default: 0.68
        :param n_sigma_for_one_sided_tail: number of sigma for the one-sided tail,
            default: 3
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
        :param progress_bar: if a progress bar should be shown, default: True
        :param alpha: alpha for the plots, overwrite alpha1D and alpha2D, default: None
        :param alpha1D: alpha for the 1D histograms, default: 1
        :param alpha2D: alpha for the 2D histograms, default: 1
        :param normalize_prob1D: if the 1D histograms should be normalized for
            scatter_prob, default: True
        :param normalize_prob2D: if the 2D histograms should be normalized for
            scatter_prob, default: True
        :param scatter_vline_1D: if a vertical line should be plotted in the 1D
            histograms for each point when using scatter, default: False
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

        :param grid_kwargs: kwargs for ax.grid, passed to ax.grid function
        :param hist_kwargs: kwargs for the 1D histograms, passed to plt.hist function
        :param labels_kwargs: kwargs for the x and y labels, passed to ax.set_xlabel (and y)
        :param line_kwargs: kwargs for the lines, passed to plt.contour and plt.contourf
        :param scatter_kwargs: kwargs for the scatter plot, passed to plt.scatter
        :param axvline_kwargs: kwargs for the vertical lines in the 1D histograms,
            passed to plt.axvline
        :param subplots_kwargs: kwargs for the subplots, passed to plt.subplots
        :param ticks_kwargs: kwargs for the ticks, passed to ax.set_xticklabels
        :param grouping_kwargs: kwargs for grouping parameters in the plot with options:

            - n_per_group:
                how many parameters are grouped together (e.g. (3, 4, 5) for grouping the
                parameters accordingly), default: None
            - empty_ratio:
                fraction of a whole plot that is left empty for separation, default: 0.2

        """

        # check if all kwargs are valid trianglechain arguments
        self._check_unexpected_kwargs(kwargs)

        # enrich kwargs with the values from the class
        kwargs_copy = deepcopy(self.kwargs)
        kwargs_copy.update(kwargs)

        # get the color from color cycle if not defined
        color = self.setup_color(color)

        if (plottype == "scatter_prob") & (prob is None):
            raise ValueError("prob needs to be defined for scatter_prob")

        if plottype == "axlines":
            kwargs_copy["scatter_vline_1D"] = True

        self.fig, self.ax = plot_triangle_marginals(
            fig=self.fig,
            size=self.size,
            func=plottype,
            data=data,
            prob=prob,
            color=color,
            label=label,
            lnprobs=lnprobs,
            **kwargs_copy,
        )
        return self.fig, self.ax


def plot_triangle_marginals(
    data,
    prob=None,
    func="contour_cl",
    color="#0063B9",
    label=None,
    lnprobs=None,
    fig=None,
    size=4,
    params="all",
    params_from=None,
    ranges={},
    labels=None,
    names=None,
    fill=False,
    grid=False,
    tri="lower",
    plot_histograms_1D=True,
    histograms_1D_density=True,
    n_ticks=3,
    ticks={},
    tick_length=3,
    show_values=False,
    bestfit_method="mode",
    levels_method="hdi",
    credible_interval=0.68,
    n_sigma_for_one_sided_tail=3,
    n_bins=100,
    density_estimation_method="smoothing",
    cmap=plt.cm.viridis,
    cmap_vmin=None,
    cmap_vmax=None,
    colorbar=False,
    colorbar_label=None,
    colorbar_ax=[0.735, 0.5, 0.03, 0.25],
    show_legend=False,
    progress_bar=True,
    alpha=None,
    alpha1D=1,
    alpha2D=1,
    normalize_prob1D=True,
    normalize_prob2D=True,
    scatter_vline_1D=False,
    alpha_for_low_density=False,
    alpha_threshold=0,
    n_points_scatter=-1,
    label_fontsize=24,
    tick_fontsize=14,
    legend_fontsize=24,
    bestfit_fontsize=14,
    de_kwargs={},
    grid_kwargs={},
    hist_kwargs={},
    labels_kwargs={},
    line_kwargs={},
    scatter_kwargs={},
    axlines_kwargs={},
    subplots_kwargs={},
    grouping_kwargs={},
    ticks_kwargs={},
    add_empty_plots_like=None,
    **kwargs,
):
    """
    Plot triangle plot with 1D and 2D histograms, contours, scatter plots, etc.

    :param data: data to plot, can be a dictionary, a recarray or a pandas DataFrame
    :param prob: probability of each point, default: None
    :param func: function to use for plotting, default: 'contour_cl', options:

        - contour_cl (default)
        - density_image
        - scatter_density
        - scatter_prob
        - scatter
        - axlines

    :param color: color for the plot, default: '#0063B9'
    :param label: label for the plot, default: None
    :param lnprobs: lnprob for each sample (used for some best-fit methods),
        default: None
    :param fig: matplotlib figure, default: None
    :param size: size of the panels, if one number is given, the panels are square,
        if two numbers are given, the figure is rectangular, default: 4
    :param params: list of parameters to plot, default: 'all'
    :param params_from: sample or list of samples from which the parameters should
        be taken, default: None
    :param ranges: dictionary with ranges for the parameters, default: {}
    :param labels: list of labels (e.g. latex style) for the parameters for the
        plot
    :param names: list of names of the parameters, only used when input data is
        unstructured array
    :param fill: if the contours should be filled, default: False
    :param grid: if the grid should be plotted, default: False
    :param tri: if upper or lower triangle should be plotted, default: "lower"
    :param plot_histograms_1D: if the 1D histograms should be plotted, default: True
    :param histograms_1D_density: if the 1D histograms should be normalized to 1, default: True
    :param n_ticks: number of ticks on the axes, default: 3
    :param ticks: dict specifying the ticks for each parameter
    :param tick_length: length of the ticks, default: 3
    :param show_values: if best-fit and uncertainty should be given, default: False
    :param bestfit_method: method to use for best-fit,
        options: "mode", "mean", "median", "best_sample" (requires lnprobs),
        default: "mode"
    :param levels_method: method to compute the uncertainty bands,
        options: "hdi", "percentile", "PJ-HPD" (requires lnprobs),
        default: "hdi"
    :param credible_interval: credible interval for the uncertainty bands, default: 0.68
    :param n_sigma_for_one_sided_tail: number of sigma for the one-sided tail,
        default: 3
    :param n_bins: number of bins for the 1D histograms, default: 100
    :param density_estimation_method: method to use for density estimation,
        default="smoothing"
    :param cmap: colormap, default: plt.cm.viridis
    :param cmap_vmin: minimum value for the colormap, default: 0
    :param cmap_vmax: maximum value for the colormap, default: None
    :param colorbar: if a colorbar should be plotted, default: False
    :param colorbar_label: label for the colorbar, default: None
    :param colorbar_ax: position of the colorbar, default: [0.735, 0.5, 0.03, 0.25]
    :param show_legend: if a legend should be plotted, default: False
    :param progress_bar: if a progress bar should be shown, default: True
    :param alpha: alpha for the plots, overwrite alpha1D and alpha2D, default: None
    :param alpha1D: alpha for the 1D histograms, default: 1
    :param alpha2D: alpha for the 2D histograms, default: 1
    :param normalize_prob1D: if the 1D histograms should be normalized for scatter_prob,
        default: True
    :param normalize_prob2D: if the 2D histograms should be normalized for scatter_prob,
        default: True
    :param scatter_vline_1D: if a vertical line should be plotted in the 1D
        histograms for each point when using scatter, default: False
    :param alpha_for_low_density: if low density areas should fade to transparent
    :param alpha_threshold: threshold for the alpha for low density areas
    :param alpha_threshold: threshold from where the fading to transparent should
        start, default: 0
    :param n_points_scatter: number of points to plot when using scatter,
        default: -1 (all)
    :param label_fontsize: fontsize for the labels, default: 24
    :param tick_fontsize: fontsize for the ticks, default: 14
    :param legend_fontsize: fontsize for the legend, default: 24
    :param bestfit_fontsize: fontsize for the bestfit, default: 14
    :param de_kwargs: dict with kwargs for the density estimation, default: {}
    :param grid_kwargs: dict with kwargs for the grid, default: {}
    :param hist_kwargs: dict with kwargs for the 1D histograms, default: {}
    :param labels_kwargs: dict with kwargs for the labels, default: {}
    :param line_kwargs: dict with kwargs for the lines, default: {}
    :param scatter_kwargs: dict with kwargs for the scatter plot, default: {}
    :param axlines_kwargs: dict with kwargs for the vertical lines, default: {}
    :param subplots_kwargs: dict with kwargs for the subplots, default: {}
    :param grouping_kwargs: dict with kwargs for the grouping, default: {}
    :param ticks_kwargs: dict with kwargs for the ticks, default: {}
    :param add_empty_plots_like: DEPRECATED, default: None
    """
    # backwards compatibility
    if "axvline_kwargs" in kwargs:
        LOGGER.warning("axvline_kwargs is deprecated, use axlines_kwargs instead. ")
        axlines_kwargs = kwargs["axvline_kwargs"]

    check_if_names_is_used_correctly(names, data)

    # make sure tri is lower or upper
    if tri[0] == "l":
        tri = "lower"
    if tri[0] == "u":
        tri = "upper"

    # overwrite alpha1D and alpha2D if alpha is given
    if alpha is not None:
        alpha1D = alpha
        alpha2D = alpha

    ###############################
    # prepare data and setup plot #
    ###############################
    data = ensure_rec(data, names=names)
    data, columns, empty_columns = prepare_columns(
        data,
        params=params,
        params_from=params_from,
        add_empty_plots_like=add_empty_plots_like,
    )
    # needed for plotting chains with different automatic limits
    current_ranges = {}
    current_ticks = {}

    # setup everything that grouping works properly
    columns, grouping_indices = setup_grouping(columns, grouping_kwargs)
    labels = get_labels(labels, columns, grouping_indices)
    hw_ratios = get_hw_ratios(columns, grouping_kwargs)

    n_dim = len(columns)

    # setup figure
    prob_label = None
    if prob is not None:
        if np.min(prob) < 0:
            prob_offset = -np.min(prob)
        else:
            prob_offset = 0
        if normalize_prob1D:
            prob1D = (prob + prob_offset) / np.sum(prob + prob_offset)
        else:
            prob1D = None

        if normalize_prob2D:
            prob2D = (prob + prob_offset) / np.sum(prob + prob_offset)
        else:
            # for example to plot an additional parameter in parameter space
            prob_label = prob
            prob2D = None
    else:
        prob1D = None
        prob2D = None

    # Setup triangle (lower or upper)
    if tri[0] == "l":
        tri_indices = np.tril_indices(n_dim, k=-1)
    elif tri[0] == "u":
        tri_indices = np.triu_indices(n_dim, k=1)
    else:
        raise ValueError("tri must be 'lower' or 'upper', not {}".format(tri))

    # Create figure if necessary and get axes
    fig, ax, old_tri = setup_figure(fig, n_dim, hw_ratios, size, subplots_kwargs)
    if old_tri is not None and old_tri != tri:
        double_tri = True
    else:
        double_tri = False
    # get ranges for each parameter (if not specified, max/min of data is used)
    update_current_ranges(current_ranges, ranges, columns, data)

    # Bins for histograms
    hist_binedges = {
        c: np.linspace(*current_ranges[c], num=n_bins + 1) for c in columns
    }
    hist_bincenters = {
        c: (hist_binedges[c][1:] + hist_binedges[c][:-1]) / 2 for c in columns
    }

    if len(color) == len(data):
        color_hist = "k"
    else:
        color_hist = color

    def get_current_ax(ax, tri, i, j):
        if tri[0] == "u":
            axc = ax[i, j]
        else:
            # lower triangle
            axc = ax[i, j]
        if i == j and not plot_histograms_1D and not scatter_vline_1D:
            # in this case axis should not be turned on in this call
            pass
        else:
            # turn on ax sinces it is used
            axc.axis("on")
        return axc

    #################
    # 1D histograms #
    #################
    if plot_histograms_1D and not (func == "axlines"):
        disable_progress_bar = True
        if show_values:
            LOGGER.info("Computing bestfits and levels")
            disable_progress_bar = False
        for i in trange(n_dim, disable=disable_progress_bar):
            if columns[i] != "EMPTY":
                axc = get_current_ax(ax, tri, i, i)
                plot_1d(
                    axc,
                    column=columns[i],
                    param_label=labels[i],
                    data=data,
                    prob=prob1D,
                    ranges=ranges,
                    current_ranges=current_ranges,
                    hist_binedges=hist_binedges,
                    hist_bincenters=hist_bincenters,
                    density_estimation_method=density_estimation_method,
                    density=histograms_1D_density,
                    de_kwargs=de_kwargs,
                    show_values=show_values,
                    color_hist=color_hist,
                    empty_columns=empty_columns,
                    alpha1D=alpha1D,
                    label=label,
                    hist_kwargs=hist_kwargs,
                    fill=fill,
                    lnprobs=lnprobs,
                    levels_method=levels_method,
                    bestfit_method=bestfit_method,
                    credible_interval=credible_interval,
                    sigma_one_tail=n_sigma_for_one_sided_tail,
                    bestfit_fontsize=bestfit_fontsize,
                )

    if (not (func == "axlines") and scatter_vline_1D) | (
        (func == "axlines") and plot_histograms_1D
    ):
        for i in range(n_dim):
            if columns[i] != "EMPTY":
                axc = get_current_ax(ax, tri, i, i)
                add_vline(axc, columns[i], data, color, axlines_kwargs)

    #################
    # 2D histograms #
    #################
    for i, j in tqdm(
        zip(*tri_indices), total=len(tri_indices[0]), disable=not progress_bar
    ):
        if (columns[i] != "EMPTY") & (columns[j] != "EMPTY"):
            axc = get_current_ax(ax, tri, i, j)
            old_xlims, old_ylims = get_old_lims(axc)
            if double_tri:
                if tri == "lower":
                    other_tri = "upper"
                else:
                    other_tri = "lower"
                axc_mirror = get_current_ax(ax, other_tri, j, i)
                old_xlims_mirror, old_ylims_mirror = get_old_lims(axc_mirror)
                old_xlims, old_ylims = get_best_old_lims(
                    old_xlims, old_ylims_mirror, old_ylims, old_xlims_mirror
                )
            if (columns[i] not in data.dtype.names) | (
                columns[j] not in data.dtype.names
            ):
                pass
            elif func == "contour_cl":
                contour_cl(
                    axc,
                    data=data,
                    ranges=current_ranges,
                    columns=columns,
                    i=i,
                    j=j,
                    fill=fill,
                    color=color,
                    de_kwargs=de_kwargs,
                    line_kwargs=line_kwargs,
                    prob=prob,
                    density_estimation_method=density_estimation_method,
                    label=label,
                    alpha=min(
                        (
                            find_alpha(columns[i], empty_columns, alpha2D),
                            find_alpha(columns[j], empty_columns, alpha2D),
                        )
                    ),
                )
            elif func == "density_image":
                density_image(
                    axc,
                    data=data,
                    ranges=current_ranges,
                    columns=columns,
                    i=i,
                    j=j,
                    cmap=cmap,
                    de_kwargs=de_kwargs,
                    vmin=cmap_vmin,
                    vmax=cmap_vmax,
                    prob=prob,
                    density_estimation_method=density_estimation_method,
                    label=label,
                    alpha=min(
                        (
                            find_alpha(columns[i], empty_columns, alpha2D),
                            find_alpha(columns[j], empty_columns, alpha2D),
                        )
                    ),
                    alpha_for_low_density=alpha_for_low_density,
                    alpha_threshold=alpha_threshold,
                )
            elif func == "scatter":
                x, y = get_n_points_for_scatter(
                    data[columns[j]],
                    data[columns[i]],
                    n_points_scatter=n_points_scatter,
                )
                axc.scatter(
                    x,
                    y,
                    c=color,
                    label=label,
                    alpha=min(
                        (
                            find_alpha(columns[i], empty_columns, alpha2D),
                            find_alpha(columns[j], empty_columns, alpha2D),
                        )
                    ),
                    **scatter_kwargs,
                )
            elif func == "scatter_prob":
                if normalize_prob2D:
                    _prob = prob2D
                else:
                    _prob = prob_label
                x, y, _prob = get_n_points_for_scatter(
                    data[columns[j]],
                    data[columns[i]],
                    prob=prob,
                    n_points_scatter=n_points_scatter,
                )
                sorting = np.argsort(_prob)
                axc.scatter(
                    x[sorting],
                    y[sorting],
                    c=_prob[sorting],
                    label=label,
                    cmap=cmap,
                    alpha=min(
                        (
                            find_alpha(columns[i], empty_columns, alpha2D),
                            find_alpha(columns[j], empty_columns, alpha2D),
                        )
                    ),
                    vmin=cmap_vmin,
                    vmax=cmap_vmax,
                    **scatter_kwargs,
                )
            elif func == "scatter_density":
                scatter_density(
                    axc,
                    points1=data[columns[j]],
                    points2=data[columns[i]],
                    n_bins=n_bins,
                    lim1=current_ranges[columns[j]],
                    lim2=current_ranges[columns[i]],
                    n_points_scatter=n_points_scatter,
                    cmap=cmap,
                    label=label,
                    alpha=min(
                        (
                            find_alpha(columns[i], empty_columns, alpha2D),
                            find_alpha(columns[j], empty_columns, alpha2D),
                        )
                    ),
                    vmin=cmap_vmin,
                    vmax=cmap_vmax,
                    **scatter_kwargs,
                )
            elif func == "axlines":
                if len(data[columns[j]]) > 1:
                    raise ValueError(
                        "axlines can only be used with one point, not with {} points".format(
                            len(data[columns[j]])
                        )
                    )
                axc.axvline(
                    x=data[columns[j]],
                    color=color,
                    label=label,
                    alpha=min(
                        (
                            find_alpha(columns[i], empty_columns, alpha2D),
                            find_alpha(columns[j], empty_columns, alpha2D),
                        )
                    ),
                    **axlines_kwargs,
                )
                axc.axhline(
                    y=data[columns[i]],
                    color=color,
                    label=label,
                    alpha=min(
                        (
                            find_alpha(columns[i], empty_columns, alpha2D),
                            find_alpha(columns[j], empty_columns, alpha2D),
                        )
                    ),
                    **axlines_kwargs,
                )
            else:  # pragma: no cover
                raise ValueError(
                    "func must be one of 'contour_cl', 'density_image', "
                    "'scatter_density', 'scatter_prob', 'scatter' or 'axlines', "
                    "not {}".format(func)
                )
            set_limits(
                axc,
                ranges,
                current_ranges,
                columns[i],
                columns[j],
                old_xlims,
                old_ylims,
            )
            if double_tri:
                set_limits(
                    axc_mirror,
                    ranges,
                    current_ranges,
                    columns[j],
                    columns[i],
                    old_ylims,
                    old_xlims,
                )
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

    def plot_xticks(axc, i, j, length=10, direction="in"):
        if i != j:
            axc.xaxis.set_ticks_position("both")
        axc.set_xticks(get_ticks(j))
        axc.tick_params(direction=direction, length=length)

    delete_all_ticks(ax)
    update_current_ticks(current_ticks, columns, ranges, current_ranges, n_ticks)
    if tri[0] == "l" or double_tri:
        local_tri = "lower"
        for i in range(1, n_dim):  # rows
            for j in range(0, i):  # columns
                if columns[i] != "EMPTY" and columns[j] != "EMPTY":
                    axc = get_current_ax(ax, local_tri, i, j)
                    plot_yticks(axc, i, tick_length)

        for i in range(0, n_dim):  # rows
            for j in range(0, i + 1):  # columns
                if columns[i] != "EMPTY" and columns[j] != "EMPTY":
                    axc = get_current_ax(ax, local_tri, i, j)
                    plot_xticks(axc, i, j, tick_length)
    if tri[0] == "u" or double_tri:
        local_tri = "upper"
        for i in range(0, n_dim):  # rows
            for j in range(i + 1, n_dim):  # columns
                if columns[i] != "EMPTY" and columns[j] != "EMPTY":
                    axc = get_current_ax(ax, local_tri, i, j)
                    plot_yticks(axc, i, tick_length)
        for i in range(0, n_dim):  # rows
            for j in range(i, n_dim):  # columns
                if columns[i] != "EMPTY" and columns[j] != "EMPTY":
                    axc = get_current_ax(ax, local_tri, i, j)
                    plot_xticks(axc, i, j, tick_length)

    # ticklabels
    def plot_tick_labels(axc, xy, i, tri, ticks_kwargs):
        ticklabels = [t for t in get_ticks(i)]
        if xy == "y":
            axc.set_yticklabels(
                ticklabels,
                rotation=0,
                fontsize=tick_fontsize,
                **ticks_kwargs,
            )
            if tri[0] == "u":
                axc.yaxis.tick_right()
                axc.yaxis.set_ticks_position("both")
                axc.yaxis.set_label_position("right")
        else:
            # xy == "x":
            axc.set_xticklabels(
                ticklabels,
                rotation=90,
                fontsize=tick_fontsize,
                **ticks_kwargs,
            )
            if tri[0] == "u":
                axc.xaxis.tick_top()
                axc.xaxis.set_ticks_position("both")
                axc.xaxis.set_label_position("top")

    if tri[0] == "l" or double_tri:
        local_tri = "lower"
        # y tick labels
        for i in range(1, n_dim):
            if columns[i] != "EMPTY":
                axc = get_current_ax(ax, local_tri, i, 0)
                plot_tick_labels(axc, "y", i, local_tri, ticks_kwargs)
        # x tick labels
        for i in range(0, n_dim):
            if columns[i] != "EMPTY":
                axc = get_current_ax(ax, local_tri, n_dim - 1, i)
                plot_tick_labels(axc, "x", i, local_tri, ticks_kwargs)
    if tri[0] == "u" or double_tri:
        local_tri = "upper"
        # y tick labels
        for i in range(0, n_dim - 1):
            if columns[i] != "EMPTY":
                axc = get_current_ax(ax, local_tri, i, n_dim - 1)
                plot_tick_labels(axc, "y", i, tri, ticks_kwargs)
        # x tick labels
        for i in range(0, n_dim):
            if columns[i] != "EMPTY":
                axc = get_current_ax(ax, local_tri, 0, i)
                plot_tick_labels(axc, "x", i, tri, ticks_kwargs)

    ########
    # grid #
    ########
    if tri[0] == "l":
        for i in range(1, n_dim):
            for j in range(i):
                if columns[i] != "EMPTY" and columns[j] != "EMPTY":
                    axc = get_current_ax(ax, tri, i, j)
                    if grid:
                        axc.grid(zorder=0, **grid_kwargs)
                    axc.set_axisbelow(True)
    else:
        # tri[0] == "u":
        for i in range(0, n_dim - 1):
            for j in range(i + 1, n_dim):
                if columns[i] != "EMPTY" and columns[j] != "EMPTY":
                    axc = get_current_ax(ax, tri, i, j)
                    if grid:
                        axc.grid(zorder=0, **grid_kwargs)
                    axc.set_axisbelow(True)

    ###########
    # legends #
    ###########
    legend_lines, legend_labels = get_lines_and_labels(ax)
    if tri[0] == "l":
        labelpad = 10
        for i in range(n_dim):
            if columns[i] != "EMPTY":
                axc = get_current_ax(ax, tri, i, 0)

                axc.set_ylabel(
                    labels[i],
                    **labels_kwargs,
                    rotation=90,
                    labelpad=labelpad,
                    fontsize=label_fontsize,
                )
                axc.yaxis.set_label_position("left")
                axc = get_current_ax(ax, tri, n_dim - 1, i)
                axc.set_xlabel(
                    labels[i],
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
                bbox_transform=ax[0, n_dim - 1].transAxes,
                fontsize=legend_fontsize,
            )
    else:
        # if tri[0] == "u":
        labelpad = 20
        for i in range(n_dim):
            if columns[i] != "EMPTY":
                axc = get_current_ax(ax, tri, i, n_dim - 1)
                axc.set_ylabel(
                    labels[i],
                    **labels_kwargs,
                    rotation=90,
                    labelpad=labelpad,
                    fontsize=label_fontsize,
                )
                axc.yaxis.set_label_position("right")
                axc = get_current_ax(ax, tri, 0, i)
                axc.set_xlabel(
                    labels[i],
                    **labels_kwargs,
                    rotation=0,
                    labelpad=labelpad,
                    fontsize=label_fontsize,
                )
                axc.xaxis.set_label_position("top")
        if legend_lines and show_legend:
            # only print legend when there are labels for it
            fig.legend(
                legend_lines,
                legend_labels,
                bbox_to_anchor=(1, 1),
                bbox_transform=ax[n_dim - 1, 0].transAxes,
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
    plt.subplots_adjust(hspace=0, wspace=0)
    fig.align_ylabels()
    fig.align_xlabels()

    rasterize_density_images(ax)

    return fig, ax
