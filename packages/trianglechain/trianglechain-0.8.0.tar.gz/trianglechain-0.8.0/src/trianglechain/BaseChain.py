# Copyright (C) 2022 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher, Tomasz Kacprzak


from functools import partial

import matplotlib.pyplot as plt


class BaseChain:
    """
    Base class to produce plots.
    Parameters defined for this class are used for all plots that are added to the
    figure. If you want to change the parameters for a specific plot, you can do so
    by passing the parameters to the plotting function.

    :param fig: matplotlib figure, default: None
    :param size: size of the panels, default: 4
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
    :param orientation: orientation for LineChain, default: "horizontal"
    :param line_space: space between lines in LineChain, default: 0.5
    :param plot_histograms_1D: if the 1D histograms should be plotted, default: True
    :param histograms_1D_density: if the 1D histograms should be normalized to 1,
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
    :param alpha1D: alpha for the 1D histograms, default: 1
    :param alpha2D: alpha for the 2D histograms, default: 1
    :param alpha: alpha for the 2D histograms in LineChain, if passed to TriangleChain,
        overwrites the alpha1D and alpha2D value, default: 1
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
    :param label_fontsize: fontsize of the parameter labels, default: 24
    :param tick_fontsize: fontsize of the numbers on the axes, default: 14
    :param legend_fontsize: fontsize of the legend, default: None (uses label_fontsize)
    :param bestfit_fontsize: fontsize of the bestfit and uncertainty, default: 14
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

    :param grid_kwargs: kwargs for the plot grid, with keys:

        - fontsize_ticklabels:
            font size for tick labels, default: 14
        - font_family:
            font family for tick labels, default: sans-serif

    :param hist_kwargs: kwargs for the 1D histograms, passed to plt.hist function
    :param labels_kwargs: kwargs for the x and y labels
    :param line_kwargs: kwargs for the lines, passed to plt.contour and plt.contourf
    :param scatter_kwargs: kwargs for the scatter plot, passed to plt.scatter
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
        kwargs.setdefault("ticks", {})
        kwargs.setdefault("ranges", {})
        kwargs.setdefault("labels", None)
        kwargs.setdefault("n_bins", 100)
        kwargs.setdefault("de_kwargs", {})
        kwargs.setdefault("grid_kwargs", {})
        kwargs.setdefault("hist_kwargs", {})
        kwargs.setdefault("labels_kwargs", {})
        kwargs.setdefault("line_kwargs", {})
        kwargs.setdefault("axlines_kwargs", {})
        kwargs.setdefault("density_estimation_method", "smoothing")
        kwargs.setdefault("n_ticks", 3)
        kwargs.setdefault("tick_length", 3)
        kwargs.setdefault("fill", False)
        kwargs.setdefault("grid", False)
        kwargs.setdefault("scatter_kwargs", {})
        kwargs.setdefault("grouping_kwargs", {})
        kwargs.setdefault("subplots_kwargs", {})
        kwargs.setdefault("add_empty_plots_like", None)
        kwargs.setdefault("label_fontsize", 24)
        kwargs.setdefault("tick_fontsize", 14)
        kwargs.setdefault("legend_fontsize", None)
        kwargs.setdefault("bestfit_fontsize", 14)
        kwargs.setdefault("params", "all")
        kwargs.setdefault("params_from", None)
        kwargs.setdefault("names", None)
        kwargs.setdefault("tri", "lower")
        kwargs.setdefault("cmap", "viridis")
        kwargs.setdefault("cmap_vmin", None)
        kwargs.setdefault("cmap_vmax", None)
        kwargs.setdefault("colorbar", False)
        kwargs.setdefault("colorbar_label", None)
        kwargs.setdefault("colorbar_ax", [0.735, 0.5, 0.03, 0.25])
        kwargs.setdefault("line_space", 0.5)
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("normalize_prob1D", True)
        kwargs.setdefault("normalize_prob2D", True)
        kwargs.setdefault("progress_bar", True)
        kwargs.setdefault("plot_histograms_1D", True)
        kwargs.setdefault("histograms_1D_density", True)
        kwargs.setdefault("bestfit_method", "mode")
        kwargs.setdefault("levels_method", "hdi")
        kwargs.setdefault("show_values", False)
        kwargs.setdefault("show_legend", False)
        kwargs.setdefault("credible_interval", 0.68)
        kwargs.setdefault("n_sigma_for_one_sided_tail", 3)
        kwargs.setdefault("alpha1D", 1)
        kwargs.setdefault("alpha2D", 1)
        kwargs.setdefault("alpha", None)
        kwargs.setdefault("alpha_for_low_density", False)
        kwargs.setdefault("alpha_threshold", 0)
        kwargs.setdefault("n_points_scatter", -1)
        kwargs.setdefault("scatter_vline_1D", False)
        kwargs["de_kwargs"].setdefault("n_points", kwargs["n_bins"])
        kwargs["de_kwargs"].setdefault("levels", [0.68, 0.95])
        kwargs["de_kwargs"].setdefault("n_levels_check", 2000)
        kwargs["de_kwargs"].setdefault("smoothing_parameter1D", 0.1)
        kwargs["de_kwargs"].setdefault("smoothing_parameter2D", 0.2)
        kwargs["de_kwargs"]["levels"].sort()
        if kwargs["fill"]:
            kwargs["line_kwargs"].setdefault("linewidths", 0.5)
        else:
            kwargs["line_kwargs"].setdefault("linewidths", 4)
        kwargs["grid_kwargs"].setdefault("linestyle", "--")
        kwargs["hist_kwargs"].setdefault("lw", 4)
        kwargs["labels_kwargs"].setdefault("family", "sans-serif")
        kwargs["grouping_kwargs"].setdefault("n_per_group", None)
        kwargs["grouping_kwargs"].setdefault("empty_ratio", 0.2)

        if kwargs["legend_fontsize"] is None:
            kwargs["legend_fontsize"] = kwargs["label_fontsize"]

        self._check_unexpected_kwargs(kwargs)
        self.fig = fig
        self.size = size
        self.kwargs = kwargs
        self.funcs = [
            "contour_cl",
            "density_image",
            "scatter",
            "scatter_prob",
            "scatter_density",
            "axlines",
        ]
        self.colors = []

    def add_plotting_functions(self, func_add_plot):
        """
        Add plotting functions to the class.

        :param func_add_plot: function that adds a plot to the class
        """

        for fname in self.funcs:
            f = partial(func_add_plot, plottype=fname)
            doc = (
                "This function is equivalent to add_plot with \n"
                f"plottype={fname} \n" + func_add_plot.__doc__
            )
            f.__doc__ = doc
            setattr(self, fname, f)

    def setup_color(self, color):
        """
        Setup color for plotting. If color is None, find next color in cycle.

        :param color: color for plotting
        :return: color
        """

        if color is None:
            # find automatic next color
            pos_in_cycle = len(self.colors)
            colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
            self.colors.append(colors)
            return colors[pos_in_cycle % len(colors)]
        else:
            return color

    def _check_unexpected_kwargs(self, kwargs):
        """
        Check for unexpected kwargs.

        :param kwargs: kwargs to check
        """
        expected_kwargs = [
            "ticks",
            "ranges",
            "labels",
            "n_bins",
            "de_kwargs",
            "grid_kwargs",
            "hist_kwargs",
            "labels_kwargs",
            "line_kwargs",
            "axvline_kwargs",  # backward compatibility
            "axlines_kwargs",
            "density_estimation_method",
            "n_ticks",
            "tick_length",
            "fill",
            "grid",
            "scatter_kwargs",
            "grouping_kwargs",
            "subplots_kwargs",
            "add_empty_plots_like",
            "label_fontsize",
            "tick_fontsize",
            "legend_fontsize",
            "bestfit_fontsize",
            "params",
            "params_from",
            "names",
            "tri",
            "cmap",
            "cmap_vmin",
            "cmap_vmax",
            "colorbar",
            "colorbar_label",
            "colorbar_ax",
            "line_space",
            "orientation",
            "normalize_prob1D",
            "normalize_prob2D",
            "progress_bar",
            "plot_histograms_1D",
            "histograms_1D_density",
            "bestfit_method",
            "levels_method",
            "show_values",
            "show_legend",
            "credible_interval",
            "n_sigma_for_one_sided_tail",
            "alpha",
            "alpha1D",
            "alpha2D",
            "alpha_for_low_density",
            "alpha_threshold",
            "n_points_scatter",
            "scatter_vline_1D",
        ]
        unexpected_kwargs = set(kwargs.keys()) - set(expected_kwargs)
        if len(unexpected_kwargs) > 0:
            raise TypeError(
                "Unexpected keyword argument: {}".format(unexpected_kwargs.pop())
            )
