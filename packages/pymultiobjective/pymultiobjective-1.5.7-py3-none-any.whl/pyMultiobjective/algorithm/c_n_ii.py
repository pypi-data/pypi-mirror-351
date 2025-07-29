############################################################################

# Created by: Prof. Valdecy Pereira, D.Sc.
# UFF - Universidade Federal Fluminense (Brazil)
# email:  valdecy.pereira@gmail.com
# Course: Metaheuristics
# Lesson: C-NSGA-II (Clustered Non-Dominated Sorting Genetic Algorithm II)

# Citation: 
# PEREIRA, V. (2021). Project: pyMultiojective, File: c_n_ii.py, GitHub repository: <https://github.com/Valdecy/pyMultiojective>

############################################################################

# Required Libraries
import numpy  as np
import random
import os

############################################################################

# Function 1
def func_1():
    return

# Function 2
def func_2():
    return

############################################################################

# Function: Initialize Variables
def initial_population(population_size = 5, min_values = [-5,-5], max_values = [5,5], list_of_functions = [func_1, func_2]):
    population = np.zeros((population_size, len(min_values) + len(list_of_functions)))
    for i in range(0, population_size):
        for j in range(0, len(min_values)):
             population[i,j] = random.uniform(min_values[j], max_values[j])      
        for k in range (1, len(list_of_functions) + 1):
            population[i,-k] = list_of_functions[-k](list(population[i,0:population.shape[1]-len(list_of_functions)]))
    return population

############################################################################

# Function: Fast Non-Dominated Sorting
def fast_non_dominated_sorting(population, number_of_functions = 2):
    num_individuals  = population.shape[0]
    fronts           = [[]]
    domination_count = np.zeros(num_individuals, dtype=int)
    dominated_sets   = [set() for _ in range(num_individuals)]
    ranks            = np.zeros(num_individuals, dtype=int)
    for p in range(num_individuals):
        for q in range(num_individuals):
            if (np.all(population[p, -number_of_functions:] <= population[q, -number_of_functions:])):
                if (np.any(population[p, -number_of_functions:] < population[q, -number_of_functions:])):
                    dominated_sets[p].add(q)
            elif (np.all(population[q, -number_of_functions:] <= population[p, -number_of_functions:])):
                if (np.any(population[q, -number_of_functions:] < population[p, -number_of_functions:])):
                    domination_count[p] = domination_count[p] + 1
        if (domination_count[p] == 0):
            ranks[p] = 0
            fronts[0].append(p)
    i = 0
    while fronts[i]:
        next_front = []
        for p in fronts[i]:
            for q in dominated_sets[p]:
                domination_count[q] = domination_count[q] - 1
                if (domination_count[q] == 0):
                    ranks[q] = i + 1
                    next_front.append(q)
        i = i + 1
        fronts.append(next_front)
    fronts.pop()
    ranks = ranks + 1
    return ranks.reshape(-1, 1)


# Function: Sort Population by Rank
def sort_population_by_rank(population, rank):
    idx        = np.argsort(rank[:,0], axis = 0).tolist()
    rank       = rank[idx,:]
    population = population[idx,:]
    return population, rank

############################################################################

# Function: Dominance
def dominance_function(solution_1, solution_2, number_of_functions = 2):
    count     = 0
    dominance = True
    for k in range (1, number_of_functions + 1):
        if (solution_1[-k] < solution_2[-k]):
            count = count + 1
    if (count == number_of_functions):
        dominance = True
    else:
        dominance = False       
    return dominance

# Function: Raw Fitness
def raw_fitness_function(population, number_of_functions = 2):    
    strength    = np.zeros((population.shape[0], 1))
    raw_fitness = np.zeros((population.shape[0], 1))
    for i in range(0, population.shape[0]):
        for j in range(0, population.shape[0]):
            if (i != j):
                if dominance_function(solution_1 = population[i,:], solution_2 = population[j,:], number_of_functions = number_of_functions):
                    strength[i,0] = strength[i,0] + 1
    for i in range(0, population.shape[0]):
        for j in range(0, population.shape[0]):
            if (i != j):
                if dominance_function(solution_1 = population[i,:], solution_2 = population[j,:], number_of_functions = number_of_functions):
                    raw_fitness[j,0] = raw_fitness[j,0] + strength[i,0]
    return raw_fitness

# Function: Build Distance Matrix
def euclidean_distance(coordinates):
   a = coordinates
   b = a.reshape(np.prod(a.shape[:-1]), 1, a.shape[-1])
   return np.sqrt(np.einsum('ijk,ijk->ij',  b - a,  b - a)).squeeze()

# Function: Fitness
def fitness_calculation(population, raw_fitness, number_of_functions = 2):
    k        = int(len(population)**(1/2)) - 1
    fitness  = np.zeros((population.shape[0], 1))
    distance = euclidean_distance(population[:,population.shape[1]-number_of_functions:])
    for i in range(0, fitness.shape[0]):
        distance_ordered = (distance[distance[:,i].argsort()]).T
        fitness[i,0]     = raw_fitness[i,0] + 1/(distance_ordered[i,k] + 2)
    return fitness

