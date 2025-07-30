import numpy as np
from sklearn.metrics import f1_score
import math
from scipy.special import erf
import datetime


class BaseMetaheuristics:

    def __init__(self,
                 N_AGENTS,
                 MAX_ITERATIONS,
                 MAX_CONVERGENCE,
                 MODEL_CLASSIFIER,
                 OBJECTIVE='max',
                 ALPHA_FITNESS=0.99,
                 BETHA_FITNESS=0.01,
                 BREAK_IF_CONVERGENCE=False,
                 TRANSFER_BINARY_FUNCTION='s_shaped_f2',
                 **kwargs):
        self.optimizer = {
            "name": None,
            "clf": MODEL_CLASSIFIER,
            "params": {
                "N_AGENTS": N_AGENTS,
                "MAX_ITERATIONS": MAX_ITERATIONS,
                "MAX_CONVERGENCE": MAX_CONVERGENCE,
                "ALPHA_FITNESS": ALPHA_FITNESS,
                "BETHA_FITNESS": BETHA_FITNESS,
            },
            "transfer_function": self._transfer_binary_function(TRANSFER_BINARY_FUNCTION)
        }
        self._IS_FIT = False
        self._IS_SOLVE = False
        self.OBJECTIVE = OBJECTIVE
        self.BREAK_IF_CONVERGENCE = BREAK_IF_CONVERGENCE
        self.LIST_BEST_FITNESS = list()

    def fit(self, X_train, y_train, X_test, y_test):
        """
        Function untuk memasukkan data training X_train,y_train dan data testing X_test, y_test dalam bentuk array untuk proses optimasi (feature selection).

        <INPUT>
        - X_train: n-d array format as input variables
        - y: n-d array format as label (dependent variables)
        """
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.N_FEATURES = X_train.shape[1]

    def solve(self):
        pass

    def _initialize_agents(self):
        """
        Function untuk initialize random agents sebagai solusi awal. Setiap agent memiliki dimensi N dengan N menyatakan jumlah fitur dari dataset yang dimasukkan. Setiap elemen pada setiap dimensi merupakan nilai biner 1/0 yang menyatakan aktif atau tidaknya suatu fitur

        <Output>
        - agents: n-d dimensional array in numpy format containing 1/0 bit
        """

        agents = np.random.randint(
            2, size=(self.optimizer['params']['N_AGENTS'], self.N_FEATURES))
        return agents

    def _evaluate_fitness(self, agent):
        """
        Function untuk evaluasi fitness setiap agent dengan menggunakan metrics F1-score (macro)
        """
        clf = self.optimizer['clf']
        ALPHA_FITNESS = self.optimizer['params']['ALPHA_FITNESS']
        BETHA_FITNESS = self.optimizer['params']['BETHA_FITNESS']

        selected_features = np.where(agent == 1)[0]
        n_selected_features = len(selected_features)
        total_features = len(agent)
        # check jika tidak ada fitur yang dipilih
        if n_selected_features == 0:
            return 0

        # calculate relative number of selected features
        relative_selected_features = abs(n_selected_features/total_features)

        # calculate macro F1-score from the classifier
        clf.fit(self.X_train[:, selected_features], self.y_train)
        y_pred = clf.predict(self.X_test[:, selected_features])
        macro_f1_score = f1_score(self.y_test, y_pred, average='macro')

        # calculate overall fitness score
        fitness_score = (ALPHA_FITNESS * macro_f1_score) - \
            (BETHA_FITNESS * relative_selected_features)
        return fitness_score

    def _transfer_binary_function(self, transfer_binary_function_name):
        """
        Transfer function merupakan fungsi untuk mengubah continous value ke dalam ruang solusi 0 sampai 1. Ada beberapa tipe transfer function, S-shaped, V-shaped, Quadratic, U-shaped, Z-shaped. Transfer function yang diimplementasikan pada modul ini masih berfokus pada S-shaped dan V-shaped.
        Transfer function S-shaped dan V-shaped yang diimplementasikan pada modul ini mengadopsi hasil penelitian:
            Haikal, V., & Suyanto, S. (2024, August). Binary Komodo Mlipir Algorithm for Feature Selection. In 2024 International Conference on Artificial Intelligence, Blockchain, Cloud Computing, and Data Analytics (ICoABCD) (pp. 255-260). IEEE.

        - S-shaped:
            - s_shaped_f1: Fungsi ke-1 dari S-shaped
            - s_shaped_f2: Fungsi ke-2 dari S-shaped (sigmoid)
            - s_shaped_f3: Fungsi ke-3 dari S-shaped
            - s_shaped_f4: Fungsi ke-4 dari S-shaped
        - V-shaped:
            - v_shaped_f1: Fungsi ke-1 dari S-shaped
            - v_shaped_f2: Fungsi ke-2 dari S-shaped
            - v_shaped_f3: Fungsi ke-3 dari S-shaped
            - v_shaped_f4: Fungsi ke-4 dari S-shaped
        """
        transfer_mapping_binary_function = {
            's_shaped_f1': self.__s_shaped_f1,
            's_shaped_f2': self.__s_shaped_f2,
            's_shaped_f3': self.__s_shaped_f3,
            's_shaped_f4': self.__s_shaped_f4,
            'v_shaped_f1': self.__v_shaped_f1,
            'v_shaped_f2': self.__v_shaped_f2,
            'v_shaped_f3': self.__v_shaped_f3,
            'v_shaped_f4': self.__v_shaped_f4,
        }
        return transfer_mapping_binary_function[transfer_binary_function_name]

    def __s_shaped_f1(self, x):
        return 1/(1+np.exp(-2*x))

    def __s_shaped_f2(self, x):
        return 1 / (1 + np.exp(-x))

    def __s_shaped_f3(self, x):
        return 1 / (1 + np.exp(-0.5*x))

    def __s_shaped_f4(self, x):
        return 1 / (1 + np.exp(-x * (1/3)))

    def __v_shaped_f1(self, x):
        """
        Calculates TF(x) = |erf(0.5*sqrt(phi)*x)|.

        Args:
            x (float or numpy.ndarray): Input value(s).
            phi (float): Parameter phi.

        Returns:
            float or numpy.ndarray: Output value(s).
        """
        return np.abs(erf(0.5 * np.sqrt(math.pi) * x))

    def __v_shaped_f2(self, x):
        """
        Calculates TF(x) = |tanh(x)|.

        Args:
            x (float or numpy.ndarray): Input value(s).

        Returns:
            float or numpy.ndarray: Output value(s).
        """
        return np.abs(np.tanh(x))

    def __v_shaped_f3(self, x):
        """
        Calculates TF(x) = |(x)/(sqrt(1+pow(x,2)))|.

        Args:
            x (float or numpy.ndarray): Input value(s).
            phi (float): Parameter phi.

        Returns:
            float or numpy.ndarray: Output value(s).
        """
        return np.abs((x)/np.sqrt(1+math.pow(x, 2)))

    def __v_shaped_f4(self, x):
        """
        Calculates TF(x) = |(2/phi) * arctan(0.5*phi*x)|.

        Args:
            x (float or numpy.ndarray): Input value(s).
            phi (float): Parameter phi.

        Returns:
            float or numpy.ndarray: Output value(s).
        """
        return np.abs((2 / math.pi) * np.arctan(0.5 * math.pi * x))

    def _retrieve_best_agent(self, agents, agents_fitness):
        idx_best_fitness = np.argmax(agents_fitness)
        best_fitness = agents_fitness[idx_best_fitness]
        best_agent = agents[idx_best_fitness].copy()
        if self.OBJECTIVE == 'min':
            idx_best_fitness = np.argmin(agents_fitness)
            best_fitness = agents_fitness[idx_best_fitness]
            best_agent = agents[idx_best_fitness].copy()
        return best_agent, best_fitness

    def _retrieve_worst_agent(self, agents, agents_fitness):
        idx_worst_fitness = np.argmin(agents_fitness)
        worst_fitness = agents_fitness[idx_worst_fitness]
        worst_agent = agents[idx_worst_fitness]
        if self.OBJECTIVE == 'min':
            idx_worst_fitness = np.argmax(agents_fitness)
            worst_fitness = agents_fitness[idx_worst_fitness]
            worst_agent = agents[idx_worst_fitness]
        return worst_agent, worst_fitness

    def _check_convergence(self, gbest_fitness, best_fitness_previous, convergence, idx_iteration):
        MAX_CONVERGENCE = self.optimizer['params']['MAX_CONVERGENCE']
        is_break = False
        if math.isclose(best_fitness_previous, gbest_fitness, rel_tol=1e-9, abs_tol=1e-9):
            convergence += 1
        else:
            convergence = 0
        print(
            f'Generation {idx_iteration + 1}, Best Fitness: {gbest_fitness}, Konvergen: {convergence}')

        if convergence == MAX_CONVERGENCE:
            print(f'Convergence is reached = {MAX_CONVERGENCE}')
            is_break = True

        best_fitness_previous = gbest_fitness
        return is_break, best_fitness_previous, convergence

    def _standard_binarization_rule(self, agents):
        """
        Function untuk melakukan binarization rules terhadap continous values yang telah berada dalam rentang 0 sampai 1 hasil dari transfer function.
        Ada banyak macam binarization rules, namun function ini mengimplementasikan "Standard Binarization Rules" dari hasil penelitian:
            Haikal, V., & Suyanto, S. (2024, August). Binary Komodo Mlipir Algorithm for Feature Selection. In 2024 International Conference on Artificial Intelligence, Blockchain, Cloud Computing, and Data Analytics (ICoABCD) (pp. 255-260). IEEE.
        """
        TRANSFER_FUNCTION = self.optimizer['transfer_function']
        for idx_agent, agent in enumerate(agents):
            for j in range(self.N_FEATURES):
                # standard binarization rule
                if np.random.rand() <= TRANSFER_FUNCTION(agent[j]):
                    agents[idx_agent][j] = 1
                else:
                    agents[idx_agent][j] = 0
        return agents

    def _calculate_total_training_time_computation(self, start_time, end_time):
        return str(datetime.timedelta(seconds=end_time-start_time))
