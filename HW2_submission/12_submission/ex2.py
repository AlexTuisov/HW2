from pysat.formula import IDPool
from itertools import combinations
from pysat.solvers import Solver
from sympy.logic import to_cnf
from sympy import symbols
from sympy.logic import SOPform, POSform
from sympy.logic.boolalg import And, Not, Or

ids = ['207668286', '316327238']
vpool = IDPool()
# possible directions for infection (right, left, down, up)
dircs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
# all states giving in the exercise
states = ['Q', 'H', 'S', 'U', 'I']
# all possible actions (including noops and infection from all directions)
actions = ['vaccinate', 'quarantine', 'infectedFromR', 'infectedFromL', 'infectedFromU', 'infectedFromD',
           'finished sick', 'finished quarantine', 'noopU', 'noopH', 'noopS', 'noopI', 'noopQ']


def var(num):
    return vpool.id(num)
def recover_var(num):
    return vpool.obj(num)


# gives a unique id for each proposition (depends on current turn, coordinates and state)
def var_id(turns, turn, num_rows, num_cols, x, y, known):
    assert turn in turns and 1 <= x <= num_rows and 1 <= y <= num_cols and known in range(1, len(states) + 1)
    return var(1000 * turn + 100 * x + 10 * y + known)


# gives a unique id for each action (depends on current turn, coordinates and action)
def action_id(turns, turn, num_rows, num_cols, x, y, action):
    assert turn in turns and 1 <= x <= num_rows and 1 <= y <= num_cols and action in range(1, len(actions) + 1)
    return var(10000 * action + 1000 * turn + 100 * x + 10 * y)


# makes sure only one literal is true for a tile in a turn
def only_one_true(literals, clauses):
    clauses.append([literal for literal in literals])
    for pair in combinations(literals, 2):
        clauses.append([-literal for literal in pair])


# creates all pre-conditions clauses
def pre_conds(clauses, turns, t, num_rows, num_cols, x, y, num_medics, num_police):
    for act, action in enumerate(actions):
        # check pre-conditions for each possible action
        if num_police and action == 'quarantine':
            clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                            var_id(turns, t, num_rows, num_cols, x, y, states.index('S') + 1)])
        if num_medics and action == 'vaccinate':
            clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                            var_id(turns, t, num_rows, num_cols, x, y, states.index('H') + 1)])
        if x > 1 and action == 'infectedFromU':
            clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                            var_id(turns, t, num_rows, num_cols, x, y, states.index('H') + 1)])
            clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                            var_id(turns, t, num_rows, num_cols, x-1, y, states.index('S') + 1)])
        if x < num_rows and action == 'infectedFromD':
            clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                            var_id(turns, t, num_rows, num_cols, x, y, states.index('H') + 1)])
            clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                            var_id(turns, t, num_rows, num_cols, x+1, y, states.index('S') + 1)])
        if y > 1 and action == 'infectedFromL':
            clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                            var_id(turns, t, num_rows, num_cols, x, y, states.index('H') + 1)])
            clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                            var_id(turns, t, num_rows, num_cols, x, y-1, states.index('S') + 1)])
        if y < num_cols and action == 'infectedFromR':
            clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                            var_id(turns, t, num_rows, num_cols, x, y, states.index('H') + 1)])
            clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                            var_id(turns, t, num_rows, num_cols, x, y+1, states.index('S') + 1)])

        # we know there are no 'I' and 'Q' tiles in the first turn,
        # so 'finished quarantine' and 'finished sick' can occur only after the 3rd turn.
        if t >= 3:
            if action == 'finished quarantine':
                clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                                var_id(turns, t, num_rows, num_cols, x, y, states.index('Q') + 1)])
                clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                                var_id(turns, t-1, num_rows, num_cols, x, y, states.index('Q') + 1)])
            if action == 'finished sick':
                clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                                var_id(turns, t, num_rows, num_cols, x, y, states.index('S') + 1)])
                clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                                var_id(turns, t-1, num_rows, num_cols, x, y, states.index('S') + 1)])
                clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                                var_id(turns, t-2, num_rows, num_cols, x, y, states.index('S') + 1)])

        # check pre-conditions for each noop, using the given dynamics of the system
        if action == 'noopI':
            clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                            var_id(turns, t, num_rows, num_cols, x, y, states.index('I') + 1)])

        if action == 'noopU':
            clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                            var_id(turns, t, num_rows, num_cols, x, y, states.index('U') + 1)])

        if action == 'noopS':
            clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                            var_id(turns, t, num_rows, num_cols, x, y, states.index('S') + 1)])
            if t >= 3:
                clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                                -var_id(turns, t-1, num_rows, num_cols, x, y, states.index('S') + 1),
                                -var_id(turns, t-2, num_rows, num_cols, x, y, states.index('S') + 1)])

        if action == 'noopQ':
            clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                            var_id(turns, t, num_rows, num_cols, x, y, states.index('Q') + 1)])
            if t >= 3:
                clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                                -var_id(turns, t-1, num_rows, num_cols, x, y, states.index('Q') + 1)])

        if action == 'noopH':
            clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                            var_id(turns, t, num_rows, num_cols, x, y, states.index('H') + 1)])
            if x > 1:
                clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                                -var_id(turns, t, num_rows, num_cols, x-1, y, states.index('S') + 1),
                                action_id(turns, t, num_rows, num_cols, x-1, y, actions.index('quarantine') + 1)])
            if x < num_rows:
                clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                                -var_id(turns, t, num_rows, num_cols, x+1, y, states.index('S') + 1),
                                action_id(turns, t, num_rows, num_cols, x+1, y, actions.index('quarantine') + 1)])
            if y > 1:
                clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                                -var_id(turns, t, num_rows, num_cols, x, y-1, states.index('S') + 1),
                                action_id(turns, t, num_rows, num_cols, x, y-1, actions.index('quarantine') + 1)])
            if y < num_cols:
                clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, act + 1),
                                -var_id(turns, t, num_rows, num_cols, x, y+1, states.index('S') + 1),
                                action_id(turns, t, num_rows, num_cols, x, y+1, actions.index('quarantine') + 1)])


