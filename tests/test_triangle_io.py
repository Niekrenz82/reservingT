from pathlib import Path

import numpy as np
import pytest

from reservingt.reserving import Triangle
from reservingt.triangle_io import (
    as_form,
    read_triangle_csv,
    run_method,
    triangle_to_csv,
)

TESTDATA = Path(__file__).resolve().parents[1] / "testdata"


def test_reads_cumulative_sample(cum_5x5):
    data = read_triangle_csv(TESTDATA / "cumulative_5x5.csv")
    np.testing.assert_array_equal(data, cum_5x5)


def test_reads_incremental_sample(cum_5x5):
    data = read_triangle_csv(TESTDATA / "incremental_5x5.csv")
    expected = Triangle(cum_5x5, incremental=False).to_incremental()
    np.testing.assert_array_almost_equal(data, expected)


def test_cumulative_and_incremental_give_same_reserves():
    cum = read_triangle_csv(TESTDATA / "cumulative_5x5.csv")
    inc = read_triangle_csv(TESTDATA / "incremental_5x5.csv")

    res_cum = run_method(cum, incremental=False, method="chain_ladder")
    res_inc = run_method(inc, incremental=True, method="chain_ladder")

    np.testing.assert_array_almost_equal(res_cum["reserves"], res_inc["reserves"])


def test_chain_ladder_total_reserve_matches_hand_values(cum_5x5, expected_CL_5x5):
    res = run_method(cum_5x5, incremental=False, method="chain_ladder")
    assert np.sum(res["reserves"]) == pytest.approx(
        expected_CL_5x5["total_reserve"], abs=0.01
    )


def test_bf_with_cl_ultimates_as_prior_returns_cl_ultimates(cum_5x5):
    cl = run_method(cum_5x5, incremental=False, method="chain_ladder")
    bf = run_method(
        cum_5x5, incremental=False, method="bornhuetter_ferguson", prior=cl["ultimates"]
    )
    np.testing.assert_array_almost_equal(cl["ultimates"], bf["ultimates"], decimal=6)


def test_bf_requires_prior_for_each_year(cum_5x5):
    with pytest.raises(ValueError, match="prior"):
        run_method(
            cum_5x5, incremental=False, method="bornhuetter_ferguson", prior=[1.0, 2.0]
        )


def test_unknown_method_rejected(cum_5x5):
    with pytest.raises(ValueError, match="Unknown method"):
        run_method(cum_5x5, incremental=False, method="nope")


def test_rejects_non_square_file():
    with pytest.raises(ValueError, match="square"):
        read_triangle_csv(TESTDATA / "invalid_non_square.csv")


def test_rejects_non_numeric_cell(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("1,2\nx,4\n")
    with pytest.raises(ValueError, match="Non-numeric value 'x'"):
        read_triangle_csv(path)


def test_header_row_is_skipped(tmp_path):
    path = tmp_path / "header.csv"
    path.write_text("dev0,dev1\n1,2\n3,\n")
    data = read_triangle_csv(path)
    np.testing.assert_array_equal(data, np.array([[1.0, 2.0], [3.0, np.nan]]))


def test_csv_round_trip_keeps_blanks(cum_5x5, tmp_path):
    text = triangle_to_csv(cum_5x5)
    assert text.splitlines()[1] == "1100.0,1800.0,2100.0,2240.0,"
    path = tmp_path / "roundtrip.csv"
    path.write_text(text)
    np.testing.assert_array_equal(read_triangle_csv(path), cum_5x5)


def test_10x10_cumulative_and_incremental_samples_agree():
    cum = read_triangle_csv(TESTDATA / "cumulative_10x10.csv")
    inc = read_triangle_csv(TESTDATA / "incremental_10x10.csv")
    assert cum.shape == (10, 10)
    np.testing.assert_array_equal(
        as_form(inc, incremental=True, want_incremental=False), cum
    )
    np.testing.assert_array_equal(
        as_form(cum, incremental=False, want_incremental=True), inc
    )


def test_10x10_developed_ultimates_are_at_least_latest_diagonal():
    cum = read_triangle_csv(TESTDATA / "cumulative_10x10.csv")
    res = run_method(cum, incremental=False, method="chain_ladder")
    latest = np.array([cum[i, 9 - i] for i in range(10)])
    assert np.all(res["ultimates"] >= latest)
    assert np.all(res["reserves"] >= 0)


def test_as_form_keeps_unobserved_cells_blank(cum_5x5):
    inc = as_form(cum_5x5, incremental=False, want_incremental=True)
    assert np.isnan(inc[4, 1])
    assert inc[1, 0] == 1100.0
