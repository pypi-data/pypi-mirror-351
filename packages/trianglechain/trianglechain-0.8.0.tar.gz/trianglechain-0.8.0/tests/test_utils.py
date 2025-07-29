# Copyright (C) 2023 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher

import itertools

import numpy as np

from trianglechain.utils_plots import (
    find_optimal_ticks,
    get_rounding_digit,
    get_values,
    round_to_significant_digits,
)


def test_find_optimal_ticks():
    # test different ranges
    ranges = [
        (19.984850143697702, 31.59213404475906),
        (2.523270560668945, 6.853178547454834),
        (9.48525226898114e-05, 0.0858542531986735),
        (0.23282038486384884, 9.973045366338624),
        (0.009471846984863282, 19.9993906484375),
        (1.1313378510967596e-06, 0.9799933300743103),
        (0.20000308589839935, 4.999992893768311),
        (0.003999033251941204, 6.301070259643555),
        (20.80723090307617, 29.99982361657715),
        (0.10643716739320755, 19.99801926477051),
        (0.06310505257749557, 299.9904489980469),
        (2.5004139726865105e-05, 0.9992773996124268),
        (-0.8691013322601319, 2.4016526208648683),
    ]
    n_ticks = np.arange(2, 8)
    for r, n in itertools.product(ranges, n_ticks):
        ticks = find_optimal_ticks(r, n_ticks=n)
        # check number of ticks is correct
        assert len(ticks) == n, f"ticks={ticks}, n={n}"
        diff = ticks[1:] - ticks[:-1]
        # check ticks are equally spaced
        assert np.allclose(diff, diff[0]), f"ticks={ticks}, diff={diff}"
        # check that first and last tick are within range
        assert r[0] <= ticks[0] <= r[1], f"ticks={ticks}, r={r}"
        assert r[0] <= ticks[-1] <= r[1], f"ticks={ticks}, r={r}"
        # check that the first and last tick are not too far away from the range
        if ticks[0] - r[0] > diff[0]:
            too_much_space = (ticks[0] - r[0]) - diff[0]
            assert too_much_space < 0.2 * diff[0]
        if r[1] - ticks[-1] > diff[0]:
            too_much_space = (r[1] - ticks[-1]) - diff[0]
            assert too_much_space < 0.2 * diff[0]


def test_round_to_significant_digits():
    round_to_significant_digits(0, 1) == 0
    round_to_significant_digits(0.000000, 2) == 0
    round_to_significant_digits(1.3462654, 2) == 1.3
    round_to_significant_digits(1.3462654, 3) == 1.35
    round_to_significant_digits(0.0013462654, 2) == 0.0013
    round_to_significant_digits(0.0013462654, 3) == 0.00135


def test_get_rounding_digit():
    mean = 0.827
    uncertainty = 0.119
    digit, frmt = get_rounding_digit(uncertainty)
    assert f"{frmt}".format(np.around(mean, digit)) == "0.83"
    assert f"{frmt}".format(np.around(uncertainty, digit)) == "0.12"

    uncertainty = 0.367
    digit, frmt = get_rounding_digit(uncertainty)
    assert f"{frmt}".format(np.around(mean, digit)) == "0.8"
    assert f"{frmt}".format(np.around(uncertainty, digit)) == "0.4"

    uncertainty = 0.097
    digit, frmt = get_rounding_digit(uncertainty)
    assert f"{frmt}".format(np.around(mean, digit)) == "0.83"
    assert f"{frmt}".format(np.around(uncertainty, digit)) == "0.10"

    mean = 827
    uncertainty = 119
    digit, frmt = get_rounding_digit(uncertainty)
    assert f"{frmt}".format(np.around(mean, digit)) == "830"
    assert f"{frmt}".format(np.around(uncertainty, digit)) == "120"

    uncertainty = 367
    digit, frmt = get_rounding_digit(uncertainty)
    assert f"{frmt}".format(np.around(mean, digit)) == "800"
    assert f"{frmt}".format(np.around(uncertainty, digit)) == "400"

    uncertainty = 97
    digit, frmt = get_rounding_digit(uncertainty)
    assert f"{frmt}".format(np.around(mean, digit)) == "830"
    assert f"{frmt}".format(np.around(uncertainty, digit)) == "100"


def test_get_values():
    data = {"a": np.random.normal(0, 1, 1000)}
    _, _, upper, lower = get_values("a", data, lnprobs=None)
    assert lower.startswith("-")
    assert upper.startswith("+")

    # Generate a skewed distribution using the gamma distribution
    shape = 2  # Shape parameter (can be adjusted to control skewness)
    scale = 2  # Scale parameter (can be adjusted to control spread)
    size = 1000  # Number of data points

    data = np.random.gamma(shape, scale, size)
    data = {"a": data}
    _, _, upper, lower = get_values("a", data, lnprobs=None, credible_interval=0.3)
    assert lower.startswith("-")
    assert upper.startswith("-")

    data = -np.random.gamma(shape, scale, size)
    data = {"a": data}
    _, _, upper, lower = get_values("a", data, lnprobs=None, credible_interval=0.3)
    assert lower.startswith("+")
    assert upper.startswith("+")
