import numpy as np
from utils import vector_add
from pysat.solvers import Glucose4
from itertools import combinations

ids = ['204729636', '201555760']


def solve_problem(input):
    police = input["police"]
    medics = input["medics"]
    observations = input["observations"]
    queries = input["queries"]

    timespan = len(observations)
    X = len(observations[0])
    Y = len(observations[0][0])

    states = ['H', 'S', 'U', 'Q', 'I']
    actions = ['P', 'M']
    if police == 0:
        states.remove('Q')
        actions.remove('P')
    if medics == 0:
        states.remove('I')
        actions.remove('M')

    states_boolean_encoding = {state: np.zeros((X, Y, timespan)) for state in states}
    if police == 0 and medics == 0:
        kb = generate_no_actions_knowledge_base(observations, states_boolean_encoding)
    else:
        actions_encoding = {action: np.zeros((X, Y, timespan)) for action in actions}
        if police > 0 and medics == 0:
            kb = generate_no_medics_knowledge_base(observations, states_boolean_encoding, actions_encoding, police)
        elif police == 0 and medics > 0:
            kb = generate_no_police_knowledge_base(observations, states_boolean_encoding, actions_encoding, medics)
        else:
            kb = generate_general_knowledge_base(observations, states_boolean_encoding, actions_encoding, police,
                                                 medics)
    kb += evidence_clauses(observations, states_boolean_encoding)

    return check_queries(queries, kb, states_boolean_encoding)



def generate_no_actions_knowledge_base(observations, states_boolean_encoding):

    timespan = len(observations)
    generate_literals_encoding(states_boolean_encoding)

    knowledge_base = []
    for t in range(timespan):
        if t == 0:
            knowledge_base += unique_state_clauses(states_boolean_encoding, 0)
        if t == 1 or t == 2:
            knowledge_base += no_actions_first_and_second_clauses(states_boolean_encoding, t)
        if t >= 3:
            knowledge_base += no_actions_clauses(states_boolean_encoding, t)
    return knowledge_base


def generate_no_medics_knowledge_base(observations, states_encoding, actions_encoding, police_teams):
    timespan = len(observations)
    generate_literals_encoding(states_encoding, actions_encoding)

    kb = []
    for t in range(timespan):
        if t == 0:
            kb += unique_state_clauses(states_encoding, 0)
            kb += no_medics_unique_initial_clauses(states_encoding, actions_encoding, police_teams)
        if t == 1 or t == 2:
            kb += no_medics_first_and_second_clauses(states_encoding, actions_encoding, police_teams, t)
        if t >= 3:
            kb += no_medics_clauses(states_encoding, actions_encoding, police_teams, t)

    return kb


def generate_no_police_knowledge_base(observations, states_encoding, actions_encoding, medics):

    timespan = len(observations)
    generate_literals_encoding(states_encoding, actions_encoding)

    kb = []
    for t in range(timespan):
        if t == 0:
            kb += unique_state_clauses(states_encoding, 0)
            kb += no_police_unique_initial_clauses(states_encoding, actions_encoding, medics)
        if t == 1 or t == 2:
            kb += no_police_first_and_second_clauses(states_encoding, actions_encoding, medics, t)
        if t > 2:
            kb += no_police_clauses(states_encoding, actions_encoding, medics, t)

    return kb


def generate_general_knowledge_base(observations, states_encoding, actions_encoding, police, medics):

    timespan = len(observations)
    generate_literals_encoding(states_encoding, actions_encoding)
    kb = []
    for t in range(timespan):
        if t == 0:
            kb += initial_clauses(states_encoding, actions_encoding, police, medics)
        if t == 1 or t == 2:
            kb += general_first_and_second_clauses(states_encoding, actions_encoding, police, medics, t)
        if t > 2:
            kb += general_clauses(states_encoding, actions_encoding, police, medics, t)

    kb += evidence_clauses(observations, states_encoding)
    return kb


def generate_literals_encoding(states_boolean_encoding, actions_encoding=None):
    X = states_boolean_encoding['H'].shape[0]
    Y = states_boolean_encoding['H'].shape[1]
    T = states_boolean_encoding['H'].shape[2]

    i = 1

    for t in range(T):
        for x in range(X):
            for y in range(Y):
                for state in states_boolean_encoding:
                    states_boolean_encoding[state][x, y, t] = i
                    i += 1

                if actions_encoding:
                    for action in actions_encoding:
                        actions_encoding[action][x, y, t] = i
                        i += 1

    for state in states_boolean_encoding:
        states_boolean_encoding[state] = states_boolean_encoding[state].astype(int)

    if actions_encoding:
        for action in actions_encoding:
            actions_encoding[action] = actions_encoding[action].astype(int)


def unique_state_clauses(states_encoding, t):
    formula = []
    X = states_encoding['H'].shape[0]
    Y = states_encoding['H'].shape[1]
    states = states_encoding.keys()
    pairs = list(combinations(states, r=2))
    for x in range(X):
        for y in range(Y):

            # if this state then no other state
            for this, other in pairs:
                formula.append([-states_encoding[this][x, y, t], -states_encoding[other][x, y, t]])

            # at least one state must be true
            formula.append([states_encoding[state][x, y, t] for state in states])

    return formula


def no_medics_unique_initial_clauses(states_encoding, actions_encoding, police_teams):
    formula = []
    formula += action_state_clauses(actions_encoding["P"], states_encoding["S"], police_teams, 0)

    Q = states_encoding["Q"]
    X = Q.shape[0]
    Y = Q.shape[1]
    # no Q (Quarantined tile) in initial state:
    for x in range(X):
        for y in range(Y):
            formula.append([-Q[x, y, 0]])

    return formula


def no_police_unique_initial_clauses(states_encoding, actions_encoding, medics_teams):
    formula = []
    formula += action_state_clauses(actions_encoding["M"], states_encoding["H"], medics_teams, 0)

    I = states_encoding["I"]
    X = I.shape[0]
    Y = I.shape[1]
    # no I (vaccinated tile) in initial state:
    for x in range(X):
        for y in range(Y):
            formula.append([-I[x, y, 0]])

    return formula


