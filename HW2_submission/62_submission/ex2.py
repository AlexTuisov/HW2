from pysat.formula import IDPool
from itertools import combinations
from pysat.solvers import Solver
from sympy.logic import to_cnf
from sympy import symbols
from sympy.logic import SOPform, POSform
from sympy.logic.boolalg import And, Not, Or

ids = ['322210949', '322643677']

vpool = IDPool()  # one-to-one mapping function for the literals numbers we will give for each action and proposition

# some virtual last elements for noop actions, infect actions, end of S (recover) and end of Q
actions = ['vaccinate', 'quarantine', 'infectR', 'infectL', 'infectU', 'infectD', 'recover', 'end of Q',
           'noopU', 'noopH', 'noopS', 'noopI', 'noopQ']
states = ['U', 'H', 'S', 'I', 'Q']  # legal and known states - not including question mark (?)
range_states = range(1, len(states) + 1)
range_actions = range(1, len(actions) + 1)
# all directions = down, up, right, left
infect_directions = {'infectD': (1, 0), 'infectU': (-1, 0), 'infectR': (0, 1), 'infectL': (0, -1)}
all_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def var(num):
    return vpool.id(num)


def recover_var(num):
    return vpool.obj(num)


# assigning for each proposition a unique number of variable (literal)
def varnum(rounds, r, m, n, i, j, k):
    # k will be the index in states list + 1
    assert r in rounds and 1 <= i <= m and 1 <= j <= n and k in range_states
    return var(1000 * r + 100 * i + 10 * j + k)


def act_num(rounds, r, m, n, i, j, act):
    # act will be the index in actions list + 1
    # this function will be used for the noop actions and the virtual actions for system dynamics
    # will be unique because of the act index for all actions
    assert r in rounds and 1 <= i <= m and 1 <= j <= n and act in range_actions
    return var(10000 * act + 1000 * r + 100 * i + 10 * j)


def exactly_one_of(literals, clauses):
    clauses.append([lit for lit in literals])
    for pair in combinations(literals, 2):
        clauses.append([-lit for lit in pair])


def preconditions_clauses(clauses, rounds, r, rows, columns, i, j, medics_teams, police_teams):
    for act, action in enumerate(actions):
        if police_teams and action == 'quarantine':
            clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                            varnum(rounds, r, rows, columns, i, j, states.index('S') + 1)])
        if medics_teams and action == 'vaccinate':
            clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                            varnum(rounds, r, rows, columns, i, j, states.index('H') + 1)])

        # splitted because being infected from different directions is independent
        for infect, direct in infect_directions.items():
            if infect == action:
                i_new = i + direct[0]
                j_new = j + direct[1]
                if 1 <= i_new <= rows and 1 <= j_new <= columns:
                    clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                                    varnum(rounds, r, rows, columns, i, j, states.index('H') + 1)])

                    clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                                    varnum(rounds, r, rows, columns, i_new, j_new, states.index('S') + 1)])

        # there are no Q tiles in first round so actions recover and end of Q can occur only in 3rd
        # turn and afterwards
        if r >= 3:
            if action == 'recover':
                # sick now
                clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                                varnum(rounds, r, rows, columns, i, j, states.index('S') + 1)])
                # was sick also one turn ago
                clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                                varnum(rounds, r - 1, rows, columns, i, j, states.index('S') + 1)])
                # was sick also two turns ago
                clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                                varnum(rounds, r - 2, rows, columns, i, j, states.index('S') + 1)])
            if action == 'end of Q':
                # quarantined now
                clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                                varnum(rounds, r, rows, columns, i, j, states.index('Q') + 1)])
                # was quarantined also one turn ago
                clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                                varnum(rounds, r - 1, rows, columns, i, j, states.index('Q') + 1)])

        if action == 'noopH':
            clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                            varnum(rounds, r, rows, columns, i, j, states.index('H') + 1)])
            # we can quarantine the neighbor before he is infecting this round,
            # so or noop H happens in parallel to quarantine the neighbor or the neighbor isn't sick
            # at all and the noop H should happen
            # {~noop_H, ~neighbor_is_S, neighbor_is_Q} = noop_H --> (~neighbor_is_S \/ neighbor_is_Q)
            # = noop_H --> ~(neighbor_is_S /\ ~neighbor_is_Q)
            for direct in all_directions:
                i_new = i + direct[0]
                j_new = j + direct[1]
                if 1 <= i_new <= rows and 1 <= j_new <= columns:
                    clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                                    -varnum(rounds, r, rows, columns, i_new, j_new, states.index('S') + 1),
                                    act_num(rounds, r, rows, columns, i_new, j_new,
                                            actions.index('quarantine') + 1)])

        if action == 'noopS':
            clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                            varnum(rounds, r, rows, columns, i, j, states.index('S') + 1)])
            # we can noop_S only if he shouldn't recover (wasn't S last turn and two turns ago)
            # {~noop_S, ~was_S_last_turn, ~was_S_two_turns_ago} =
            # noop_S --> (~was_S_last_turn \/ ~was_S_two_turns_ago)
            # = noop_S --> ~(was_S_last_turn /\ was_S_two_turns_ago)
            if r >= 3:
                clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                                -varnum(rounds, r - 1, rows, columns, i, j, states.index('S') + 1),
                                -varnum(rounds, r - 2, rows, columns, i, j, states.index('S') + 1)])

        if action == 'noopQ':
            clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                            varnum(rounds, r, rows, columns, i, j, states.index('Q') + 1)])
            # we can noop_Q only if he shouldn't end Q (wasn't Q last turn)
            # {~noop_Q, ~was_Q_last_turn} = noop_Q --> ~was_Q_last_turn
            if r >= 3:  # we don't have Q in initial observation so r>=3 and not r>=2
                clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                                -varnum(rounds, r - 1, rows, columns, i, j, states.index('Q') + 1)])

        if action == 'noopI':
            clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                            varnum(rounds, r, rows, columns, i, j, states.index('I') + 1)])
        if action == 'noopU':
            clauses.append([-act_num(rounds, r, rows, columns, i, j, act + 1),
                            varnum(rounds, r, rows, columns, i, j, states.index('U') + 1)])


