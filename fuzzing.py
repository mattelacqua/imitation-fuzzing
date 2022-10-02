from copy import copy, deepcopy
import random
def get_fitness(game, trace):
    trial = {}
    trial["boundary_states"] = 0
    trial["illegal_moves"] = 0
    trial["bad_states"] = 0
    trial["reaches_goal"] = False
    trial["actual_path"] = []
    trial["fitness"] = 0

    for move in trace:
        moved = game.makeMove(move)
        player_pos = game.board.components['Player'].pos
        up = player_pos[0]-1, player_pos[1]
        down = player_pos[0]+1, player_pos[1]
        left = player_pos[0], player_pos[1]-1
        right = player_pos[0], player_pos[1]+1
        # If first time being in this state and there is a pit around it
        if (game.is_pit(up) or game.is_pit(down) or game.is_pit(left) or game.is_pit(right)) and moved:
            trial["boundary_states"] += 1 

        if game.is_pit(player_pos):
            trial["bad_states"] += 1
        if not moved:
            trial["illegal_moves"] += 1
        else:
            trial["actual_path"].append(move)
            trial["fitness"] += 1 # Reward exploration and making good moves
        if game.is_goal(player_pos):
            trial["reaches_goal"] = True
            break

    
    # Let fitness be a function of the number of boundary states we get to without going to bad state. Reward for getting to goal. Penalize for not.
    ratio_of_boundary_states = (trial["boundary_states"] / trial["bad_states"]) if trial["bad_states"] else trial["boundary_states"]
    trial["fitness"] +=  ratio_of_boundary_states + ((game.board.size*game.board.size) if trial["reaches_goal"] else 1)

    return trial

# DFS Traversal to get a winning path.
def get_first_trace(game, preference_order='u'): # preference order is what node to explore first.
    start = game.board.components["Player"].pos
    stack = [(start, 'start', None)]
    visited = [(start, 'start', None)]
    path = []
    boundary_states = set()
    while stack:
        curr = stack.pop()
        path.append(curr)
        neighbors = []
        up = (curr[0][0]-1, curr[0][1]) 
        down = (curr[0][0]+1, curr[0][1]) 
        left = (curr[0][0], curr[0][1]-1) 
        right = (curr[0][0], curr[0][1]+1) 
        if game.is_pit(up):
            boundary_states.add(curr[0])
        if game.is_pit(down):
            boundary_states.add(curr[0])
        if game.is_pit(right):
            boundary_states.add(curr[0])
        if game.is_pit(left):
            boundary_states.add(curr[0])

        if preference_order == 'u':
            neighbors.append((up, 'u', curr)) #up
            neighbors.append((down, 'd', curr)) #down
            neighbors.append((left, 'l', curr)) #left
            neighbors.append((right, 'r', curr)) #right
        elif preference_order == 'd':
            neighbors.append((down, 'd', curr)) #down
            neighbors.append((left, 'l', curr)) #left
            neighbors.append((right, 'r', curr)) #right
            neighbors.append((up, 'u', curr)) #up
        elif preference_order == 'l':
            neighbors.append((left, 'l', curr)) #left
            neighbors.append((right, 'r', curr)) #right
            neighbors.append((up, 'u', curr)) #up
            neighbors.append((down, 'd', curr)) #down
        elif preference_order == 'r':
            neighbors.append((right, 'r', curr)) #right
            neighbors.append((up, 'u', curr)) #up
            neighbors.append((down, 'd', curr)) #down
            neighbors.append((left, 'l', curr)) #left
        for (neighbor, action, parent) in neighbors:
            if game.valid_move(neighbor) and neighbor not in visited:
                visited.append(neighbor)
                stack.append((neighbor, action, parent))
                if game.is_goal(neighbor):
                    path.append((neighbor,action, parent))

                    return backtrack_path(path)

def backtrack_path(path):
    proper_path =[]
    curr = path[-1]
    while curr[2] != None:
        proper_path.append(curr)
        curr = curr[2]
    
    proper_path.reverse()
    return proper_path

def get_actions(path):
    actions = []
    for (_, action, _) in path:
        actions.append(action)
    
    return actions
   
def initialize_population(num_population, game):

    # create the genetic material for the population size and have it be random for each of them other then the first 4, which
    # are DFS traversals with directional preferences
    
    if num_population < 4:
        print("POP SIZE MUST BE GREATER THAN 4")
        exit()
    
    trace0 = get_actions(get_first_trace(game, preference_order='r'))
    trace1 = get_actions(get_first_trace(game, preference_order='u'))
    trace2 = get_actions(get_first_trace(game, preference_order='l'))
    trace3 = get_actions(get_first_trace(game, preference_order='d'))
    population = [trace0, trace1, trace2, trace3]
    

    extra_randoms = num_population - 4
    # create a gene for the population number
    for x in range(extra_randoms):

        # Set initial values to choose from
        moves = ['u', 'd', 'l', 'r']
        

        rand_trace = []
        # For a random amount of moves make random moves.
        for i in range(game.board.size, game.board.size * 2):
            rand_trace.append(random.choice(moves))

        # Append the gene
        population.append(rand_trace)

    return population