def initial_clauses(states_encoding, actions_encoding, police_teams, medics_teams):
    """
    General case - apply when all teams exist
    """
    formula = []
    formula += unique_state_clauses(states_encoding, 0)
    formula += no_medics_unique_initial_clauses(states_encoding, actions_encoding, police_teams)
    formula += no_police_unique_initial_clauses(states_encoding, actions_encoding, medics_teams)

    return formula


def no_actions_first_and_second_clauses(states_encoding, t):
    """
    Quarantine(x, y, t) => Police(x, y, t-1)
    healthy[t] ==> healthy(t-1) & ~sick_neighbors[t-1]
    unpopulated[t] ==> unpopulated(t-1)
    sick ==> sick(t-1) | (healthy(t-1) & sick_neighbor(t-1)) ==
            == (sick(t-1) | healthy(t-1)) &  (sick(t-1) | sick_neighbor(t-1))
    """

    if t != 1 and t != 2:
        print("timestamp does not match clauses generation method")
        return

    formula = []
    formula += unique_state_clauses(states_encoding, t)
    H = states_encoding["H"]
    S = states_encoding["S"]
    U = states_encoding["U"]

    X = H.shape[0]
    Y = H.shape[1]
    for x in range(X):
        for y in range(Y):

            # unpopulated[t] ==> unpopulated[t-1]
            # unpopulated[t-1] ==> unpopulated[t]
            formula.append([-U[x, y, t], U[x, y, t-1]])
            formula.append([-U[x, y, t-1], U[x, y, t]])

            # healthy[t] ==> healthy[t-1]
            formula.append([-H[x, y, t], H[x, y, t-1]])

            # sick[t-1] ==> sick[t]
            formula.append([-S[x, y, t-1], S[x, y, t]])
            # sick[t] ==> sick[t-1] | healthy[t-1]
            formula.append([-S[x, y, t], S[x, y, t-1], H[x, y, t-1]])

            adjacent_neighbors = neighbors((x, y), (X, Y))
            # construct gradually the clause of  (was_sick(t-1) OR one_of_neighbor_was_sick(t-1))
            sick_neighbors = []

            for neighbor_x, neighbor_y in adjacent_neighbors:
                # healthy[t] ==> ~sick_neighbor[t-1]
                formula.append([-H[x, y, t], -S[neighbor_x, neighbor_y, t-1]])
                # sick_neighbor[t-1] & healthy[t-1] ==> S[t]
                formula.append([-S[neighbor_x, neighbor_y, t-1], -H[x, y, t-1], S[x, y, t]])
                sick_neighbors.append(S[neighbor_x, neighbor_y, t-1])

            formula.append([-S[x, y, t], S[x, y, t-1]] + sick_neighbors)
            # H[t-1] & ~S[x-1, y, t-1] & ~S[x+1, y, t-1] & ~ S[x, y+1, t-1] ... ==> H[t]
            formula.append([-H[x, y, t-1], H[x, y, t]]+sick_neighbors)

    return formula


def no_medics_first_and_second_clauses(states_encoding, actions_encoding, police_teams, t):
    """
    quarantined[t] ==> Police[t-1] | Quarantined[t-1]
    healthy[t] ==> healthy(t-1) & [~sick_neighbor[t-1] | police_sick_neighbor[t-1] ] (for all neighbors)
    """

    if t != 1 and t != 2:
        print("timestamp does not match clauses generation method")
        return

    formula = []
    formula += unique_state_clauses(states_encoding, t)
    H = states_encoding["H"]
    S = states_encoding["S"]
    U = states_encoding["U"]
    Q = states_encoding["Q"]
    P = actions_encoding["P"]
    formula += action_state_clauses(P, S, police_teams, t)

    X = H.shape[0]
    Y = H.shape[1]

    for x in range(X):
        for y in range(Y):
            # Q[x, y, t] ==> Q[x, y, t-1] | P[x, y, t-1]
            # Q[x, y, t-1] ==> Q[x, y, t]
            # P[x, y, t-1] ==> Q[x, y, t]
            formula.append([-Q[x, y, t], P[x, y, t-1], Q[x, y, t-1]])
            # check whether this helps/interrupts:
            formula.append([-P[x, y, t-1], Q[x, y, t]])
            formula.append([-Q[x, y, t-1], Q[x, y, t]])

            # U[x, y, t] ==> U[x, y, t-1]
            # U[x, y, t-1] ==> U[x, y, t]
            formula.append([-U[x, y, t], U[x, y, t-1]])
            formula.append([-U[x, y, t-1], U[x, y, t]])

            # if healthy[t] then was healthy[t-1]
            formula.append([-H[x, y, t], H[x, y, t-1]])

            adjacent_neighbors = neighbors((x, y), (X, Y))
            for neighbor_x, neighbor_y in adjacent_neighbors:
                # healthy[t] ==> ~sick_neighbor[t-1] | police_at_neighbor[t-1]
                formula.append([-H[x, y, t], -S[neighbor_x, neighbor_y, t-1], P[neighbor_x, neighbor_y, t-1]])

                # healthy[t-1] & sick_neighbor[t-1] & ~police_sick_neighbor[t-1] ==> sick[t]
                # formula.append([~H[x, y, t-1], ~S[neighbor_x, neighbor_y, t-1], P[neighbor_x, neighbor_y, t-1],
                #                 S[x, y, t]])

            # sick[t-1] & ~police[t-1] ==> sick[t]
            formula.append([-S[x, y, t-1], P[x, y, t-1], S[x, y, t]])

            # sick[t] ==> (sick[t-1] & ~police[t-1]) |
            #               (H[t-1] & [(sick_neighbor1[t-1] & ~police_sick_neighbor[t-1]) |
            #                          (sick_neighbor2[t-1] & ~police_sick_neighbor[t-1]) | ... ])
            formula += [[-S[x, y, t], S[x, y, t - 1], H[x, y, t - 1]], [-S[x, y, t], -P[x, y, t - 1], H[x, y, t - 1]]]
            clause_prefix = [[-S[x, y, t], S[x, y, t - 1]], [-S[x, y, t], -P[x, y, t - 1]]]

            if len(adjacent_neighbors) == 2:
                neighbors_suffix = two_neighbor_suffix(adjacent_neighbors, t, S, P)
            elif len(adjacent_neighbors) == 3:
                neighbors_suffix = three_neighbor_suffix(adjacent_neighbors, t, S, P)
            else:
                neighbors_suffix = four_neighbor_suffix(adjacent_neighbors, t, S, P)
            formula += [base_cond + neighbor_cond for base_cond in clause_prefix
                        for neighbor_cond in neighbors_suffix]

    return formula


