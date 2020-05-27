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
        self.f = {'curr' : 0, 'neigh' : 0}
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

        self.f['curr'] = self.get_grouping_efficacy('initial')
        while (self.c['MC'] < self.L and self.c['trapped'] < self.L/2):
            #print(self.S['neigh']['p'], self.f)
            self.single_move()
            self.S['current']['m'] = tools.get_asignments_by_machine(self.machine_part_matrix, self.S['current']['p'])
            self.f['neigh'] = self.get_grouping_efficacy('neigh')
            if (self.f['neigh'] > self.f['curr']):
                self.f['curr'] = self.f['neigh']
                self.c['stagnant'] = 0
            elif (self.f['neigh'] == self.f['curr'])
                
        #self.print_params()
    def get_grouping_efficacy(type_efficacy):
        return tools.compute_grouping_efficacy(self.S[type_efficacy]['p'], self.S[type_efficacy]['m'],                                                                             tools.solution_df(self.S[type_efficacy]['p'], 
                                            self.S[type_efficacy]['m'], 
                                            self.machine_part_matrix))
            
    def print_params(self):
        print("              f: {}".format(self.f))
        print("solution       : {}\n{}".format(self.S['neigh']['p']))
        print("temperature    : {}".format(self.t))
        print("cooling_rate   : {}".format(self.cooling_rate))
        print("L: {},        D : {}".format(self.L, self.D))
        print("number of cells: {}".format(self.n))

    def single_move(self):
        for ind_source, cell_source in enumerate(list(self.S['neigh']['p'].values())):
            if len(cell_source) == 1:
                continue

            for j in cell_source:
                self.S['neigh']['p'][ind_source].remove(j)

                for ind_dest, cell_destination in enumerate(list(self.S['neigh']['p'].values())):
                    if ind_dest == ind_source:
                        continue
                    self.S['neigh']['p'][ind_dest].append(j)
                    #print("current: {}\n, f: {}".format(
                    #        self.S['neigh']['p'], 
                    #        self.f))
                    curr_f = tools.compute_grouping_efficacy(self.S['neigh']['p'], self.S['neigh']['m'],                                                                             tools.solution_df(self.S['neigh']['p'], 
                                        self.S['neigh']['m'], 
                                        self.machine_part_matrix))
                    if curr_f > self.f['neigh']:
                        self.S['current'] = copy.deepcopy(self.S['neigh'])
                        self.f['neigh'] = copy.deepcopy(curr_f)
                    self.S['neigh']['p'][ind_dest].remove(j)
                self.S['neigh']['p'][ind_source].append(j)

