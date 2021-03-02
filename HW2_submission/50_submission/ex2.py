import pysat
from pysat.formula import CNF
from pysat.solvers import Solver
import itertools
from copy import deepcopy
from pysat.formula import IDPool


ids = ['322212630', '322721283']


def solve_problem(input):
    num_police = input["police"]
    num_medics = input["medics"]
    answer = {}
    if num_police == 0 and num_medics == 0:
        c = solve_problem1(input)
        s = Solver()
        s.append_formula(c)
        for q in input["queries"]:
            if not s.solve(assumptions=[get_n(q[2], q[1], q[0][0], q[0][1])]):  # if unsatisfiable
                answer[q] = 'F'
                continue
            elif s.solve(assumptions=[-get_n(q[2], q[1], q[0][0], q[0][1])]):  # if negation is satisfiable
                answer[q] = '?'
                continue
            answer[q] = 'T'
        s.delete()
        return answer
    else:
        c = solve_problem2(input)
        s = Solver()
        s.append_formula(c)
        for q in input["queries"]:
            if q[2] != 'S' and q[2] != 'Q':
                if not s.solve(assumptions=[get_k(q[2], q[1], q[0][0], q[0][1])]):  # if unsatisfiable
                    answer[q] = 'F'
                    continue
                elif s.solve(assumptions=[-get_k(q[2], q[1], q[0][0], q[0][1])]):  # if negation is satisfiable
                    answer[q] = '?'
                    continue
                answer[q] = 'T'
            elif q[2] == 'S':
                a1 = s.solve(assumptions=[get_k(q[2], q[1], q[0][0], q[0][1], 1)])
                a2 = s.solve(assumptions=[get_k(q[2], q[1], q[0][0], q[0][1], 2)])
                a3 = s.solve(assumptions=[get_k(q[2], q[1], q[0][0], q[0][1], 3)])
                if (not a1) and (not a2) and (not a3):
                    answer[q] = 'F'
                    continue
                else:
                    lst = []
                    if a1:
                        lst.append(-get_k(q[2], q[1], q[0][0], q[0][1], 1))
                    if a2:
                        lst.append(-get_k(q[2], q[1], q[0][0], q[0][1], 2))
                    if a3:
                        lst.append(-get_k(q[2], q[1], q[0][0], q[0][1], 3))
                    if s.solve(assumptions=lst):
                        answer[q] = '?'
                        continue
                answer[q] = 'T'
            elif q[2] == 'Q':
                a1 = s.solve(assumptions=[get_k(q[2], q[1], q[0][0], q[0][1], 1)])
                a2 = s.solve(assumptions=[get_k(q[2], q[1], q[0][0], q[0][1], 2)])
                if (not a1) and (not a2):
                    answer[q] = 'F'
                    continue
                else:
                    lst = []
                    if a1:
                        lst.append(-get_k(q[2], q[1], q[0][0], q[0][1], 1))
                    if a2:
                        lst.append(-get_k(q[2], q[1], q[0][0], q[0][1], 2))
                    if s.solve(assumptions=lst):
                        answer[q] = '?'
                        continue
                answer[q] = 'T'
        s.delete()
        return answer

class v_id:
    vpool = IDPool()

    def __init__(self):
        pass

def get_n(condition, round, i, j):
    round = "0" + str(round) if len(str(round)) == 1 else str(round)
    i = "0" + str(i) if len(str(i)) == 1 else str(i)
    j = "0" + str(j) if len(str(j)) == 1 else str(j)
    if condition == 'H':
        condition = "1"
    elif condition == 'S':
        condition = "2"
    elif condition == 'Q':
        condition = "3"
    elif condition == 'I':
        condition = "4"
    elif condition == 'U':
        condition = "5"
    return v_id.vpool.id(int(condition + round + i + j))