def no_actions_clauses(states_encoding, t):
    """
    healthy[t] ==> (healthy[t-1] & ~sick_neighbors[t-1]) | (sick(t-1) & sick(t-2) & sick (t-3)) ==
                == (healthy[t-1] | sick[t-1] ) & (healthy[t-1] | sick[t-2]) & (healthy[t-1] | sick[t-3] )
                   & ( ~sick_neighbors[t-1] | sick(t-1) ) & ( ~sick_neighbors[t-1] | sick(t-2) ) &
                   ( ~sick_neighbors[t-1] | sick(t-3) )

    sick[t] ==> (sick[t-1] & (~sick[t-2] | ~sick[t-3]) | (healthy[t-1] & sick_neighbor[t-1]) ===
                (sick[t-1]| healthy[t-1] ) & (healthy[t-1] | ~sick[t-2] | ~sick[t-3])&
                (sick[t-1] | sick_neighbors[t-1]) & (~sick[t-2] | ~sick[t-3] | sick_neighbors[t-1])
    """
    if t < 3:
        print("timestamp does not match clauses generation method")
        return

    formula = []
    formula += unique_state_clauses(states_encoding, t)

    H = states_encoding["H"]
    S = states_encoding["S"]
    U = states_encoding["U"]

    X = H.shape[0]
    Y = H.shape[1]

    for x in range(X):
        for y in range(Y):

            # if unpopulated[t] ==> unpopulated[t-1]
            formula.append([-U[x, y, t], U[x, y, t-1]])
            # if unpopulated[t-1] ==> unpopulated[t]
            formula.append([-U[x, y, t-1], U[x, y, t]])

            # S[t-1] & S[t-2] & S[t-3] ==> H[t]
            formula.append([-S[x, y, t-1], -S[x, y, t-2], -S[x, y, t-3], H[x, y, t]])

            # S[t-1] & ~S[t-2] ==> S[t]
            formula.append([-S[x, y, t-1], S[x, y, t-2], S[x, y, t]])

            adjacent_neighbors = neighbors((x, y), (X, Y))

            # H[x, y, t] ==> (S[t-1] & S[t-2] & S[t-3]) | (H[x, y, t-1] & ~S[x+1, y, t-1] & ~S[x-1, y, t-1]...)
            healthy_condition_prefixes = [[-H[x, y, t], S[x, y, t-1]], [-H[x, y, t], S[x, y, t-2]],
                                          [-H[x, y, t], S[x, y, t-3]]]
            healthy_condition_suffixed = [[H[x, y, t-1]]]
            sick_neighbors = []
            for neighbor_x, neighbor_y in adjacent_neighbors:
                healthy_condition_suffixed.append([-S[neighbor_x, neighbor_y, t-1]])

                # H[t-1] & sick_neighbor[t-1] ==> S[t]
                formula.append([-H[x, y, t-1], -S[neighbor_x, neighbor_y, t-1], S[x, y, t]])

                # build or clause between sick neighbors sick conditions
                sick_neighbors.append(S[neighbor_x, neighbor_y, t-1])

            formula += [prefix + suffix for prefix in healthy_condition_prefixes
                        for suffix in healthy_condition_suffixed]

            # S[t] ==> (S[t-1] & (~S[t-2] | ~ S[t-3]) | (H[t-1] & (S[x+1, y, t-1] | S[x-1, y, t-1]...))
            sick_condition_prefixes = [[-S[x, y, t], S[x, y, t-1]], [-S[x, y, t], -S[x, y, t-2], -S[x, y, t-3]]]
            sick_condition_suffixes = [[H[x, y, t-1]], sick_neighbors]
            formula += [prefix + suffix for prefix in sick_condition_prefixes
                        for suffix in sick_condition_suffixes]

    return formula


def evidence_clauses(observations, states_encoding):
    formula = []
    t = 0
    for observation in observations:
        for x in range(len(observation)):
            for y in range(len(observation[0])):
                state = observation[x][y]
                if state != "?":
                    formula.append([states_encoding[state][x, y, t]])
        t += 1
    return formula


def check_queries(queries, kb, states_encoding):

    g = Glucose4()
    for clause in kb:
        g.add_clause(map(int, clause))

    answers = dict()
    for query in queries:
        x, y = query[0]
        t = query[1]
        state = query[2]
        if not g.solve(assumptions=map(int, [states_encoding[state][x, y, t]])):
            answers[query] = 'F'
        elif g.solve(assumptions=map(int, [-states_encoding[state][x, y, t]])):
            answers[query] = '?'
        else:
            answers[query] = 'T'

    g.delete()
    return answers


def neighbors(coordinate, tile_size):
    available = [(-1, 0), (1, 0), (0, 1), (0, -1)]
    x = coordinate[0]
    y = coordinate[1]
    X = tile_size[0]
    Y = tile_size[1]
    if x == 0:
        available.remove((-1, 0))
    if x == X-1:
        available.remove((1, 0))
    if y == 0:
        available.remove((0, -1))
    if y == Y-1:
        available.remove((0, 1))

    return [vector_add(coordinate, elem) for elem in available]


