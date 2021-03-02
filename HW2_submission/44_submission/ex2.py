from pysat.solvers import Glucose3
from pysat.formula import CNF
from itertools import chain, combinations

ids = ['314653270']


def solve_problem(input):
    no_police = input["police"]
    no_medics = input["medics"]
    observations = input["observations"]
    no_rounds = len(observations)
    n = len(observations[0])
    m = len(observations[0][0])
    indices_list = [(i, j) for i in range(n) for j in range(m)]
    queries = input["queries"]

    state_codes = ['U', 'H', 'S']
    actions_codes = ['infected_left', 'infected_right', 'infected_down', 'infected_up', 'healed']
    if no_medics > 0:
        state_codes.append('I')
        actions_codes.append('vaccinate')
    if no_police > 0:
        state_codes.append('Q')
        actions_codes.extend(['quarantine', 'free'])
    actions_codes.extend(state_codes)

    decision_variables_p = get_decision_variables_p(state_codes, indices_list, no_rounds)
    p_to_atom = get_translation_dictionary(decision_variables_p, 2)

    decision_variables_a = get_decision_variables_a(observations, state_codes, no_police, no_medics, n, m)
    a_to_atom = get_translation_dictionary(decision_variables_a, len(decision_variables_p) + 2)

    formula = get_formula(observations, decision_variables_p, p_to_atom, decision_variables_a, a_to_atom, no_police,
                          no_medics, indices_list, state_codes, no_rounds)

    g = Glucose3(bootstrap_with=formula.clauses)

    answers = {}
    for query in queries:
        if query[2] == 'Q' and (no_police == 0 or query[1] == 0):
            answer = False
        elif query[2] == 'I' and (no_medics == 0 or query[1] == 0):
            answer = False
        else:
            answer = g.solve(assumptions=[p_to_atom[query]])

        if answer:
            answer = g.solve(assumptions=[-p_to_atom[query]])
            if answer:
                answers[query] = '?'
            else:
                answers[query] = 'T'
        else:
            answers[query] = 'F'

    return answers


def get_formula(observations, decision_variables_p, p_to_atom, decision_variables_a, a_to_atom, no_police, no_medics,
                indices_list, state_codes, no_rounds):
    formula = CNF()

    initial_state_clauses = get_initial_state_clauses(observations, decision_variables_p, p_to_atom, state_codes,
                                                      indices_list)

    action_precondition_clauses = get_action_precondition_clauses(decision_variables_a, p_to_atom, a_to_atom,
                                                                  no_police, no_medics, indices_list)

    action_interference_clauses = get_action_interference_clauses(decision_variables_a, a_to_atom, state_codes,
                                                                  no_rounds)

    fact_achievement_clauses = get_fact_achievement_clauses(decision_variables_p, p_to_atom, decision_variables_a,
                                                            a_to_atom)

    permanent_clauses = get_permanent_clauses(p_to_atom, decision_variables_a, a_to_atom, no_police, no_medics,
                                              indices_list, state_codes)

    clauses = initial_state_clauses + action_precondition_clauses + action_interference_clauses +\
              fact_achievement_clauses + permanent_clauses

    formula.extend(clauses)

    return formula


