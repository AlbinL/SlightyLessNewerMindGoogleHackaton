#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

import random

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

IND_INIT_SIZE = 5
MAX_ITEM = 50
MAX_WEIGHT = 50
NBR_ITEMS = 20

# To assure reproductibility, the RNG seed is set prior to the items
# dict initialization. It is also seeded in main().
random.seed(64)

# Load data
def load_input(path):
    with open(path, 'r') as f:
        first_line = f.readline()
        (R, C, F, N, B, T) = first_line.split(' ' )
        env_params = {'R': int(R), 'C': int(C), 'F': int(F), 'N': int(N),
                      'B': int(B), 'T': T}
        rides = [None for x in range(int(N))]
        for i, row in enumerate(f):
            rides[i] = make_ride(row.strip('\n'))
    return rides, env_params

def make_ride(input_string):
    input_list = input_string.split(' ')
    ride = {'start': (int(input_list[0]), int(input_list[1])),
            'stop': (int(input_list[2]), int(input_list[3])),
            'timeframe': (int(input_list[4]), int(input_list[5]))}
    distance = abs(ride['start'][0]-ride['stop'][0]) + abs(ride['start'][1]-ride['stop'][1])
    ride['distance'] = distance
    return ride

# Create the item dictionary: item name is an integer, and value is 
# a (weight, value) 2-uple.
items = {}
# Create random items and store them in the items' dictionary.
for i in range(NBR_ITEMS):
    items[i] = (random.randint(1, 10), random.uniform(0, 100))

creator.create("Fitness", base.Fitness, weights=(-1.0, 1.0))
creator.create("Individual", set, fitness=creator.Fitness)

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("attr_item", random.randrange, NBR_ITEMS)

# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual, 
    toolbox.attr_item, IND_INIT_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalFleet(chromosome, rides, env_params):

    fitness = 0
    violation = 0

    bonus = env_params['B']
    nr_vehicles = env_params['F']


    for i_vehicle in range(nr_vehicles):

        earliest_leave_previous_ride_time = 0
        current_row = 0
        current_col = 0

        # Get all rides travelling with current vehicle
        ride_indices = [i for i, x in enumerate(chromosome) if x == i_vehicle]

        # Get latest arrival times for all rides travelling with current vehicle
        latest_arrival_times = []
        for i in range(len(ride_indices)):
            i_ride = ride_indices[i]
            ride_dict = rides[i_ride]
            latest_arrival_times.append(ride_dict['timeframe'][1])

        ride_indices = [x for _, x in sorted(zip(latest_arrival_times, ride_indices))]

        for i_ride in ride_indices:

            ride_dict = rides[i_ride]

            earliest_departure = ride_dict['timeframe'][0]
            latest_arrival = ride_dict['timeframe'][1]
            current_ride_distance = ride_dict['distance']
            current_ride_start_row = ride_dict['start'][0]
            current_ride_start_col = ride_dict['start'][1]
            current_ride_stop_row = ride_dict['stop'][0]
            current_ride_stop_col= ride_dict['stop'][1]

            current_ride_duration = current_ride_distance

            travel_to_ride_duration = abs(current_ride_start_col - current_col) + abs(current_ride_start_row - current_row)

            actual_departure = max(earliest_departure, earliest_leave_previous_ride_time + current_ride_duration + travel_to_ride_duration)

            earliest_leave_previous_ride_time = actual_departure + current_ride_duration + travel_to_ride_duration
            current_row = current_ride_stop_row
            current_col = current_ride_stop_col

            if actual_departure <= latest_arrival:
                fitness += current_ride_distance
                if actual_departure == earliest_departure:
                    fitness += bonus
            else:
                violation -= 1

    if violation < 0:
        return violation
    else:
        return fitness

def cxSet(ind1, ind2):
    """Apply a crossover operation on input sets. The first child is the
    intersection of the two sets, the second child is the difference of the
    two sets.
    """
    temp = set(ind1)                # Used in order to keep type
    ind1 &= ind2                    # Intersection (inplace)
    ind2 ^= temp                    # Symmetric Difference (inplace)
    return ind1, ind2
    
def mutSet(individual):
    """Mutation that pops or add an element."""
    if random.random() < 0.5:
        if len(individual) > 0:     # We cannot pop from an empty set
            individual.remove(random.choice(sorted(tuple(individual))))
    else:
        individual.add(random.randrange(NBR_ITEMS))
    return individual,

toolbox.register("evaluate", evalFleet)
toolbox.register("mate", cxSet)
toolbox.register("mutate", mutSet)
toolbox.register("select", tools.selNSGA2)

def main():
    rides, env_params = load_input("/home/viktor/Downloads/a_example.in")

    random.seed(64)
    NGEN = 50
    MU = 50
    LAMBDA = 100
    CXPB = 0.7
    MUTPB = 0.2
    
    pop = toolbox.population(n=MU)
    hof = tools.ParetoFront()
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)
    
    algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats,
                              halloffame=hof)
    
    return pop, stats, hof
                 
if __name__ == "__main__":
    main()  