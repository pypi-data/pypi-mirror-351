import unittest
import numpy as np
from src.crossover import one_point_crossover, two_point_crossover

# python -m unittest discover test from parent directory to import modules

parents = np.array([[0,0,0,0,0,0],[1,1,1,1,1,1],[2,2,2,2,2,2],[3,3,3,3,3,3],[4,4,4,4,4,4],[5,5,5,5,5,5],[0,0,0,0,0,0],[1,1,1,1,1,1],[2,2,2,2,2,2],[3,3,3,3,3,3],[4,4,4,4,4,4],[5,5,5,5,5,5]])


class TestOnePointCrossover(unittest.TestCase):

    def test_children_are_modified(self):
        children = one_point_crossover(parents)
        self.assertFalse(np.array_equal(children,parents))


    def test_parents_are_not_modified(self):
        parents_backup = parents.copy()
        children = one_point_crossover(parents)
        self.assertTrue(np.array_equal(parents_backup,parents))
    

    def test_paired_genes(self):
        children = one_point_crossover(parents)

        for row_n in range(0,parents.shape[0],2):
            for col_n in range(parents.shape[1]):
                self.assertTrue(children[row_n,col_n] in parents[row_n,:] or children[row_n,col_n] in parents[row_n+1,:] )


class TestTwoPointCrossover(unittest.TestCase):

    def test_children_are_modified(self):
        children = two_point_crossover(parents)
        self.assertFalse(np.array_equal(children,parents))


    def test_parents_are_not_modified(self):
        parents_backup = parents.copy()
        children = two_point_crossover(parents)
        self.assertTrue(np.array_equal(parents_backup,parents))
    

    def test_paired_genes(self):
        children = two_point_crossover(parents)

        for row_n in range(0,parents.shape[0],2):
            for col_n in range(parents.shape[1]):
                self.assertTrue(children[row_n,col_n] in parents[row_n,:] or children[row_n,col_n] in parents[row_n+1,:] )


if __name__ == '__main__':
    unittest.main()