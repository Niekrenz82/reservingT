"""
Reading, writing and running loss triangles from CSV files.

Non-UI helpers used by the Streamlit app. They call into `reserving.py`
for all reserve calculations and never modify it.
"""

import numpy as np
import pandas as pd

from reservingt.reserving import BornhuetterFerguson, ChainLadder, Triangle


def _is_number(text: str) -> bool:
    try:
        float(text)
    except ValueError:
        return False
    return True


def read_triangle_csv(source) -> np.ndarray:
    """
    Read a square loss triangle from a CSV file.

    Rows are accident years, columns are development years. Unobserved cells
    are left blank in the file and returned as NaN. A first row that contains
    text (a header) is skipped.
    """
    raw = pd.read_csv(source, header=None, dtype=str).fillna("")
    rows = [[str(cell).strip() for cell in row] for row in raw.itertuples(index=False)]

    if rows and any(cell and not _is_number(cell) for cell in rows[0]):
        rows = rows[1:]

    values = []
    for r, row in enumerate(rows, start=1):
        line = []
        for c, cell in enumerate(row, start=1):
            if cell == "":
                line.append(np.nan)
            elif _is_number(cell):
                line.append(float(cell))
            else:
                raise ValueError(
                    f"Non-numeric value {cell!r} in data row {r}, column {c}."
                )
        values.append(line)

    if len(values) < 2:
        raise ValueError("The triangle needs at least two rows.")

    n_rows, n_cols = len(values), len(values[0])
    if n_rows != n_cols:
        raise ValueError(
            "The triangle must be square: one row per accident year and one "
            f"column per development year. Got {n_rows} rows and {n_cols} columns."
        )

    return np.array(values, dtype=float)


def triangle_to_csv(data: np.ndarray) -> str:
    """Return a triangle as CSV text, with NaN written as blank cells."""
    return pd.DataFrame(data).to_csv(index=False, header=False, na_rep="")


def as_form(data: np.ndarray, incremental: bool, want_incremental: bool) -> np.ndarray:
    """
    Return the observed triangle in cumulative or incremental form, for display.
    Unobserved cells stay NaN.
    """
    cumulative = (
        Triangle(data, incremental=incremental).to_cumulativ() if incremental else data
    )
    if want_incremental:
        return Triangle(cumulative, incremental=False).to_incremental()
    return cumulative


def run_method(data: np.ndarray, incremental: bool, method: str, prior=None) -> dict:
    """
    Run a reserving method on a triangle.

    `method` is "chain_ladder" or "bornhuetter_ferguson". BF needs `prior`,
    one prior ultimate loss per accident year. The triangle is converted to
    cumulative form first, because the BF method expects cumulative data.
    """
    tri = Triangle(data, incremental=incremental)
    cumulative = Triangle(tri.to_cumulativ(), incremental=False) if incremental else tri

    if method == "chain_ladder":
        return ChainLadder().calc_reserve(triangle=cumulative)

    if method == "bornhuetter_ferguson":
        if prior is None:
            raise ValueError(
                "Bornhuetter-Ferguson needs a prior ultimate for each accident year."
            )
        prior = np.asarray(prior, dtype=float)
        if prior.shape != (tri.n,):
            raise ValueError(f"Expected {tri.n} prior ultimates, got {prior.shape[0]}.")
        return BornhuetterFerguson(prior=prior).calc_reserve(triangle=cumulative)

    raise ValueError(f"Unknown method {method!r}.")
