# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 18:02:42 2018

@author: Rasmus
"""

def load_input(path):
    with open(path, 'r') as f:
        first_line = f.readline()
        (R, C, F, N, B, T) = first_line.split(' ' )
        env_params = {'R': int(R), 'C': int(C), 'F': int(F), 'N': int(N),
                      'B': int(B), 'T': int(T)}
        rides = [None for x in range(int(N))]
        for i, row in enumerate(f):
            rides[i] = make_ride(row.strip('\n'))
            rides[i]['ID'] = i
    return rides, env_params

def make_ride(input_string):
    input_list = input_string.split(' ')
    ride = {'start': (int(input_list[0]), int(input_list[1])),
            'stop': (int(input_list[2]), int(input_list[3])),
            'timeframe': (int(input_list[4]), int(input_list[5]))}
    distance = abs(ride['start'][0]-ride['stop'][0]) + abs(ride['start'][1]-ride['stop'][1])
    ride['distance'] = distance
    return ride
