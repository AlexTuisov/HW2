import numpy as np
import pysat
import itertools
from pysat.solvers import Solver
from sympy.logic import to_cnf
from sympy import symbols
from sympy.logic import SOPform, POSform
from sympy.logic.boolalg import Xor, And, Not, Or
from itertools import combinations
import collections

ids = ['207530551', '322401100']


# def get_all_actions(input):


def check_queries(queries, input):
    solutions = {}

    num_police = input['police']
    num_medics = input['medics']
    observations = input['observations']

    encoded_pop = {}
    encoded_actions = {}

    board_size = len(observations[0]) * len(observations[0][0])
    row_len = len(observations[0])
    pop_and_actions_num = 5 + 8 + 5
    pops_encoded = {pop: i + 1 for i, pop in enumerate(['H', 'S', 'Q', 'I', 'U'])}
    actions_encoded = {action: i + 6 for i, action in enumerate(['VA', 'QR', 'IR', 'IL', 'ID', 'IU', 'HS', 'HQ',
                                                                 'NOH', 'NOS', 'NOQ', 'NOI', 'NOU'])}

    KB = []

    for turn, observation in enumerate(observations):
        for i, row in enumerate(observation):
            for j, pop in enumerate(row):
                for population in pops_encoded.keys():
                    encoded_pop[(turn, i, j, population)] = turn*board_size*pop_and_actions_num + \
                                                            (i*row_len + j)*pop_and_actions_num + pops_encoded[population]
                if turn < len(observations) - 1:
                    for action in actions_encoded.keys():
                        if (action == 'HS' or action == 'HQ') and turn < 2:
                            continue
                        encoded_actions[(turn, i, j, action)] = turn*board_size*pop_and_actions_num + \
                                                                (i*row_len + j)*pop_and_actions_num + actions_encoded[action]
                # Known facts:
                if pop != '?':
                    KB.append([encoded_pop[(turn, i, j, pop)]])
                    for p in pops_encoded.keys():
                        if not p == pop:
                            KB.append([-encoded_pop[(turn, i, j, p)]])

                else:
                    KB.append([encoded_pop[(turn, i, j, population)] for population in pops_encoded.keys()])
                    combs = itertools.combinations(pops_encoded.keys(), 2)
                    for comb in combs:
                        KB.append([-encoded_pop[(turn, i, j, comb[0])], -encoded_pop[(turn, i, j, comb[1])]])
                    # First turn can't have 'I's and 'Q's
                    if turn == 0:
                        KB.append([-encoded_pop[(0, i, j, 'Q')]])
                        KB.append([-encoded_pop[(0, i, j, 'I')]])

                # no medics no vacc:
                if not num_medics:
                    KB.append([-encoded_pop[(turn, i, j, 'I')]])
                # no police no quar:
                if not num_police:
                    KB.append([-encoded_pop[(turn, i, j, 'Q')]])

    grid_size = (len(observations[0]), len(observations[0][0]))

    # Action Precondition Clauses
    for action_key, action_value in encoded_actions.items():
        (turn, i, j, action) = action_key

        if num_medics and action == 'VA':
            KB.append([-action_value, encoded_pop[(turn, i, j, 'H')]])

        if num_police and action == 'QR':
            KB.append([-action_value, encoded_pop[(turn, i, j, 'S')]])

        if j < grid_size[1] - 1 and action == 'IR':
            KB += [[-action_value, encoded_pop[(turn, i, j, 'H')]], [-action_value, encoded_pop[(turn, i, j+1, 'S')]]]

        if j > 0 and action == 'IL':
            KB += [[-action_value, encoded_pop[(turn, i, j, 'H')]], [-action_value, encoded_pop[(turn, i, j-1, 'S')]]]

        if i < grid_size[0] - 1 and action == 'ID':
            KB += [[-action_value, encoded_pop[(turn, i, j, 'H')]], [-action_value, encoded_pop[(turn, i+1, j, 'S')]]]

        if i > 0 and action == 'IU':
            KB += [[-action_value, encoded_pop[(turn, i, j, 'H')]], [-action_value, encoded_pop[(turn, i-1, j, 'S')]]]

        if action == 'HS':
            KB += [[-action_value, encoded_pop[(turn, i, j, 'S')]], [-action_value, encoded_pop[(turn-1, i, j, 'S')]],
                                                                    [-action_value, encoded_pop[(turn-2, i, j, 'S')]]]
        if action == 'HQ':
            KB += [[-action_value, encoded_pop[(turn, i, j, 'Q')]], [-action_value, encoded_pop[(turn-1, i, j, 'Q')]]]

        if action == 'NOH':
            KB.append([-action_value, encoded_pop[(turn, i, j, 'H')]])
            if j < grid_size[1] - 1:
                KB.append([-action_value, -encoded_pop[(turn, i, j+1, 'S')], encoded_actions[(turn, i, j+1, 'QR')]])
            if j > 0:
                KB.append([-action_value, -encoded_pop[(turn, i, j-1, 'S')], encoded_actions[(turn, i, j-1, 'QR')]])
            if i < grid_size[0] - 1:
                KB.append([-action_value, -encoded_pop[(turn, i+1, j, 'S')], encoded_actions[(turn, i+1, j, 'QR')]])
            if i > 0:
                KB.append([-action_value, -encoded_pop[(turn, i-1, j, 'S')], encoded_actions[(turn, i-1, j, 'QR')]])

        if action == 'NOS':
            KB.append([-action_value, encoded_pop[(turn, i, j, 'S')]])
            if turn >= 2:
                KB.append([-action_value, -encoded_pop[(turn-1, i, j, 'S')], -encoded_pop[(turn-2, i, j, 'S')]])

        if action == 'NOQ':
            KB.append([-action_value, encoded_pop[(turn, i, j, 'Q')]])
            if turn >= 2:
                KB.append([-action_value, -encoded_pop[(turn-1, i, j, 'Q')]])

        if action == 'NOI':
            KB.append([-action_value, encoded_pop[(turn, i, j, 'I')]])

        if action == 'NOU':
            KB.append([-action_value, encoded_pop[(turn, i, j, 'U')]])

    # Action Interference Clauses
    for turn, observation in enumerate(observations):
        if turn < len(observations) - 1:
            for i, row in enumerate(observation):
                for j, pop in enumerate(row):
                    for action_key, action_code in actions_encoded.items():
                        if action_key != 'VA':
                            if turn >= 2 or (action_key != 'HS' and action_key != 'HQ'):
                                KB.append([-encoded_actions[(turn, i, j, 'VA')], -encoded_actions[(turn, i, j, action_key)]])
                        if action_key != 'QR':
                            if turn >= 2 or (action_key != 'HS' and action_key != 'HQ'):
                                KB.append([-encoded_actions[(turn, i, j, 'QR')], -encoded_actions[(turn, i, j, action_key)]])
                        if action_key != 'NOH':
                            if turn >= 2 or (action_key != 'HS' and action_key != 'HQ'):
                                KB.append([-encoded_actions[(turn, i, j, 'NOH')], -encoded_actions[(turn, i, j, action_key)]])
                        if action_key != 'NOS':
                            if turn >= 2 or (action_key != 'HS' and action_key != 'HQ'):
                                KB.append([-encoded_actions[(turn, i, j, 'NOS')], -encoded_actions[(turn, i, j, action_key)]])
                        if action_key != 'NOQ':
                            if turn >= 2 or (action_key != 'HS' and action_key != 'HQ'):
                                KB.append([-encoded_actions[(turn, i, j, 'NOQ')], -encoded_actions[(turn, i, j, action_key)]])
                        if action_key != 'NOI':
                            if turn >= 2 or (action_key != 'HS' and action_key != 'HQ'):
                                KB.append([-encoded_actions[(turn, i, j, 'NOI')], -encoded_actions[(turn, i, j, action_key)]])
                        if action_key != 'NOU':
                            if turn >= 2 or (action_key != 'HS' and action_key != 'HQ'):
                                KB.append([-encoded_actions[(turn, i, j, 'NOU')], -encoded_actions[(turn, i, j, action_key)]])

                    if j < grid_size[1] - 1:
                        KB.append([-encoded_actions[(turn, i, j, 'IR')], -encoded_actions[(turn, i, j+1, 'QR')]])

                    if j > 0:
                        KB.append([-encoded_actions[(turn, i, j, 'IL')], -encoded_actions[(turn, i, j-1, 'QR')]])

                    if i < grid_size[0] - 1:
                        KB.append([-encoded_actions[(turn, i, j, 'ID')], -encoded_actions[(turn, i+1, j, 'QR')]])

                    if i > 0:
                        KB.append([-encoded_actions[(turn, i, j, 'IU')], -encoded_actions[(turn, i-1, j, 'QR')]])

                    if turn >= 2:
                        KB.append([-encoded_actions[(turn, i, j, 'HS')], -encoded_actions[(turn, i, j, 'HQ')]])
                        for ac in ['IR', 'IL', 'ID', 'IU']:
                            KB.append([-encoded_actions[(turn, i, j, ac)], -encoded_actions[(turn, i, j, 'HS')]])
                            KB.append([-encoded_actions[(turn, i, j, ac)], -encoded_actions[(turn, i, j, 'HQ')]])


    # Fact Achievement Clauses
    for pop_key, pop_val in encoded_pop.items():
        (turn, i, j, pop) = pop_key
        if turn > 0:
            if pop == 'H':
                clause = [-pop_val, encoded_actions[(turn-1, i, j, 'NOH')]]
                if turn > 2:
                    clause.append(encoded_actions[(turn-1, i, j, 'HS')])
                    clause.append(encoded_actions[(turn-1, i, j, 'HQ')])
                KB.append(clause)

            if pop == 'S':
                clause = [-pop_val, encoded_actions[(turn-1, i, j, 'NOS')]]
                if j < grid_size[1] - 1:
                    clause.append(encoded_actions[(turn-1, i, j, 'IR')])
                if j > 0:
                    clause.append(encoded_actions[(turn-1, i, j, 'IL')])
                if i < grid_size[0] - 1:
                    clause.append(encoded_actions[(turn-1, i, j, 'ID')])
                if i > 0:
                    clause.append(encoded_actions[(turn-1, i, j, 'IU')])
                KB.append(clause)

            if pop == 'Q':
                KB.append([-pop_val, encoded_actions[(turn-1, i, j, 'NOQ')], encoded_actions[(turn-1, i, j, 'QR')]])

            if pop == 'I':
                KB.append([-pop_val, encoded_actions[(turn-1, i, j, 'NOI')], encoded_actions[(turn-1, i, j, 'VA')]])

            if pop == 'U':
                KB.append([-pop_val, encoded_actions[(turn-1, i, j, 'NOU')]])


    # TEAMS
    def cnf_to_clauses(teams_cnf):
        clauses = str(teams_cnf).replace(" ", "").replace("(", "").replace(")", "").replace("~", "-").split('&')
        return [[int(c) for c in clause.split("|")] for clause in clauses]

    if num_medics or num_police:
        # Inferred from teams:
        for turn, observation in enumerate(observations):
            if turn == len(observations) - 1:
                break
            healthy = []
            sick = []

            curr_num_medics = num_medics
            curr_num_police = num_police

            for i, row in enumerate(observation):
                for j, pop in enumerate(row):
                    if pop == 'H':
                        if observations[turn + 1][i][j] == 'I':
                            curr_num_medics -= 1
                        elif observations[turn + 1][i][j] == '?':
                            healthy.append(encoded_pop[(turn + 1, i, j, 'I')])
                    elif pop == 'S':
                        if observations[turn + 1][i][j] == 'Q':
                            curr_num_police -= 1
                        elif observations[turn + 1][i][j] == '?':
                            sick.append(encoded_pop[(turn + 1, i, j, 'Q')])
                    elif pop == '?':
                        healthy.append(encoded_pop[(turn + 1, i, j, 'I')])
                        sick.append(encoded_pop[(turn + 1, i, j, 'Q')])

            for i, row in enumerate(observation):
                for j, pop in enumerate(row):
                    if observations[turn + 1][i][j] == '?':
                        if not curr_num_medics:
                            KB.append([-encoded_actions[(turn, i, j, 'VA')]])
                        if not curr_num_police:
                            KB.append([-encoded_actions[(turn, i, j, 'QR')]])

            def teams_clauses(curr_num_teams, team_locs):
                if len(team_locs) == 1:
                    return [team_locs]

                syms = ''
                for i in team_locs:
                    syms += str(i) + ' '

                symbs = symbols(syms)
                and_groups = [POSform(group, minterms=[{symb: 1 for symb in group}]) for group in
                              combinations(symbs, min(curr_num_teams, len(team_locs)))]

                SOP = SOPform(and_groups, minterms=[{group: 1} for group in and_groups])

                Xor_group = True
                if len(team_locs) > curr_num_teams:
                    for clause1, clause2 in combinations(SOP.args, 2):
                        Xor_group = And(Xor_group, Or(Not(clause1), Not(clause2)))

                final_teams_cnf = to_cnf(And(Xor_group, SOP))
                return cnf_to_clauses(final_teams_cnf)

            if curr_num_medics and len(healthy):
                KB += teams_clauses(curr_num_medics, healthy)

            if curr_num_police and len(sick):
                KB += teams_clauses(curr_num_police, sick)

    for query in queries:
        solver1 = Solver()
        alpha = [encoded_pop[(query[1], query[0][0], query[0][1], query[2])]]
        solver1.append_formula(KB + [alpha])

        with_alpha = solver1.solve(assumptions=alpha)

        solver2 = Solver()
        not_alpha = [-encoded_pop[(query[1], query[0][0], query[0][1], query[2])]]
        solver2.append_formula(KB + [not_alpha])

        with_not_alpha = solver2.solve()

        if with_alpha and with_not_alpha:
            solutions[query] = '?'
        elif with_alpha and not with_not_alpha:
            solutions[query] = 'T'
        elif not with_alpha:
            solutions[query] = 'F'

    return solutions


def solve_problem(input):
    solution = check_queries(input['queries'], input)
    return solution
    # put your solution here, remember the format needed
