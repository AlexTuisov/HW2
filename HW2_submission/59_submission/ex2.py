#!/usr/bin/python
# coding=utf-8
"""
Author:  moshed
Created on 21/12/2020

"""
from pysat.solvers import Solver
from pysat.solvers import Glucose3

ids = ["311395834", "314981259"]
F, T = False, True
status_map = {'U': 0, 'H': 1, 'S': 2, 'I': 3, 'Q': 4, '?': 5, 'SN': 6, 'R': 7, 'LQ': 8, 'EQ': 9, 'VAC': 10}


# translator: '-'9XXXX <-> 'not' (9,(i,j), t , status) 9-> to keep leading zeros
def int_plus(int_list, isNot=False):
    concat = '9' if not isNot else '-9'
    for x in int_list:
        concat += str(x)
    return int(concat)


def linearity_constraints(objs_count, row_count, col_count):
    clauses = []
    # res = list(itertools.combinations(test_dict, 2)) - check performance
    couples = [(x, y) for idx, x in enumerate(list(status_map)[:6]) for y in (list(status_map)[:6])[idx + 1:]]
    for t in range(objs_count):
        for i in range(row_count):
            for j in range(col_count):
                for c in couples:
                    clauses.append([int_plus([i, j, t, status_map[c[0]]], isNot=True),
                                    int_plus([i, j, t, status_map[c[1]]], isNot=True)])
    return clauses


def clauses_parse(phrase, predicates):
    clauses = []
    and_split = phrase.split(' ∧ ')
    for a_n in and_split:
        temp = []
        or_split = a_n.replace('(', '').replace(')', '').split(' ∨ ')
        for o_r in or_split:
            if o_r.startswith('¬'):
                temp.append(-predicates[o_r[1]])
            else:
                temp.append(predicates[o_r[0]])
        clauses.append(temp)
    return clauses


def R_Implication(i, j, t):
    pysat_clauses = []
    if t < 3:
        pysat_clauses.append([int_plus([i, j, t, status_map['R']], isNot=True)])
    else:
        predicates = {
            'a': int_plus([i, j, t, status_map['R']]),
            'b': int_plus([i, j, t - 1, status_map['S']]),
            'c': int_plus([i, j, t - 2, status_map['S']]),
            'd': int_plus([i, j, t - 3, status_map['S']])
        }
        # a <-> ( b && c && d)
        pysat_clauses += clauses_parse('(¬a ∨ b) ∧ (¬a ∨ c) ∧ (¬a ∨ d) ∧ (a ∨ ¬b ∨ ¬c ∨ ¬d)', predicates)
    return pysat_clauses


def SN_Implication(i, j, t, S_Neighbors):
    pysat_clauses = []
    S_Neighbors_count = len(S_Neighbors[t][i][j])
    predicates = {
        'a': int_plus([i, j, t, status_map['SN']]),
        'b': S_Neighbors[t][i][j][0],
        'c': S_Neighbors[t][i][j][1],
    }
    if S_Neighbors_count == 2:
        # a <-> ( b || c)
        pysat_clauses += clauses_parse('(¬a ∨ b ∨ c) ∧ (a ∨ ¬b) ∧ (a ∨ ¬c)', predicates)

    if S_Neighbors_count == 3:
        predicates['d'] = S_Neighbors[t][i][j][2]
        # a <-> ( b || c || d)
        pysat_clauses += clauses_parse('(¬a ∨ b ∨ c ∨ d) ∧ (a ∨ ¬b) ∧ (a ∨ ¬c) ∧ (a ∨ ¬d)', predicates)

    if S_Neighbors_count == 4:
        predicates['d'] = S_Neighbors[t][i][j][2]
        predicates['e'] = S_Neighbors[t][i][j][3]
        # a <-> ( b || c || d || e)
        pysat_clauses += clauses_parse('(¬a ∨ b ∨ c ∨ d ∨ e) ∧ (a ∨ ¬b) ∧ (a ∨ ¬c) ∧ (a ∨ ¬d) ∧ (a ∨ ¬e)', predicates)

    return pysat_clauses


