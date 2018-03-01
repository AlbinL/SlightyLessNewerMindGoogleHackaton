import random

from deap import base
from deap import creator
from deap import tools
from deap import algorithms
import numpy

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

rides, env_params = load_input('/home/viktor/Downloads/e_high_bonus.in')

def evalFleet(chromosome, rides, env_params):

    fitness = 0
    violation = 0

    bonus = env_params['B']
    nr_vehicles = env_params['F']

    for i_vehicle in range(1, nr_vehicles):

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
        return (violation,)
    else:
        return (fitness,)

def initialGeneValue(max_gene_value):
    if random.uniform(0, 1) < 0.05:
        return random.randint(0, max_gene_value)
    else:
        return 0

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_bool", initialGeneValue, env_params['F'] + 1)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_bool, env_params['N'])
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evalFleet, rides=rides, env_params=env_params)
toolbox.register("mate", tools.cxOnePoint)
toolbox.register("mutate", tools.mutUniformInt, low=0, up=env_params['F'] + 1, indpb=1.0 / env_params['N'])
toolbox.register("select", tools.selTournament, tournsize=3)


def main():

    random.seed(64)

    # create an initial population of 300 individuals (where
    # each individual is a list of integers)
    pop = toolbox.population(n=100)
    CXPB, MUTPB = 0.5, 0.2
    number_of_generations = 100

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))

    pop = toolbox.population(n=100)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=number_of_generations,
                                   stats=stats, halloffame=hof, verbose=True)

    printBestIndividualGoogleStyle(hof, rides)

    return pop, log, hof


def printBestIndividualGoogleStyle(bestIndividual, rides):
    info = {}
    print(bestIndividual)

    for index, vehicle in enumerate(bestIndividual[0]):

        # ride_indicies = [i for i, x in enumerate(bestIndividual) if x == vehicle]
        try:
            info[vehicle].append(index)
        except:
            info[vehicle] = [index]

    with open("./best_solution", 'w') as f:
        for key, item in info.iteritems():
            latest_arrival_times = []
            ride_indices = item
            for i in range(len(ride_indices)):
                i_ride = ride_indices[i]
                ride_dict = rides[i_ride]
                latest_arrival_times.append(ride_dict['timeframe'][1])

            ride_indices = [x for _, x in sorted(zip(latest_arrival_times, ride_indices))]

            outlist = [len(ride_indices)]
            outlist.extend(ride_indices)
            outlist = [str(x) for x in outlist]
            print(' '.join(outlist))
            f.write(' '.join(outlist))
            f.write("\n")


if __name__ == "__main__":
    main()