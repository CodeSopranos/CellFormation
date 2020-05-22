import requests
import numpy as np
import pandas as pd
from datetime import datetime
from algorithm.base import Algorithm

def get_data(path):
    with open(path, 'r') as f:
        file = f.read().split('\n')
        file = [[int(i)-1 for i in l.split()] for l in file]
    machine_part_matrix = np.zeros((file[0][0] + 1, file[0][1] + 1), int)

    for row_num, m_row in enumerate(file[1:]):
        machine_part_matrix[row_num][[m_row]] = 1

    return machine_part_matrix

def get_similarity_matrix(machine_part_matrix):
    def get_similarity_coeff(i, j):
        a, b, c = 0, 0, 0
        for k in range(machine_part_matrix.shape[0]):
            i_part, j_part = machine_part_matrix.T[i][k], machine_part_matrix.T[j][k]
            if i_part == 1 and j_part == 1:
                a+=1
            elif i_part == 1 and j_part == 0:
                b+=1
            elif i_part == 0 and j_part == 1:
                c+=1
        return a/(a + b + c)

    similarity_matrix = np.negative(np.ones(machine_part_matrix.shape))
    for i in range(machine_part_matrix.shape[0]):
        for j in range(i + 1, machine_part_matrix.shape[1]):
            similarity_matrix[i][j] = get_similarity_coeff(i, j)
    return similarity_matrix

#def compute_initial_solution(machine_part_matrix):
    