def U_Implication(i, j, t):
    pysat_clauses = []
    predicates = {
        'a': int_plus([i, j, t, status_map['H']]),
        'b': int_plus([i, j, t - 1, status_map['H']]),
    }
    # a <-> b
    pysat_clauses.append([predicates['a']])
    pysat_clauses += clauses_parse('(¬a ∨ b) ∧ (a ∨ ¬b)', predicates)
    return pysat_clauses


def H_Implication(i, j, t, S_Neighbors):
    pysat_clauses = []
    predicates = {
        'a': int_plus([i, j, t, status_map['H']]),
        'b': int_plus([i, j, t - 1, status_map['H']]),
        'c': int_plus([i, j, t - 1, status_map['SN']]),
        'd': int_plus([i, j, t, status_map['R']])
    }
    # a <-> (b & ~c) || d
    pysat_clauses.append([predicates['a']])
    pysat_clauses += clauses_parse('(¬a ∨ b ∨ d) ∧ (¬a ∨ ¬c ∨ d) ∧ (a ∨ ¬b ∨ c) ∧ (a ∨ ¬d)', predicates)
    pysat_clauses += R_Implication(i, j, t)
    pysat_clauses += SN_Implication(i, j, t - 1, S_Neighbors)
    return pysat_clauses


def S_Implication(i, j, t, S_Neighbors):
    pysat_clauses = []
    predicates = {
        'a': int_plus([i, j, t, status_map['S']]),
        'b': int_plus([i, j, t - 1, status_map['S']]),
        'c': int_plus([i, j, t, status_map['R']]),
        'd': int_plus([i, j, t - 1, status_map['H']]),
        'e': int_plus([i, j, t - 1, status_map['SN']])
    }
    pysat_clauses.append([predicates['a']])
    # a <-> ((b && ~c) || (d && e))
    pysat_clauses += clauses_parse(
        '(¬a ∨ b ∨ d) ∧ (¬a ∨ b ∨ e) ∧ (¬a ∨ ¬c ∨ d) ∧ (¬a ∨ ¬c ∨ e) ∧ (a ∨ ¬b ∨ c) ∧ (a ∨ ¬d ∨ ¬e)', predicates)
    pysat_clauses += R_Implication(i, j, t)
    pysat_clauses += SN_Implication(i, j, t - 1, S_Neighbors)
    return pysat_clauses


def I_Implication(i, j, t):
    pysat_clauses = []
    predicates = {
        'a': int_plus([i, j, t, status_map['I']]),
        'b': int_plus([i, j, t - 1, status_map['I']]),
        'c': int_plus([i, j, t, status_map['VAC']])
    }
    # a <-> (b || c)
    pysat_clauses += clauses_parse('(¬a ∨ b ∨ c) ∧ (a ∨ ¬b) ∧ (a ∨ ¬c)', predicates)
    return pysat_clauses


def Q_Implication(i, j, t):
    pysat_clauses = []
    predicates = {
        'a': int_plus([i, j, t, status_map['Q']]),
        'b': int_plus([i, j, t - 1, status_map['Q']]),
        'c': int_plus([i, j, t, status_map['LQ']]),
        'd': int_plus([i, j, t, status_map['EQ']])
    }
    # a <-> (b && ~c) || d
    pysat_clauses += clauses_parse('(¬a ∨ b ∨ d) ∧ (¬a ∨ ¬c ∨ d) ∧ (a ∨ ¬b ∨ c) ∧ (a ∨ ¬d)', predicates)
    return pysat_clauses


