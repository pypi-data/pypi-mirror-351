import numpy as np
from .utils import sort_population, evaluate


def roulette_wheel_selection(fitness: np.ndarray) -> np.ndarray:

    fitness = fitness - np.min(fitness)
    fitnes_sum = np.sum(fitness)
    cum_prob = np.cumsum(fitness / fitnes_sum)
    population_size = len(fitness)

    parent_indexes = [
        np.searchsorted(cum_prob, selector)
        for selector in np.random.uniform(0, 1, population_size)
    ]

    parent_indexes = np.array(parent_indexes)
    return parent_indexes


def stochastic_sampling(fitness: np.ndarray) -> np.ndarray:

    cumulative_fitness = np.cumsum(fitness)
    mean_fitness = np.mean(fitness)
    first_step = np.random.uniform(0, mean_fitness)
    step_size = mean_fitness
    step_generator = (first_step + k * step_size for k in range(len(fitness)))

    parent_indexes = [
        np.searchsorted(cumulative_fitness, selector) for selector in step_generator
    ]

    return parent_indexes


def tournament_sampling(pop_size :int, tournament_size :int) -> np.ndarray:
    """Population must be sorted before calling this function!"""
    
    participants_indexes = np.random.randint(low=0, high=pop_size, size=(pop_size,tournament_size))
    winners_indexes = np.min(participants_indexes,axis=1)
    
    return winners_indexes
   

if __name__ == "__main__":
    population = np.array(
        [[0.0, 0, 0], [1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4], [5, 5, 5]]
    )

    def f(X: np.ndarray) -> np.ndarray:
        return X[0] + X[1] + 0.5 * X[2] ** 2

    fitness = evaluate(population, f)
    population, fitness = sort_population(population, fitness)

    print(fitness)


    print(stochastic_sampling(population))
