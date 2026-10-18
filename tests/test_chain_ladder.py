import numpy as np
import pytest

from reservingt.reserving import Triangle, ChainLadder

def test_CL_reserving_calc(cum_5x5, expected_CL_5x5):
    """
    Testing calculations using the chain ladder method.
    """
    tri = Triangle(cum_5x5, incremental=False)
    CL = ChainLadder()
    res = CL.calc_reserve(triangle=tri)
    
    np.testing.assert_array_almost_equal(
        expected_CL_5x5['full_triangle'],
        res['full_triangle'],
        decimal=2
    )