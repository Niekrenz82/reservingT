import pytest
import numpy

from reservingt.reserving import Triangle

def test_wrong_dimensions(triangle_3x2):
    with pytest.raises(ValueError, match= "Must have same rows and columns"):
        Triangle(data=triangle_3x2, incremental=False)