def action_state_clauses(action, applied_state, teams, t):
    """
    Generate all basic conditions of applying an action on tile:
    1. Action(P/M) on (x,y,t) ==> necessary_state(S/H) at (x, y, t)
    2. No more than number_of_teams actions can be applied at time T
    3. Use maximum possible teams at each turn

    For police = [action = P, applied_state = S, teams = number_of_police_teams]
    For medics = [action = M, applied_state = H, teams = number_of_medics_teams]

    """

    formula = []
    X = applied_state.shape[0]
    Y = applied_state.shape[1]
    # police action can be made only on sick tiles
    for x in range(X):
        for y in range(Y):
            formula.append([-action[x, y, t], applied_state[x, y, t]])

    #  no more than police_teams actions a turn: not allowing more than #p_teams coordinates to be true
    # Taking for example police_teams=2, the clauses are of the form:
    # ~P(x1, y1, t) | ~P(x2, y2, t) | ~P(x3, y3, t) for each triplet (x1, y1), (x2, y2), (x3, y3)
    # (if two first literals evaluate as True, then the third one must be false)
    coordinates = [(x, y) for x in range(X) for y in range(Y)]

    # creating combinations of size police_teams+1
    coordinates_comb = list(combinations(coordinates, r=teams+1))
    for elem in coordinates_comb:
        clause = []
        for coordinate in elem:
            clause.append(-action[coordinate[0], coordinate[1], t])
        formula.append(clause)

    # use max police available: if s(x,y,t) ==> p(x,y,t) | applied all your #police teams on other tiles
    # the clauses are of the form: ~s(x,y,t) | p(x,y,t) | (OR combination of (X*Y-1)-(#p_teams-1) = X*Y - p coordinates)
    # when going for all the (X*Y-1)-(#p_teams-1) combinations that does not include x,y,t. Thus, we are not allowing
    # police on just #p_teams - 1 coordinates.
    for x in range(X):
        for y in range(Y):
            relevant_coordinates = set(coordinates)
            relevant_coordinates.discard((x, y))
            coordinates_comb = list(combinations(relevant_coordinates, r=X*Y - teams))
            for elem in coordinates_comb:
                clause = [-applied_state[x, y, t], action[x, y, t]]
                for coordinate in elem:
                    clause.append(action[coordinate[0], coordinate[1], t])
                formula.append(clause)

    return formula


def no_medics_clauses(states_encoding, actions_encoding, police_teams, t):
    if t < 3:
        print("timestamp does not match clauses generation method")
        return

    formula = []
    formula += unique_state_clauses(states_encoding, t)
    H = states_encoding["H"]
    S = states_encoding["S"]
    U = states_encoding["U"]
    Q = states_encoding["Q"]
    P = actions_encoding["P"]
    formula += action_state_clauses(P, S, police_teams, t)

    X = H.shape[0]
    Y = H.shape[1]

    for x in range(X):
        for y in range(Y):
            # U[t] ==> U[t-1]
            formula.append([-U[x, y, t], U[x, y, t-1]])
            # U[t-1] ==> U[t]
            formula.append([-U[x, y, t-1], U[x, y, t]])
            # Q[t] ==> P[t-1] | (Q[t-1] & ~Q[t-2]) = (P[t-1] | Q[t-1]) & (P[t-1] | ~Q[t-2])
            formula.append([-Q[x, y, t], P[x, y, t-1], Q[x, y, t-1]])
            formula.append([-Q[x, y, t], P[x, y, t-1], -Q[x, y, t-2]])
            # P[t-1] ==> Q[t]
            formula.append([-P[x, y, t-1], Q[x, y, t]])
            # Q[t-1] & ~Q[t-2] ==> Q[t]
            formula.append([-Q[x, y, t-1], Q[x, y, t-2], Q[x, y, t]])
            # Q[t-1] & Q[t-2] ==> H[t]
            formula.append([-Q[x, y, t-1], -Q[x, y, t-2], H[x, y, t]])
            # S[t-1] & ~P[t-1] & S[t-2] & S[t-3] ==> H[t]
            formula.append([-S[x, y, t-1], P[x, y, t-1], -S[x, y, t-2], -S[x, y, t-3], H[x, y, t]])

            # H[t] ==> (S[t-1]& -P[t-1] & S[t-2] & S[t-3]) |
            #           (Q[t-1] & Q[t-2]) |
            #           (H[t-1] & (-Sick_neighbor1[t-1] | P_neighbor1[t-1]) &
            #                     (-sick_neighbor2[t-1] | P_neighbor2[t-1]) &...)
            adjacent_neighbors = neighbors((x, y), (X, Y))
            formula += healthy_clauses_with_police(x, y, t, adjacent_neighbors, H, P, S, Q, immune=False)

            # H[t-1] & sick_neighbor[t-1] & ~Q_sick_neighbor[t-1] ==> S[t]
            for neighbor_x, neighbor_y in adjacent_neighbors:
                formula.append([-H[x, y, t-1], -S[neighbor_x, neighbor_y, t-1], Q[neighbor_x, neighbor_y, t-1],
                                H[x, y, t]])

            # S[t] ==> [S[t-1]& -P[t-1] & (~S[t-2] | ~S[t-3])] |
            #           {H[t-1] & [(sick_neighbor1[t-1] & ~police_neighbor1[t-1]) |
            #                      (sick_neighbor2[t-1] & ~police_neighbor2[t-1]) |...]}
            formula += [[-S[x, y, t], S[x, y, t-1], H[x, y, t-1]],
                        [-S[x, y, t], -P[x, y, t-1], H[x, y, t-1]],
                        [-S[x, y, t], H[x, y, t-1], -S[x, y, t-2], -S[x, y, t-3]]]

            clause_prefix = [[-S[x, y, t], S[x, y, t-1]], [-S[x, y, t], -P[x, y, t-1]],
                             [-S[x, y, t], -S[x, y, t-2], -S[x, y, t-3]]]

            if len(adjacent_neighbors) == 2:
                neighbors_suffix = two_neighbor_suffix(adjacent_neighbors, t, S, P)
            elif len(adjacent_neighbors) == 3:
                neighbors_suffix = three_neighbor_suffix(adjacent_neighbors, t, S, P)
            else:
                neighbors_suffix = four_neighbor_suffix(adjacent_neighbors, t, S, P)
            formula += [base_cond + neighbor_cond for base_cond in clause_prefix
                        for neighbor_cond in neighbors_suffix]

    return formula


