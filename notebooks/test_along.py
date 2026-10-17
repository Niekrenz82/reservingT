
#%%
import importlib
import numpy as np

import reservingt.reserving as reserving
from reservingt.reserving import Triangle, ChainLadder, BornhuetterFerguson

importlib.reload(reserving) 

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
prior = np.array([170, 200, 230])
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
prior[1]

# %%
triangle_test_inc.to_cumulativ()

# %%
tri_1[0,0:3].sum()

# %% 
CL = ChainLadder()
dev_factor = CL._calc_dev_factors(triangle_test_cum)

# %%

BF = BornhuetterFerguson(prior=prior)
BF.calc_reserve(triangle_test_cum)

# %%
dev_factor[1]

# %%
triangle_test_cum.n
# %%
