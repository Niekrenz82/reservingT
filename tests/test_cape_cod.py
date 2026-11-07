import numpy as np
import pytest

from reservingt.cape_cod import CapeCod
from reservingt.reserving import Triangle


def test_cape_cod_matches_hand_values(cum_5x5, expected_CC_5x5):
    tri = Triangle(cum_5x5, incremental=False)
    res = CapeCod(exposure=expected_CC_5x5["exposure"]).calc_reserve(triangle=tri)

    assert res["elr"] == pytest.approx(expected_CC_5x5["elr"], abs=1e-9)
    np.testing.assert_array_almost_equal(
        res["ultimates"], expected_CC_5x5["ultimates"], decimal=3
    )
    assert np.sum(res["reserves"]) == pytest.approx(
        expected_CC_5x5["total_reserve"], abs=0.01
    )


def test_scaling_exposure_leaves_ultimates_unchanged(cum_5x5, expected_CC_5x5):
    tri = Triangle(cum_5x5, incremental=False)
    base = CapeCod(exposure=expected_CC_5x5["exposure"]).calc_reserve(triangle=tri)
    scaled = CapeCod(exposure=2 * expected_CC_5x5["exposure"]).calc_reserve(triangle=tri)

    np.testing.assert_array_almost_equal(base["ultimates"], scaled["ultimates"], decimal=6)
    assert scaled["elr"] == pytest.approx(base["elr"] / 2, abs=1e-9)


def test_first_accident_year_ultimate_equals_latest_value(cum_5x5, expected_CC_5x5):
    tri = Triangle(cum_5x5, incremental=False)
    res = CapeCod(exposure=expected_CC_5x5["exposure"]).calc_reserve(triangle=tri)

    assert res["ultimates"][0] == pytest.approx(cum_5x5[0, -1], abs=1e-9)
    assert res["reserves"][0] == pytest.approx(0.0, abs=1e-9)


def test_incremental_input_gives_same_result_as_cumulative(cum_5x5, expected_CC_5x5):
    exposure = expected_CC_5x5["exposure"]
    cum = Triangle(cum_5x5, incremental=False)
    inc = Triangle(Triangle(cum_5x5, incremental=False).to_incremental(), incremental=True)

    res_cum = CapeCod(exposure=exposure).calc_reserve(triangle=cum)
    res_inc = CapeCod(exposure=exposure).calc_reserve(triangle=inc)

    np.testing.assert_array_almost_equal(res_cum["ultimates"], res_inc["ultimates"], decimal=6)
    np.testing.assert_array_almost_equal(res_cum["reserves"], res_inc["reserves"], decimal=6)


def test_wrong_length_exposure_raises(cum_5x5):
    tri = Triangle(cum_5x5, incremental=False)
    with pytest.raises(ValueError):
        CapeCod(exposure=np.array([10000.0, 11000.0, 12000.0])).calc_reserve(triangle=tri)


def test_negative_exposure_raises(cum_5x5, expected_CC_5x5):
    tri = Triangle(cum_5x5, incremental=False)
    exposure = expected_CC_5x5["exposure"].copy()
    exposure[2] = -1.0
    with pytest.raises(ValueError):
        CapeCod(exposure=exposure).calc_reserve(triangle=tri)