# Function: Selection
def roulette_wheel(fitness):
    total_fitness            = np.sum(fitness)
    cumulative_probabilities = np.cumsum(fitness) / total_fitness
    spin                     = int.from_bytes(os.urandom(8), byteorder = 'big') / ((1 << 64) - 1)
    for i, cumulative_probability in enumerate(cumulative_probabilities):
        if (spin <= cumulative_probability):
            return i
    return len(fitness) - 1

############################################################################

# Function: Offspring
def breeding(population, fitness, min_values = [-5,-5], max_values = [5,5], mu = 1, list_of_functions = [func_1, func_2]):
    offspring   = np.copy(population)
    b_offspring = 0
    for i in range (0, offspring.shape[0]):
        parent_1, parent_2 = roulette_wheel(fitness), roulette_wheel(fitness)
        while parent_1 == parent_2:
            parent_2 = random.sample(range(0, len(population) - 1), 1)[0]
        for j in range(0, offspring.shape[1] - len(list_of_functions)):
            rand   = int.from_bytes(os.urandom(8), byteorder = 'big') / ((1 << 64) - 1)
            rand_b = int.from_bytes(os.urandom(8), byteorder = 'big') / ((1 << 64) - 1)  
            rand_c = int.from_bytes(os.urandom(8), byteorder = 'big') / ((1 << 64) - 1)                               
            if (rand <= 0.5):
                b_offspring = 2*(rand_b)
                b_offspring = b_offspring**(1/(mu + 1))
            elif (rand > 0.5):  
                b_offspring = 1/(2*(1 - rand_b))
                b_offspring = b_offspring**(1/(mu + 1))       
            if (rand_c >= 0.5):
                offspring[i,j] = np.clip(((1 + b_offspring)*population[parent_1, j] + (1 - b_offspring)*population[parent_2, j])/2, min_values[j], max_values[j])           
            else:   
                offspring[i,j] = np.clip(((1 - b_offspring)*population[parent_1, j] + (1 + b_offspring)*population[parent_2, j])/2, min_values[j], max_values[j]) 
        for k in range (1, len(list_of_functions) + 1):
            offspring[i,-k] = list_of_functions[-k](offspring[i,0:offspring.shape[1]-len(list_of_functions)])
    return offspring

# Function: Mutation
def mutation(offspring, mutation_rate = 0.1, eta = 1, min_values = [-5,-5], max_values = [5,5], list_of_functions = [func_1, func_2]):
    d_mutation = 0            
    for i in range (0, offspring.shape[0]):
        for j in range(0, offspring.shape[1] - len(list_of_functions)):
            probability = int.from_bytes(os.urandom(8), byteorder = 'big') / ((1 << 64) - 1)
            if (probability < mutation_rate):
                rand   = int.from_bytes(os.urandom(8), byteorder = 'big') / ((1 << 64) - 1)
                rand_d = int.from_bytes(os.urandom(8), byteorder = 'big') / ((1 << 64) - 1)                                     
                if (rand <= 0.5):
                    d_mutation = 2*(rand_d)
                    d_mutation = d_mutation**(1/(eta + 1)) - 1
                elif (rand > 0.5):  
                    d_mutation = 2*(1 - rand_d)
                    d_mutation = 1 - d_mutation**(1/(eta + 1))                
                offspring[i,j] = np.clip((offspring[i,j] + d_mutation), min_values[j], max_values[j])                        
        for k in range (1, len(list_of_functions) + 1):
            offspring[i,-k] = list_of_functions[-k](offspring[i,0:offspring.shape[1]-len(list_of_functions)])
    return offspring 

############################################################################

# C-NSGA II Function
def clustered_non_dominated_sorting_genetic_algorithm_II(population_size = 5, mutation_rate = 0.1, min_values = [-5,-5], max_values = [5,5], list_of_functions = [func_1, func_2], generations = 50, mu = 1, eta = 1, verbose = True):        
    count      = 0   
    population = initial_population(population_size = population_size, min_values = min_values, max_values = max_values, list_of_functions = list_of_functions)  
    offspring  = initial_population(population_size = population_size, min_values = min_values, max_values = max_values, list_of_functions = list_of_functions)  
    while (count <= generations):  
        if (verbose == True):
            print('Generation = ', count)
        population        = np.vstack([population, offspring])
        rank              = fast_non_dominated_sorting(population, number_of_functions = len(list_of_functions))
        population, rank  = sort_population_by_rank(population, rank)
        population, rank  = population[0:population_size,:], rank[0:population_size,:] 
        raw_fitness       = raw_fitness_function(population, number_of_functions = len(list_of_functions))
        fitness           = fitness_calculation(population, raw_fitness, number_of_functions = len(list_of_functions))  
        offspring         = breeding(population, fitness, mu = mu, min_values = min_values, max_values = max_values, list_of_functions = list_of_functions)
        offspring         = mutation(offspring, mutation_rate = mutation_rate, eta = eta, min_values = min_values, max_values = max_values, list_of_functions = list_of_functions)             
        count             = count + 1              
    return population

############################################################################