import numpy as np
import pytest

NAN = np.nan

@pytest.fixture
def cum_5x5():
    """
    Cumulativ 5x5 triangle for testing.
    """
    return np.array([
        [1000, 1600, 1900, 2050, 2120],
        [1100.0, 1800.0, 2100.0, 2240.0, NAN],
        [1200.0, 1950.0, 2300.0, NAN, NAN],
        [1250.0, 2000.0, NAN, NAN, NAN],
        [1300.0, NAN, NAN, NAN, NAN]
    ])
    
@pytest.fixture
def expected_CL_5x5():
    """
    Expected values, computed by hand with exact fractions in a separate script.
    """
    return {
        "factors": [21 / 13, 126 / 107, 429 / 400, 212 / 205],
        "full_triangle": np.array([
            [1000.0, 1600.0, 1900.0, 2050.0, 2120.0],
            [1100.0, 1800.0, 2100.0, 2240.0, 2316.4878],
            [1200.0, 1950.0, 2300.0, 2466.7500, 2550.9805],
            [1250.0, 2000.0, 2355.1402, 2525.8879, 2612.1377],
            [1300.0, 2100.0, 2472.8972, 2652.1822, 2742.7446],
        ]),
        "ultimates": [2120.0, 2316.4878, 2550.9805, 2612.1377, 2742.7446],
        "reserves": [0.0, 76.4878, 250.9805, 612.1377, 1442.7446],
        "total_reserve": 2382.3505,
    }

@pytest.fixture
def triangle_3x2():
    """
    Triangle with wrong dimensions.
    """
    return np.array([
        [1, 2, 3],
        [1, 2, NAN]
    ])