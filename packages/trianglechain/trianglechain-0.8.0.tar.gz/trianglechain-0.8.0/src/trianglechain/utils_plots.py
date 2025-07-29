# Copyright (C) 2022 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Tomasz Kacprzak, Silvan Fischbacher

import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from cosmic_toolbox import arraytools as at
from cosmic_toolbox import logger
from matplotlib.ticker import FormatStrFormatter
from scipy.stats import median_abs_deviation
from sklearn.decomposition import PCA

from trianglechain import bestfit, limits
from trianglechain.params import ensure_rec

LOGGER = logger.get_logger(__file__)


def prepare_columns(data, params="all", params_from=None, add_empty_plots_like=None):
    """
    Prepare the columns of the data to be plotted.

    :param data: The data to plot.
    :param params: The parameters to plot.
        If "all", all parameters in the data will be plotted.
        If a list of strings, only the parameters with the given names will be plotted.
    :param params_from: data to get the parameters from.
    :param add_empty_plots_like: DEPRECATED: data to get the parameters from.
    :return: The data with only the columns to be plotted, the list of column names
        and the list of empty columns.
    """
    empty_columns = []
    if params_from is not None:
        par = []
        if not isinstance(params_from, (list, tuple)):
            # make a list out of single samples
            params_from = [params_from]

        for p in params_from:
            # add all the parameters of the samples
            par.append(ensure_rec(p).dtype.names)
        if params == "all":
            params = merge_lists(par)
            LOGGER.debug(f"new params: {params}")
        else:
            LOGGER.warning("parameter params_from overwritten with params")
    if add_empty_plots_like is not None:
        columns = data.dtype.names
        data2 = ensure_rec(add_empty_plots_like)
        columns2 = data2.dtype.names
        new_data = np.zeros(len(data), dtype=data2.dtype)
        for c in columns2:
            if c in columns:
                new_data[c] = data[c]
            else:
                new_data[c] = data2[c][np.random.randint(0, len(data2), len(data))]
                empty_columns.append(c)
        data = new_data
    if params != "all":
        columns = []
        new_data = {}
        for i, p in enumerate(params):
            try:
                new_data[p] = data[p]
                columns.append(p)
            except Exception:
                columns.append(p)
                empty_columns.append(i)
        data = at.dict2rec(new_data)
    else:
        columns = data.dtype.names
    return data, columns, empty_columns


def merge_lists(lists):
    """
    Merge a list of lists into a new list, removing duplicates and maintaining the
    order of the elements.

    :param lists: A list of input lists.
    :return: A new list with unique elements, maintaining the order of the elements.

    Example:
    >>> lists = [["a", "b", "c"], ["c", "d"], ["e", "f", "g"], ["a", "g"]]
    >>> merge_lists(lists)
    ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    """
    merged_list = []
    for li in lists:
        for i in li:
            if i not in merged_list:
                merged_list.append(i)
    return merged_list


def setup_grouping(columns, grouping_kwargs):
    """
    Setup the grouping of the plots.

    :param columns: The list of columns to be plotted.
    :param grouping_kwargs: The grouping keyword arguments.
    :return: The new list of columns, the grouping indices and the number of columns
        per group.
    """
    try:
        grouping_indices = np.asarray(grouping_kwargs["n_per_group"])[:-1]
        ind = 0
        for g in grouping_indices:
            ind += g
            columns = np.insert(np.array(columns, dtype="<U32"), ind, "EMPTY")
            ind += 1
        return columns, grouping_indices
    except Exception:
        return columns, None


def get_labels(labels, columns, grouping_indices=[]):
    """
    Get the labels for the plots. If no labels are given, the columns are used as labels.

    :param labels: The labels to be used.
    :param columns: The list of columns to be plotted.
    :param grouping_indices: The grouping indices.
    :return: The new list of labels.
    """
    # Axes labels
    if labels is None:
        labels = columns
    else:
        try:
            ind = 0
            for g in grouping_indices:
                ind += g
                labels = np.insert(labels, ind, "EMPTY")
                ind += 1
        except Exception:
            pass
    return labels


def get_hw_ratios(columns, grouping_kwargs):
    """
    Get the height/width ratios for the plots.

    :param columns: The list of columns to be plotted.
    :param grouping_kwargs: The grouping keyword arguments.
    :return: The new list of height/width ratios.
    """
    hw_ratios = np.ones_like(columns, dtype=float)
    for i, lab in enumerate(columns):
        if lab == "EMPTY":
            hw_ratios[i] = grouping_kwargs["empty_ratio"]
    return hw_ratios


