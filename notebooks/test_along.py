
#%%
import importlib
import reservingt.reserving as reserving
importlib.reload(reserving) 
from reservingt.reserving import Triangle, ChainLadder 
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
triangle_test_cum = Triangle(data=tri_1, incremental=False)
triangle_test_inc = Triangle(data=tri_3, incremental=True)
triangle_test = Triangle(data=tri_2, incremental=False)

# %%
triangle_test_cum.to_incremental()
# %%
triangle_test_inc.to_cumulativ()

# %%
tri_1[0,0:3].sum()

# %% 
CL = ChainLadder()
dev_factor = CL._calc_dev_factors(triangle_test_cum)
# %%
CL._fill_triangle(triangle_test_cum, dev_factor)
# %%
CL.calc_reserve(triangle_test_cum)
# %%
