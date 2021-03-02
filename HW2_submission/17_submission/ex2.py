from pysat.solvers import Glucose3
import itertools

ids = ['208241760', '205567514']


def solve_problem(input):
    states = ['S', 'I', 'H', 'Q', 'U']
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    n_cols = len(input['observations'][0][0])
    n_rows = len(input['observations'][0])
    num_turns = len(input['observations'])
    medics = input['medics']
    police = input['police']
    queries = input['queries']  # todo: check if [0] is necessary

    g = Glucose3()

    # variables creation:
    variables = [0]
    for i in range(n_rows):
        for j in range(n_cols):
            for turn in range(num_turns):
                for state in states:
                    variables.append(((i, j), turn, state))
                for counter in range(3):
                    variables.append(((i, j), turn, counter))

    # actions:
    for i in range(n_rows):
        for j in range(n_cols):
            for turn in range(num_turns - 1):
                variables.append(((i, j), turn, 'immune'))
                variables.append(((i, j), turn, 'quarantine'))

    # action_flags for vaccination:
    for turn in range(num_turns):
        for f in range(medics + 1):
            variables.append((turn, 'immune_flag', f))

    # action flags for quarantine:
    for turn in range(num_turns):
        for f in range(police + 1):
            variables.append((turn, 'quarantine_flag', f))

    # changed flag:
    for i in range(n_rows):
        for j in range(n_cols):
            for turn in range(num_turns):
                variables.append((turn, (i, j), 'changed'))

    # spreading
    for i in range(n_rows):
        for j in range(n_cols):
            for turn in range(num_turns):
                variables.append((turn, (i, j), 'spread'))

    m = {variables[i]: i for i in range(len(variables))}  # mapping our representation to integers for pysat

    # ------------------------------------------- #
    # clauses computation

    # immune action:
    for i in range(n_rows):
        for j in range(n_cols):
            for turn in range(num_turns - 1):
                # pre-conditions
                g.add_clause([-m[((i, j), turn, 'immune')],
                               m[((i, j), turn, 'H')]])
                # add-effects
                g.add_clause([-m[((i, j), turn, 'immune')],
                               m[((i, j), turn + 1, 'I')]])
                g.add_clause([-m[((i, j), turn, 'immune')],
                               m[(turn, (i, j), 'changed')]])

                # iff <==>
                g.add_clause([m[((i, j), turn, 'immune')],
                             -m[((i, j), turn, 'H')],
                             -m[((i, j), turn + 1, 'I')]])

    # quarantine action:
    for i in range(n_rows):
        for j in range(n_cols):
            for turn in range(num_turns - 1):
                # pre-conditions
                g.add_clause([-m[((i, j), turn, 'quarantine')],
                               m[((i, j), turn, 'S')]])
                # add-effects
                g.add_clause([-m[((i, j), turn, 'quarantine')],
                               m[((i, j), turn + 1, 'Q')]])
                g.add_clause([-m[((i, j), turn, 'quarantine')],
                               m[((i, j), turn + 1, 1)]])
                g.add_clause([-m[((i, j), turn, 'quarantine')],
                               m[(turn, (i, j), 'changed')]])

                # iff <==>
                g.add_clause([m[((i, j), turn, 'quarantine')],
                             -m[((i, j), turn, 'S')],
                             -m[((i, j), turn + 1, 'Q')]])

    # spread:
    for i in range(n_rows):
        for j in range(n_cols):
            for turn in range(num_turns - 1):
                for d in directions:
                    i2 = i + d[0]
                    j2 = j + d[1]
                    if 0 <= i2 < n_rows and 0 <= j2 < n_cols:
                        # change state to 'S'
                        g.add_clause([-m[((i, j), turn, 'S')],
                                       m[((i, j), turn + 1, 'Q')],
                                      -m[((i2, j2), turn, 'H')],
                                       m[((i2, j2), turn + 1, 'I')],
                                       m[((i2, j2), turn + 1, 'S')]])
                        # changed
                        g.add_clause([-m[((i, j), turn, 'S')],
                                       m[((i, j), turn + 1, 'Q')],
                                      -m[((i2, j2), turn, 'H')],
                                       m[((i2, j2), turn + 1, 'I')],
                                       m[(turn, (i2, j2), 'changed')]])
                        # change counter
                        g.add_clause([-m[((i, j), turn, 'S')],
                                       m[((i, j), turn + 1, 'Q')],
                                      -m[((i2, j2), turn, 'H')],
                                       m[((i2, j2), turn + 1, 'I')],
                                       m[((i2, j2), turn + 1, 2)]])
                # spread
                g.add_clause([-m[((i, j), turn, 'S')],
                               m[((i, j), turn + 1, 'Q')],
                               m[(turn, (i, j), 'spread')]])
                g.add_clause([ m[((i, j), turn, 'S')],
                              -m[(turn, (i, j), 'spread')]])
                g.add_clause([-m[((i, j), turn + 1, 'Q')],
                              -m[(turn, (i, j), 'spread')]])

    # decreasing counters for relevant states and healing
    for i in range(n_rows):
        for j in range(n_cols):
            for turn in range(num_turns - 1):
                for state in ['S', 'Q']:
                    for counter in [1, 2]:
                        g.add_clause([-m[((i, j), turn, state)],
                                      -m[((i, j), turn + 1, state)],
                                      -m[((i, j), turn, counter)],
                                       m[((i, j), turn + 1, counter - 1)]])
                    g.add_clause([-m[((i, j), turn, state)],
                                   m[((i, j), turn + 1, 'H')],
                                  -m[((i, j), turn, 0)]])
                    g.add_clause([-m[((i, j), turn, state)],
                                   m[(turn, (i, j), 'changed')],
                                  -m[((i, j), turn, 0)]])

                    # iff <==>
                    g.add_clause([-m[((i, j), turn, state)],
                                  -m[((i, j), turn + 1, 'H')],
                                   m[((i, j), turn, 0)]])

    # constrains:

    # const.1 : not 2 states per same (i,j), turn
    for turn in range(num_turns):
        for i in range(n_rows):
            for j in range(n_cols):
                for state1 in states:
                    for state2 in states:
                        if state1 < state2:
                            g.add_clause([-m[((i, j), turn, state1)],
                                            -m[((i, j), turn, state2)]])
                g.add_clause([m[((i, j), turn, state)] for state in states])

    # const.2 : not 2 counters per same (i,j), turn
    for turn in range(num_turns):
        for i in range(n_rows):
            for j in range(n_cols):
                for k1 in range(3):
                    for k2 in range(3):
                        if k1 < k2:
                            g.add_clause([-m[((i, j), turn, k1)],
                                            -m[((i, j), turn, k2)]])
                g.add_clause([m[((i, j), turn, k)] for k in range(3)])

    # const.3 : maximum action
    for action_name, force, action_let in [('immune', medics, 'H'), ('quarantine', police, 'S')]:
        # const.3.1 : exactly one flag
        for turn in range(num_turns - 1):
            for f in range(force + 1):
                for not_f in range(force + 1):
                    if not_f < f:
                        g.add_clause([-m[(turn, action_name + '_flag', f)],
                                        -m[(turn, action_name + '_flag', not_f)]])
            g.add_clause([m[(turn, action_name + '_flag', f)] for f in range(force + 1)])

        # const.3.2 : make sure relevant flags are on
        indices = [(i, j) for i in range(n_rows) for j in range(n_cols)]
        for turn in range(num_turns - 1):
            for f in range(force + 1):
                subsets = list(itertools.combinations(indices, f))
                for subset in subsets:
                    c = [-m[((i2, j2), turn, action_name)] for i2, j2 in subset]
                    c.append(-m[(turn, action_name + '_flag', f)])
                    for i, j in indices:
                        if (i, j) not in subset:
                            g.add_clause(c + [-m[((i, j), turn, action_name)]])
                subsets = list(itertools.combinations(indices, len(indices) - f + 1))
                for subset in subsets:
                    c = [m[((i2, j2), turn, action_name)] for i2, j2 in subset]
                    c.append(-m[(turn, action_name + '_flag', f)])
                    g.add_clause(c)

        # const.3.3 : if max force not reached -> no population that haven't got action
        for turn in range(num_turns - 1):
            for f in range(force):
                for i in range(n_rows):
                    for j in range(n_cols):
                        g.add_clause([-m[(turn, action_name + '_flag', f)],
                                        -m[((i, j), turn, action_let)],
                                        m[((i, j), turn, action_name)]])

    # const.4 : if action didn't occur -> state doesn't change
    for turn in range(num_turns - 1):
        for i in range(n_rows):
            for j in range(n_cols):
                for state in states:
                    g.add_clause([m[(turn, (i, j), 'changed')],
                                    -m[((i, j), turn, state)],
                                    m[((i, j), turn + 1, state)]])

    # const.5 : if healthy(t) and sick(t+1) then counter(t+1)=2
    for turn in range(num_turns - 1):
        for i in range(n_rows):
            for j in range(n_cols):
                g.add_clause([-m[((i, j), turn, 'H')],
                                -m[((i, j), turn + 1, 'S')],
                                m[((i, j), turn + 1, 2)]])

    # const.6 : if healthy(t) and sick(t+1) then one of my neighbors was sick and spreaded
    for i in range(n_rows):
        for j in range(n_cols):
            for turn in range(num_turns - 1):
                c = [-m[((i, j), turn, 'H')],
                     -m[((i, j), turn + 1, 'S')]]
                for d in directions:
                    i2 = i + d[0]
                    j2 = j + d[1]
                    if 0 <= i2 < n_rows and 0 <= j2 < n_cols:
                        c.append(m[(turn, (i2, j2), 'spread')])
                g.add_clause(c)

    # const.7 : if immune(t + 1) then immune(t) or immuned(t)
    #           if quarantine(t + 1) then quarantine(t) or quarantined(t)
    for i in range(n_rows):
        for j in range(n_cols):
            for turn in range(num_turns - 1):
                g.add_clause([-m[((i, j), turn + 1, 'I')],
                                m[((i, j), turn, 'I')],
                                m[((i, j), turn, 'immune')]])
                g.add_clause([-m[((i, j), turn + 1, 'Q')],
                                m[((i, j), turn, 'Q')],
                                m[((i, j), turn, 'quarantine')]])
                g.add_clause([-m[((i, j), turn + 1, 'S')],
                                m[((i, j), turn, 'S')],
                                m[((i, j), turn, 'H')]])
                g.add_clause([-m[((i, j), turn + 1, 'H')],
                                m[((i, j), turn, 'S')],
                                m[((i, j), turn, 'Q')],
                                m[((i, j), turn, 'H')]])
                g.add_clause([-m[((i, j), turn + 1, 'U')],
                                m[((i, j), turn, 'U')]])

    # initial states clauses
    for turn, observation in enumerate(input['observations']):
        for i in range(n_rows):
            for j in range(n_cols):
                if observation[i][j] == '?':
                    continue
                g.add_clause([m[((i, j), turn, observation[i][j])]])
                for state in states:
                    if state != observation[i][j]:
                        g.add_clause([-m[((i, j), turn, state)]])

    for i in range(n_rows):
        for j in range(n_cols):
            g.add_clause([-m[((i, j), 0, 'Q')]])
            g.add_clause([-m[((i, j), 0, 'I')]])
            g.add_clause([m[((i, j), 0, 2)]])

    # ---------------------------------------------------
    # sat problem solver:

    solutions = {}
    for query in queries:
        true_solution = g.solve(assumptions=[m[query]])
        if true_solution:
            false_solution = g.solve(assumptions=[-m[query]])
            if false_solution:
                res = '?'
            else:
                res = 'T'
        else:
            res = 'F'
        solutions[query] = res
    return solutions