def setup_figure(fig, n_box, hw_ratios, size, subplots_kwargs):
    """
    Setup the figure.

    :param fig: The figure to be used.
    :param n_box: The number of boxes.
    :param hw_ratios: The height/width ratios.
    :param size: The size of the figure.
    :param subplots_kwargs: The keyword arguments for the subplots.
    :return: The figure and the axes.
    """
    # Setup the figure size
    if isinstance(size, (list, tuple)):
        x_size = size[0]
        y_size = size[1]
    else:
        x_size = size
        y_size = size

    if fig is None:
        fig, _ = plt.subplots(
            nrows=n_box,
            ncols=n_box,
            figsize=(sum(hw_ratios) * x_size, sum(hw_ratios) * y_size),
            gridspec_kw={
                "height_ratios": hw_ratios,
                "width_ratios": hw_ratios,
            },
            **subplots_kwargs,
        )
        ax = np.array(fig.get_axes()).reshape(n_box, n_box)
        for axc in ax.ravel():
            # remove all unused axs
            axc.axis("off")
        old_tri = None
    else:
        ax = np.array(fig.get_axes())
        while len(ax) != n_box * n_box:
            # remove colorbar from before
            ax = ax[:-1]
        ax = ax.reshape(n_box, n_box)
        old_tri = check_orientation(ax)
    return fig, ax, old_tri


def check_orientation(ax):
    """
    Check the orientation of the axes of an previously created figure.

    :param ax: The axes.
    :return: The orientation of the axes, either "upper", "lower" or "both".
    """
    if ax[-1, 0].axison:
        if ax[0, -1].axison:
            return "both"
        return "lower"
    else:
        return "upper"


def update_current_ranges(current_ranges, ranges, columns, data):
    """
    Update the current ranges of the data.

    :param current_ranges: The current ranges.
    :param ranges: The ranges.
    :param columns: The list of columns to be plotted.
    :param data: The data.
    :return: The new current ranges.
    """
    eps = 1e-6
    for c in columns:
        if c not in ranges:
            if (c == "EMPTY") | (c not in data.dtype.names):
                current_ranges[c] = (np.nan, np.nan)
            else:
                current_ranges[c] = (np.amin(data[c]) - eps, np.amax(data[c]) + eps)
        else:
            current_ranges[c] = ranges[c]


def update_current_ticks(current_ticks, columns, ranges, current_ranges, n_ticks):
    """
    Update the current ticks of the data.

    :param current_ticks: The current ticks.
    :param columns: The list of columns to be plotted.
    :param ranges: The ranges.
    :param current_ranges: The current ranges.
    :param n_ticks: The number of ticks.
    :return: The new current ticks.
    """
    for c in columns:
        if c not in current_ticks:
            if c == "EMPTY":
                current_ticks[c] = np.zeros(n_ticks)
            else:
                try:
                    current_ticks[c] = find_optimal_ticks(
                        (ranges[c][0], ranges[c][1]), n_ticks
                    )
                except Exception:
                    if not np.isnan(current_ranges[c][0]):
                        current_ticks[c] = find_optimal_ticks(
                            (current_ranges[c][0], current_ranges[c][1]), n_ticks
                        )
                    else:
                        current_ticks[c] = np.zeros(n_ticks)


def get_old_lims(axc):
    """
    Get the old limits of the axes.

    :param axc: The axes.
    :return: The old limits.
    """
    if axc.lines or axc.collections:
        old_ylims = axc.get_ylim()
        old_xlims = axc.get_xlim()
    else:
        old_ylims = (np.nan, np.nan)
        old_xlims = (np.nan, np.nan)
    return old_xlims, old_ylims


def get_best_old_lims(xlim1, xlim2, ylim1, ylim2):
    """
    Get the best old limits of the axes. This is used to ensure that the limits
    of the axes are not changed when a new plot is added.

    :param xlim1: The old x-limits.
    :param xlim2: The new x-limits.
    :param ylim1: The old y-limits.
    :param ylim2: The new y-limits.
    :return: The best old limits.
    """
    xlow = np.nanmin([xlim1[0], xlim2[0]])
    xhigh = np.nanmax([xlim1[1], xlim2[1]])
    ylow = np.nanmin([ylim1[0], ylim2[0]])
    yhigh = np.nanmax([ylim1[1], ylim2[1]])
    return (xlow, xhigh), (ylow, yhigh)


