
#%%
import importlib
import reservingt.reserving as reserving
importlib.reload(reserving) 
from reservingt.reserving import triangle
import numpy as np

# %%
tri = np.array([
    [100.0, 150.0, 170.0],
    [110.0, 165.0, np.nan],
    [120.0, np.nan, np.nan],
])
triangle_test = triangle(data=tri, incremental=True)

# %%
triangle_test.data

# %%
