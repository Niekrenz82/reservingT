
#%%
import importlib
import reservingt.reserving as reserving
importlib.reload(reserving) 
from reservingt.reserving import triangle
import numpy as np

# %%
tri_1 = np.array([
    [100.0, 150.0, 170.0],
    [110.0, 165.0, np.nan],
    [120.0, np.nan, np.nan],
])
tri_2 = np.array([
    [100.0, 150.0, 170.0],
    [110.0, 165.0, np.nan],
    [120.0, np.nan, np.nan],
    [120.0, np.nan, np.nan],
])
tri_3 = np.array([
    [100.,  50.,  20.],
    [110.,  55.,   0.],
    [120.,   0.,   0.]
])
triangle_test_cum = triangle(data=tri_1, incremental=False)
triangle_test_inc = triangle(data=tri_3, incremental=True)
triangle_test = triangle(data=tri_2, incremental=False)

# %%
triangle_test_cum.to_incremental()
# %%
triangle_test_inc.to_cumulativ()

# %%
