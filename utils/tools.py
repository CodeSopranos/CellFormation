import requests
import numpy as np
import pandas as pd
from datetime import datetime
from algorithm.base import Algorithm
import collections
import itertools

def get_assignment_matrix(similarity_pairs):
    def get_index_by_key(d, k):
        try:
            return [key for key, corresponding_list in d.items() if k in corresponding_list][0]
        except IndexError:
            return -1
    def remove_empty_keys(d):
        for k in list(d):
            if not d[k]:
                del d[k]
        return d

    cells = {k: [] for k in range(len(similarity_pairs))}
    for ind, pair in enumerate(similarity_pairs):
        empty_list = 0
        slice_cells = dict(itertools.islice(cells.items(), ind)) #для поиска только в предыдущих ячейках
        first_key = get_index_by_key(slice_cells, pair[0][0])
        second_key = get_index_by_key(slice_cells, pair[0][1])
        if first_key == -1 and second_key == -1:
            cells[ind].append(pair[0][0])
            cells[ind].append(pair[0][1])
        elif first_key == -1:
            cells[second_key].append(pair[0][0])
        elif second_key == -1:
            cells[first_key].append(pair[0][1])
        else:
            continue
    return remove_empty_keys(cells)

def get_data(path):
    with open(path, 'r') as f:
        file = f.read().split('\n')
        file = [[int(i)-1 for i in l.split()] for l in file]
    machine_part_matrix = np.zeros((file[0][0] + 1, file[0][1] + 1), int)

    for row_num, m_row in enumerate(file[1:]):
        machine_part_matrix[row_num][[m_row]] = 1

    return machine_part_matrix

def get_similarity_pairs(machine_part_matrix):
    similarity_pairs = []
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
            coeff = get_similarity_coeff(i, j)
            similarity_matrix[i][j] = coeff
            if coeff != 0.0:
                similarity_pairs.append([(i, j), coeff])
    similarity_pairs.sort(key=lambda x: -x[1])
    return similarity_matrix, similarity_pairs

#def compute_initial_solution(machine_part_matrix):
    
