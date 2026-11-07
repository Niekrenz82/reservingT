"""
Cape Cod (Stanard-Buhlmann) reserving method.

Cape Cod is Bornhuetter-Ferguson with a prior that comes from the data: one
expected loss ratio (ELR) is estimated from the whole triangle and applied to
the exposure of each accident year. The ELR is kept in `reserving.py`'s
`ReservingMethod` interface, and the projection reuses `BornhuetterFerguson`.
"""

import numpy as np

from reservingt.reserving import (
    BornhuetterFerguson,
    ChainLadder,
    ReservingMethod,
    Triangle,
)


class CapeCod(ReservingMethod):
    """
    Cape Cod reserving. `exposure` holds one exposure (e.g. premium) per accident year.
    """

    def __init__(self, exposure: np.ndarray):
        self.exposure = np.asarray(exposure, dtype=float)

    def calc_reserve(self, triangle: Triangle):
        cumulative = (
            Triangle(triangle.to_cumulativ(), incremental=False)
            if triangle.incremental
            else triangle
        )
        n = cumulative.n
        exposure = self.exposure
        if exposure.shape != (n,):
            raise ValueError(f"Expected {n} exposures, got {exposure.shape[0]}.")
        if not np.all(np.isfinite(exposure)) or np.any(exposure <= 0):
            raise ValueError("Every accident year needs a positive exposure.")

        factors = ChainLadder().calc_reserve(triangle=cumulative)["development_factor"]

        # Cumulative to ultimate for each accident year, from its latest observed
        # development year (row i has its latest value in column n-1-i).
        cdf = np.array([np.prod(factors[n - 1 - i:]) for i in range(n)])
        percent_developed = 1 / cdf
        latest = np.array([cumulative.data[i, n - 1 - i] for i in range(n)])

        elr = latest.sum() / np.sum(exposure * percent_developed)
        result = BornhuetterFerguson(prior=elr * exposure).calc_reserve(triangle=cumulative)
        return {
            **result,
            "elr": elr,
            "percent_developed": percent_developed,
        }
