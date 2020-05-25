import requests
import numpy as np
import pandas as pd
from datetime import datetime
from algorithm.base import Algorithm
import collections
import itertools

def get_solution(machine_part_matrix):
    similarity_matrix, np_similarity = get_similarity_pairs(machine_part_matrix)
    cells_p = get_assignments_by_parts(np_similarity)
    cells_m = get_asignments_by_machine(machine_part_matrix, cells_p)
    return cells_p, cells_m

def remove_empty_keys(d):
    for k in list(d):
        if not d[k]:
            del d[k]
    for ind, k in enumerate(list(d)):
        d[ind] = d.pop(k)
    return d

def get_asignments_by_machine(machine_part_matrix, cells_p):
    def get_v_e_sum(machine_part_line, cell):
        all_ind = [i for i in range(len(machine_part_line))]
        out_ind = list(set(all_ind) ^ set(cell))
        v = np.array(machine_part_line)[out_ind].sum()
        e = len(cell) - np.array(machine_part_line)[cell].sum()
        return v + e
    bit_mask = np.zeros(len(cells_p))
    cells_m = {k: [] for k in range(len(cells_p))}
    for ind, line in enumerate(machine_part_matrix):
        cell_num = np.argmin([get_v_e_sum(line, cell) for cell in cells_p.values()])
        if (ind == len(machine_part_matrix) - 1):
            empty_cell_num = [i for i,x in enumerate(list(cells_m.values())) if not x]
            #print(empty_cell_num)
            cell_num = empty_cell_num[0]
        cells_m[cell_num].append(ind)
        bit_mask[cell_num]+=1
    return remove_empty_keys(cells_m)

def get_assignments_by_parts(similarity_pairs):
    def get_index_by_key(d, k):
        try:
            return [key for key, corresponding_list in d.items() if k in corresponding_list][0]
        except IndexError:
            return -1
    cells_p = {k: [] for k in range(len(similarity_pairs))}
    for ind, pair in enumerate(similarity_pairs):
        empty_list = 0
        slice_cells_p = dict(itertools.islice(cells_p.items(), ind)) #для поиска только в предыдущих ячейках
        first_key = get_index_by_key(slice_cells_p, pair[0][0])
        second_key = get_index_by_key(slice_cells_p, pair[0][1])
        if first_key == -1 and second_key == -1:
            cells_p[ind].append(pair[0][0])
            cells_p[ind].append(pair[0][1])
        elif first_key == -1:
            cells_p[second_key].append(pair[0][0])
        elif second_key == -1:
            cells_p[first_key].append(pair[0][1])
        else:
            continue
    return remove_empty_keys(cells_p)

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

def print_solution_df(cells_p, cells_m, machine_part_matrix):
    list_cells_m = list(itertools.chain.from_iterable(list(cells_m.values())))
    list_cells_p = list(itertools.chain.from_iterable(list(cells_p.values())))
    df = pd.DataFrame(machine_part_matrix)
    df = df[list_cells_p]
    return df.T[list_cells_m].T

