ids = ["204241202", "204411730"]

'''
List of states:
H- healthy
U- unpopulated
S1- sick 1st day
S2- sick 2st day
S3- sick 3st day
I- immune
Q1- Quarantined 1st day
Q2- Quarantined 2st day
?- Unknown

List of actions:
vaccinate
quarantine
noop
?
'''

'''
steps:
Go through every map and try to infer the actions made on each step
Write clauses for each time
Input to solver
'''

import numpy as np
from pysat.formula import CNF
from pysat.solvers import Solver

def solve_problem(input):
    observation = input['observations']
    medics = input['medics']
    police = input['police']
    queries = input['queries']

    observation = np.array(observation)
    [length, row, col] = observation.shape

    return check_queries(observation, length, row, col, queries, medics, police)

def check_queries(observations, length, row, col, queries, medics, police):
    answer = {}
    M = 8 # number of maps (Healthy, Sick, D(sick2), F(sick3), Quarentined, W(quarentined2), Immune, Unpopulated)
    A = 4 # number of actions (vaccinate, quarentine, noop, spread)
    for query in queries:
        # Create new CNF formula
        cnf = CNF()

        # ================= Initial condition clauses =================
        for i in range(row):
            for j in range(col):
                ind = -1
                if (observations[0, i, j] == "H"):
                    ind = 0
                if (observations[0, i, j] == "S"):
                    ind = 1
                if (observations[0, i, j] == "U"):
                    ind = 7
                if (ind == 0 or ind == 1 or ind == 7):
                    for m in range(M):
                        clause = [-(m * row * col + i * row + j + 1)]
                        if(m==ind):
                            clause = [(m * row * col + i * row + j + 1)]
                        cnf.append(clause)
                else:
                    continue

        # ======================= Goal clauses ========================
        if (query[2] == "H"):
            cnf.append([((0 * row * col + query[0][0] * row + query[0][1]) + query[1] * M * row * col + 1)])
        if (query[2] == "S"):
            cnf.append([((1 * row * col + query[0][0] * row + query[0][1]) + query[1] * M * row * col + 1)])
        if (query[2] == "Q"):
            cnf.append([((5 * row * col + query[0][0] * row + query[0][1]) + query[1] * M * row * col + 1)])
        if (query[2] == "I"):
            cnf.append([((6 * row * col + query[0][0] * row + query[0][1]) + query[1] * M * row * col + 1)])
        if (query[2] == "U"):
            cnf.append([((7 * row * col + query[0][0] * row + query[0][1]) + query[1] * M * row * col + 1)])

        # =============== Action Precondition clauses =================
        #actions = find_actions(observations, length, row, col)
        for time in range(length - 1):
            for i in range(row):
                for j in range(col):
                    # Precondition for vaccinate
                    cnf.append([-((M * length * row * col) + A * (time * row * col) + 0 * row * col + i * row + j + 1),
                                ((0 * row * col + i * row + j) + time * M * row * col + 1)])

                    # Precondition for quarentine
                    cnf.append([-((M * length * row * col) + A * (time * row * col) + 1 * row * col + i * row + j + 1),
                                ((1 * row * col + i * row + j) + time * M * row * col + 1)])
                    cnf.append([-((M * length * row * col) + A * (time * row * col) + 1 * row * col + i * row + j + 1),
                                ((2 * row * col + i * row + j) + time * M * row * col + 1)])
                    cnf.append([-((M * length * row * col) + A * (time * row * col) + 1 * row * col + i * row + j + 1),
                                ((3 * row * col + i * row + j) + time * M * row * col + 1)])

                    # Precondition for spread
                    cnf.append([-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                ((1 * row * col + i * row + j) + time * M * row * col + 1)])
                    cnf.append([-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                ((2 * row * col + i * row + j) + time * M * row * col + 1)])
                    cnf.append([-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                ((3 * row * col + i * row + j) + time * M * row * col + 1)])
        # =============== Actions Interference clauses ================
        for time in range(length - 1):
            for i in range(row):
                for j in range(col):
                    cnf.append([-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                -((M * length * row * col) + A * (time * row * col) + 0 * row * col + i * row + j + 1)])
                    cnf.append([-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                -((M * length * row * col) + A * (time * row * col) + 1 * row * col + i * row + j + 1)])
                    cnf.append([-((M * length * row * col) + A * (time * row * col) + 0 * row * col + i * row + j + 1),
                                -((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1)])
                    cnf.append([-((M * length * row * col) + A * (time * row * col) + 1 * row * col + i * row + j + 1),
                                -((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1)])
                    cnf.append([-((M * length * row * col) + A * (time * row * col) + 1 * row * col + i * row + j + 1),
                                -((M * length * row * col) + A * (time * row * col) + 0 * row * col + i * row + j + 1)])
                    cnf.append([-((M * length * row * col) + A * (time * row * col) + 0 * row * col + i * row + j + 1),
                                -((M * length * row * col) + A * (time * row * col) + 1 * row * col + i * row + j + 1)])

                    case = check_borders(i, j, row, col)
                    if (case == 0):
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i + 1) * row + (j) + 1)])
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j + 1) + 1)])
                    if (case == 1):
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j - 1) + 1)])
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j + 1) + 1)])
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i + 1) * row + (j) + 1)])
                    if (case == 2):
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i - 1) * row + (j) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i + 1) * row + (j) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j + 1) + 1)])
                    if (case == 3):
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i - 1) * row + (j) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j - 1) + 1)])
                    if (case == 4):
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j - 1) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j + 1) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i - 1) * row + (j) + 1)])
                    if (case == 5):
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                             ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i - 1) * row + (j) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                             ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i + 1) * row + (j) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                             ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j - 1) + 1)])
                    if (case == 6):
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                             ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j + 1) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                             ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i - 1) * row + (j) + 1)])
                    if (case == 7):
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j - 1) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i + 1) * row + (j) + 1)])
                    if (case == 8):
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j + 1) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j - 1) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i + 1) * row + (j) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i - 1) * row + (j) + 1)])

                    if (case == 0):
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i + 1) * row + (j) + 1)])
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i) * row + (j + 1) + 1)])
                    if (case == 1):
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i) * row + (j - 1) + 1)])
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i) * row + (j + 1) + 1)])
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i + 1) * row + (j) + 1)])
                    if (case == 2):
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i - 1) * row + (j) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i + 1) * row + (j) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i) * row + (j + 1) + 1)])
                    if (case == 3):
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i - 1) * row + (j) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i) * row + (j - 1) + 1)])
                    if (case == 4):
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i) * row + (j - 1) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i) * row + (j + 1) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i - 1) * row + (j) + 1)])
                    if (case == 5):
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                             ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i - 1) * row + (j) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                             ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i + 1) * row + (j) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                             ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i) * row + (j - 1) + 1)])
                    if (case == 6):
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                             ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i) * row + (j + 1) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                             ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i - 1) * row + (j) + 1)])
                    if (case == 7):
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i) * row + (j - 1) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i + 1) * row + (j) + 1)])
                    if (case == 8):
                        cnf.append([-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i) * row + (j + 1) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i) * row + (j - 1) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i + 1) * row + (j) + 1)])
                        cnf.append(
                            [-((M * length * row * col) + A * (time * row * col) + 3 * row * col + i * row + j + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 2 * row * col + (i - 1) * row + (j) + 1)])
        # ================== Fact achievement clauses =================
        for time in range(length - 1):
            for i in range(row):
                for j in range(col):
                    # H1 -> noop(H)0
                    cnf.append([-((0 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                             ((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1)])
                    # D1 -> noop(S)0
                    cnf.append([-((2 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                            ((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1)])
                    # F1 -> noop(D)0
                    cnf.append([-((3 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                            ((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1)])
                    # Q1 -> quarentine(S)0
                    cnf.append([-((4 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                            ((M * length * row * col) + A * (time * row * col) + 1 * row * col + i * row + j + 1)])
                    # W1 -> noop(Q)0
                    cnf.append([-((5 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                            ((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1)])
                    # I1 -> noop(I)0 \/ vaccinate(H)0
                    cnf.append([-((6 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                            ((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1),
                            ((M * length * row * col) + A * (time * row * col) + 1 * row * col + i * row + j + 1)])
                    # U1 -> noop(U)0
                    cnf.append([-((7 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                            ((M * length * row * col) + A * (time * row * col) + 2 * row * col + i * row + j + 1)])
                    # S1 -> spread(H)0
                    case = check_borders(i, j, row, col)
                    if(case == 0):
                        cnf.append([-((1 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i + 1) * row + (j) + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j + 1) + 1)])
                    if (case == 1):
                        cnf.append([-((1 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j - 1) + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j + 1) + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i + 1) * row + (j) + 1)])
                    if (case == 2):
                        cnf.append([-((1 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i - 1) * row + (j) + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i + 1) * row + (j) + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j + 1) + 1)])
                    if (case == 3):
                        cnf.append([-((1 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i - 1) * row + (j) + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j - 1) + 1)])
                    if (case == 4):
                        cnf.append([-((1 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j - 1) + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j + 1) + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i - 1) * row + (j) + 1)])
                    if (case == 5):
                        cnf.append(
                            [-((1 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                             ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i - 1) * row + (j) + 1),
                             ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i + 1) * row + (j) + 1),
                             ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j - 1) + 1)])
                    if (case == 6):
                        cnf.append(
                            [-((1 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                             ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j + 1) + 1),
                             ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i - 1) * row + (j) + 1)])
                    if (case == 7):
                        cnf.append([-((1 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j - 1) + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i + 1) * row + (j) + 1)])
                    if (case == 8):
                        cnf.append([-((1 * row * col + i * row + j) + (time + 1) * M * row * col + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j + 1) + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i) * row + (j - 1) + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i + 1) * row + (j) + 1),
                                    ((M * length * row * col) + A * (time * row * col) + 3 * row * col + (i - 1) * row + (j) + 1)])

        s = Solver(bootstrap_with=cnf.clauses)
        answer[query] = s.solve()
        if(answer[query] == True):
            answer[query] = "T"
        if (answer[query] == False):
            answer[query] = "F"
        if (answer[query] == None):
            answer[query] = "?"
    return answer

# ================= actions inference functions =================
def healty_infer(pt):
    if(pt == "H"):
        return "noop"
    if(pt == "S"):
        return "noop"
    if(pt == "I"):
        return "vaccinate"
    if(pt == "?"):
        return "?"

    return "noop"

def sick_infer(pt, pt_next):
    if (pt == "S" and pt_next == "D"):
        return "noop"
    if (pt == "S" and pt_next == "Q"):
        return "quarentine"
    if (pt == "D" and pt_next == "F"):
        return "noop"
    if (pt == "D" and pt_next == "Q"):
        return "quarentine"
    if (pt == "F" and pt_next == "H"):
        return "noop"
    if (pt == "F" and pt_next == "Q"):
        return "quarentine"
    if (pt_next == "?"):
        return "?"

    return "noop"

def check_borders(i, j, row, col):
    if(i==0 and j == 0):
        return 0
    if (i == 0 and j < col - 1):
        return 1
    if (j == 0 and i < row - 1):
        return 2
    if (i == row - 1 and j == col - 1):
        return 3
    if (i == row - 1 and j > 0):
        return 4
    if (j == col - 1 and i > 0):
        return 5
    if (i == row - 1 and j == 0):
        return 6
    if (j == col - 1 and i == 0):
        return 7
    return 8
'''
def find_actions(observations, length, row, col):
    observations = np.array(observations)

    # Create the map of actions of size (number of actions x time-1 x map size)
    a = np.zeros([4 * (length-1), row, col])

    # Iterate over the maps and infer the actions made on each time
    for time in range(length - 1): # for each map
        for i in range(row):
            for j in range(col):
                # Infer actions assuming pt==healthy
                if(observations[time + 1, i, j] == "H"):
                    action_type = healty_infer(observations[time, i, j])

                # Infer actions assuming pt==sick
                if (observations[time + 1, i, j] == "S" or
                        observations[time + 1, i, j] == "D" or
                        observations[time + 1, i, j] == "F" or
                        observations[time + 1, i, j] == "S"):
                    action_type = sick_infer(observations[time, i, j], observations[time + 1, i, j])

                # Infer actions assuming pt==quarentined
                if (observations[time + 1, i, j] == "Q" or
                        observations[time + 1, i, j] == "W"):
                    action_type = "noop"

                # Infer actions assuming pt==immune
                if (observations[time + 1, i, j] == "I"):
                    action_type = "noop"

                # Infer actions assuming pt==unpopulated
                if (observations[time + 1, i, j] == "U"):
                    action_type = "noop"

                # Infer actions assuming pt==unknown
                if (observations[time + 1, i, j] == "?"):
                    action_type = "?"

                # Update actions map
                if (action_type == "vaccinate"):
                    a[0 + 4*time, i, j] = 1
                if (action_type == "quarentine"):
                    a[1 + 4*time, i, j] = 1
                if (action_type == "noop"):
                    a[2 + 4*time, i, j] = 1
                if (action_type == "?"):
                    a[3 + 4*time, i, j] = 1
    return a'''