def get_values(
    column,
    data,
    lnprobs,
    levels_method="hdi",
    bestfit_method="mean",
    credible_interval=0.68,
    sigma_one_tail=3,
):
    """
    Get the values for the best fit and the uncertainty.

    :param column: The column.
    :param data: The data.
    :param lnprobs: The log probabilities.
    :param levels_method: The method to compute the uncertainty.
    :param bestfit_method: The method to compute the best fit.
    :param credible_interval: The credible interval.
    :param sigma_one_tail: how many sigma should be used to decide if one tailed
        credible interval should be used
        defaults to 3
    :return: The best fit and the uncertainty.
    """
    lim, two_tail, side = limits.get_levels(
        data[column],
        lnprobs,
        levels_method,
        credible_interval,
        sigma_one_tail=sigma_one_tail,
    )
    if two_tail:
        lower, upper = lim
        bf = bestfit.get_bestfit(data[column], lnprobs, bestfit_method)
        uncertainty = (upper - lower) / 2
        rounding_digit, frmt = get_rounding_digit(uncertainty)
        str_bf = f"{frmt}".format(np.around(bf, rounding_digit))

        if np.around(bf - lower, rounding_digit) < 0:
            # special case where the bestfit is not in the interval
            low = f"+{frmt}".format(abs(np.around(bf - lower, rounding_digit)))
        else:
            low = f"-{frmt}".format(abs(np.around(bf - lower, rounding_digit)))

        if np.around(upper - bf, rounding_digit) < 0:
            # special case where the bestfit is not in the interval
            up = f"-{frmt}".format(abs(np.around(upper - bf, rounding_digit)))
        else:
            up = f"+{frmt}".format(abs(np.around(upper - bf, rounding_digit)))

        return two_tail, str_bf, up, low
    else:
        uncertainty_estimate = np.std(data[column])
        rounding_digit, frmt = get_rounding_digit(uncertainty_estimate)
        return two_tail, side, f"{frmt}".format(np.around(lim, rounding_digit)), None


def get_rounding_digit(uncertainty):
    """
    Get the rounding digit and the format from PDG conventions.

    :param uncertainty: The uncertainty.
    :return: The rounding digit and the format.
    """
    first_significant_digit = math.floor(np.log10(uncertainty))
    u = round_to_significant_digits(uncertainty, 3) * 10 ** (
        -first_significant_digit + 2
    )
    if u > 100 and u < 354:
        significant_digits_to_round = 2
    elif u < 949:
        significant_digits_to_round = 1
    else:
        # technically, u should be rounded up to 1000 and two significant digits
        # should be used, but keeping u as is and using one significant digit
        # is more equivalent to that.
        significant_digits_to_round = 1
    uncertainty = 1000 / 10 ** (-first_significant_digit + 2)
    rounding_digit = -(math.floor(np.log10(uncertainty)) - significant_digits_to_round)
    if rounding_digit > 0:
        frmt = "{{:.{}f}}".format(rounding_digit)
    else:
        frmt = "{:.0f}"
    return rounding_digit, frmt


def safe_normalise(p):
    """
    Normalise the array without x values.

    :param p: The array.
    :return: The normalised array.
    """
    # fix to use arrays
    if np.sum(p) != 0:
        p = p / np.sum(p)
    return p


def normalise(y, x):
    """
    Normalise the array with x values.

    :param y: The array.
    :param x: The x values.
    :return: The normalised array.
    """
    return y / np.trapz(y, x)


def delete_all_ticks(ax):
    """
    Delete all ticks from the axes.

    :param ax: The axes.
    """
    for axc in ax.ravel():
        axc.set_xticks([])
        axc.set_yticks([])
        axc.set_xticklabels([])
        axc.set_yticklabels([])
        axc.set_axisbelow(True)


def round_to_significant_digits(number, significant_digits):
    """
    Round the number to the given number of significant digits.

    :param number: The number.
    :param significant_digits: The number of significant digits.
    :return: The rounded number.
    """
    try:
        return round(
            number,
            significant_digits - int(math.floor(math.log10(abs(number)))) - 1,
        )
    except Exception:
        return number


