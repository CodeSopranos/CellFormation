import copy
import random
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm, tqdm_notebook
from algorithm.base import Algorithm
from utils import tools


class SimulatedAnnealing(Algorithm):

    def __init__(self, machine_part_matrix):
        self.machine_part_matrix = machine_part_matrix
        self.history = []
        # solution
        self.S = {'current' :  {'p' : {}, 'm' : {}},
                  'neigh': {'p' : {}, 'm' : {}},
                  'best' : {'p' : {}, 'm' : {}},
                  'initial' : {'p' : {}, 'm' : {}}}


    def set_params(self, params):
        self.t = {'initial' : params['initial_temperature'], 'final' : params['final_temperature']}
        self.cooling_rate = 0
        self.L = params['chain_len']                                   # Markov chain len
        self.D = params['len_of_period']
        self.n = {'initial' : params['numb_of_cells'], 'optimal' : 0}  # number of cells
        self.c = {'MC' : 0, 'trapped' : 0, 'stagnant' : 0, 'counter' : 0}

    @property
    def name(self):
        return 'SimulatedAnnealing'

    def solve(self):
        # generate initial solution by
        # using parts assignment and machines assignment
        self.S['initial']['p'], self.S['initial']['m'] = tools.get_solution(self.machine_part_matrix, self.n['initial'])
        self.S['neigh'] = self.S['best'] = self.S['current'] = copy.copy(self.S['initial'])
        self.print_params()

    def print_params(self):
        # print("solution       : {}".format(self.S))
        print("temperature    : {}".format(self.t))
        print("cooling_rate   : {}".format(self.cooling_rate))
        print("L: {},        D : {}".format(self.L, self.D))
        print("number of cells: {}".format(self.n))

    def single_move(self):
        for ind_source, cell_source in enumerate(list(self.S['neigh']['p'])):
            for j in cell_source:
                if len(cell_source) == 1:
                    continue
                for ind_dest, cell_destination in enumerate(list(self.S['neigh']['p'])):
                    if ind_dest == ind_source:
                        continue
                    cell_source.remove(j)
                    cell_destination.append(j)
                    