def solve_problem1(input):
    num_rounds = len(input["observations"])
    observations = input["observations"]
    rows = len(observations[0])
    columns = len(observations[0][0])
    c = CNF()

    # init
    unpopulated = set()
    for round in range(num_rounds):
        for i in range(rows):
            for j in range(columns):
                condition = observations[round][i][j]
                if condition == "?":  # one condition only
                    c.extend([[-get_n("S", round, i, j), -get_n("H", round, i, j)],
                              [-get_n("S", round, i, j), -get_n("U", round, i, j)],
                              [-get_n("U", round, i, j), -get_n("H", round, i, j)],
                              [get_n("S", round, i, j), get_n("H", round, i, j), get_n("U", round, i, j)]])
                if condition == "S":
                    c.extend([[get_n("S", round, i, j)], [-get_n("H", round, i, j)], [-get_n("U", round, i, j)]])
                if condition == "H":
                    c.extend([[-get_n("S", round, i, j)], [get_n("H", round, i, j)], [-get_n("U", round, i, j)]])
                if condition == "U":
                    unpopulated.add((i, j))
                if round == 0:
                    if condition == "S":  # if S, stay S for 3 rounds
                        c.append([get_n("S", 1, i, j)])
                        c.append([get_n("S", 2, i, j)])
                        c.append([get_n("H", 3, i, j)])
                    elif condition == "?":
                        c.extend([[-get_n("S", 0, i, j), get_n("S", 1, i, j)],
                                  [-get_n("S", 0, i, j), get_n("S", 2, i, j)],
                                  [-get_n("S", 0, i, j), get_n("H", 3, i, j)]])

    # all unpopulated are unpopulated in all rounds
    for pair in unpopulated:
        for round in range(num_rounds):
            c.extend([[-get_n("S", round, pair[0], pair[1])], [-get_n("H", round, pair[0], pair[1])],
                      [get_n("U", round, pair[0], pair[1])]])

    # infect each round
    for round in range(num_rounds - 1):
        for i in range(rows):
            for j in range(columns):
                condition = observations[round][i][j]
                neighbors_unknown = []
                if condition == "H":
                    # infect if there's an S
                    if ((i - 1 >= 0 and observations[round][i - 1][j] == 'S') or
                            (i + 1 < rows and observations[round][i + 1][j] == 'S') or
                            (j - 1 >= 0 and observations[round][i][j - 1] == 'S') or
                            (j + 1 < columns and observations[round][i][j + 1] == 'S')):
                        c.extend([[get_n("S", round + 1, i, j)],
                                  [get_n("S", round + 2, i, j)],
                                  [get_n("S", round + 3, i, j)],
                                  [get_n("H", round + 4, i, j)]])
                        continue

                    # conditional infect if there's a ? (if ? is S)
                    else:
                        if i - 1 >= 0 and observations[round][i - 1][j] == '?':
                            c.extend([[-get_n("S", round, i - 1, j), get_n("S", round + 1, i, j)],
                                      [-get_n("S", round, i - 1, j), get_n("S", round + 2, i, j)],
                                      [-get_n("S", round, i - 1, j), get_n("S", round + 3, i, j)],
                                      [-get_n("S", round, i - 1, j), get_n("H", round + 4, i, j)]])
                            neighbors_unknown.append((i - 1, j))
                        if i + 1 < rows and observations[round][i + 1][j] == '?':
                            c.extend([[-get_n("S", round, i + 1, j), get_n("S", round + 1, i, j)],
                                      [-get_n("S", round, i + 1, j), get_n("S", round + 2, i, j)],
                                      [-get_n("S", round, i + 1, j), get_n("S", round + 3, i, j)],
                                      [-get_n("S", round, i + 1, j), get_n("H", round + 4, i, j)]])
                            neighbors_unknown.append((i + 1, j))
                        if j - 1 >= 0 and observations[round][i][j - 1] == '?':
                            c.extend([[-get_n("S", round, i, j - 1), get_n("S", round + 1, i, j)],
                                      [-get_n("S", round, i, j - 1), get_n("S", round + 2, i, j)],
                                      [-get_n("S", round, i, j - 1), get_n("S", round + 3, i, j)],
                                      [-get_n("S", round, i, j - 1), get_n("H", round + 4, i, j)]])
                            neighbors_unknown.append((i, j - 1))
                        if j + 1 < columns and observations[round][i][j + 1] == '?':
                            c.extend([[-get_n("S", round, i, j + 1), get_n("S", round + 1, i, j)],
                                      [-get_n("S", round, i, j + 1), get_n("S", round + 2, i, j)],
                                      [-get_n("S", round, i, j + 1), get_n("S", round + 3, i, j)],
                                      [-get_n("S", round, i, j + 1), get_n("H", round + 4, i, j)]])
                            neighbors_unknown.append((i, j + 1))

                    # if no one infected, stay H
                    l = [get_n("S", round, pair[0], pair[1]) for pair in neighbors_unknown]
                    l.append(get_n("H", round + 1, i, j))
                    c.append(l)

                elif condition == '?':
                    # conditional infect if there's an S (if current ? is H)
                    if ((i - 1 >= 0 and observations[round][i - 1][j] == 'S') or
                            (i + 1 < rows and observations[round][i + 1][j] == 'S') or
                            (j - 1 >= 0 and observations[round][i][j - 1] == 'S') or
                            (j + 1 < columns and observations[round][i][j + 1] == 'S')):
                        c.extend([[-get_n("H", round, i, j), get_n("S", round + 1, i, j)],
                                  [-get_n("H", round, i, j), get_n("S", round + 2, i, j)],
                                  [-get_n("H", round, i, j), get_n("S", round + 3, i, j)],
                                  [-get_n("H", round, i, j), get_n("H", round + 4, i, j)]])
                        continue

                    # conditional infect of there's a ? (if current ? is H and other ? is S)
                    else:
                        if i - 1 >= 0 and observations[round][i - 1][j] == '?':
                            c.extend(
                                [[-get_n("H", round, i, j), -get_n("S", round, i - 1, j), get_n("S", round + 1, i, j)],
                                 [-get_n("H", round, i, j), -get_n("S", round, i - 1, j), get_n("S", round + 2, i, j)],
                                 [-get_n("H", round, i, j), -get_n("S", round, i - 1, j), get_n("S", round + 3, i, j)],
                                 [-get_n("H", round, i, j), -get_n("S", round, i - 1, j), get_n("H", round + 4, i, j)]])
                            neighbors_unknown.append((i - 1, j))
                        if i + 1 < rows and observations[round][i + 1][j] == '?':
                            c.extend(
                                [[-get_n("H", round, i, j), -get_n("S", round, i + 1, j), get_n("S", round + 1, i, j)],
                                 [-get_n("H", round, i, j), -get_n("S", round, i + 1, j), get_n("S", round + 2, i, j)],
                                 [-get_n("H", round, i, j), -get_n("S", round, i + 1, j), get_n("S", round + 3, i, j)],
                                 [-get_n("H", round, i, j), -get_n("S", round, i + 1, j), get_n("H", round + 4, i, j)]])
                            neighbors_unknown.append((i + 1, j))
                        if j - 1 >= 0 and observations[round][i][j - 1] == '?':
                            c.extend(
                                [[-get_n("H", round, i, j), -get_n("S", round, i, j - 1), get_n("S", round + 1, i, j)],
                                 [-get_n("H", round, i, j), -get_n("S", round, i, j - 1), get_n("S", round + 2, i, j)],
                                 [-get_n("H", round, i, j), -get_n("S", round, i, j - 1), get_n("S", round + 3, i, j)],
                                 [-get_n("H", round, i, j), -get_n("S", round, i, j - 1), get_n("H", round + 4, i, j)]])
                            neighbors_unknown.append((i, j - 1))
                        if j + 1 < columns and observations[round][i][j + 1] == '?':
                            c.extend(
                                [[-get_n("H", round, i, j), -get_n("S", round, i, j + 1), get_n("S", round + 1, i, j)],
                                 [-get_n("H", round, i, j), -get_n("S", round, i, j + 1), get_n("S", round + 2, i, j)],
                                 [-get_n("H", round, i, j), -get_n("S", round, i, j + 1), get_n("S", round + 3, i, j)],
                                 [-get_n("H", round, i, j), -get_n("S", round, i, j + 1), get_n("H", round + 4, i, j)]])
                            neighbors_unknown.append((i, j + 1))
                    # if no one infected, stay H (if ? is H)
                    l = [get_n("S", round, pair[0], pair[1]) for pair in neighbors_unknown]
                    l.append(-get_n("H", round, i, j))
                    l.append(get_n("H", round + 1, i, j))
                    c.append(l)
        for i in range(rows):
            for j in range(columns):
                condition = observations[round][i][j]
                if condition == '?':
                    c.extend([[-get_n("U", round, i, j), get_n("U", round + 1, i, j)],
                              [-get_n("U", round + 1, i, j), get_n("U", round, i, j)]])
    return c


