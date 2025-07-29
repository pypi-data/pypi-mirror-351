############################################################################

# Created by: Prof. Valdecy Pereira, D.Sc.
# UFF - Universidade Federal Fluminense (Brazil)
# email:  valdecy.pereira@gmail.com
# Course: Metaheuristics
# Lesson: PAES (Pareto Archived Evolution Strategy)

# Citation: 
# PEREIRA, V. (2021). Project: pyMultiojective, File: paes.py, GitHub repository: <https://github.com/Valdecy/pyMultiojective>

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

# Function: Mutation
def mutation(population, eta = 1, min_values = [-5,-5], max_values = [5,5], list_of_functions = [func_1, func_2]):
    d_mutation    = 0
    mutation_rate = 2
    offspring     = np.copy(population)         
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

# PAES Function
def pareto_archived_evolution_strategy(population_size = 5, min_values = [-5,-5], max_values = [5,5], list_of_functions = [func_1, func_2], generations = 50, eta = 1, verbose = True):     
    count         = 0
    M             = len(list_of_functions)
    population    = initial_population(population_size, min_values, max_values, list_of_functions)  
    offspring     = mutation(population, eta, min_values, max_values, list_of_functions) 
    while (count <= generations): 
        if (verbose == True):
            print('Generation = ', count)
        population    = np.vstack([population, offspring])
        rank          = fast_non_dominated_sorting(population, number_of_functions = M)
        population, _ = sort_population_by_rank(population, rank)
        population    = population[0:population_size,:]
        offspring     = mutation(population, eta, min_values, max_values, list_of_functions)  
        count         = count + 1              
    return population

##############################################################################
