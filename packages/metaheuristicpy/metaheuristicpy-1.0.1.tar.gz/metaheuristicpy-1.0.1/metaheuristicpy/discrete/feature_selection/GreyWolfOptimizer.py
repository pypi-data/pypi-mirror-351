from .BaseMetaFeatureSelection import BaseMetaheuristics
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import time


class GWO(BaseMetaheuristics):

    def __init__(self,
                 N_WOLVES=30,
                 MAX_ITERATIONS=100,
                 MAX_CONVERGENCE=10,
                 OPTIMIZER_NAME='Grey Wolf Optimizer',
                 MODEL_CLASSIFIER=KNeighborsClassifier(),
                 OBJECTIVE='max',
                 BREAK_IF_CONVERGENCE=False,
                 TRANSFER_BINARY_FUNCTION='s_shaped_f2'
                 ):
        super().__init__(
            N_AGENTS=N_WOLVES,
            MAX_ITERATIONS=MAX_ITERATIONS,
            MAX_CONVERGENCE=MAX_CONVERGENCE,
            OBJECTIVE=OBJECTIVE,
            MODEL_CLASSIFIER=MODEL_CLASSIFIER,
            BREAK_IF_CONVERGENCE=BREAK_IF_CONVERGENCE,
            TRANSFER_BINARY_FUNCTION=TRANSFER_BINARY_FUNCTION,
        )
        self.optimizer['name'] = OPTIMIZER_NAME
        self.optimizer['params'].update({
            "UB": 1,
            "LB": 0,
        })

    def fit(self, X_train, y_train, X_test, y_test):
        super().fit(X_train, y_train, X_test, y_test)
        self._IS_FIT = True
        return self

    def solve(self):
        if self._IS_FIT:
            MAX_ITERATIONS = self.optimizer['params']['MAX_ITERATIONS']
            N_WOLVES = self.optimizer['params']['N_AGENTS']

            start_time = time.time()
            # 1. Initialize agents
            agents, agents_fitness, best_fitness_previous = self._initialize_agents()
            # Initialize alpha, beta, and delta positions
            alpha_wolves, betha_wolves, delta_wolves = self._initialize_alpha_betha_delta_wolves()

            # 2. GWO main loop
            convergence = 0
            for iteration in range(MAX_ITERATIONS):
                # 4. update wolves position
                agents = self.__update_wolves_position(
                    agents, iteration, alpha_wolves, betha_wolves, delta_wolves)

                # evaluate fitness, and update alpha, betha, and delta wolves
                for i in range(N_WOLVES):
                    # binarization and evaluate fitness
                    binary_wolf = self._standard_binarization_rule(
                        np.array([agents[i]])
                    )[0]
                    agents_fitness[i] = self._evaluate_fitness(binary_wolf)

                    # Update alpha, beta, and delta positions
                    if agents_fitness[i] > alpha_wolves['fitness']:
                        alpha_wolves = {
                            'position': agents[i].copy(),
                            'fitness': agents_fitness[i]
                        }
                    elif agents_fitness[i] > betha_wolves['fitness']:
                        betha_wolves = {
                            'position': agents[i].copy(),
                            'fitness': agents_fitness[i]
                        }
                    elif agents_fitness[i] > delta_wolves['fitness']:
                        delta_wolves = {
                            'position': agents[i].copy(),
                            'fitness': agents_fitness[i]
                        }

                # binarization of best wolves
                GBest = self._standard_binarization_rule(
                    np.array([alpha_wolves['position']])
                )[0]
                GBest_fitness = alpha_wolves['fitness']

                # check convergence
                self.LIST_BEST_FITNESS.append(GBest_fitness)
                is_break, best_fitness_previous, convergence = self._check_convergence(
                    GBest_fitness, best_fitness_previous, convergence, iteration)
                if is_break and self.BREAK_IF_CONVERGENCE:
                    break

            end_time = time.time()
            # Get optimal features
            optimal_solution = {
                'features_subset': GBest,
                'selected_features': np.where(GBest == 1)[0],
                'optimal_n_features': len(np.where(GBest == 1)[0]),
                'best_fitness': GBest_fitness,
                'start_time_computation': start_time,
                'end_time_computation': end_time,
                'total_train_time_computation': self._calculate_total_training_time_computation(start_time, end_time)
            }
            return optimal_solution

        else:
            raise Exception('Please fit your dataset first!')

    def _initialize_agents(self):
        N_AGENTS = self.optimizer['params']['N_AGENTS']
        UB = self.optimizer['params']['UB']
        LB = self.optimizer['params']['UB']
        N_FEATURES = self.N_FEATURES
        # Continuous positions in [lb, ub]
        agents = np.random.uniform(LB, UB, (N_AGENTS, N_FEATURES))
        agents_fitness = np.zeros(N_AGENTS)

        best_fitness_previous = -np.inf
        if self.OBJECTIVE == 'min':
            best_fitness_previous = np.inf
        return agents, agents_fitness, best_fitness_previous

    def __update_wolves_position(self, agents, current_index_iteration, alpha_wolves, betha_wolves, delta_wolves):
        """
        Function for update wolves position
        """
        MAX_ITERATIONS = self.optimizer['params']['MAX_ITERATIONS']
        N_FEATURES = self.N_FEATURES
        alpha_pos = alpha_wolves['position']
        betha_pos = betha_wolves['position']
        delta_pos = delta_wolves['position']
        a = 2 - current_index_iteration * (2 / MAX_ITERATIONS)
        for idx_agent, agent in enumerate(agents):
            for j in range(N_FEATURES):
                # Update position using GWO equations
                A1 = 2 * a * np.random.rand() - a
                C1 = 2 * np.random.rand()
                D_alpha = abs(C1 * alpha_pos[j] - agents[idx_agent][j])
                X1 = alpha_pos[j] - A1 * D_alpha

                A2 = 2 * a * np.random.rand() - a
                C2 = 2 * np.random.rand()
                D_beta = abs(C2 * betha_pos[j] - agents[idx_agent][j])
                X2 = betha_pos[j] - A2 * D_beta

                A3 = 2 * a * np.random.rand() - a
                C3 = 2 * np.random.rand()
                D_delta = abs(C3 * delta_pos[j] - agents[idx_agent][j])
                X3 = delta_pos[j] - A3 * D_delta

                agents[idx_agent][j] = (X1+X2+X3)/3
        return agents

    def _initialize_alpha_betha_delta_wolves(self):
        N_FEATURES = self.N_FEATURES
        alpha_wolves = {
            'position': np.zeros(N_FEATURES),
            'fitness': -np.inf
        }
        betha_wolves = {
            'position': np.zeros(N_FEATURES),
            'fitness': -np.inf
        }
        delta_wolves = {
            'position': np.zeros(N_FEATURES),
            'fitness': -np.inf
        }
        return alpha_wolves, betha_wolves, delta_wolves
