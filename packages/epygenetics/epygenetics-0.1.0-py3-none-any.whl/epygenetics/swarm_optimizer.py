import numpy as np

from epygenetics.generation import generate_uniform
from epygenetics.utils import evaluate, update_history,change_sign,  bounce_population, create_bound_matrix


def swarm_optimize(p, target_function):

    if p['minimize']:
        fitness_function = change_sign(target_function)
    else:
        fitness_function = target_function

            
    lower_bound_matrix, upper_bound_matrix = create_bound_matrix(lower_bounds=p['lower_bound'],
                                                                 upper_bounds=p["upper_bound"],
                                                                 pop_size=p["pop_size"])

    population:np.ndarray = generate_uniform(lower_bound=p["lower_bound"], upper_bound=p["upper_bound"], pop_size=p['pop_size'])
    inertia:np.ndarray = generate_uniform(lower_bound=p["lower_bound"], upper_bound=p["upper_bound"], pop_size=p['pop_size'])
    history = population.copy() #best value is the only value

    fitness = evaluate(population=population, function=fitness_function)
    best_individual = population[np.argmax(fitness)].copy()


    for i in range(p['n_iterations']):
        
        next_population = population + (best_individual-population)*p['social_w'] + inertia*p['inertia_w'] + (history-population) *p['memory_w']
        
        
        fitness = evaluate(population=next_population, function=fitness_function)
        best_individual = next_population[np.argmax(fitness)].copy()

        inertia = next_population - population
        history = update_history(history=history,population=next_population, population_fitness=fitness,fitness_function=fitness_function)

        population = bounce_population(next_population,lower_bound_matrix=lower_bound_matrix, upper_bound_matrix=upper_bound_matrix)


    fitness = evaluate(population=population, function=fitness_function)
    best_individual = next_population[np.argmax(fitness)].copy()
    optimum_value = evaluate(population=population, function=target_function)[np.argmax(fitness)]

    print(best_individual)
    print(optimum_value)

    return best_individual, optimum_value