def action_interference_clauses(clauses, rounds, r, rows, columns, i, j, medics_teams, police_teams):
    for act, action in enumerate(actions):
        # we can only activate one action on a specific tile so each action that is on the same
        # tile is interfering to each other
        if r < 3 and (action == 'recover' or action == 'end of Q'):
            # if action is recover or end of Q then it will be legal (r>=3)
            continue
        # TODO: See that I changed here to have if statement for no teams
        if not police_teams and action == 'quarantine':
            # we gave literals for these actions iff police_teams > 0
            continue
        if not medics_teams and action == 'vaccinate':
            # we gave literals for these actions iff medics_teams > 0
            continue
        action_num = act_num(rounds, r, rows, columns, i, j, act + 1)
        for act_2 in range(act + 1, len(actions)):
            action_2 = actions[act_2]
            if r < 3 and (action_2 == 'recover' or action_2 == 'end of Q'):
                # if action_2 is recover or end of Q then it will be legal (r>=3)
                continue
            if not police_teams and action_2 == 'quarantine':
                # we gave literals for these actions iff police_teams > 0
                continue
            if not medics_teams and action_2 == 'vaccinate':
                # we gave literals for these actions iff medics_teams > 0
                continue
            action_num_2 = act_num(rounds, r, rows, columns, i, j, act_2 + 1)
            clauses.append([-action_num, -action_num_2])

    #  action interference clauses for actions not in the same tile
    for infect, direct in infect_directions.items():
        i_new = i + direct[0]
        j_new = j + direct[1]
        if 1 <= i_new <= rows and 1 <= j_new <= columns:
            # cannot be infected from direct while his direct neighbor is being quarantined
            clauses.append([-act_num(rounds, r, rows, columns, i, j, actions.index(infect) + 1),
                            -act_num(rounds, r, rows, columns, i_new, j_new, actions.index('quarantine') + 1)])