def genetic_algorithm(population, game, max_generation, probability_crossover, probability_mutation, generational_stats, gen_count):
    while max_generation > 0:
        fitness = []
        trials = []
        pop_no_extra_moves = []
        for trace in population:
            new_game = deepcopy(game)
            trial = get_fitness(new_game, trace)
            fitness.append(trial["fitness"])
            trials.append(trial)
            pop_no_extra_moves.append(trial["actual_path"])
            #new_game.dispGrid()
            #print(f"Fitness: {trial['fitness']}")
            #print(f"Moves Taken: {trial['actual_path']}")
            #trial_num += 1
        
        population = pop_no_extra_moves

        # Book Keeping
        final_fitness = fitness.copy()
        final_population = population.copy()
        max_fitness = max(fitness)
        min_fitness = min(fitness)
        avg_fitness = sum(fitness)/len(fitness)
        max_fitness_gene = population[fitness.index(max_fitness)]
        max_fitness_trial = trials[fitness.index(max_fitness)]
        this_generation_stats = (max_fitness, min_fitness, avg_fitness, gen_count)
        generational_stats.append(this_generation_stats)
        max_generation = max_generation - 1
        gen_count = gen_count + 1
        
        # Take our population of ants and get the top 2 for later
        elite1, elite2 = select_max(population, fitness)

        # Select the two for crossover and mutation (Two Random Rank)
        parent1, parent2 = select(population, fitness)

        # Crossover the selected  with a 2 point crossover (split into thirds, alternate between parents.)
        crossed1, crossed2 = crossover(parent1, parent2, probability_crossover)

        # Grab the information for the elites
        elite1_gene = population[elite1]
        elite2_gene = population[elite2]

        # Mutate the entire population by potentially increasing (wrap around) digits 2 and 3 of every single state. (chance for random reset of 0
        # as well)
        population = mutate_population(population, probability_mutation)
       
        # Remove the elites so that they will not be culled
        population.remove(population[elite1])
        population.remove(population[elite2])
        fitness.remove(fitness[elite1])
        fitness.remove(fitness[elite2])
        
        
        # Create new population by culling random 2 and replace with the crossed over ones, keep the elite ones in.
        new_population = cull_random(population, fitness)
        new_population.append(elite1_gene)
        new_population.append(elite2_gene)
        new_population.append(crossed1)
        new_population.append(crossed2)

    return max_fitness, max_fitness_gene, max_fitness_trial, generational_stats, population, final_fitness, final_population

# Perform single point crossover based on crossover probability, halfway through
def crossover(parent1, parent2, probability_crossover):

    # If we hit the probability, then crossover on the parents
    random_val = random.random()
    if random_val < probability_crossover:

        # Get the poritons for parent 1
        parent1_portion1 = parent1[0:int(len(parent1)/2)]
        parent1_portion2 = parent1[int(len(parent1)/2):-1]

        # Get the portions for parent 2
        parent2_portion1 = parent2[0:int(len(parent1)/2)]
        parent2_portion2 = parent2[int(len(parent1)/2):-1]
        
        # Perform the crossover
        crossover1 = parent1_portion1 + parent2_portion2 
        crossover2 = parent2_portion1 + parent1_portion2 

        # Return the Crossover
        return crossover1, crossover2
    else:
        return parent1, parent2

# Mutate the entire population by potentially adding a move in the mix randomly
def mutate_population(population, probability_mutation):
    for trace in population:
        random_val = random.random()

        # If we hit the probabilty, mutate
        if random_val < probability_mutation:

            #Get transitions out of state1 and state2 + new random checks
            rand_move = random.choice(['u', 'd', 'l', 'r'])
            rand_index = random.randint(0, len(trace))
            trace.insert(rand_index, rand_move)
               
    return population
       

# Select and return two via roulette, with probability of choice weighted on their fitness in the old generation
def select(old_gen1, fitness1):
    old_gen = old_gen1.copy()
    fitness = fitness1.copy()

    # Get the first gene
    gene1 = random.choices(old_gen1, weights=fitness, k=1)
    gene1 = gene1[0]

    # Get the index from first gene and  remove the fitness of it from fitness, and the gene from oldgen to get the second
    gene1_index = old_gen.index(gene1)
    old_gen.remove(gene1)
    fitness.remove(fitness[gene1_index])

    # Get the second
    #print(f"Fitness {fitness}")
    gene2 = random.choices(old_gen, weights=fitness, k=1)
    gene2 = gene2[0] 

    return gene1, gene2


# Select and return two best indexes in the old generation for elitism later. Remember their indexes
def select_max(old_gen, fitness1):
    fitness = fitness1.copy()

    # Get the first index
    max1 = (max(fitness))
    index1 = fitness.index(max1) 

    # Remove first and get second best index
    fitness.remove(max1)
    index2 = fitness.index(max(fitness)) 

    return index1, index2

# Cull random 2 in population (keeping the elite values) and then add in the mutated. This produces the next generation.
def cull_random(population, fitness):

    
    # Inverse the fitness so we can weigh bad ones higher, +1 for smoothing of weights
    inverse = fitness.copy()
    max_inverse = max(inverse)
    inverse = list(map(lambda x: max_inverse - x + 1, inverse))

    # Cull two random ones weighted towards the bad ones.
    #print(population)
    #print(inverse)
    to_cull1 = random.choices(population, weights=inverse, k = 1)
    to_cull1 = to_cull1[0]
    inverse.remove(inverse[population.index(to_cull1)])
    population.remove(to_cull1)

    to_cull2 = random.choices(population, weights=inverse, k = 1)
    to_cull2 = to_cull2[0]
    inverse.remove(inverse[population.index(to_cull2)])
    population.remove(to_cull2)

    # Return population
    return population