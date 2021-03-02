from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Minisat22


ids = ['312146897', '311418214']


def req_imply(var_and, var_or):  # and(var_and) implies or(var_or)
    return [[-a for a in var_and] + [o for o in var_or]]


def req_equiv(var_and, var_or):  # and(var_and) equiv or(var_or)
    clauses = req_imply(var_and, var_or)
    clauses.extend([[a, -o] for a in var_and for o in var_or])
    return clauses


def nearby(r, c, n_rows, n_cols):
    neighbors = []
    for delta_r, delta_c in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
        r_, c_ = r + delta_r, c + delta_c
        if 0 <= r_ < n_rows and 0 <= c_ < n_cols:
            neighbors.append((r_, c_))
    return neighbors


def make_formula(n_police, n_medics, n_rows, n_cols, n_time):
    states = {'U', 'H', 'S', 'I', 'Q'}
    variables = {}
    formula = CNF()
    var_pool = IDPool()
    for t in range(n_time):
        for r in range(n_rows):
            for c in range(n_cols):
                for s in states:
                    variables[(r, c), t, s] = var_pool.id(f'({r}, {c}), {t}, {s}')
                variables[(r, c), t, 'P'] = var_pool.id(f'({r}, {c}), {t}, P')  # Police were used
                variables[(r, c), t, 'M'] = var_pool.id(f'({r}, {c}), {t}, M')  # Medics were used
                variables[(r, c), t, 'SS'] = var_pool.id(f'({r}, {c}), {t}, SS')  # Stayed sick from last time
    for t in range(n_time):
        formula.extend(CardEnc.atmost([variables[(r, c), t, 'P'] for r in range(n_rows) for c in range(n_cols)],
                                      bound=n_police, vpool=var_pool))
        formula.extend(CardEnc.atmost([variables[(r, c), t, 'M'] for r in range(n_rows) for c in range(n_cols)],
                                      bound=n_medics, vpool=var_pool))
        for r in range(n_rows):
            for c in range(n_cols):
                formula.extend(CardEnc.equals([variables[(r, c), t, s] for s in states], vpool=var_pool))
                if t > 0:
                    formula.extend(req_equiv([-variables[(r, c), t - 1, 'Q'], variables[(r, c), t, 'Q']],
                                             [variables[(r, c), t, 'P']]))
                    formula.extend(req_equiv([-variables[(r, c), t - 1, 'I'], variables[(r, c), t, 'I']],
                                             [variables[(r, c), t, 'M']]))
                    formula.extend(req_equiv([variables[(r, c), t - 1, 'S'], variables[(r, c), t, 'S']],
                                             [variables[(r, c), t, 'SS']]))
                    nearby_sick_condition = []
                    for r_, c_ in nearby(r, c, n_rows, n_cols):
                        nearby_sick_condition.append(variables[(r_, c_), t, 'SS'])
                        formula.extend(req_imply([variables[(r, c), t, 'SS'], variables[(r_, c_), t - 1, 'H']],
                                                 [variables[(r_, c_), t, 'S'], variables[(r_, c_), t, 'I']]))
                        # formula.extend(req_imply([variables[(r, c), t, 'SS']], [-variables[(r_, c_), t, 'H']]))
                    formula.extend(req_imply([variables[(r, c), t - 1, 'H'], variables[(r, c), t, 'S']],
                                             nearby_sick_condition))
                if t + 1 < n_time:
                    formula.extend(req_equiv([variables[(r, c), t, 'U']], [variables[(r, c), t + 1, 'U']]))
                    formula.extend(req_imply([variables[(r, c), t, 'I']], [variables[(r, c), t + 1, 'I']]))
                    formula.extend(req_imply([variables[(r, c), t + 1, 'S']],
                                             [variables[(r, c), t, 'S'], variables[(r, c), t, 'H']]))
                    formula.extend(req_imply([variables[(r, c), t + 1, 'Q']],
                                             [variables[(r, c), t, 'Q'], variables[(r, c), t, 'S']]))
                if t == 0:
                    formula.append([-variables[(r, c), t, 'Q']])
                    formula.append([-variables[(r, c), t, 'I']])
                    if t + 1 < n_time:
                        formula.extend(req_imply([variables[(r, c), t, 'S']],
                                                 [variables[(r, c), t + 1, 'S'], variables[(r, c), t + 1, 'Q']]))
                        formula.extend(req_imply([variables[(r, c), t, 'Q']], [variables[(r, c), t + 1, 'Q']]))
                    if t + 2 < n_time:
                        formula.extend(req_imply(
                            [variables[(r, c), t, 'S'], variables[(r, c), t + 1, 'S']],
                            [variables[(r, c), t + 2, 'S'], variables[(r, c), t + 2, 'Q']]))
                        formula.extend(req_imply(
                            [variables[(r, c), t, 'S'], variables[(r, c), t + 1, 'Q']],
                            [variables[(r, c), t + 2, 'Q']]))
                        formula.extend(req_imply([variables[(r, c), t, 'Q']], [variables[(r, c), t + 2, 'H']]))
                    if t + 3 < n_time:
                        formula.extend(req_imply(
                            [variables[(r, c), t, 'S'], variables[(r, c), t + 1, 'S'],
                             variables[(r, c), t + 2, 'S']], [variables[(r, c), t + 3, 'H']]))
                if 0 < t and t + 1 < n_time:
                    formula.extend(req_imply([-variables[(r, c), t - 1, 'S'], variables[(r, c), t, 'S']],
                                             [variables[(r, c), t + 1, 'S'], variables[(r, c), t + 1, 'Q']]))
                    formula.extend(req_imply([-variables[(r, c), t - 1, 'Q'], variables[(r, c), t, 'Q']],
                                             [variables[(r, c), t + 1, 'Q']]))
                if 0 < t and t + 2 < n_time:
                    formula.extend(req_imply(
                        [-variables[(r, c), t - 1, 'S'], variables[(r, c), t, 'S'], variables[(r, c), t + 1, 'S']],
                        [variables[(r, c), t + 2, 'S'], variables[(r, c), t + 2, 'Q']]))
                    formula.extend(req_imply(
                        [-variables[(r, c), t - 1, 'S'], variables[(r, c), t, 'S'], variables[(r, c), t + 1, 'Q']],
                        [variables[(r, c), t + 2, 'Q']]))
                    formula.extend(req_imply([-variables[(r, c), t - 1, 'Q'], variables[(r, c), t, 'Q']],
                                             [variables[(r, c), t + 2, 'H']]))
                if 0 < t and t + 3 < n_time:
                    formula.extend(req_imply(
                        [-variables[(r, c), t - 1, 'S'], variables[(r, c), t, 'S'], variables[(r, c), t + 1, 'S'],
                         variables[(r, c), t + 2, 'S']], [variables[(r, c), t + 3, 'H']]))
    return var_pool, formula


def solve_problem(problem):
    n_police = problem['police']
    n_medics = problem['medics']
    observations = problem['observations']
    queries = problem['queries']
    n_rows = len(observations[0])
    n_cols = len(observations[0][0])
    n_time = len(observations) + 1 + 3  # All the information we could have
    var_pool, formula = make_formula(n_police, n_medics, n_rows, n_cols, n_time)
    assumptions = [var_pool.id(f'({r}, {c}), {t}, {s}')
                   for t, obs in enumerate(observations)
                   for r, row in enumerate(obs)
                   for c, s in enumerate(row) if s != '?']
    results = {query: '?' for query in queries}
    with Minisat22(bootstrap_with=formula) as solver:
        for query in results:
            (r, c), t, s = query
            with_query = solver.solve(assumptions + [var_pool.id(f'({r}, {c}), {t}, {s}')])
            with_not_query = solver.solve(assumptions + [-var_pool.id(f'({r}, {c}), {t}, {s}')])
            if with_query and not with_not_query:
                results[query] = 'T'
            elif with_not_query and not with_query:
                results[query] = 'F'
    return results
