from epygenetics import swarm_optimize
from epygenetics import rastrigin, booth, himmelblau

p : dict = {
    "n_iterations"  : 50,
    "lower_bound" : (-5.12,-5.12),
    "upper_bound"  : ( 5.12, 5.12),
    "pop_size"  : 200,
    "minimize": True,
    "inertia_w": 0.1,
    "social_w": 0.3,
    "memory_w": 0.1,
    "minimize": True
}

if __name__ == "__main__":
    best_individual, optimum_value = swarm_optimize(p=p, target_function=rastrigin)