# check for actions that may interfere each other
def interfering_actions(clauses, turns, t, num_rows, num_cols, x, y, num_medics, num_police):
    for act1, action in enumerate(actions):
        # skip on non-possible actions
        if t < 3 and (action == 'finished quarantine' or action == 'finished sick'):
            continue
        if (not num_police and action == 'quarantine') or (not num_medics and action == 'vaccinate'):
            continue
        act_id = action_id(turns, t, num_rows, num_cols, x, y, act1 + 1)
        for act2 in range(act1 + 1, len(actions)):
            scnd_act = actions[act2]
            # skip on non-possible actions
            if t < 3 and (scnd_act == 'finished quarantine' or scnd_act == 'finished sick'):
                continue
            if (not num_police and scnd_act == 'quarantine') or (not num_medics and scnd_act == 'vaccinate'):
                continue
            scnd_act_id = action_id(turns, t, num_rows, num_cols, x, y, act2 + 1)
            clauses.append([-act_id, -scnd_act_id])

    # check for interfering actions from different tiles (tile that is quarantined can't infect)
    if x > 1:
        clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, actions.index('infectedFromD') + 1),
                        -action_id(turns, t, num_rows, num_cols, x-1, y, actions.index('quarantine') + 1)])
    if x < num_rows:
        clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, actions.index('infectedFromD') + 1),
                        -action_id(turns, t, num_rows, num_cols, x+1, y, actions.index('quarantine') + 1)])
    if y > 1:
        clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, actions.index('infectedFromL') + 1),
                        -action_id(turns, t, num_rows, num_cols, x, y-1, actions.index('quarantine') + 1)])
    if y < num_cols:
        clauses.append([-action_id(turns, t, num_rows, num_cols, x, y, actions.index('infectedFromR') + 1),
                        -action_id(turns, t, num_rows, num_cols, x, y+1, actions.index('quarantine') + 1)])


