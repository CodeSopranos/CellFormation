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
        self.S = {'current' :  {'p' : {}, 'm' : {}},
                  'neigh': {'p' : {}, 'm' : {}},
                  'best' : {'p' : {}, 'm' : {}},
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
        delta = 0


        while (self.c['MC'] < self.L and self.c['trapped'] < self.L/2):
            if flag:
                # generate initial solution by
                # using parts assignment and machines assignment
                self.S['initial']['p'], self.S['initial']['m'] = tools.get_solution(self.machine_part_matrix, self.n['initial'])
                self.S['neigh'] = self.S['current'] = copy.deepcopy(self.S['initial'])

                self.f['current'] = self.get_grouping_efficacy('initial')
                flag = False
            
            self.single_move()
            print('begin')
            self.print_params()
            #print(self.S['current']['p'], self.S['neigh']['p'])
            self.S['neigh']['m'] = tools.get_asignments_by_machine(self.machine_part_matrix, self.S['neigh']['p'])
            if self.f['current'] < self.f['neigh']:
                #self.S['best'] = copy.deepcopy(self.S['neigh'])
                self.S['current'] = copy.deepcopy(self.S['neigh'])
                self.f['current'] = copy.deepcopy(self.f['neigh'])
                #self.f['best'] = copy.deepcopy(self.f['neigh'])
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
            if self.t['current'] > self.t['final'] or self.c['stagnant'] >= self.c['check']:
                if self.f['current'] > self.f['best']:
                    self.S['best'] = copy.deepcopy(self.S['current'])
                    self.f['best'] = copy.deepcopy(self.f['current'])
                    self.n['optimal'] = copy.deepcopy(self.n['initial'])
                    self.n['initial'] += 1
                    flag = True
            else:
                self.t['current'] = self.t['current'] * self.cooling_rate
                self.c['MC'] = 0
            self.c['MC'] += 1
            print('end')
            self.print_params()
        self.print_params()
    def get_grouping_efficacy(self, type_efficacy):
        return tools.compute_grouping_efficacy(self.S[type_efficacy]['p'], self.S[type_efficacy]['m'],                                                                             tools.solution_df(self.S[type_efficacy]['p'], 
                                            self.S[type_efficacy]['m'], 
                                            self.machine_part_matrix))
            
    def print_params(self):
        print("              f: {}".format(self.f))
        #print("solution       : {}\n {}".format(self.S['neigh']['p'], self.S['current']['p']))
        print("temperature    : {}".format(self.t))
        #print("cooling_rate   : {}".format(self.cooling_rate))
        #print("L: {},        D : {}".format(self.L, self.D))
        print("number of cells: {}\n\n".format(self.n))

    def single_move(self):
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
                    curr_f = tools.compute_grouping_efficacy(self.S['current']['p'], self.S['current']['m'],                                                                             tools.solution_df(self.S['neigh']['p'], 
                                        self.S['current']['m'], 
                                        self.machine_part_matrix))
                    if curr_f > self.f['current']:
                        self.S['neigh'] = copy.deepcopy(self.S['neigh'])
                        self.f['neigh'] = copy.deepcopy(curr_f)
                    self.S['current']['p'][ind_dest].remove(j)
                self.S['current']['p'][ind_source].append(j)

            # self.single_move()
            
            # self.S['neigh']['m'] = tools.get_asignments_by_machine(self.machine_part_matrix, self.S['neigh']['p'])
            # print('0 ', self.f, self.S['current']['p'], self.S['neigh']['p'])

            # if (self.get_grouping_efficacy('neigh') > self.get_grouping_efficacy('best')):
                # self.S['best'] = copy.deepcopy(self.S['neigh'])
                # self.S['current'] = copy.deepcopy(self.S['neigh'])
                # self.c['stagnant'] = 0
                # self.c['MC'] += 1
                # print('1 ', self.f)
            # elif (self.get_grouping_efficacy('neigh') == self.get_grouping_efficacy('best')):
                # print('2 ', self.f)

                # self.S['curr'] = copy.deepcopy(self.S['neigh'])
                # self.c['stagnant'] += 1
                # self.c['MC'] += 1
            # delta = self.get_grouping_efficacy('current') - self.get_grouping_efficacy('neigh')
            # rand = random.random()
            # if (math.exp(delta/self.t['curr'])):
                # self.S['current'] = copy.deepcopy(self.S['neigh'])
                # self.c['trapped'] = 0
            # else:
                # self.c['trapped'] += 1
            # print('3 ', self.f)

            # if self.t['curr'] <= self.t['final'] or self.c['stagnant'] >= self.c['check']:
                # if self.get_grouping_efficacy('best') > self.get_grouping_efficacy('best_so_far'):
                    # self.S['best_so_far'] = copy.deepcopy(self.S['best'])
                    # self.n['optimal'] = copy.deepcopy(self.n['initial'])
                    # self.n['initial'] += 1
                    # flag = True
                # else:
                    # self.t['curr'] = self.t['curr'] * self.cooling_rate
                    # self.c['MC'] = 0
            # self.c['MC']+=1