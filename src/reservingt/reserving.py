from abc import ABC, abstractmethod
import numpy as np

class Triangle:
    """
    Triangle to hold losses over origin and development.
    """
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

class ReservingMethod(ABC):
    
    @abstractmethod
    def calc_reserve(self, triangle: Triangle):
        """calculate the reserve."""

class ChainLadder(ReservingMethod):
    """
    Method for ChainLadder based reserving
    """
    
    def __init__(self):
        dev_factors = None
        full_triangle = None
    
    def _calc_dev_factors(self, triangle: Triangle):
        n = triangle.n
        dev_factors = np.zeros(n-1)
        C = triangle.data
        for j in range (1,n):
            dev_factors[j-1] = C[0:(n-j),j].sum()/C[0:(n-j),j-1].sum()
        return dev_factors
    
    def calc_reserve():
        """
        TO-DO:
        """