# check for the actions that brought the tile to its current known state
def previous_actions(clauses, turns, t, num_rows, num_cols, x, y):
    for known, state in enumerate(states):
        # only noopU can make 'U'
        if state == 'U':
            temp_clause = [-var_id(turns, t, num_rows, num_cols, x, y, known + 1),
                           action_id(turns, t - 1, num_rows, num_cols, x, y, actions.index('noopU') + 1)]
            clauses.append(temp_clause)
        # quarantine or noopQ can make 'Q'
        if state == 'Q':
            temp_clause = [-var_id(turns, t, num_rows, num_cols, x, y, known + 1),
                           action_id(turns, t - 1, num_rows, num_cols, x, y, actions.index('noopQ') + 1),
                           action_id(turns, t - 1, num_rows, num_cols, x, y, actions.index('quarantine') + 1)]
            clauses.append(temp_clause)
        # vaccinate or noopI can make 'I'
        if state == 'I':
            temp_clause = [-var_id(turns, t, num_rows, num_cols, x, y, known + 1),
                           action_id(turns, t - 1, num_rows, num_cols, x, y, actions.index('noopI') + 1),
                           action_id(turns, t - 1, num_rows, num_cols, x, y, actions.index('vaccinate') + 1)]
            clauses.append(temp_clause)
        # finishing being sick, finishing quarantine or noopH can make 'H'
        if state == 'H':
            temp_clause = [-var_id(turns, t, num_rows, num_cols, x, y, known + 1),
                           action_id(turns, t - 1, num_rows, num_cols, x, y, actions.index('noopH') + 1)]
            if t >= 4:
                temp_clause.append(action_id(turns, t - 1, num_rows, num_cols, x, y, actions.index('finished sick') + 1))
                temp_clause.append(action_id(turns, t - 1, num_rows, num_cols, x, y, actions.index('finished quarantine') + 1))
            clauses.append(temp_clause)

        # being infected of at least one direction or noopS can make 'S'
        if state == 'S':
            temp_clause = [-var_id(turns, t, num_rows, num_cols, x, y, known + 1),
                           action_id(turns, t - 1, num_rows, num_cols, x, y, actions.index('noopS') + 1)]
            if y < num_cols:
                temp_clause.append(action_id(turns, t - 1, num_rows, num_cols, x, y, actions.index('infectedFromR') + 1))
            if y > 1:
                temp_clause.append(action_id(turns, t - 1, num_rows, num_cols, x, y, actions.index('infectedFromL') + 1))
            if x < num_rows:
                temp_clause.append(action_id(turns, t - 1, num_rows, num_cols, x, y, actions.index('infectedFromD') + 1))
            if x > 1:
                temp_clause.append(action_id(turns, t - 1, num_rows, num_cols, x, y, actions.index('infectedFromU') + 1))
            clauses.append(temp_clause)


# makes sure we use all the possible available teams given
def possible_teams(clauses, turns, obss, num_police, num_medics, num_rows, num_cols):
    for turn in turns:
        # no action can be preformed in the last turn
        if turn == len(obss):
            break
        current_obs = obss[turn - 1]
        next_obs = obss[turn]
        updated_police = num_police
        updated_medics = num_medics
        act_of_police = []
        act_of_medics = []

        for x in range(1, num_rows + 1):
            for y in range(1, num_cols + 1):
                current_state_name = current_obs[x - 1][y - 1]
                next_state_name = next_obs[x - 1][y - 1]
                if current_state_name == 'H':
                    if next_state_name == 'I':
                        updated_medics = updated_medics - 1
                    elif next_state_name == '?':
                        act_of_medics.append(action_id(turns, turn, num_rows, num_cols, x, y, actions.index('vaccinate') + 1))
                elif current_state_name == 'S':
                    if next_state_name == 'Q':
                        updated_police = updated_police - 1
                    elif next_state_name == '?':
                        act_of_police.append(action_id(turns, turn, num_rows, num_cols, x, y, actions.index('quarantine') + 1))
                elif current_state_name == '?':
                    act_of_medics.append(action_id(turns, turn, num_rows, num_cols, x, y, actions.index('vaccinate') + 1))
                    act_of_police.append(action_id(turns, turn, num_rows, num_cols, x, y, actions.index('quarantine') + 1))

        for x in range(1, num_rows + 1):
            for y in range(1, num_cols + 1):
                next_state_name = next_obs[x - 1][y - 1]
                if next_state_name == '?':
                    if not updated_medics:
                        clauses.append([-action_id(turns, turn, num_rows, num_cols, x, y, actions.index('vaccinate') + 1)])
                    if not updated_police:
                        clauses.append([-action_id(turns, turn, num_rows, num_cols, x, y, actions.index('quarantine') + 1)])

        # check if there are teams left and if there are actions to preform.
        # if so, choose a valid sequence of actions for the team to preform, in the size of the available teams
        if updated_medics and len(act_of_medics):
            clauses += only_one_sequence(updated_medics, act_of_medics)
        if updated_police and len(act_of_police):
            clauses += only_one_sequence(updated_police, act_of_police)