def get_k(condition, round, i, j, time=-1):
    round = "0" + str(round) if len(str(round)) == 1 else str(round)
    i = "0" + str(i) if len(str(i)) == 1 else str(i)
    j = "0" + str(j) if len(str(j)) == 1 else str(j)
    if time == -1:
        if condition == 'H':
            condition = "1"
        elif condition == 'I':
            condition = "4"
        elif condition == 'U':
            condition = "5"
        return v_id.vpool.id(int(condition + round + i + j))
    if condition == 'S':
        condition = "2"
    elif condition == 'Q':
        condition = "3"
    return v_id.vpool.id(int(condition + round + i + j + str(time)))


def solve_problem2(input):
    num_rounds = len(input["observations"])
    observations = input["observations"]
    num_police = input["police"]
    num_medics = input["medics"]
    rows = len(observations[0])
    columns = len(observations[0][0])
    c = CNF()

    # init
    unpopulated = set()
    for round in range(num_rounds):
        for i in range(rows):
            for j in range(columns):
                condition = observations[round][i][j]
                if condition == "?":  # one condition only
                    c.extend([[-get_k("H", round, i, j), -get_k("I", round, i, j)],
                              [-get_k("H", round, i, j), -get_k("U", round, i, j)],
                              [-get_k("H", round, i, j), -get_k("S", round, i, j, 1)],
                              [-get_k("H", round, i, j), -get_k("S", round, i, j, 2)],
                              [-get_k("H", round, i, j), -get_k("S", round, i, j, 3)],
                              [-get_k("H", round, i, j), -get_k("Q", round, i, j, 1)],
                              [-get_k("H", round, i, j), -get_k("Q", round, i, j, 2)],
                              [-get_k("I", round, i, j), -get_k("U", round, i, j)],
                              [-get_k("I", round, i, j), -get_k("S", round, i, j, 1)],
                              [-get_k("I", round, i, j), -get_k("S", round, i, j, 2)],
                              [-get_k("I", round, i, j), -get_k("S", round, i, j, 3)],
                              [-get_k("I", round, i, j), -get_k("Q", round, i, j, 1)],
                              [-get_k("I", round, i, j), -get_k("Q", round, i, j, 2)],
                              [-get_k("U", round, i, j), -get_k("S", round, i, j, 1)],
                              [-get_k("U", round, i, j), -get_k("S", round, i, j, 2)],
                              [-get_k("U", round, i, j), -get_k("S", round, i, j, 3)],
                              [-get_k("U", round, i, j), -get_k("Q", round, i, j, 1)],
                              [-get_k("U", round, i, j), -get_k("Q", round, i, j, 2)],
                              [-get_k("Q", round, i, j, 1), -get_k("S", round, i, j, 1)],
                              [-get_k("Q", round, i, j, 1), -get_k("S", round, i, j, 2)],
                              [-get_k("Q", round, i, j, 1), -get_k("S", round, i, j, 3)],
                              [-get_k("Q", round, i, j, 1), -get_k("Q", round, i, j, 2)],
                              [-get_k("Q", round, i, j, 2), -get_k("S", round, i, j, 1)],
                              [-get_k("Q", round, i, j, 2), -get_k("S", round, i, j, 2)],
                              [-get_k("Q", round, i, j, 2), -get_k("S", round, i, j, 3)],
                              [-get_k("S", round, i, j, 1), -get_k("S", round, i, j, 2)],
                              [-get_k("S", round, i, j, 1), -get_k("S", round, i, j, 3)],
                              [-get_k("S", round, i, j, 2), -get_k("S", round, i, j, 3)],
                              [get_k("H", round, i, j), get_k("I", round, i, j), get_k("U", round, i, j),
                               get_k("Q", round, i, j, 1), get_k("Q", round, i, j, 2),
                               get_k("S", round, i, j, 1), get_k("S", round, i, j, 2), get_k("S", round, i, j, 3)]])
                if condition == "S":
                    c.extend([[-get_k("H", round, i, j)], [-get_k("I", round, i, j)], [-get_k("U", round, i, j)],
                              [-get_k("Q", round, i, j, 1)], [-get_k("Q", round, i, j, 2)],
                              [get_k("S", round, i, j, 1), get_k("S", round, i, j, 2), get_k("S", round, i, j, 3)]])
                if condition == "H":
                    c.extend([[get_k("H", round, i, j)], [-get_k("I", round, i, j)], [-get_k("U", round, i, j)],
                              [-get_k("Q", round, i, j, 1)], [-get_k("Q", round, i, j, 2)],
                              [-get_k("S", round, i, j, 1)], [-get_k("S", round, i, j, 2)],
                              [-get_k("S", round, i, j, 3)]])
                if condition == "Q":
                    c.extend([[-get_k("H", round, i, j)], [-get_k("I", round, i, j)], [-get_k("U", round, i, j)],
                              [get_k("Q", round, i, j, 1), get_k("Q", round, i, j, 2)],
                              [-get_k("S", round, i, j, 1)], [-get_k("S", round, i, j, 2)],
                              [-get_k("S", round, i, j, 3)]])
                if condition == "I":
                    c.extend([[-get_k("H", round, i, j)], [get_k("I", round, i, j)], [-get_k("U", round, i, j)],
                              [-get_k("Q", round, i, j, 1)], [-get_k("Q", round, i, j, 2)],
                              [-get_k("S", round, i, j, 1)], [-get_k("S", round, i, j, 2)],
                              [-get_k("S", round, i, j, 3)]])
                if condition == "U":
                    unpopulated.add((i, j))
                if round == 0:
                    if condition == '?':
                        c.extend(
                            [[get_k("S", 0, i, j, 3), get_k("H", 0, i, j), get_k("U", 0, i, j)],
                             [-get_k("S", 0, i, j, 2)]
                                , [-get_k("S", 0, i, j, 1)], [-get_k("Q", 0, i, j, 1)], [-get_k("Q", 0, i, j, 2)],
                             [-get_k("I", 0, i, j)]])
                    if condition == "S":  # if S, stay S for 3 rounds
                        c.append([get_k("S", 0, i, j, 3)])

    # all unpopulated are unpopulated in all rounds
    for pair in unpopulated:
        for round in range(num_rounds):
            c.extend([[-get_k("H", round, pair[0], pair[1])], [-get_k("I", round, pair[0], pair[1])],
                      [get_k("U", round, pair[0], pair[1])],
                      [-get_k("Q", round, pair[0], pair[1], 1)], [-get_k("Q", round, pair[0], pair[1], 2)],
                      [-get_k("S", round, pair[0], pair[1], 1)], [-get_k("S", round, pair[0], pair[1], 2)],
                      [-get_k("S", round, pair[0], pair[1], 3)]])

    index = 1
    k = v_id.vpool.id(1)  # current action
    for round in range(num_rounds - 1):
        round_actions = []
        for a in all_actions(observations[round], num_police, num_medics):
            affected = []
            cur_map = [list(r) for r in observations[round]]
            stop = False
            l = []  # consists of preconditions and effects of current action
            num_Q = 0
            num_I = 0
            for pair in a:
                if observations[round + 1][pair[1][0]][pair[1][1]] != '?' and pair[0] != \
                        observations[round + 1][pair[1][0]][pair[1][1]]:
                    stop = True
                    break
                affected.append(pair[1])
                cur_map[pair[1][0]][pair[1][1]] = pair[0]  # updated map if action occurs, used for infection
                if pair[0] == 'Q':  # precondition + effects
                    l.append(
                        [-k, get_k("S", round, pair[1][0], pair[1][1], 1), get_k("S", round, pair[1][0], pair[1][1], 2),
                         get_k("S", round, pair[1][0], pair[1][1], 3)])
                    l.append([-k, get_k("Q", round + 1, pair[1][0], pair[1][1], 2)])
                    num_Q += 1
                if pair[0] == 'I':
                    l.append([-k, get_k("H", round, pair[1][0], pair[1][1])])
                    l.append([-k, get_k("I", round + 1, pair[1][0], pair[1][1])])
                    num_I += 1
            if stop == True:
                index += 1
                k = v_id.vpool.id(index)
                continue

            round_actions.append(k)
            c.extend(l)

            # if not all police or medics were used, then ? cant be H or S respectively
            if num_I < num_medics:
                for i in range(rows):
                    for j in range(columns):
                        if cur_map[i][j] == '?':
                            c.append([-k, -get_k("H", round, i, j)])

            if num_Q < num_police:
                for i in range(rows):
                    for j in range(columns):
                        if cur_map[i][j] == '?':
                            c.extend([[-k, -get_k("S", round, i, j, 1)],
                                      [-k, -get_k("S", round, i, j, 2)],
                                      [-k, -get_k("S", round, i, j, 3)]])

            for i in range(rows):
                for j in range(columns):
                    if (i, j) in affected:
                        continue
                    else:
                        condition = cur_map[i][j]

                    # update S (depends on the chosen action)
                    if condition == 'S':
                        c.extend([[-k, -get_k("S", round, i, j, 3), get_k("S", round + 1, i, j, 2)],
                                  [-k, -get_k("S", round, i, j, 2), get_k("S", round + 1, i, j, 1)],
                                  [-k, -get_k("S", round, i, j, 1), get_k("H", round + 1, i, j)]])
                        continue

                    if condition == '?':
                        c.extend([[-k, -get_k("S", round, i, j, 3), get_k("S", round + 1, i, j, 2)],
                                  [-k, -get_k("S", round, i, j, 2), get_k("S", round + 1, i, j, 1)],
                                  [-k, -get_k("S", round, i, j, 1), get_k("H", round + 1, i, j)]])

                    # conditional infection
                    neighbors_unknown = []
                    if condition == "H":
                        # infect if there's an S
                        if ((i - 1 >= 0 and cur_map[i - 1][j] == 'S') or
                                (i + 1 < rows and cur_map[i + 1][j] == 'S') or
                                (j - 1 >= 0 and cur_map[i][j - 1] == 'S') or
                                (j + 1 < columns and cur_map[i][j + 1] == 'S')):
                            c.extend([[-k, get_k("S", round + 1, i, j, 3)]])
                            continue

                        # conditional infect if there's a ? (if ? is S)
                        else:
                            if i - 1 >= 0 and cur_map[i - 1][j] == '?':
                                c.extend([[-k, -get_k("S", round, i - 1, j, 1), get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i - 1, j, 2), get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i - 1, j, 3), get_k("S", round + 1, i, j, 3)]])
                                neighbors_unknown.append((i - 1, j))
                            if i + 1 < rows and cur_map[i + 1][j] == '?':
                                c.extend([[-k, -get_k("S", round, i + 1, j, 1), get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i + 1, j, 2), get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i + 1, j, 3), get_k("S", round + 1, i, j, 3)]])
                                neighbors_unknown.append((i + 1, j))
                            if j - 1 >= 0 and cur_map[i][j - 1] == '?':
                                c.extend([[-k, -get_k("S", round, i, j - 1, 1), get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i, j - 1, 2), get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i, j - 1, 3), get_k("S", round + 1, i, j, 3)]])
                                neighbors_unknown.append((i, j - 1))
                            if j + 1 < columns and cur_map[i][j + 1] == '?':
                                c.extend([[-k, -get_k("S", round, i, j + 1, 1), get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i, j + 1, 2), get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i, j + 1, 3), get_k("S", round + 1, i, j, 3)]])
                                neighbors_unknown.append((i, j + 1))

                        # if no one infected, stay H
                        lst = [get_k("S", round, n[0], n[1], 1) for n in neighbors_unknown] + \
                              [get_k("S", round, n[0], n[1], 2) for n in neighbors_unknown] + \
                              [get_k("S", round, n[0], n[1], 3) for n in neighbors_unknown]
                        lst.append(get_k("H", round + 1, i, j))
                        lst.append(-k)
                        c.append(lst)

                    elif condition == '?':
                        # conditional infect if there's an S (if current ? is H)
                        if ((i - 1 >= 0 and cur_map[i - 1][j] == 'S') or
                                (i + 1 < rows and cur_map[i + 1][j] == 'S') or
                                (j - 1 >= 0 and cur_map[i][j - 1] == 'S') or
                                (j + 1 < columns and cur_map[i][j + 1] == 'S')):
                            c.extend([[-k, -get_k("H", round, i, j), get_k("S", round + 1, i, j, 3)]])
                            continue

                        # conditional infect of there's a ? (if current ? is H and other ? is S)
                        else:
                            if i - 1 >= 0 and cur_map[i - 1][j] == '?':
                                c.extend([[-k, -get_k("S", round, i - 1, j, 1), -get_k("H", round, i, j),
                                           get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i - 1, j, 2), -get_k("H", round, i, j),
                                           get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i - 1, j, 3), -get_k("H", round, i, j),
                                           get_k("S", round + 1, i, j, 3)]])
                                neighbors_unknown.append((i - 1, j))
                            if i + 1 < rows and cur_map[i + 1][j] == '?':
                                c.extend([[-k, -get_k("S", round, i + 1, j, 1), -get_k("H", round, i, j),
                                           get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i + 1, j, 2), -get_k("H", round, i, j),
                                           get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i + 1, j, 3), -get_k("H", round, i, j),
                                           get_k("S", round + 1, i, j, 3)]])
                                neighbors_unknown.append((i + 1, j))
                            if j - 1 >= 0 and cur_map[i][j - 1] == '?':
                                c.extend([[-k, -get_k("S", round, i, j - 1, 1), -get_k("H", round, i, j),
                                           get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i, j - 1, 2), -get_k("H", round, i, j),
                                           get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i, j - 1, 3), -get_k("H", round, i, j),
                                           get_k("S", round + 1, i, j, 3)]])
                                neighbors_unknown.append((i, j - 1))
                            if j + 1 < columns and cur_map[i][j + 1] == '?':
                                c.extend([[-k, -get_k("S", round, i, j + 1, 1), -get_k("H", round, i, j),
                                           get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i, j + 1, 2), -get_k("H", round, i, j),
                                           get_k("S", round + 1, i, j, 3)],
                                          [-k, -get_k("S", round, i, j + 1, 3), -get_k("H", round, i, j),
                                           get_k("S", round + 1, i, j, 3)]])
                                neighbors_unknown.append((i, j + 1))

                        # if no one infected, stay H (if ? is H)
                        lst = [get_k("S", round, n[0], n[1], 1) for n in neighbors_unknown] + \
                              [get_k("S", round, n[0], n[1], 2) for n in neighbors_unknown] + \
                              [get_k("S", round, n[0], n[1], 3) for n in neighbors_unknown]
                        lst.append(get_k("H", round + 1, i, j))
                        lst.append(-get_k("H", round, i, j))
                        lst.append(-k)
                        c.append(lst)

            index += 1
            k = v_id.vpool.id(index)

        lst = []
        for r in round_actions:
            lst.append(r)
            for t in round_actions:
                if r > t:
                    c.append([-r, -t])
        c.append(lst)

        for i in range(rows):
            for j in range(columns):
                condition = observations[round][i][j]
                if condition == 'Q':
                    c.extend([[-get_k("Q", round, i, j, 1), get_k("H", round + 1, i, j)],
                              [-get_k("Q", round, i, j, 2), get_k("Q", round + 1, i, j, 1)]])
                if condition == 'I':
                    c.append([get_k("I", round + 1, i, j)])
                if condition == '?':
                    c.extend([[-get_k("I", round, i, j), get_k("I", round + 1, i, j)],
                              [-get_k("Q", round, i, j, 1), get_k("H", round + 1, i, j)],
                              [-get_k("Q", round, i, j, 2), get_k("Q", round + 1, i, j, 1)],
                              [-get_k("U", round, i, j), get_k("U", round + 1, i, j)],
                              [-get_k("U", round + 1, i, j), get_k("U", round, i, j)]])
    return c


