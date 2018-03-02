# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 20:50:20 2018

@author: Rasmus
"""

from util import load_input
import numpy as np




def choose_next_ride(car_pos, time, T, B, rides):
    best_score = -1
    chosen_ride = None
    next_pos = None
    next_time = None
    
    for i_ride in rides:
        if i_ride['Taken']:
            continue
        distance_from_car_pos = abs(i_ride['start'][0]-car_pos[0]) + abs(i_ride['start'][1]-car_pos[1])
        car_ready_at = distance_from_car_pos + time
        actual_start_time = max([car_ready_at, i_ride['timeframe'][0]])
        time_at_finish = actual_start_time + i_ride['distance']
        score = i_ride['distance']
        if actual_start_time == i_ride['timeframe'][0]:
            score += B
        # normalize score
        score = score/(i_ride['distance'] + distance_from_car_pos)
        if time_at_finish >= T or time_at_finish > i_ride['timeframe'][1]:
            score = 0
        if score > best_score:
            best_score = score
            chosen_ride = i_ride
            next_pos = i_ride['stop']
            next_time = time_at_finish
    return chosen_ride, next_pos, next_time

def stupid_algorithm(path = 'a_example.in'):
    rides, env_params = load_input(path)  
    for ride in rides:
        ride['Taken'] = False
    cars = {}
    for i in range(env_params['F']):
        cars[i] = {'pos': (0,0), 'time': 0, 'rides': []}
    T = env_params['T']
    B = env_params['B']
    score = 0
    cars_done = 0
    while cars_done < env_params['F']:
        for i, i_car in cars.items():
            chosen_ride, next_pos, next_time = choose_next_ride(i_car['pos'], i_car['time'], T, B, rides)
            if chosen_ride is None:
                cars_done += 1
                continue
            i_car['rides'].append(chosen_ride['ID'])
            score += take_ride(i_car, chosen_ride, T, B)
    print(score)
    save_path = path.split('.')[0]+'_schedule'
    with open(save_path, 'w') as f:
        for i, i_car in cars.items():
            i_rides = i_car['rides']
            outlist = [len(i_rides)]
            outlist.extend(i_rides)
            outlist = [str(x) for x in outlist]
            f.write(' '.join(outlist))
            f.write("\n")

def evaluate(setup_path='a_example.in'):
    rides, env_params = load_input(setup_path)
    T = env_params['T']
    B = env_params['B']
    save_path = setup_path.split('.')[0]+'_schedule'
    for ride in rides:
        ride['Taken'] = False
    with open(save_path, 'r') as f:
        score = 0
        for row in f:
            row_lst = row.strip('\n').split(' ')
            car = {'pos': (0,0), 'time': 0, 'rides': []}
            for ride_ID_str in row_lst[1:len(row_lst)]:
                ride_ID = int(ride_ID_str)
                ride = get_ride(rides, ride_ID)
                if ride['Taken']:
                    raise ValueError()
                score += take_ride(car, ride, T, B)   
    return score
        
def take_ride(car, ride, T, B):
    car_pos = car['pos']
    distance_from_car_pos = abs(ride['start'][0]-car_pos[0]) + abs(ride['start'][1]-car_pos[1])
    car_ready_at = distance_from_car_pos+car['time']
    actual_start_time = max([car_ready_at, ride['timeframe'][0]])
    time_at_finish = actual_start_time + ride['distance']
    score = ride['distance']
    if actual_start_time == ride['timeframe'][0]:
        score += B
    if time_at_finish >= T or time_at_finish > ride['timeframe'][1]:
        score = 0
    car['pos'] = ride['stop']
    car['time'] = time_at_finish
    ride['Taken'] = True
    return score

def get_ride(rides, ride_ID):
    for i_ride in rides:
        if i_ride['ID'] == ride_ID:
            return i_ride
       
stupid_algorithm('a_example.in')
stupid_algorithm('b_should_be_easy.in')
stupid_algorithm('c_no_hurry.in')
stupid_algorithm('d_metropolis.in')
stupid_algorithm('e_high_bonus.in') 
#print(evaluate('b_should_be_easy.in'))        