def solve_problem(input):
    s = Solver()
    res = {}
    status_dict = {'U': {}, 'H': {}, 'S': {}, 'I': {}, 'Q': {}}
    police, medics, observations, queries = input['police'], input['medics'], input['observations'], input['queries']
    objs_count = len(observations)
    row_count = len(observations[0])
    col_count = len(observations[0][0])
    # if input['police'] is 0 and input['medics'] is 0:
    pysat_clauses = []
    pysat_clauses += linearity_constraints(objs_count, row_count, col_count)
    for status in status_dict:
        status_dict[status] = {o: [[F] * col_count for _ in range(row_count)] for o in range(objs_count)}

    for t, obs in enumerate(observations):
        for i, row in enumerate(obs):
            for j, cell in enumerate(row):
                if cell in status_dict:
                    status_dict[cell][t][i][j] = T
                elif cell == '?':
                    for status in status_dict:
                        status_dict[status][t][i][j] = '?'
    S_Neighbors = {o: [[F] * col_count for _ in range(row_count)] for o in range(objs_count)}
    for t, obs in enumerate(observations):
        for i, row in enumerate(obs):
            for j, cell in enumerate(row):
                temp = []
                if i - 1 >= 0:
                    temp.append(int_plus([i - 1, j, t, status_map['S']]))
                if j - 1 >= 0:
                    temp.append(int_plus([i, j - 1, t, status_map['S']]))
                if i + 1 < len(obs):
                    temp.append(int_plus([i + 1, j, t, status_map['S']]))
                if j + 1 < len(row):
                    temp.append(int_plus([i, j + 1, t, status_map['S']]))
                S_Neighbors[t][i][j] = temp

    start_observation = 0
    for i in range(len(status_dict['U'][start_observation])):
        for j in range(len(status_dict['U'][start_observation][0])):
            if status_dict['U'][start_observation][i][j] == T:
                pysat_clauses.append([int_plus([i, j, start_observation, status_map['U']])])
            elif status_dict['H'][start_observation][i][j] == T:
                pysat_clauses.append([int_plus([i, j, start_observation, status_map['H']])])
            elif status_dict['S'][start_observation][i][j] == T:
                pysat_clauses.append([int_plus([i, j, start_observation, status_map['S']])])
            elif status_dict['I'][start_observation][i][j] == T:
                pysat_clauses.append([int_plus([i, j, start_observation, status_map['I']])])
            elif status_dict['Q'][start_observation][i][j] == T:
                pysat_clauses.append([int_plus([i, j, start_observation, status_map['Q']])])

    # U Implication
    for t in range(1, len(status_dict['U'])):
        for i, row in enumerate(status_dict['U'][t]):
            for j, cell in enumerate(row):
                if cell == T:
                    pysat_clauses.append([int_plus([i, j, t, status_map['U']])])
                    pysat_clauses.append([int_plus([i, j, t, status_map['U']], isNot=True),
                                          int_plus([i, j, t - 1, status_map['U']])])

    # H Implication
    for t in range(1, len(status_dict['H'])):
        for i, row in enumerate(status_dict['H'][t]):
            for j, cell in enumerate(row):
                if cell == T:
                    pysat_clauses += H_Implication(i, j, t, S_Neighbors)

    # S Implication
    for t in range(1, len(status_dict['S'])):
        for i, row in enumerate(status_dict['S'][t]):
            for j, cell in enumerate(row):
                if cell == T:
                    pysat_clauses += S_Implication(i, j, t, S_Neighbors)

    knowledge_base = pysat_clauses
    """ Queries Parsing"""
    if input['police'] is 0 and input['medics'] is 0:
        for query in queries:
            test_query = []
            s = Solver()
            if query[1] == 0:
                test_query = knowledge_base.copy()
                test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map[query[2]]])])
                with Glucose3(bootstrap_with=test_query) as g:
                    result = g.solve()
                if not result:
                    res[query] = 'F'
                else:
                    res[query] = 'T'
                    for status in status_map:
                        if status in ['U', 'H', 'S', 'I', 'Q']:
                            if status != query[2]:
                                test_query = knowledge_base.copy()
                                test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map[status]])])
                                with Glucose3(bootstrap_with=test_query) as g:
                                    result = g.solve()

                                if result:
                                    res[query] = '?'
                                    break
            if query[1] >= 1:
                if query[2] == 'U':
                    test_query = knowledge_base.copy()
                    test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']])])
                    test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']], isNot=True),
                                       int_plus([query[0][0], query[0][1], query[1] - 1, status_map['U']])])
                    with Glucose3(bootstrap_with=test_query) as g:
                        result = g.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
                        test_query = knowledge_base.copy()
                        test_query += H_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += S_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue
                elif query[2] == 'H':
                    test_query = knowledge_base.copy()
                    test_query += H_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                    with Glucose3(bootstrap_with=test_query) as g:
                        result = g.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
                        test_query = knowledge_base.copy()
                        test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']])])
                        test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']], isNot=True),
                                           int_plus([query[0][0], query[0][1], query[1] - 1, status_map['U']])])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += S_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue
                elif query[2] == 'S':
                    test_query = knowledge_base.copy()
                    test_query += S_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                    with Glucose3(bootstrap_with=test_query) as g:
                        result = g.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
                        test_query = knowledge_base.copy()
                        test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']])])
                        test_query.append(
                            [int_plus([query[0][0], query[0][1], query[1], status_map['U']], isNot=True),
                             int_plus([query[0][0], query[0][1], query[1] - 1, status_map['U']])])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += H_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

    if input['police'] is 0 and input['medics'] >= 1:
        for query in queries:
            test_query = []
            s = Solver()
            if query[1] == 0:
                test_query = knowledge_base.copy()
                test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map[query[2]]])])
                with Glucose3(bootstrap_with=test_query) as g:
                    result = g.solve()

                if not result:
                    res[query] = 'F'
                else:
                    res[query] = 'T'
                    for status in status_map:
                        if status in ['U', 'H', 'S']:
                            if status != query[2]:
                                test_query = knowledge_base.copy()
                                test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map[status]])])
                                with Glucose3(bootstrap_with=test_query) as g:
                                    result = g.solve()

                                if result:
                                    res[query] = '?'
                                    break
            if query[1] >= 1:
                if query[2] == 'U':
                    test_query = knowledge_base.copy()
                    test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']])])
                    test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']], isNot=True),
                                       int_plus([query[0][0], query[0][1], query[1] - 1, status_map['U']])])
                    with Glucose3(bootstrap_with=test_query) as g:
                        result = g.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
                        test_query = knowledge_base.copy()
                        test_query += H_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += S_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += I_Implication(query[0][0], query[0][1], query[1])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue
                elif query[2] == 'H':
                    test_query = knowledge_base.copy()
                    test_query += H_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                    with Glucose3(bootstrap_with=test_query) as g:
                        result = g.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
                        test_query = knowledge_base.copy()
                        test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']])])
                        test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']], isNot=True),
                                           int_plus([query[0][0], query[0][1], query[1] - 1, status_map['U']])])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += S_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += I_Implication(query[0][0], query[0][1], query[1])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue
                elif query[2] == 'S':
                    test_query = knowledge_base.copy()
                    test_query += S_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                    with Glucose3(bootstrap_with=test_query) as g:
                        result = g.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
                        test_query = knowledge_base.copy()
                        test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']])])
                        test_query.append(
                            [int_plus([query[0][0], query[0][1], query[1], status_map['U']], isNot=True),
                             int_plus([query[0][0], query[0][1], query[1] - 1, status_map['U']])])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += H_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += I_Implication(query[0][0], query[0][1], query[1])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue
                elif query[2] == 'I':
                    test_query = knowledge_base.copy()
                    test_query += I_Implication(query[0][0], query[0][1], query[1])
                    for clause in test_query:
                        s.add_clause(clause)
                    result = s.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
    if input['police'] >= 1 and input['medics'] is 0:
        for query in queries:
            test_query = []
            s = Solver()
            if query[1] == 0:
                test_query = knowledge_base.copy()
                test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map[query[2]]])])
                with Glucose3(bootstrap_with=test_query) as g:
                    result = g.solve()

                if not result:
                    res[query] = 'F'
                else:
                    res[query] = 'T'
                    for status in status_map:
                        if status in ['U', 'H', 'S']:
                            if status != query[2]:
                                test_query = knowledge_base.copy()
                                test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map[status]])])
                                with Glucose3(bootstrap_with=test_query) as g:
                                    result = g.solve()

                                if result:
                                    res[query] = '?'
                                    break
            if query[1] >= 1:
                if query[2] == 'U':
                    test_query = knowledge_base.copy()
                    test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']])])
                    test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']], isNot=True),
                                       int_plus([query[0][0], query[0][1], query[1] - 1, status_map['U']])])
                    with Glucose3(bootstrap_with=test_query) as g:
                        result = g.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
                        test_query = knowledge_base.copy()
                        test_query += H_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += S_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += Q_Implication(query[0][0], query[0][1], query[1])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue
                elif query[2] == 'H':
                    test_query = knowledge_base.copy()
                    test_query += H_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                    with Glucose3(bootstrap_with=test_query) as g:
                        result = g.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
                        test_query = knowledge_base.copy()
                        test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']])])
                        test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']], isNot=True),
                                           int_plus([query[0][0], query[0][1], query[1] - 1, status_map['U']])])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += S_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += Q_Implication(query[0][0], query[0][1], query[1])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue
                elif query[2] == 'S':
                    test_query = knowledge_base.copy()
                    test_query += S_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                    with Glucose3(bootstrap_with=test_query) as g:
                        result = g.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
                        test_query = knowledge_base.copy()
                        test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']])])
                        test_query.append(
                            [int_plus([query[0][0], query[0][1], query[1], status_map['U']], isNot=True),
                             int_plus([query[0][0], query[0][1], query[1] - 1, status_map['U']])])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += H_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += Q_Implication(query[0][0], query[0][1], query[1])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue
                elif query[2] == 'Q':
                    test_query = knowledge_base.copy()
                    test_query += Q_Implication(query[0][0], query[0][1], query[1])
                    with Glucose3(bootstrap_with=test_query) as g:
                        result = g.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
    if input['police'] >= 1 and input['medics'] >= 1:
        for query in queries:
            test_query = []
            s = Solver()
            if query[1] == 0:
                test_query = knowledge_base.copy()
                test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map[query[2]]])])
                with Glucose3(bootstrap_with=test_query) as g:
                    result = g.solve()

                if not result:
                    res[query] = 'F'
                else:
                    res[query] = 'T'
                    for status in status_map:
                        if status in ['U', 'H', 'S']:
                            if status != query[2]:
                                test_query = knowledge_base.copy()
                                test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map[status]])])
                                with Glucose3(bootstrap_with=test_query) as g:
                                    result = g.solve()

                                if result:
                                    res[query] = '?'
                                    break
            if query[1] >= 1:
                if query[2] == 'U':
                    test_query = knowledge_base.copy()
                    test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']])])
                    test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']], isNot=True),
                                       int_plus([query[0][0], query[0][1], query[1] - 1, status_map['U']])])
                    with Glucose3(bootstrap_with=test_query) as g:
                        result = g.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
                        test_query = knowledge_base.copy()
                        test_query += H_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += S_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += I_Implication(query[0][0], query[0][1], query[1])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += Q_Implication(query[0][0], query[0][1], query[1])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue
                elif query[2] == 'H':
                    test_query = knowledge_base.copy()
                    test_query += H_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                    with Glucose3(bootstrap_with=test_query) as g:
                        result = g.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
                        test_query = knowledge_base.copy()
                        test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']])])
                        test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']], isNot=True),
                                           int_plus([query[0][0], query[0][1], query[1] - 1, status_map['U']])])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += S_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += I_Implication(query[0][0], query[0][1], query[1])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += Q_Implication(query[0][0], query[0][1], query[1])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue
                elif query[2] == 'S':
                    test_query = knowledge_base.copy()
                    test_query += S_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                    with Glucose3(bootstrap_with=test_query) as g:
                        result = g.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
                        test_query = knowledge_base.copy()
                        test_query.append([int_plus([query[0][0], query[0][1], query[1], status_map['U']])])
                        test_query.append(
                            [int_plus([query[0][0], query[0][1], query[1], status_map['U']], isNot=True),
                             int_plus([query[0][0], query[0][1], query[1] - 1, status_map['U']])])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += H_Implication(query[0][0], query[0][1], query[1], S_Neighbors)
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += I_Implication(query[0][0], query[0][1], query[1])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue

                        test_query = knowledge_base.copy()
                        test_query += Q_Implication(query[0][0], query[0][1], query[1])
                        with Glucose3(bootstrap_with=test_query) as g:
                            result = g.solve()

                        if result:
                            res[query] = '?'
                            continue
                elif query[2] == 'Q':
                    test_query = knowledge_base.copy()
                    test_query += Q_Implication(query[0][0], query[0][1], query[1])
                    with Glucose3(bootstrap_with=test_query) as g:
                        result = g.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
                elif query[2] == 'I':
                    test_query = knowledge_base.copy()
                    test_query += I_Implication(query[0][0], query[0][1], query[1])
                    for clause in test_query:
                        s.add_clause(clause)
                    result = s.solve()

                    if not result:
                        res[query] = 'F'
                    else:
                        res[query] = 'T'
    return res