def get_permanent_clauses(p_to_atom, decision_variables_a, a_to_atom, no_police, no_medics, indices_list, state_codes):
    permanent_clauses = []

    if no_police == 0 and no_medics == 0:
        for action in decision_variables_a:

            if action[2] in state_codes:
                continue

            pre_action = get_pre_action(action, p_to_atom, no_police, no_medics, indices_list)
            not_pre_action = [-p for p in pre_action]

            clause = not_pre_action + [a_to_atom[action]]
            permanent_clauses.append(clause)

    elif no_police == 0 and no_medics > 0:
        for action1 in decision_variables_a:
            loc, r, a = action1
            if a == 'infected_left' or a == 'infected_right' or a == 'infected_up' or a == 'infected_down':
                pre_action = get_pre_action(action1, p_to_atom, no_police, no_medics, indices_list)
                not_pre_action = [-p for p in pre_action]

                add_v = []
                for action2 in decision_variables_a:
                    a_loc, a_r, a2 = action2
                    if a_r == r and a2 == 'vaccinate' and loc in a_loc:
                        add_v.append(a_to_atom[action2])

                clause = not_pre_action + add_v + [a_to_atom[action1]]
                permanent_clauses.append(clause)

            elif a == 'healed':
                pre_action = get_pre_action(action1, p_to_atom, no_police, no_medics, indices_list)
                not_pre_action = [-p for p in pre_action]

                clause = not_pre_action + [a_to_atom[action1]]
                permanent_clauses.append(clause)

    elif no_police > 0 and no_medics == 0:
        for action1 in decision_variables_a:
            loc, r, a = action1
            if a == 'infected_left':
                row, col = loc
                pre_action = get_pre_action(action1, p_to_atom, no_police, no_medics, indices_list)
                not_pre_action = [-p for p in pre_action]

                add_q = []
                for action2 in decision_variables_a:
                    a_loc, a_r, a2 = action2
                    if a_r == r and a2 == 'quarantine' and (row, col - 1) in a_loc:
                        add_q.append(a_to_atom[action2])

                clause = not_pre_action + add_q + [a_to_atom[action1]]
                permanent_clauses.append(clause)

            elif a == 'infected_right':
                row, col = loc
                pre_action = get_pre_action(action1, p_to_atom, no_police, no_medics, indices_list)
                not_pre_action = [-p for p in pre_action]

                add_q = []
                for action2 in decision_variables_a:
                    a_loc, a_r, a2 = action2
                    if a_r == r and a2 == 'quarantine' and (row, col + 1) in a_loc:
                        add_q.append(a_to_atom[action2])

                clause = not_pre_action + add_q + [a_to_atom[action1]]
                permanent_clauses.append(clause)

            elif a == 'infected_up':
                row, col = loc
                pre_action = get_pre_action(action1, p_to_atom, no_police, no_medics, indices_list)
                not_pre_action = [-p for p in pre_action]

                add_q = []
                for action2 in decision_variables_a:
                    a_loc, a_r, a2 = action2
                    if a_r == r and a2 == 'quarantine' and (row - 1, col) in a_loc:
                        add_q.append(a_to_atom[action2])

                clause = not_pre_action + add_q + [a_to_atom[action1]]
                permanent_clauses.append(clause)

            elif a == 'infected_down':
                row, col = loc
                pre_action = get_pre_action(action1, p_to_atom, no_police, no_medics, indices_list)
                not_pre_action = [-p for p in pre_action]

                add_q = []
                for action2 in decision_variables_a:
                    a_loc, a_r, a2 = action2
                    if a_r == r and a2 == 'quarantine' and (row + 1, col) in a_loc:
                        add_q.append(a_to_atom[action2])

                clause = not_pre_action + add_q + [a_to_atom[action1]]
                permanent_clauses.append(clause)

            elif a == 'healed':
                pre_action = get_pre_action(action1, p_to_atom, no_police, no_medics, indices_list)
                not_pre_action = [-p for p in pre_action]

                add_q = []
                for action2 in decision_variables_a:
                    a_loc, a_r, a2 = action2
                    if a_r == r and a2 == 'quarantine' and loc in a_loc:
                        add_q.append(a_to_atom[action2])

                clause = not_pre_action + add_q + [a_to_atom[action1]]
                permanent_clauses.append(clause)

            elif a == 'free':
                pre_action = get_pre_action(action1, p_to_atom, no_police, no_medics, indices_list)
                not_pre_action = [-p for p in pre_action]

                clause = not_pre_action + [a_to_atom[action1]]
                permanent_clauses.append(clause)

    else:
        for action1 in decision_variables_a:
            loc, r, a = action1
            if a == 'infected_left':
                row, col = loc
                pre_action = get_pre_action(action1, p_to_atom, no_police, no_medics, indices_list)
                not_pre_action = [-p for p in pre_action]

                add_q = []
                for action2 in decision_variables_a:
                    a_loc, a_r, a2 = action2
                    if a_r == r and a2 == 'quarantine' and (row, col - 1) in a_loc:
                        add_q.append(a_to_atom[action2])

                add_v = []
                for action2 in decision_variables_a:
                    a_loc, a_r, a2 = action2
                    if a_r == r and a2 == 'vaccinate' and loc in a_loc:
                        add_v.append(a_to_atom[action2])

                clause = not_pre_action + add_q + add_v + [a_to_atom[action1]]
                permanent_clauses.append(clause)

            elif a == 'infected_right':
                row, col = loc
                pre_action = get_pre_action(action1, p_to_atom, no_police, no_medics, indices_list)
                not_pre_action = [-p for p in pre_action]

                add_q = []
                for action2 in decision_variables_a:
                    a_loc, a_r, a2 = action2
                    if a_r == r and a2 == 'quarantine' and (row, col + 1) in a_loc:
                        add_q.append(a_to_atom[action2])

                add_v = []
                for action2 in decision_variables_a:
                    a_loc, a_r, a2 = action2
                    if a_r == r and a2 == 'vaccinate' and loc in a_loc:
                        add_v.append(a_to_atom[action2])

                clause = not_pre_action + add_q + add_v + [a_to_atom[action1]]
                permanent_clauses.append(clause)

            elif a == 'infected_up':
                row, col = loc
                pre_action = get_pre_action(action1, p_to_atom, no_police, no_medics, indices_list)
                not_pre_action = [-p for p in pre_action]

                add_q = []
                for action2 in decision_variables_a:
                    a_loc, a_r, a2 = action2
                    if a_r == r and a2 == 'quarantine' and (row - 1, col) in a_loc:
                        add_q.append(a_to_atom[action2])

                add_v = []
                for action2 in decision_variables_a:
                    a_loc, a_r, a2 = action2
                    if a_r == r and a2 == 'vaccinate' and loc in a_loc:
                        add_v.append(a_to_atom[action2])

                clause = not_pre_action + add_q + add_v + [a_to_atom[action1]]
                permanent_clauses.append(clause)

            elif a == 'infected_down':
                row, col = loc
                pre_action = get_pre_action(action1, p_to_atom, no_police, no_medics, indices_list)
                not_pre_action = [-p for p in pre_action]

                add_q = []
                for action2 in decision_variables_a:
                    a_loc, a_r, a2 = action2
                    if a_r == r and a2 == 'quarantine' and (row + 1, col) in a_loc:
                        add_q.append(a_to_atom[action2])

                add_v = []
                for action2 in decision_variables_a:
                    a_loc, a_r, a2 = action2
                    if a_r == r and a2 == 'vaccinate' and loc in a_loc:
                        add_v.append(a_to_atom[action2])

                clause = not_pre_action + add_q + add_v +[a_to_atom[action1]]
                permanent_clauses.append(clause)

            elif a == 'healed':
                pre_action = get_pre_action(action1, p_to_atom, no_police, no_medics, indices_list)
                not_pre_action = [-p for p in pre_action]

                add_q = []
                for action2 in decision_variables_a:
                    a_loc, a_r, a2 = action2
                    if a_r == r and a2 == 'quarantine' and loc in a_loc:
                        add_q.append(a_to_atom[action2])

                clause = not_pre_action + add_q + [a_to_atom[action1]]
                permanent_clauses.append(clause)

            elif a == 'free':
                pre_action = get_pre_action(action1, p_to_atom, no_police, no_medics, indices_list)
                not_pre_action = [-p for p in pre_action]

                clause = not_pre_action + [a_to_atom[action1]]
                permanent_clauses.append(clause)

    return permanent_clauses