def no_police_first_and_second_clauses(states_encoding, actions_encoding, medics, t):

    if t != 1 and t != 2:
        print("timestamp does not match clauses generation method")
        return

    formula = []
    formula += unique_state_clauses(states_encoding, t)
    H = states_encoding["H"]
    S = states_encoding["S"]
    U = states_encoding["U"]
    I = states_encoding["I"]
    M = actions_encoding["M"]
    formula += action_state_clauses(M, H, medics, t)

    X = H.shape[0]
    Y = H.shape[1]

    for x in range(X):
        for y in range(Y):
            # U[x, y, t] ==> U[x, y, t-1]
            # U[x, y, t-1] ==> U[x, y, t]
            formula.append([-U[x, y, t], U[x, y, t - 1]])
            formula.append([-U[x, y, t - 1], U[x, y, t]])

            # I[x, y, t] ==> I[x, y, t-1] | M[x, y, t-1]
            # M[x, y, t-1] ==> I[x, y, t]
            # I[x, y, t-1] ==> I[x, y, t]
            formula.append([-I[x, y, t], I[x, y, t-1], M[x, y, t-1]])
            formula.append([-I[x, y, t-1], I[x, y, t]])
            formula.append([-M[x, y, t-1], I[x, y, t]])

            # H[x, y, t] ==> H[x, y, t-1] & ~M[x, y, t-1] & ~S[x+1, y, t-1] & ~S[x-1, y, t-1]
            #                 & ~S[x, y+1, t-1] & ~S[x, y-1, t-1]
            formula.append([-H[x, y, t], H[x, y, t-1]])
            formula.append([-H[x, y, t], -M[x, y, t-1]])

            adjacent_neighbors = neighbors((x, y), (X, Y))
            for neighbor_x, neighbor_y in adjacent_neighbors:
                formula.append([-H[x, y, t], -S[neighbor_x, neighbor_y, t-1]])

            # S[x, y, t] ==> S[x, y, t-1] | [H[x, y, t-1] & ~M[x, y, t-1] & (
            #                  S[x+1, y, t-1] | S[x-1, y, t-1] | S[x, y+1, t-1] | S[x, y-1, t-1])]
            # Equivalent to:
            # (~S[x, y, t] | S[x, y, t-1] | H[x, y, t-1]) & (~S[x, y, t] | S[x, y, t-1]| ~M[x, y, t-1])
            # & (~S[x, y, t] | S[x, y, t-1] | S[x+1, y, t-1] | S[x-1, y, t-1] | S[x, y+1, t-1] | S[x, y-1, t-1])
            formula.append([-S[x, y, t], S[x, y, t-1], H[x, y, t-1]])
            formula.append([-S[x, y, t], S[x, y, t-1], -M[x, y, t-1]])
            sick_neighbors = []
            for neighbor_x, neighbor_y in adjacent_neighbors:
                sick_neighbors.append(S[neighbor_x, neighbor_y, t-1])

            formula.append([-S[x, y, t], S[x, y, t-1]]+sick_neighbors)

    return formula


def no_police_clauses(states_encoding, actions_encoding, medics, t):

    if t < 3:
        print("timestamp does not match clauses generation method")
        return

    formula = []
    formula += unique_state_clauses(states_encoding, t)
    H = states_encoding["H"]
    S = states_encoding["S"]
    U = states_encoding["U"]
    I = states_encoding["I"]
    M = actions_encoding["M"]
    formula += action_state_clauses(M, H, medics, t)

    X = H.shape[0]
    Y = H.shape[1]

    for x in range(X):
        for y in range(Y):
            # U[x, y, t] ==> U[x, y, t-1]
            # U[x, y, t-1] ==> U[x, y, t]
            formula.append([-U[x, y, t], U[x, y, t - 1]])
            formula.append([-U[x, y, t - 1], U[x, y, t]])

            # I[x, y, t] ==> I[x, y, t-1] | M[x, y, t-1]
            # M[x, y, t-1] ==> I[x, y, t]
            # I[x, y, t-1] ==> I[x, y, t]
            formula.append([-I[x, y, t], I[x, y, t-1], M[x, y, t-1]])
            formula.append([-I[x, y, t-1], I[x, y, t]])
            formula.append([-M[x, y, t-1], I[x, y, t]])

            # H[x, y, t] ==>(S[x, y, t-1] & S[x, y, t-2] & S[x, y, t-3]) |
            #                (H[x, y, t-1] & ~M[x, y, t-1] & ~S[x+1, y, t-1] & ~S[x-1, y, t-1] & ~S[x, y+1, t-1] &
            #                ~S[x, y-1, t-1])
            formula += [[-H[x, y, t], H[x, y, t-1], S[x, y, t-1]], [-H[x, y, t], H[x, y, t-1], S[x, y, t-2]],
                        [-H[x, y, t], H[x, y, t-1], S[x, y, t-3]], [-H[x, y, t], -M[x, y, t-1], S[x, y, t-1]],
                        [-H[x, y, t], -M[x, y, t-1], S[x, y, t-2]], [-H[x, y, t], -M[x, y, t-1], S[x, y, t-3]]]

            adjacent_neighbors = neighbors((x, y), (X, Y))
            for neighbor_x, neighbor_y in adjacent_neighbors:
                formula += [[-H[x, y, t], S[x, y, t-1], -S[neighbor_x, neighbor_y, t-1]],
                            [-H[x, y, t], S[x, y, t - 2], -S[neighbor_x, neighbor_y, t - 1]],
                            [-H[x, y, t], S[x, y, t - 3], -S[neighbor_x, neighbor_y, t - 1]]]


            # S[x, y, t] == > [S[x, y, t - 1] & (~S[x, y, t-2] | ~S[x, y, t-3])] |
            #                 [H[x, y, t - 1] & ~M[x, y, t - 1] & ( S[x+1, y, t-1] | S[x-1, y, t-1] |
            #                 S[x, y+1, t-1] | S[x, y-1, t-1])]
            formula += [[-S[x, y, t], S[x, y, t - 1], H[x, y, t - 1]],
                        [-S[x, y, t], S[x, y, t - 1], -M[x, y, t - 1]],
                        [-S[x, y, t], H[x, y, t - 1], -S[x, y, t - 2], -S[x, y, t - 3]],
                        [-S[x, y, t], -M[x, y, t - 1], -S[x, y, t - 2], -S[x, y, t - 3]]]

            neighbors_condition = []
            for neighbor_x, neighbor_y in adjacent_neighbors:
                neighbors_condition.append(S[neighbor_x, neighbor_y, t-1])
            formula.append([-S[x, y, t], S[x, y, t - 1]] + neighbors_condition)
            formula.append([-S[x, y, t], -S[x, y, t - 2], -S[x, y, t - 3]] + neighbors_condition)

    return formula

