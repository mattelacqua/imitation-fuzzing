from src.Gridworld.Gridworld import *
import argparse
import random
from fuzzing import *
from copy import copy, deepcopy
     

# Create Traces.
def play(args):

    random.seed(args.seed)
    if args.random:
        game = Gridworld(size=args.size, mode='random')
    else:
        game = Gridworld(size=args.size, mode='static')
    game.dispGrid()



    generational_stats = []
    population = initialize_population(args.pop_size, game)

    max_fitness, max_fitness_trace, max_fitness_trial, generational_stats, population, final_fitness, final_population = \
        genetic_algorithm(population, game, args.generations, args.crossover, args.mutation, generational_stats, 0)
    
    print(f"Max_Fitness = {max_fitness}")
    #for stat in generational_stats:
    #    print(stat)
    print(f"Population: {population}")
    print(f"Final_Population: {final_population}")
    print(f"Final_Fitness: {final_fitness}")
    print(f"Final_Fitness: {final_fitness}")

    print(f"Max_Fitness_Trial = {max_fitness_trial}")
    print(f"Max_Fitness_Trace = {max_fitness_trace}")
    

    # Play out the winning scenaro
    for move in max_fitness_trace:
        game.makeMove(move)
    game.dispGrid()
    

    




        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Q learning Args
    parser.add_argument("--size", default=4, type=int)  #  Set the default size
    parser.add_argument("--seed", default=1, type=int)  #  Set the default seed
    parser.add_argument("--generations", default=1, type=int)  #  Set the default number of generations to run for
    parser.add_argument("--crossover", default=.7, type=float)  #  Set the crossover probability
    parser.add_argument("--mutation", default=.1, type=float)  #  Set the mutation probability
    parser.add_argument("--pop-size", default=4, type=int)  #  Set the size of the initial population. Must be at least 4.
    parser.add_argument("--random", action='store_true')  #  Store random

    args = parser.parse_args()

    # Train 
    play(args)