def get_fact_achievement_clauses(decision_variables_p, p_to_atom, decision_variables_a, a_to_atom):
    fact_achievement_clauses = []

    for p in decision_variables_p:
        p_loc, p_r, sc = p
        atom_p = p_to_atom[p]

        if p_r == 0:
            continue

        add_p = []
        for action in decision_variables_a:
            a_loc, a_r, a = action
            if a_r != p_r - 1:
                continue
            if atom_p in get_add_action(action, p_to_atom):
                add_p.append(a_to_atom[action])

        clause = [-atom_p] + add_p
        # print('clause\n', clause)

        fact_achievement_clauses.append(clause)

    return fact_achievement_clauses


def get_add_action(action, p_to_atom):
    add_action = []
    loc, r, a = action

    if a == 'infected_left' or a == 'infected_right' or a == 'infected_up' or a == 'infected_down':
        add_action = [p_to_atom[(loc, r + 1, 'S')]]

    elif a == 'healed' or a == 'free':
        add_action = [p_to_atom[(loc, r + 1, 'H')]]

    elif a == 'vaccinate':
        for l in loc:
            add_action.append(p_to_atom[(l, r + 1, 'I')])

    elif a == 'quarantine':
        for l in loc:
            add_action.append(p_to_atom[(l, r + 1, 'Q')])

    else:
        add_action = [p_to_atom[(loc, r + 1, a)]]

    return add_action