def general_first_and_second_clauses(states_encoding, actions_encoding, police, medics, t):
    if t != 1 and t != 2:
        print("timestamp does not match clauses generation method")
        return

    formula = []
    formula += unique_state_clauses(states_encoding, t)
    H = states_encoding["H"]
    S = states_encoding["S"]
    U = states_encoding["U"]
    Q = states_encoding["Q"]
    I = states_encoding["I"]
    P = actions_encoding["P"]
    M = actions_encoding["M"]
    formula += action_state_clauses(P, S, police, t)
    formula += action_state_clauses(M, H, medics, t)

    X = H.shape[0]
    Y = H.shape[1]

    for x in range(X):
        for y in range(Y):
            # U[x, y, t] ==> U[x, y, t-1]
            # U[x, y, t-1] ==> U[x, y, t]
            formula.append([-U[x, y, t], U[x, y, t - 1]])
            formula.append([-U[x, y, t - 1], U[x, y, t]])

            # I[x, y, t] ==> I[x, y, t-1] | M[x, y, t-1]
            # I[x, y, t-1] ==> I[x, y, t]
            # M[x, y, t-1] ==> I[x, y, t]
            formula.append([-I[x, y, t], I[x, y, t-1], M[x, y, t-1]])
            formula.append([-I[x, y, t-1], I[x, y, t]])
            formula.append([-M[x, y, t - 1], I[x, y, t]])

            # Q[x, y, t] ==> Q[x, y, t-1] | P[x, y, t-1]
            # Q[x, y, t-1] ==> Q[x, y, t]
            # P[x, y, t-1] ==> Q[x, y, t]
            formula.append([-Q[x, y, t], P[x, y, t - 1], Q[x, y, t - 1]])
            formula.append([-P[x, y, t - 1], Q[x, y, t]])
            formula.append([-Q[x, y, t - 1], Q[x, y, t]])

            # S[t-1] & ~P[t-1] ==> S[t]
            formula.append([-S[x, y, t-1], P[x, y, t-1], S[x, y, t]])

            # H[x, y, t] ==> H[x, y, t-1] & ~M[x, y, t-1] & (~S[x+1, y, t-1] | P[x+1, y, t-1]) &
            #                 & (~S[x-1, y, t-1] | P[x-1, y, t-1]) (~S[x, y+1, t-1] | P[x, y+1, t-1]) &
            #               (~S[x, y-1, t-1] | P[x, y-1, t-1])
            formula.append([-H[x, y, t], H[x, y, t-1]])
            formula.append([-H[x, y, t], -M[x, y, t-1]])
            adjacent_neighbors = neighbors((x, y), (X, Y))
            for neighbor_x, neighbor_y in adjacent_neighbors:
                formula.append([-H[x, y, t], -S[neighbor_x, neighbor_y, t-1], P[neighbor_x, neighbor_y, t-1]])
                # H[t-1] & ~M[t-1] & Sick_neighbor[t-1] & ~Police_sick_neighbor[t-1] ==> sick[t]
                # formula.append([-H[x, y, t-1], M[x, y, t-1], -S[neighbor_x, neighbor_y, t-1],
                #                 P[neighbor_x, neighbor_y, t-1], S[x, y, t]])

            # S[x, y, t] ==> (S[x, y, t-1] & ~P[x, y, t-1]) | {H[x, y, t-1] & ~M[x, y, t-1] &
            #                   [(S[x+1, y, t-1] & ~P[x+1, y, t-1]) | (S[x-1, y, t-1] & ~P[x-1, y, t-1]) |
            #                      (S[x, y+1, t-1] & ~P[x, y+1, t-1]) | (S[x, y-1, t-1] & ~P[x, y-1, t-1])]}
            formula += [[-S[x, y, t], S[x, y, t - 1], -M[x, y, t - 1]], [-S[x, y, t], -P[x, y, t - 1], -M[x, y, t - 1]],
                        [-S[x, y, t], S[x, y, t - 1], H[x, y, t - 1]], [-S[x, y, t], -P[x, y, t - 1], H[x, y, t - 1]]]
            clause_prefix = [[-S[x, y, t], S[x, y, t - 1]], [-S[x, y, t], -P[x, y, t - 1]]]

            if len(adjacent_neighbors) == 2:
                neighbors_suffix = two_neighbor_suffix(adjacent_neighbors, t, S, P)
            elif len(adjacent_neighbors) == 3:
                neighbors_suffix = three_neighbor_suffix(adjacent_neighbors, t, S, P)
            else:
                neighbors_suffix = four_neighbor_suffix(adjacent_neighbors, t, S, P)
            formula += [base_cond + neighbor_cond for base_cond in clause_prefix
                        for neighbor_cond in neighbors_suffix]

    return formula


