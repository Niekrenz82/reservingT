import numpy as np


class triangle:
    def __init__(self, data: np.ndarray, incremental: bool):
        self.data = data
        self.incremental = incremental
