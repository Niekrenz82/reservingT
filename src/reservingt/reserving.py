import numpy as np


class triangle:
    def __init__(self, data: np.ndarray, incremental: bool, ):
        data_shape = data.shape
        if data.ndim != 2:
            raise ValueError("Triangle must be 2d")
        if data_shape[0] != data_shape[1]:
            raise ValueError("Must have same rows and columns")
        self.data = data
        self.incremental = incremental
        self.n = data.shape[0]
    
    # Method: Go from cumulativ to incremental triangle
    def to_incremental(self) -> np.ndarray:
        if self.incremental:
            raise ValueError("Triangle is already incremental.")
        incremental = np.zeros_like(self.data)
        C = self.data.copy()
        for i in range(self.n):
            for j in range(self.n - i):
                if j == 0:
                    incremental[i,j] = C[i,j]
                else:
                    incremental[i,j] = C[i,j] - C[i, j-1]
        return incremental
    
    # Method: Go from incremental to cumulativ triangle
    def to_cumulativ(self) -> np.ndarray:
        if not self.incremental:
            raise ValueError("Triangle is already cumulativ.")
        cumulativ = np.zeros_like(self.data)
        I = self.data
        for i in range(self.n):
            for j in range(self.n - i):
                if j == 0:
                    cumulativ[i,j] = I[i,j]
                else:
                    cumulativ[i,j] = I[i,j] + cumulativ[i,j-1]
        return cumulativ