def general_clauses(states_encoding, actions_encoding, police, medics, t):
    if t < 3:
        print("timestamp does not match clauses generation method")
        return

    formula = []
    formula += unique_state_clauses(states_encoding, t)
    H = states_encoding["H"]
    S = states_encoding["S"]
    U = states_encoding["U"]
    Q = states_encoding["Q"]
    I = states_encoding["I"]
    P = actions_encoding["P"]
    M = actions_encoding["M"]
    formula += action_state_clauses(P, S, police, t)
    formula += action_state_clauses(M, H, medics, t)

    X = H.shape[0]
    Y = H.shape[1]

    for x in range(X):
        for y in range(Y):
            # U[x, y, t] ==> U[x, y, t-1]
            # U[x, y, t-1] ==> U[x, y, t]
            formula.append([-U[x, y, t], U[x, y, t - 1]])
            formula.append([-U[x, y, t - 1], U[x, y, t]])

            # I[x, y, t] ==> I[x, y, t-1] | M[x, y, t-1]
            # I[x, y, t-1] ==> I[x, y, t]
            # M[x, y, t-1] ==> I[x, y, t]
            formula.append([-I[x, y, t], I[x, y, t-1], M[x, y, t-1]])
            formula.append([-I[x, y, t-1], I[x, y, t]])
            formula.append([-M[x, y, t - 1], I[x, y, t]])

            # Q[t] ==> P[t-1] | (Q[t-1] & ~Q[t-2]) <==> (P[t-1] | Q[t-1]) & (P[t-1] | ~Q[t-2])
            formula.append([-Q[x, y, t], P[x, y, t-1], Q[x, y, t-1]])
            formula.append([-Q[x, y, t], P[x, y, t-1], -Q[x, y, t-2]])
            # P[x, y, t-1] ==> Q[x, y, t]
            formula.append([-P[x, y, t - 1], Q[x, y, t]])
            # Q[t-1] & ~Q[t-2] ==> Q[t]
            formula.append([-Q[x, y, t-1], Q[x, y, t-2], Q[x, y, t]])
            # Q[t-1] & Q[t-2] ==> H[t]
            formula.append([-Q[x, y, t-1], -Q[x, y, t-2], H[x, y, t]])
            # S[t-1] & ~P[t-1] & S[t-2] & S[t-3] ==> H[t]
            formula.append([-S[x, y, t-1], P[x, y, t-1], -S[x, y, t-2], -S[x, y, t-3], H[x, y, t]])
            # S[t-1] & ~P[t-1] & ~S[t-2] ==> S[t]
            formula.append([-S[x, y, t-1], P[x, y, t-1], S[x, y, t-2], S[x, y, t]])
            # S[t-1] & ~P[t-1] & S[t-2] & ~S[t-3] ==> S[t]
            # formula.append([-S[x, y, t - 1], P[x, y, t - 1], -S[x, y, t - 2], S[x, y, t-3], S[x, y, t]])

            adjacent_neighbors = neighbors((x, y), (X, Y))
            # for neighbor_x, neighbor_y in adjacent_neighbors:
            #     # H[t-1] & ~M[t-1] & Sick_neighbor[t-1] & ~Police_sick_neighbor[t-1] ==> sick[t]
            #     formula.append([-H[x, y, t-1], M[x, y, t-1], -S[neighbor_x, neighbor_y, t-1],
            #                     P[neighbor_x, neighbor_y, t-1], S[x, y, t]])

            # H[x, y, t] ==> (Q[t-2] & Q[t-1]) | (S[t-1] & ~P[t-1] & S[t-2] & S[t-3]) |
            #                (H[t-1] & ~M[t-1] & (~S[x+1, y, t-1] | Q[x+1, y, t-1]) &...)
            formula += healthy_clauses_with_police(x, y, t, adjacent_neighbors, H, P, S, Q, M, immune=True)

            # S[x, y, t] ==> [S[x, y, t-1] & ~P[x, y, t-1] & (~S[x, y, t-2] | ~S[x, y, t-3])] |
            #                [H[x, y, t-1] & ~M[x, y, t-1] & [(S[x+1, y, t-1] & ~P[x+1, y, t-1]) |
            #                (S[x-1, y, t-1] & ~P[x-1, y, t-1]) |...]}
            # clauses that are common to all neighbors possibilities
            formula += [[-S[x, y, t], S[x, y, t-1], H[x, y, t-1]],
                         [-S[x, y, t], S[x, y, t-1], -M[x, y, t-1]],
                         [-S[x, y, t], -P[x, y, t-1], H[x, y, t-1]],
                         [-S[x, y, t], -P[x, y, t-1], -M[x, y, t-1]],
                         [-S[x, y, t], H[x, y, t-1], -S[x, y, t-2], -S[x, y, t-3]],
                         [-S[x, y, t], -M[x, y, t-1], -S[x, y, t-2], -S[x, y, t-3]]]

            fixed_clause_prefix = [[-S[x, y, t], S[x, y, t-1]], [-S[x, y, t], -P[x, y, t-1]],
                                   [-S[x, y, t], -S[x, y, t-2], -S[x, y, t-3]]]

            if len(adjacent_neighbors) == 2:
                neighbors_suffix = two_neighbor_suffix(adjacent_neighbors, t, S, P)
            elif len(adjacent_neighbors) == 3:
                neighbors_suffix = three_neighbor_suffix(adjacent_neighbors, t, S, P)
            else:
                neighbors_suffix = four_neighbor_suffix(adjacent_neighbors, t, S, P)
            formula += [base_cond + neighbor_cond for base_cond in fixed_clause_prefix
                        for neighbor_cond in neighbors_suffix]

    return formula