def all_actions(map, num_police, num_medics):
    sick_list = []  # coordinates of all sick
    healthy_list = []  # coordinates of all healthy
    unknown_list = []

    for i, line in enumerate(map):
        for j, x in enumerate(line):
            if x == 'S':
                sick_list.append((i, j))
            elif x == 'H':
                healthy_list.append((i, j))
            elif x == '?':
                unknown_list.append((i, j))
    actions_list = []
    for new_sicks in powerset(unknown_list):
        remainder = list(set(unknown_list) - set(new_sicks))
        for new_healthy in powerset(remainder):
            sick_list_new = sick_list + list(new_sicks)
            healthy_list_new = healthy_list + list(new_healthy)
            if num_police > len(sick_list_new):
                sick_iter = [sick_list_new]
            else:
                sick_iter = itertools.combinations(sick_list_new, num_police)
            if num_medics > len(healthy_list_new):
                healthy_iter = [healthy_list_new]
            else:
                healthy_iter = itertools.combinations(healthy_list_new, num_medics)

            healthy_iter_save = deepcopy(healthy_iter)
            for s in sick_iter:
                for h in healthy_iter:
                    action = []
                    for c in s:
                        action.append(('Q', c))
                    for c in h:
                        action.append(('I', c))
                    actions_list.append(tuple(action))
                healthy_iter = deepcopy(healthy_iter_save)

    return list(set(actions_list))


def powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s) + 1))