def get_action_interference_clauses(decision_variables_a, a_to_atom, state_codes, no_rounds):
    action_interference_clauses = []

    actions_per_round = [[] for i in range(no_rounds)]
    for action in decision_variables_a:
        loc, r, a = action
        actions_per_round[r].append(action)

    for actions_round_r in actions_per_round:

        for action1 in actions_round_r:
            loc1, r1, a1 = action1
            for action2 in actions_round_r:
                loc2, r2, a2 = action2

                if (a1 == 'infected_left' and a2 == 'quarantine' and (loc1[0], loc1[1] - 1) in loc2) or \
                   (a1 == 'infected_left' and a2 == 'vaccinate' and loc1 in loc2) or \
                   (a1 == 'infected_right' and a2 == 'quarantine' and (loc1[0], loc1[1] + 1) in loc2) or \
                   (a1 == 'infected_right' and a2 == 'vaccinate' and loc1 in loc2) or \
                   (a1 == 'infected_up' and a2 == 'quarantine' and (loc1[0] - 1, loc1[1]) in loc2) or \
                   (a1 == 'infected_up' and a2 == 'vaccinate' and loc1 in loc2) or \
                   (a1 == 'infected_down' and a2 == 'quarantine' and (loc1[0] + 1, loc1[1]) in loc2) or \
                   (a1 == 'infected_down' and a2 == 'vaccinate' and loc1 in loc2) or \
                   (a1 == 'healed' and a2 == 'quarantine' and loc1 in loc2) or \
                   (a1 == 'vaccinate' and a2 == 'vaccinate' and loc1 != loc2) or \
                   (a1 == 'quarantine' and a2 == 'quarantine' and loc1 != loc2):

                    action_interference_clauses.append([-a_to_atom[action1], -a_to_atom[action2]])

                elif (a1 == 'H' and a2 == 'infected_left' and loc1 == loc2) or \
                     (a1 == 'H' and a2 == 'infected_right' and loc1 == loc2) or \
                     (a1 == 'H' and a2 == 'infected_up' and loc1 == loc2) or \
                     (a1 == 'H' and a2 == 'infected_down' and loc1 == loc2) or \
                     (a1 == 'H' and a2 == 'vaccinate' and loc1 in loc2) or \
                     (a1 == 'S' and a2 == 'healed' and loc1 == loc2) or \
                     (a1 == 'S' and a2 == 'quarantine' and loc1 in loc2) or \
                     (a1 in state_codes and a2 in state_codes and a1 != a2 and loc1 == loc2) or \
                     (a1 == 'Q' and a2 == 'free' and loc1 == loc2):

                    action_interference_clauses.append([-a_to_atom[action1], -a_to_atom[action2]])

    return action_interference_clauses


def get_action_precondition_clauses(decision_variables_a, p_to_atom, a_to_atom, no_police, no_medics, indices_list):
    action_precondition_clauses = []

    for action in decision_variables_a:
        pre_action_list = get_pre_action(action, p_to_atom, no_police, no_medics, indices_list)
        for pa in pre_action_list:
            action_precondition_clauses.append([-a_to_atom[action], pa])

    return action_precondition_clauses


def get_pre_action(action, p_to_atom, no_police, no_medics, indices_list):
    pre_action = []
    loc, r, a = action

    if a == 'infected_left':
        row, col = loc
        pre_action = [p_to_atom[(loc, r, 'H')], p_to_atom[((row, col - 1), r, 'S')]]

    elif a == 'infected_right':
        row, col = loc
        pre_action = [p_to_atom[(loc, r, 'H')], p_to_atom[((row, col + 1), r, 'S')]]

    elif a == 'infected_up':
        row, col = loc
        pre_action = [p_to_atom[(loc, r, 'H')], p_to_atom[((row - 1, col), r, 'S')]]

    elif a == 'infected_down':
        row, col = loc
        pre_action = [p_to_atom[(loc, r, 'H')], p_to_atom[((row + 1, col), r, 'S')]]

    elif a == 'healed':
        if r < 2:
            pre_action = [-1, 1]
        else:
            pre_action = [p_to_atom[(loc, r, 'S')], p_to_atom[(loc, r - 1, 'S')], p_to_atom[(loc, r - 2, 'S')]]

    elif a == 'vaccinate':
        for l in loc:
            pre_action.append(p_to_atom[(l, r, 'H')])

        if len(loc) < no_medics:
            for l in indices_list:
                if l not in loc:
                    pre_action.append(-p_to_atom[(l, r, 'H')])

    elif a == 'quarantine':
        for l in loc:
            pre_action.append(p_to_atom[(l, r, 'S')])

        if len(loc) < no_police:
            for l in indices_list:
                if l not in loc:
                    pre_action.append(-p_to_atom[(l, r, 'S')])

    elif a == 'free':
        if r < 2:
            pre_action = [-1, 1]
        else:
            pre_action = [p_to_atom[(loc, r, 'Q')], p_to_atom[(loc, r - 1, 'Q')]]

    else:
        pre_action = [p_to_atom[action]]

    return pre_action


