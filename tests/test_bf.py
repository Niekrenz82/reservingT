import numpy as np
import pytest

from reservingt.reserving import Triangle, ChainLadder, BornhuetterFerguson

def test_bf_calculations(cum_5x5, expected_CL_5x5):
    tri = Triangle(cum_5x5, incremental=False)
    BF = BornhuetterFerguson(prior=expected_CL_5x5['ultimates'])
    res = BF.calc_reserve(triangle=tri)
    
    np.testing.assert_array_almost_equal(
        expected_CL_5x5['ultimates'],
        res['ultimates'],
        decimal=1
    )