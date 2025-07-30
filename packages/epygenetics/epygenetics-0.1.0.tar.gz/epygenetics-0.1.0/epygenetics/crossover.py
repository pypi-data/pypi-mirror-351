import numpy as np
import random


def perform_crossover(parents: np.ndarray, method="tpc") -> np.ndarray:
    if method == "opc":
        return one_point_crossover(parents)
    if method == "tpc":
        return two_point_crossover(parents)
    
    raise ValueError("invalid method, choose opc or tpc")

# esta programado solo el reeplazo generacional

def one_point_crossover(parents: np.ndarray) -> np.ndarray:
    '''
    [o,o,o,o,o,o] => [o,o,x,x,x,x]
    [x,x,x,x,x,x] => [x,x,x,x,o,o]
    '''

    population = parents.copy()
    pop_size:int = len(population)
    dim:int = len(population[0])

    for row in range(0, pop_size, 2):
        
        crossover_index_1 = random.randint(0, dim)
        crossover_index_2 = random.randint(0, dim)

        for column in range(0, crossover_index_1):
            population[row, column]  = parents[row + 1, column]
        for column in range(0, crossover_index_2):
            population[row +1, column] = parents[row , column]

    return population


def two_point_crossover(parents: np.ndarray) -> np.ndarray:

    '''
    [o,o,o,o,o,o] => [o,o,x,x,o,o]
    [x,x,x,x,x,x] => [x,o,o,x,x,x]
    '''

    population = parents.copy()
    pop_size = len(population)
    dim = len(population[0])

    for row in range(0, pop_size, 2):
        crossover_index_1 = random.randint(0, dim)
        crossover_index_2 = random.randint(crossover_index_1, dim)

        for column in range(crossover_index_1, crossover_index_2):
            population[row, column], population[row + 1, column] = (
                population[row + 1, column],
                population[row, column],
            )

    return population


if __name__ == "__main__":
    parents = np.array(
        [[0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2], [3, 3, 3, 3, 3, 3]]
    )
    parents = np.concatenate((parents, parents), axis=0)
    children = one_point_crossover(parents)
    print(children)
