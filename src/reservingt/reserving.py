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
        self.dev_factors = None
        self.full_triangle = None
    
    # Method: Calc dev factors
    def _calc_dev_factors(self, triangle: Triangle):
        n = triangle.n
        dev_factors = np.zeros(n-1)
        C = triangle.data
        for j in range (1,n):
            dev_factors[j-1] = C[0:(n-j),j].sum()/C[0:(n-j),j-1].sum()
        return dev_factors
    
    # Method: Fill triangle using CL method
    def _fill_triangle(self, triangle: Triangle, dev_factors):
        full_data = triangle.data.copy()
        n = triangle.n
        for i in range(1, n):
            for j in range(n-i, n):
                full_data[i, j] = full_data[i, j-1] * dev_factors[j-1]
        return full_data
    
    # Method: Main for calculating the reserve
    def calc_reserve(self, triangle: Triangle):
        """
        TO-DO:
        """
        cumulativ = Triangle(triangle.to_cumulativ(), incremental=False) if triangle.incremental else triangle
        self.dev_factors = self._calc_dev_factors(cumulativ)
        full_triangle = self._fill_triangle(cumulativ, self.dev_factors)
        n = triangle.n
        
        ultimates = full_triangle[:,-1]
        diagnol = [full_triangle[i,n-(i+1)] for i in range(n)]
        reserves = ultimates - diagnol
        
        full_incremental = np.zeros_like(full_triangle)
        for i in range(n):
            for j in range(n):
                if j == 0:
                    full_incremental[i,j] = full_triangle[i,j]
                else:
                    full_incremental[i,j] = full_triangle[i,j] - full_triangle[i,j-1]
        
        return {
            "ultimates": ultimates,
            "reserves": reserves,
            "development_factor": self.dev_factors,
            "full_triangle": full_triangle,
            "full_incremental_triangle": full_incremental
        }
        