import numpy as np

#population
#   individual_1[ gen_1, gen_2,.., gen_n]
#   ...
#   individual_m[ gen_1, gen_2,.., gen_n]
   
def mutate_real(population: np.ndarray, mutation_rate: float, mutation_n_stdevs:float=1) -> np.ndarray:
    mutated_population = population.copy()
    stdevs_per_column = np.std(mutated_population,axis=0)
    gen_size = len(mutated_population[0])

    for row_i in range(len(mutated_population)):
        mutation_probability = np.random.uniform(0,1)
        if mutation_probability < mutation_rate:
            gen_to_mutate = np.random.randint(0,gen_size)
            mutated_population[row_i,gen_to_mutate] += np.random.normal(0,stdevs_per_column[gen_to_mutate]) * mutation_n_stdevs
    
    return mutated_population


def mutate_discrete():
    pass


if __name__ == "__main__":
    population = np.array([[0.0,0,0],[1,1,1],[2,2,2],[3,3,3],[2,2,2]])
    population = np.concatenate((population,population),axis=0)
    print(population)
    population = mutate_real(population,0.5)
    print(population)
