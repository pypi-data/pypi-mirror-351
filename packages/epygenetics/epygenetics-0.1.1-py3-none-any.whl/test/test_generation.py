import unittest
import numpy as np
from src.generation import generate_uniform, generate_bool, generate_categorical

class TestGenerateUniform(unittest.TestCase):

    def test_generate_uniform(self):
        np.random.seed(0)
        population = generate_uniform([0, 0, 0], [1, 1, 1], 10)
  
        self.assertTrue(population.shape == (10, 3))
        self.assertTrue(np.all(population >= 0))
        self.assertTrue(np.all(population <= 1))