def fact_achievement_clauses(clauses, rounds, r, rows, columns, i, j):
    for k, state in enumerate(states):
        if state == 'H':
            fact_achievement_clause = [-varnum(rounds, r, rows, columns, i, j, k + 1),
                                       act_num(rounds, r - 1, rows, columns, i, j,
                                               actions.index('noopH') + 1)]
            if r >= 4:
                # recent round was the last one that he was sick
                fact_achievement_clause.append(act_num(rounds, r - 1, rows, columns, i, j,
                                                       actions.index('recover') + 1))
                # recent round was the last one that he is quarantined
                fact_achievement_clause.append(act_num(rounds, r - 1, rows, columns, i, j,
                                                       actions.index('end of Q') + 1))
            clauses.append(fact_achievement_clause)

        if state == 'S':
            fact_achievement_clause = [-varnum(rounds, r, rows, columns, i, j, k + 1),
                                       act_num(rounds, r - 1, rows, columns, i, j,
                                               actions.index('noopS') + 1)]
            # got infected (S) last round
            for infect, direct in infect_directions.items():
                i_new = i + direct[0]
                j_new = j + direct[1]
                if 1 <= i_new <= rows and 1 <= j_new <= columns:
                    fact_achievement_clause.append(act_num(rounds, r - 1, rows, columns, i, j,
                                                           actions.index(infect) + 1))
            clauses.append(fact_achievement_clause)

        if state == 'Q':
            fact_achievement_clause = \
                [-varnum(rounds, r, rows, columns, i, j, k + 1),
                 act_num(rounds, r - 1, rows, columns, i, j, actions.index('noopQ') + 1),
                 act_num(rounds, r - 1, rows, columns, i, j, actions.index('quarantine') + 1)]
            clauses.append(fact_achievement_clause)

        if state == 'I':
            fact_achievement_clause = \
                [-varnum(rounds, r, rows, columns, i, j, k + 1),
                 act_num(rounds, r - 1, rows, columns, i, j, actions.index('noopI') + 1),
                 act_num(rounds, r - 1, rows, columns, i, j, actions.index('vaccinate') + 1)]
            clauses.append(fact_achievement_clause)

        if state == 'U':
            fact_achievement_clause = [-varnum(rounds, r, rows, columns, i, j, k + 1),
                                       act_num(rounds, r - 1, rows, columns, i, j,
                                               actions.index('noopU') + 1)]
            clauses.append(fact_achievement_clause)


def cnf_with_boolean_symbols_to_valid_clauses(cnf_with_boolean_symbols):
    cnf_in_lists = str(cnf_with_boolean_symbols).replace(" ", "").replace("(", "").replace(")", "").replace("~", "-")\
        .split('&')
    return [[int(lit) for lit in clause.split("|")] for clause in cnf_in_lists]


def exactly_one_permutation_of_actions(curr_teams, teams_actions):
    if len(teams_actions) == 1:
        return [teams_actions]

    if curr_teams >= len(teams_actions):
        return [[act] for act in teams_actions]

    symbols_string = (" ".join([str(act) for act in teams_actions]))
    symbols_sympy = symbols(symbols_string)
    all_and_combinations = [POSform(comb, minterms=[{symbol: 1 for symbol in comb}]) for comb in
                            combinations(symbols_sympy, min(curr_teams, len(teams_actions)))]

    sop = SOPform(all_and_combinations, minterms=[{comb: 1} for comb in all_and_combinations])
    exactly_one_perm_clauses = True
    if len(teams_actions) > curr_teams:  # more actions than teams, has to choose one exactly permutation
        for set1, set2 in combinations(sop.args, 2):
            exactly_one_perm_clauses = And(exactly_one_perm_clauses, Or(Not(set1), Not(set2)))
    final_cnf = to_cnf(And(exactly_one_perm_clauses, sop))
    return cnf_with_boolean_symbols_to_valid_clauses(final_cnf)


def using_all_teams_available(clauses, rounds, observations, police_teams, medics_teams, rows, columns):
    for r in rounds:
        if r == len(observations):
            break
        curr_observation = observations[r - 1]
        next_observation = observations[(r - 1) + 1]
        police_actions = []  # will save all possible actions of police that can be done in current round
        medics_actions = []  # will save all possible actions of medics that can be done in current round
        curr_police_teams = police_teams
        curr_medics_teams = medics_teams
        # extracting number of left police_teams and medics_teams
        for i in range(1, rows + 1):
            for j in range(1, columns + 1):
                tile = curr_observation[i - 1][j - 1]
                if tile == 'H':
                    if next_observation[i - 1][j - 1] == 'I':
                        # counting in observations the number of medics teams that were already used
                        curr_medics_teams -= 1
                    elif next_observation[i - 1][j - 1] == '?':
                        # can maybe vaccinate this tile
                        medics_actions.append(act_num(rounds, r, rows, columns, i, j,
                                                      actions.index('vaccinate') + 1))
                elif tile == 'S':
                    if next_observation[i - 1][j - 1] == 'Q':
                        # counting in observations the number of police teams that were already used
                        curr_police_teams -= 1
                    elif next_observation[i - 1][j - 1] == '?':
                        # can maybe quarantine this tile
                        police_actions.append(act_num(rounds, r, rows, columns, i, j,
                                                      actions.index('quarantine') + 1))
                elif tile == '?':
                    medics_actions.append(act_num(rounds, r, rows, columns, i, j, actions.index('vaccinate') + 1))
                    police_actions.append(act_num(rounds, r, rows, columns, i, j, actions.index('quarantine') + 1))
        # entering clauses if there aren't available teams - curr_teams == 0 that we cam't activate teams' actions
        for i in range(1, rows + 1):
            for j in range(1, columns + 1):
                if next_observation[i - 1][j - 1] == '?':
                    if not curr_medics_teams:
                        clauses.append([-act_num(rounds, r, rows, columns, i, j, actions.index('vaccinate') + 1)])
                    if not curr_police_teams:
                        clauses.append([-act_num(rounds, r, rows, columns, i, j, actions.index('quarantine') + 1)])

        if curr_medics_teams and len(medics_actions):
            clauses += exactly_one_permutation_of_actions(curr_medics_teams, medics_actions)

        if curr_police_teams and len(police_actions):
            clauses += exactly_one_permutation_of_actions(curr_police_teams, police_actions)