def get_initial_state_clauses(observations, decision_variables_p, p_to_atom, state_codes, indices_list):
    initial_state_clauses = []
    question_mark_list = []

    for (row, col), r, sc in decision_variables_p:

        if observations[r][row][col] == '?':
            question_mark_list.append(((row, col), r))

        else:
            if observations[r][row][col] == sc:
                initial_state_clauses.append([p_to_atom[((row, col), r, sc)]])
            else:
                initial_state_clauses.append([-p_to_atom[((row, col), r, sc)]])

    for (row, col), r in question_mark_list:
        if r == 0:
            clause1 = [p_to_atom[((row, col), r, sc)] for sc in state_codes if (sc != 'Q' and sc != 'I')]
        else:
            clause1 = [p_to_atom[((row, col), r, sc)] for sc in state_codes]
        initial_state_clauses.append(clause1)
        initial_state_clauses += [list(clause2) for clause2 in list(combinations([-atom for atom in clause1], 2))]

    if 'Q' in state_codes:
        for loc in indices_list:
            idx = p_to_atom[(loc, 0, 'Q')]
            initial_state_clauses.append([-idx])

    if 'I' in state_codes:
        for loc in indices_list:
            idx = p_to_atom[(loc, 0, 'I')]
            initial_state_clauses.append([-idx])

    return initial_state_clauses


def get_decision_variables_a(observations, state_codes, no_police, no_medics, n, m):
    A = []

    for r, o in enumerate(observations):
        sick_list = []
        healthy_list = []
        must_v = []
        must_q = []
        no_question_marks = 0

        for i, row in enumerate(o):
            for j, sc in enumerate(row):

                if sc != '?' and r != len(observations)-1 and observations[r+1][i][j] in [sc, '?']:
                    A.append(((i, j), r, sc))
                elif sc == '?':
                    no_question_marks += 1

                    for sc2 in state_codes:
                        if r == 0 and sc2 in ['Q', 'I']:
                            continue
                        A.append(((i, j), r, sc2))

                if sc in ['H', '?']:
                    if r != len(observations)-1 and observations[r+1][i][j] == 'I':
                        must_v.append((i, j))
                    else:
                        healthy_list.append((i, j))

                    if j != 0 and observations[r][i][j-1] in ['S', '?']:
                        A.append(((i, j), r, 'infected_left'))
                    if j != m - 1 and observations[r][i][j+1] in ['S', '?']:
                        A.append(((i, j), r, 'infected_right'))
                    if i != 0 and observations[r][i-1][j] in ['S', '?']:
                        A.append(((i, j), r, 'infected_up'))
                    if i != n - 1 and observations[r][i+1][j] in ['S', '?']:
                        A.append(((i, j), r, 'infected_down'))

                if sc in ['S', '?']:
                    A.append(((i, j), r, 'healed'))

                    if r != len(observations)-1 and observations[r+1][i][j] == 'Q':
                        must_q.append((i, j))
                    else:
                        sick_list.append((i, j))

                if sc in ['Q', '?'] and no_police > 0:
                    A.append(((i, j), r, 'free'))

        if no_medics > 0:
            vaccinate_range = range(min(no_medics - len(must_v), len(healthy_list) - no_question_marks),
                                    min(no_medics - len(must_v) + 1, len(healthy_list) + 1))

            vaccinate_actions = list(chain.from_iterable(combinations(healthy_list, i) for i in vaccinate_range))
            final_vaccinate_actions = []
            for va in vaccinate_actions:
                final_vaccinate_actions.append(tuple(list(va) + must_v))

            A.extend([(loc, r, 'vaccinate') for loc in final_vaccinate_actions])

        if no_police > 0:
            quarantine_range = range(min(no_police - len(must_q), len(sick_list) - no_question_marks),
                                     min(no_police - len(must_q) + 1, len(sick_list) + 1))

            quarantine_actions = list(chain.from_iterable(combinations(sick_list, i) for i in quarantine_range))
            final_quarantine_actions = []
            for qa in quarantine_actions:
                final_quarantine_actions.append(tuple(list(qa) + must_q))

            A.extend([(loc, r, 'quarantine') for loc in final_quarantine_actions])

    return A


def get_translation_dictionary(dvs, start_index):
    dv_to_atom = {}

    for i, dv in enumerate(dvs):
        dv_to_atom[dv] = start_index + i

    return dv_to_atom


def get_decision_variables_p(state_codes, indices_list, no_rounds):
    P = []

    for loc in indices_list:
        for r in range(no_rounds):
            for sc in state_codes:
                P.append((loc, r, sc))

    return P