def find_optimal_ticks(range_of_param, n_ticks=3):
    """
    Find the optimal ticks for the given range.

    :param range_of_param: The range of the parameter.
    :param n_ticks: The number of ticks.
    :return: The ticks.
    """
    diff = range_of_param[1] - range_of_param[0]
    ticks = np.zeros(n_ticks)

    # mathematical center and tick interval
    tick_interval = diff / (n_ticks + 1)
    center = range_of_param[0] + diff / 2

    # first significant digit for rounding
    significant_digit = math.floor(np.log10(tick_interval))

    for i in range(10 * n_ticks):
        rounded_center = np.around(center, -significant_digit + i)
        if abs(rounded_center - center) / tick_interval < 0.05:
            break
    for i in range(10 * n_ticks):
        # determine tick_interval when rounding to significant digit
        rounded_tick_interval = np.around(tick_interval, -significant_digit)
        start = np.around(
            rounded_center - (n_ticks - 1) / 2 * rounded_tick_interval,
            -significant_digit,
        )

        for j in range(n_ticks):
            if n_ticks % 2 != 0:
                ticks[j] = np.around(
                    start + j * rounded_tick_interval, -significant_digit
                )
            else:
                ticks[j] = np.around(
                    start + j * rounded_tick_interval, -significant_digit + 1
                )

        # check if ticks are inside parameter space and
        # not too close to each other
        if (
            (ticks[0] < range_of_param[0])
            or (ticks[-1] > range_of_param[1])
            or ((ticks[0] - range_of_param[0]) > 1.2 * rounded_tick_interval)
            or ((range_of_param[1] - ticks[-1]) > 1.2 * rounded_tick_interval)
        ):
            significant_digit -= 1
        else:
            break
    if (
        significant_digit == math.floor(np.log10(tick_interval)) - 10 * n_ticks
    ):  # pragma: no cover
        LOGGER.warning(
            "Could not find optimal ticks, please report this to the developer."
        )
        LOGGER.warning("Send the following information:")
        LOGGER.warning(f"range_of_param: {range_of_param}, n_ticks: {n_ticks}")
        LOGGER.warning("to silvanf@phys.ethz")
        for i in range(n_ticks):
            start = center - (n_ticks - 1) / 2 * tick_interval
            ticks[i] = np.around(start + i * tick_interval, -significant_digit)
    return ticks


def get_best_lims(new_xlims, new_ylims, old_xlims, old_ylims):
    """
    Get the best limits for the axes.

    :param new_xlims: The new x limits.
    :param new_ylims: The new y limits.
    :param old_xlims: The old x limits.
    :param old_ylims: The old y limits.
    :return: The best limits.
    """
    xlims = (
        np.nanmin([new_xlims[0], old_xlims[0]]),
        np.nanmax([new_xlims[1], old_xlims[1]]),
    )
    ylims = (
        np.nanmin([new_ylims[0], old_ylims[0]]),
        np.nanmax([new_ylims[1], old_ylims[1]]),
    )
    return xlims, ylims


def add_vline(axc, column, data, color, axvline_kwargs):
    """
    Add a vertical line to the axes.

    :param axc: The axes to add the line to.
    :param column: The column of the data to add the line to.
    :param data: The data which is used to add a line
    :param color: The color of the line.
    :param axvline_kwargs: The kwargs for the axvline.
    """
    if np.size(data[column]) > 1:
        for d in data[column]:
            axc.axvline(d, color=color, **axvline_kwargs)
    else:
        axc.axvline(data[column], color=color, **axvline_kwargs)


def set_limits(axc, ranges, current_ranges, col1, col2, old_xlims, old_ylims):
    """
    Set the limits of the axes. If ranges are not specified, the range is determined
    automatically using current and previous plots.

    :param axc: The axis to set the limits for.
    :param ranges: The ranges to set. If not specified, the current ranges are used.
    :param current_ranges: The current ranges.
    :param col1: The first column of the data.
    :param col2: The second column of the data.
    :param old_xlims: previous limits of the x axis
    :param old_ylims: previous limits of the y axis
    """
    current_ranges[col2], current_ranges[col1] = get_best_lims(
        current_ranges[col2],
        current_ranges[col1],
        old_xlims,
        old_ylims,
    )
    try:
        xlims = ranges[col2]
    except Exception:
        xlims = current_ranges[col2]
    try:
        ylims = ranges[col1]
    except Exception:
        ylims = current_ranges[col1]

    axc.set_xlim(xlims)
    if np.isfinite(ylims[0]):
        axc.set_ylim(ylims)
    axc.get_yaxis().set_major_formatter(FormatStrFormatter("%.3e"))
    axc.get_xaxis().set_major_formatter(FormatStrFormatter("%.3e"))


