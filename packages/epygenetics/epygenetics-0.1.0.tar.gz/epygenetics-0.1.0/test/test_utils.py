import unittest
import numpy as np
from src.utils import evaluate, sort_population, get_stats, bounce_population, create_bound_matrix
from src.generation import generate_uniform


class TestSortPopulation(unittest.TestCase):

    def test_keeps_original_population(self):
        population = generate_uniform([0, 0, 0], [1, 1, 1], 10)
        sorted_population, sorted_fitness = sort_population(population=population, fitness=np.array([5,2,12,4,2,6,7,8,9,10]))
        self.assertFalse(np.array_equal(population, sorted_population))

    def test_is_ordered(self):
        population = generate_uniform([0, 0, 0], [1, 1, 1], 10)
        sorted_population, sorted_fitness = sort_population(population=population, fitness=np.array([5,2,12,4,2,6,7,8,9,10]))
        self.assertTrue(np.all(sorted_fitness == np.sort(np.array([5,2,12,4,2,6,7,8,9,10]))[::-1]))