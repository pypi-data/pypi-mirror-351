import numpy as np
from collections.abc import Callable


def evaluate(population: np.ndarray, function:Callable) -> np.ndarray:
    return function(population)


def create_bound_matrix(lower_bounds:list,upper_bounds:list,pop_size:int) -> tuple[np.ndarray,np.ndarray]:
    n_vars = len(lower_bounds)
    lower_bound_matrix:np.ndarray = np.repeat(lower_bounds,repeats=pop_size).reshape(n_vars,pop_size).transpose()
    upper_bound_matrix:np.ndarray = np.repeat(upper_bounds,repeats=pop_size).reshape(n_vars,pop_size).transpose()
    return lower_bound_matrix, upper_bound_matrix


def bounce_population(population:np.ndarray,lower_bound_matrix:np.ndarray,upper_bound_matrix:np.ndarray):
    
    bounced_pop = population.copy()
    
    bounced_pop = np.maximum(bounced_pop,lower_bound_matrix)
    bounced_pop = np.minimum(bounced_pop,upper_bound_matrix)

    return bounced_pop


def sort_population(population: np.ndarray, fitness: np.ndarray) -> tuple:
    order_indexes = fitness.argsort(axis=0)[::-1]  #argsort orders from smallest to largest, is reversed
    oredered_population = population[order_indexes].reshape(population.shape)
    fitness = fitness[order_indexes].reshape(fitness.shape)
    return oredered_population, fitness


def get_stats(fitness: np.ndarray) -> dict:
    mean_fitness = np.mean(fitness)
    stdev_fitness = np.std(fitness, ddof=1)
    max_fitness = np.max(fitness)
    min_fitness = np.min(fitness)
    median_fitness = np.median(fitness)

    return {"mean":float(mean_fitness), 
            "stdev":float(stdev_fitness),
            "max_fit":float(max_fitness),
            "min_fit": float( min_fitness),
            "median":float(median_fitness)}


def change_sign(func:Callable) -> Callable:
    def wrapper(x:np.ndarray):
        return -1*func(x)
    return wrapper


def update_history(history:np.ndarray,
                   population:np.ndarray,
                   population_fitness:np.ndarray,
                   fitness_function:Callable)->np.ndarray:
    
    """updates history for the swarm optimzer"""

    history_fitness = evaluate(population=history, function=fitness_function)

    mask_1d = history_fitness>population_fitness

    mask = np.repeat(mask_1d,history.shape[1],axis=0).reshape(population.shape)
    updated_history = mask*history + ~mask*population
    
    return updated_history
    

    
