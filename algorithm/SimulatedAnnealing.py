import copy
import math
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
        self.f = {'current' : 0, 'neigh' : 0, 'best' : 0}
        # solution
        self.last_cell_nums = [] 
        self.S = {'current' :  {'p' : {}, 'm' : {}},
                  'neigh': {'p' : {}, 'm' : {}},
                  'neigh_curr' : {'p' : {}, 'm' : {}},
                  'best_so_far' : {'p' : {}, 'm' : {}},
                  'initial' : {'p' : {}, 'm' : {}}}


    def set_params(self, params):
        self.t = {'current' : params['initial_temperature'], 'final' : params['final_temperature']}
        self.cooling_rate = params['cooling_rate']
        self.L = params['chain_len']                                   # Markov chain len
        self.D = params['len_of_period']
        self.n = {'initial' : params['numb_of_cells'], 'optimal' : 0}  # number of cells
        self.c = {'MC' : 0, 'trapped' : 0, 'stagnant' : 0, 'check' : params['check']}

    @property
    def name(self):
        return 'SimulatedAnnealing'

    def solve(self):
        flag = True
        delta, counter = 0, 0
        while (self.c['MC'] < self.L and self.c['trapped'] < self.L/2):
            counter+=1
            if flag:
                # generate initial solution by
                # using parts assignment and machines assignment
                self.S['initial']['p'], self.S['initial']['m'] = tools.get_solution(self.machine_part_matrix, self.n['initial'])
                self.S['neigh'] = self.S['current'] = copy.deepcopy(self.S['initial'])

                self.f['current'] = self.get_grouping_efficacy('initial')
                flag = False
            if counter == 1:
                self.print_params()

            self.single_move()
            
            if counter % self.D == 0:
                self.exchange_move()
            self.S['neigh']['m'] = tools.get_asignments_by_machine(self.machine_part_matrix, self.S['neigh']['p'])
            if self.f['current'] < self.f['neigh']:
                self.S['current'] = copy.deepcopy(self.S['neigh'])
                self.f['current'] = copy.deepcopy(self.f['neigh'])
                self.c['stagnant'] = 0
            elif self.f['current'] == self.f['neigh']:
                self.c['stagnant'] += 1
            else:
                delta = self.get_grouping_efficacy('current') - self.get_grouping_efficacy('neigh')
                rand = random.random()
                if (math.exp(delta/self.t['curr'])):
                    self.S['current'] = copy.deepcopy(self.S['neigh'])
                    self.c['trapped'] = 0
                else:
                    self.c['trapped'] += 1
            if self.t['current'] < self.t['final'] or self.c['stagnant'] >= self.c['check']:
                if self.f['current'] > self.f['best']:
                    self.S['best'] = copy.deepcopy(self.S['current'])
                    self.f['best'] = copy.deepcopy(self.f['current'])
                    self.n['optimal'] = copy.deepcopy(self.n['initial'])
                    self.n['initial'] += 1
                    flag = True
            else:
                self.t['current'] = copy.deepcopy(self.t['current'] * self.cooling_rate)
                self.c['MC'] = 0
            self.c['MC'] += 1
        self.print_params()

    def get_grouping_efficacy(self, type_efficacy):
        return tools.compute_grouping_efficacy(self.S[type_efficacy]['p'], self.S[type_efficacy]['m'],                                                                             tools.solution_df(self.S[type_efficacy]['p'], 
                                      self.S[type_efficacy]['m'], 
                                      self.machine_part_matrix))

    def print_params(self):
        print("              f: {}".format(self.f))
        # print("solution       : {}".format(self.S['neigh']['p']))
        print("temperature    : {}".format(self.t))
        #print("last cell: {},     D : {}".format(set(self.last_cell_nums), self.D))
        print("number of cells: {} cool_rate: {}\n\n".format(self.n, self.cooling_rate))
        
    def single_move(self):
        self.last_cell_nums = []
        for ind_source, cell_source in enumerate(list(self.S['current']['p'].values())):
            if len(cell_source) == 1:
                continue

            for j in cell_source:
                self.S['current']['p'][ind_source].remove(j)

                for ind_dest, cell_destination in enumerate(list(self.S['current']['p'].values())):
                    if ind_dest == ind_source:
                        continue
                    self.S['current']['p'][ind_dest].append(j)
                    #print("current: {}\n, f: {}".format(
                    #        self.S['neigh']['p'], 
                    #        self.f))
                    curr_f = tools.compute_grouping_efficacy(self.S['current']['p'], self.S['current']['m'],                                                                             tools.solution_df(self.S['current']['p'], 
                                        self.S['current']['m'], 
                                        self.machine_part_matrix))
                    if curr_f > self.f['current']:
                        self.last_cell_nums.append((ind_source, ind_dest, j))
                        self.S['neigh'] = copy.deepcopy(self.S['neigh'])
                        self.f['neigh'] = copy.deepcopy(curr_f)
                    self.S['current']['p'][ind_dest].remove(j)
                self.S['current']['p'][ind_source].append(j)
    
    def exchange_move(self):
        solution = {}
        f_best, curr_f = copy.deepcopy(self.f['neigh']), copy.deepcopy(self.f['neigh'])
        for history in self.last_cell_nums:
            ind_source, ind_dest, j = history
            for part in self.S['neigh']['p'][ind_dest]:
                if part == j:
                    continue
                self.S['neigh']['p'][ind_dest].remove(part)
                self.S['neigh']['p'][ind_source].append(part)
                curr_f = tools.compute_grouping_efficacy(self.S['neigh']['p'], self.S['neigh']['m'],                                                                             tools.solution_df(self.S['neigh']['p'], 
                                        self.S['neigh']['m'], 
                                        self.machine_part_matrix))
                if curr_f > f_best:
                    solution = copy.deepcopy(self.S['neigh'])
                    f_best = copy.deepcopy(self.f['neigh'])
                self.S['neigh']['p'][ind_dest].append(part)
                self.S['neigh']['p'][ind_source].remove(part)
        if f_best > self.f['neigh']:
            self.S['neigh'] = copy.deepcopy(solution)
            self.f['neigh'] = copy.deepcopy(f_best)
