import pytest
import numpy as np

from reservingt.reserving import Triangle

def test_wrong_dimensions(triangle_3x2):
    with pytest.raises(ValueError, match= "Must have same rows and columns"):
        Triangle(data=triangle_3x2, incremental=False)
        
def test_cum_inc_cum(cum_5x5):
    tri = Triangle(data=cum_5x5, incremental=False)
    tri_inc = Triangle(tri.to_incremental(),incremental=True)
    tri_cum = tri_inc.to_cumulativ()
    
    np.testing.assert_array_almost_equal(cum_5x5, tri_cum)