def two_neighbor_suffix(adjacent_neighbors, t, S, P):
    xn1, yn1 = adjacent_neighbors[0]
    xn2, yn2 = adjacent_neighbors[1]
    return [[S[xn1, yn1, t-1], S[xn2, yn2, t-1]], [-P[xn1, yn1, t-1], S[xn2, yn2, t-1]],
            [S[xn1, yn1, t-1], -P[xn2, yn2, t-1]], [-P[xn1, yn1, t-1], -P[xn2, yn2, t-1]]]


def three_neighbor_suffix(adjacent_neighbors, t, S, P):
    xn1, yn1 = adjacent_neighbors[0]
    xn2, yn2 = adjacent_neighbors[1]
    xn3, yn3 = adjacent_neighbors[2]
    return [[S[xn1, yn1, t-1], S[xn2, yn2, t-1], S[xn3, yn3, t-1]],
            [-P[xn1, yn1, t-1], S[xn2, yn2, t-1], S[xn3, yn3, t-1]],
            [S[xn1, yn1, t-1], -P[xn2, yn2, t-1], S[xn3, yn3, t-1]],
            [S[xn1, yn1, t - 1], S[xn2, yn2, t - 1], -P[xn3, yn3, t - 1]],
            [-P[xn1, yn1, t - 1], -P[xn2, yn2, t - 1], S[xn3, yn3, t - 1]],
            [-P[xn1, yn1, t - 1], S[xn2, yn2, t - 1], -P[xn3, yn3, t - 1]],
            [S[xn1, yn1, t - 1], -P[xn2, yn2, t - 1], -P[xn3, yn3, t - 1]],
            [-P[xn1, yn1, t-1], -P[xn2, yn2, t-1], -P[xn3, yn3, t-1]]]


def four_neighbor_suffix(adjacent_neighbors, t, S, P):
    xn1, yn1 = adjacent_neighbors[0]
    xn2, yn2 = adjacent_neighbors[1]
    xn3, yn3 = adjacent_neighbors[2]
    xn4, yn4 = adjacent_neighbors[3]
    return [[S[xn1, yn1, t - 1], S[xn2, yn2, t - 1], S[xn3, yn3, t - 1], S[xn4, yn4, t - 1]],
            [-P[xn1, yn1, t - 1], S[xn2, yn2, t - 1], S[xn3, yn3, t - 1], S[xn4, yn4, t - 1]],
            [S[xn1, yn1, t - 1], -P[xn2, yn2, t - 1], S[xn3, yn3, t - 1], S[xn4, yn4, t - 1]],
            [S[xn1, yn1, t - 1], S[xn2, yn2, t - 1], -P[xn3, yn3, t - 1], S[xn4, yn4, t - 1]],
            [S[xn1, yn1, t - 1], S[xn2, yn2, t - 1], S[xn3, yn3, t - 1], -P[xn4, yn4, t - 1]],
            [S[xn1, yn1, t - 1], S[xn2, yn2, t - 1], -P[xn3, yn3, t - 1], -P[xn4, yn4, t - 1]],
            [S[xn1, yn1, t - 1], -P[xn2, yn2, t - 1], S[xn3, yn3, t - 1], -P[xn4, yn4, t - 1]],
            [S[xn1, yn1, t - 1], -P[xn2, yn2, t - 1], -P[xn3, yn3, t - 1], S[xn4, yn4, t - 1]],
            [-P[xn1, yn1, t - 1], -P[xn2, yn2, t - 1], S[xn3, yn3, t - 1], S[xn4, yn4, t - 1]],
            [-P[xn1, yn1, t - 1], S[xn2, yn2, t - 1], -P[xn3, yn3, t - 1], S[xn4, yn4, t - 1]],
            [-P[xn1, yn1, t - 1], S[xn2, yn2, t - 1], S[xn3, yn3, t - 1], -P[xn4, yn4, t - 1]],
            [S[xn1, yn1, t - 1], -P[xn2, yn2, t - 1], -P[xn3, yn3, t - 1], -P[xn4, yn4, t - 1]],
            [-P[xn1, yn1, t - 1], S[xn2, yn2, t - 1], -P[xn3, yn3, t - 1], -P[xn4, yn4, t - 1]],
            [-P[xn1, yn1, t - 1], -P[xn2, yn2, t - 1], S[xn3, yn3, t - 1], -P[xn4, yn4, t - 1]],
            [-P[xn1, yn1, t - 1], -P[xn2, yn2, t - 1], -P[xn3, yn3, t - 1], S[xn4, yn4, t - 1]],
            [-P[xn1, yn1, t - 1], -P[xn2, yn2, t - 1], -P[xn3, yn3, t - 1], -P[xn4, yn4, t - 1]]]


def healthy_clauses_with_police(x, y, t, adjacent_neighbors, H, P, S, Q, M= None, immune = False):

    condition_prefixes = [[-H[x, y, t], S[x, y, t-1], Q[x, y, t-1]],
                          [-H[x, y, t], S[x, y, t-2], Q[x, y, t-1]],
                          [-H[x, y, t], S[x, y, t - 3], Q[x, y, t - 1]],
                          [-H[x, y, t], S[x, y, t - 1], Q[x, y, t - 2]],
                          [-H[x, y, t], S[x, y, t - 2], Q[x, y, t - 2]],
                          [-H[x, y, t], S[x, y, t - 3], Q[x, y, t - 2]],
                          [-H[x, y, t], -P[x, y, t - 1], Q[x, y, t - 1]],
                          [-H[x, y, t], -P[x, y, t - 1], Q[x, y, t - 2]]]
    condition_suffixes = [[H[x, y, t-1]]]
    if immune:
        condition_suffixes.append([-M[x, y, t-1]])
    for neighbor_x, neighbor_y in adjacent_neighbors:
        condition_suffixes.append([-S[neighbor_x, neighbor_y, t-1], P[neighbor_x, neighbor_y, t-1]])
        
    return [prefix + suffix for prefix in condition_prefixes for suffix in condition_suffixes]