# choose a valid sequence of actions for the team to preform
def only_one_sequence(updated_crew, acts_of_crew):
    if len(acts_of_crew) == 1:
        return [acts_of_crew]
    strs = ''
    for action in acts_of_crew:
        strs += str(action) + ' '
    symbols_strs = symbols(strs)
    sequence_and = [POSform(comb, minterms=[{symb: 1 for symb in comb}]) for comb in
                    combinations(symbols_strs, min(updated_crew, len(acts_of_crew)))]
    sop = SOPform(sequence_and, minterms=[{comb: 1} for comb in sequence_and])

    only_one_sequence_clause = True
    if len(acts_of_crew) > updated_crew:
        for combination1, combination2 in combinations(sop.args, 2):
            only_one_sequence_clause = And(only_one_sequence_clause, Or(Not(combination1), Not(combination2)))

    convert_sequence = to_cnf(And(only_one_sequence_clause, sop))
    final_sequence = convert_cnf_for_clauses(convert_sequence)
    return final_sequence


# converting to valid syntax
def convert_cnf_for_clauses(seq):
    to_list = str(seq).replace(" ", "").replace("(", "").replace(")", "").replace("~", "-").split('&')
    return [[int(lit) for lit in clause.split("|")] for clause in to_list]


# using the solver for the queries
def solve_the_queries(clauses, all_queries, turns, num_rows, num_cols):
    solution = {}
    g = Solver(name='glucose3', bootstrap_with=clauses)
    for query in all_queries:
        x = query[0][0]
        y = query[0][1]
        x += 1
        y += 1
        turn = query[1] + 1
        state = query[2]
        # running the solver with the assumption given in the query
        assumption = var_id(turns, turn, num_rows, num_cols, x, y, states.index(state) + 1)
        result = g.solve(assumptions=[assumption])
        # if the solver returns false then we know the assumption in the query is false
        if not result:
            solution[query] = 'F'
        else:
            # else, if the solver return true, then we'll run it again with ~assumption
            # to make sure there is no other possible state that gives true as well.
            scnd_result = g.solve(assumptions=[-assumption])
            # if there is another state that gives true (different from the state in the query)
            # then we can't return a conclusive answer to whether the query is true.
            # if there is no more states that return true, then we know for sure the query is true.
            if not scnd_result:
                solution[query] = 'T'
            else:
                solution[query] = '?'
    # delete the solver
    g.delete()
    return solution


def solve_problem(input):
    obss = input['observations']
    num_rows = len(obss[0])
    num_cols = len(obss[0][0])
    total_turns = len(obss)
    turns = range(1, total_turns + 1)
    num_police = input['police']
    num_medics = input['medics']
    all_queries = input['queries']
    clauses = []
    for turn in turns:
        current_obs = obss[turn-1]
        for x in range(1, num_rows + 1):
            for y in range(1, num_cols + 1):
                if current_obs[x - 1][y - 1] == '?':
                    only_one_true([var_id(turns, turn, num_rows, num_cols, x, y, known)
                                   for known in range(1, len(states) + 1)], clauses)
                    # we know there are no 'I' and 'Q' tiles in the first turn
                    if turn == 1:
                        clauses.append([-var_id(turns, turn, num_rows, num_cols, x, y, states.index('I') + 1)])
                        clauses.append([-var_id(turns, turn, num_rows, num_cols, x, y, states.index('Q') + 1)])
                else:
                    known = states.index(current_obs[x - 1][y - 1]) + 1
                    clauses.append([var_id(turns, turn, num_rows, num_cols, x, y, known)])
                    # when the state is known, we know that it can't be other states
                    for known, state in enumerate(states):
                        if state != current_obs[x - 1][y - 1]:
                            clauses.append([-var_id(turns, turn, num_rows, num_cols, x, y, known + 1)])

                # if there are 0 teams then we know that the actions 'vaccinate' and 'quarantine' are not available
                # therefore a tile can't be 'I' or 'Q'
                if num_medics == 0:
                    clauses.append([-var_id(turns, turn, num_rows, num_cols, x, y, states.index('I') + 1)])
                if num_police == 0:
                    clauses.append([-var_id(turns, turn, num_rows, num_cols, x, y, states.index('Q') + 1)])

                # check for pre-conditions and interfering actions.
                if turn < total_turns:
                    pre_conds(clauses, turns, turn, num_rows, num_cols, x, y, num_medics, num_police)
                    interfering_actions(clauses, turns, turn, num_rows, num_cols, x, y, num_medics, num_police)

                if turn >= 2:
                    previous_actions(clauses, turns, turn, num_rows, num_cols, x, y)

    if num_medics or num_police:
        possible_teams(clauses, turns, obss, num_police, num_medics, num_rows, num_cols)

    solution = solve_the_queries(clauses, all_queries, turns, num_rows, num_cols)
    return solution