def pixel_coords(x, ranges, n_pix_img):
    """
    Convert the coordinates to pixel coordinates.

    :param x: The coordinates.
    :param ranges: The ranges.
    :param n_pix_img: The number of pixels.
    :return: The pixel coordinates.
    """
    xt = np.atleast_2d(x.copy())
    for i in range(xt.shape[0]):
        xt[i] -= ranges[i][0]
        xt[i] /= ranges[i][1] - ranges[i][0]
    return xt * n_pix_img


def get_smoothing_sigma(x, max_points=5000):
    """
    Get the smoothing sigma for the KDE.

    :param x: The data to smooth.
    :param max_points: The maximum number of points to use.
    :return: The smoothing sigma.
    """

    x = np.atleast_2d(x)

    assert x.shape[0] in [1, 2], "x must be 1D or 2D array"
    if x.shape[0] == 2:
        pca = PCA()
        pca.fit(x.T)
        sig_pix = np.sqrt(pca.explained_variance_[-1])
        return sig_pix

    # x.shape[0] == 1:
    mad = median_abs_deviation(x, axis=1)
    sig_pix = np.min(mad)
    return sig_pix


def find_alpha(column, empty_columns, alpha=1):
    """
    Find the alpha value for the column.

    :param column: The column to find the alpha for.
    :param empty_columns: The empty columns.
    :param alpha: The alpha value.
    :return: The alpha value.
    """
    if column in empty_columns:
        return 0
    else:
        return alpha


def get_lines_and_labels(ax):
    """
    Get the lines and labels of the axes for the legend.

    :param ax: The axes to get the lines and labels from.
    :return: The lines and labels.
    """
    lines = []
    labels = []

    x, y = ax.shape
    for i in range(x):
        for j in range(y):
            lis, las = ax[i, j].get_legend_handles_labels()
            for li, la in zip(lis, las):
                if la not in labels:
                    labels.append(la)
                    lines.append(li)
    return lines, labels


def compute_plot_limits(x, margin=0.05):
    """
    Compute the plot limits.

    :param x: The data to compute the limits for.
    :param margin: The margin to add to the limits.
    :return: The limits.
    """
    min_x = np.nanmin(x)
    max_x = np.nanmax(x)
    diff_x = max_x - min_x
    min_x -= diff_x * margin
    max_x += diff_x * margin
    return min_x, max_x


def get_n_points_for_scatter(x, y, n_points_scatter=-1, prob=None):
    """
    Get the number of points to use for the scatter plot.

    :param x: The x data.
    :param y: The y data.
    :param n_points_scatter: The number of points to use for the scatter plot.
        If -1, all points are used.
    :param prob: The probability to use for the scatter plot.
    :return: The x, y and prob data.
    """
    if n_points_scatter > 0:
        select = np.random.choice(x.shape[0], n_points_scatter)
        if prob is None:
            return x[select], y[select]
        else:
            return x[select], y[select], prob[select]
    else:
        if prob is None:
            return x, y
        else:
            return x, y, prob


def add_colorbar(
    fig,
    cmap_vmin,
    cmap_vmax,
    cmap,
    colorbar_ax,
    colorbar_label,
    label_fontsize,
    tick_fonsize,
    prob_label=None,
):
    """
    Add a colorbar to the figure.

    :param fig: The figure to add the colorbar to.
    :param cmap_vmin: The minimum value of the colorbar.
    :param cmap_vmax: The maximum value of the colorbar.
    :param cmap: The colormap to use.
    :param colorbar_ax: The axes to use for the colorbar.
    :param colorbar_label: The label of the colorbar.
    :param label_fontsize: The fontsize of the label.
    :param grid_kwargs: The keyword arguments for the grid.
    :param prob_label: The probability label.
    """
    # get correct labels for the colorbar if prob is not a probability
    if cmap_vmin is None:
        try:
            cmap_vmin = min(prob_label)
        except Exception:
            pass
    if cmap_vmax is None:
        try:
            cmap_vmax = max(prob_label)
        except Exception:
            pass
    norm = mpl.colors.Normalize(vmin=cmap_vmin, vmax=cmap_vmax)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    cbar = fig.colorbar(sm, cax=fig.add_axes(colorbar_ax))
    cbar.ax.tick_params(labelsize=tick_fonsize)
    cbar.set_label(colorbar_label, fontsize=label_fontsize)


def rasterize_density_images(ax):
    """
    Rasterize the density images.

    :param ax: The axes to rasterize.
    """
    for axc in ax.flatten():
        for c in axc.collections:
            if isinstance(c, mpl.collections.QuadMesh):
                # rasterize density images to avoid ugly aliasing
                # when saving as a pdf
                c.set_rasterized(True)
