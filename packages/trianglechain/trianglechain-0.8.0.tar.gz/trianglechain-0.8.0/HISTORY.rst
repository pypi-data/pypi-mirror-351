.. :changelog:

History
-------

0.8.0 (2025-05-27)
++++++++++++++++++

**New features:**

* `axlines` as a new plot type to add vertical and horizontal lines to the plot.
* consistent font size handling

**Fixes:**

* consistent use of kwargs

0.7.1 (2024-10-02)
++++++++++++++++++

**Fixes:**

* Fixed bug where plotting multiple distributions with tri="u" caused empty plots in the lower triangle.

0.7.0 (2024-09-08)
++++++++++++++++++

**New feature:**

* 1D histograms can be without normalization: `histograms_1D_density=False`

0.6.0 (2024-03-27)
++++++++++++++++++

**New feature:**

* RectangleChain class

0.5.1 (2023-09-01)
++++++++++++++++++

**Fixes:**

* alhpa2D is now an option for all plot types.
* cmap_vmin and cmap_vmax is now an option for all plot types.

0.5.0 (2023-08-08)
++++++++++++++++++

**New features:**

* TypeError when using unknown argument
* non-square panels are now possible
* n_points_scatter to set the number of points in the scatter plot

**Fixes:**

* equally spaced automatic ticks

**Further improvements:**

* improved documentation and docstrings
* coverage tests
* improved tests
* cleanup

0.4.3 (2023-07-01)
++++++++++++++++++

**Fixes:**

* grid is also plotted in the upper triangle if the plotting order is lower upper lower (and vice versa)
* ranges of empty plots are correctly displayed
* added warning for people like Arne that use the parameter names incorrectly.

0.4.2 (2023-06-19)
++++++++++++++++++

**Fix:** scatter_kwargs for scatter_density

0.4.1 (2023-06-09)
++++++++++++++++++

**Fix:** RGB(A) colors in plt.contour

0.4.0 (2023-06-05)
++++++++++++++++++

**New feature:**

* n_sigma_for_one_sided_tail free parameter to manually set the threshold when to use a 2-sided or 1-sided interval

**Fixes:**

* correct normalization when using samples with prob
* avoid upper limits with +- 0.0 and lower limits with -- 0.0

0.3.1 (2023-05-11)
++++++++++++++++++

**Fix:** Labels showing correctly when using upper triangle. Improved documentation.

0.3.0 (2023-04-26)
++++++++++++++++++

**New features:**

* LineChain class
* params_from argument to select parameter from chain
* add_derived_params to add derived_params to the input
* input data can be pandas dataframes
* colors follow the matplotlib color cycles by default
* when computing bestfits and uncertainties, it automatically detects if to show bestfit +/- uncertainty or a lower/upper limit.

**Fixes:**

* ylimits in 1D plots
* tick values when choosing many ticks

**Further improvements:**

* documentation
* dependency cleanup

0.2.1 (2023-03-20)
++++++++++++++++++

**Fix:** 1D histograms when using prob.

0.2.0 (2023-02-09)
++++++++++++++++++

First release on PyPI.

**New features:**

* dictionaries are new possible inputs
* progressbar can be disabled

0.1.2 (2023-02-02)
++++++++++++++++++

**Fix:** Correct normalization of 1D posteriors (credit to Alexander Charles Tikam)

0.1.1 (2022-11-24)
++++++++++++++++++

**Fix:** Number of digits of bestfits and uncertainties are now correctly set.

0.1.0 (2022-10-31)
++++++++++++++++++

First public release on Gitlab.