def answer_queries(clauses, queries, rounds, rows, columns):
    answers = {}
    g = Solver(name='glucose3', bootstrap_with=clauses)
    for query in queries:
        i, j = query[0]
        i += 1
        j += 1
        r = query[1] + 1
        state = query[2]
        assumption = varnum(rounds, r, rows, columns, i, j, states.index(state) + 1)
        result = g.solve(assumptions=[assumption])
        if not result:
            answers[query] = 'F'
            continue
        # else result == True
        # need to check whether there are other state values that give true
        result_2 = g.solve(assumptions=[-assumption])
        if result_2:
            answers[query] = '?'
        else:
            answers[query] = 'T'
    g.delete()
    return answers


def solve_problem(input):
    observations = input['observations']
    # getting the dimensions of the table
    first_observation = observations[0]
    rows = len(first_observation)
    columns = len(first_observation[0])
    num_of_observations = len(observations)
    rounds = range(1, num_of_observations + 1)
    queries = input['queries']
    clauses = []
    police_teams = input['police']
    medics_teams = input['medics']
    for r in rounds:  # iterating through rounds (time): time should start at 0, but we started at 1- will be treated.
        curr_observation = observations[r - 1]
        for i in range(1, rows + 1):  # iterating through rows in current observation (time)
            for j in range(1, columns + 1):  # iterating through columns in current observation (time)
                # no police teams --> no tiles with Q
                if police_teams == 0:
                    clauses.append([-varnum(rounds, r, rows, columns, i, j, states.index('Q') + 1)])
                # no medics teams --> no tiles with I
                if medics_teams == 0:
                    clauses.append([-varnum(rounds, r, rows, columns, i, j, states.index('I') + 1)])
                # assigning propositional for initial state
                if curr_observation[i - 1][j - 1] in states:  # current tile is known
                    k = states.index(curr_observation[i - 1][j - 1]) + 1
                    clauses.append([varnum(rounds, r, rows, columns, i, j, k)])
                    for k, state in enumerate(states):
                        if state == curr_observation[i - 1][j - 1]:
                            continue
                        clauses.append([-varnum(rounds, r, rows, columns, i, j, k + 1)])
                else:
                    # making sure only one of each literal that represents a tile in a round (observation)
                    # is assigned to true
                    exactly_one_of([varnum(rounds, r, rows, columns, i, j, k) for k in range_states], clauses)
                    # first turn can't have I and Q
                    if r == 1:
                        clauses.append([-varnum(rounds, r, rows, columns, i, j, states.index('Q') + 1)])
                        clauses.append([-varnum(rounds, r, rows, columns, i, j, states.index('I') + 1)])

                if r < num_of_observations:
                    # ------ preconditions clauses handling including noop clauses and system dynamics ------
                    preconditions_clauses(clauses, rounds, r, rows, columns, i, j, medics_teams, police_teams)

                    # ------ action interference clauses ------
                    action_interference_clauses(clauses, rounds, r, rows, columns, i, j, medics_teams, police_teams)

                # ------ fact achievement clauses ------
                # checking if there is an action that got current proposition in round r-1
                if r >= 2:  # equals to time >= 1
                    fact_achievement_clauses(clauses, rounds, r, rows, columns, i, j)


    # entering clauses that will make sure we are using all police and medics teams at each round if possible
    if police_teams or medics_teams:
        using_all_teams_available(clauses, rounds, observations, police_teams, medics_teams, rows, columns)

    answers = answer_queries(clauses, queries, rounds, rows, columns)
    return answers
    # put your solution here, remember the format needed
