from itertools import product, combinations
from pysat.solvers import Glucose4

ids = ['207541293', '205968043']

# CONSTS
true = 1
false = 0
unknown = -1


# take the input and parse it into variables
def input_parser(input):
    num_police = input["police"]
    num_medics = input["medics"]
    observations = input["observations"]
    queries_list = []
    for query in input["queries"]:
        query_dict = {'tile': query[0], 'turn': query[1], 'question': query[2]}
        queries_list.append(query_dict)
    num_of_rows = len(observations[0])
    num_of_cols = len(observations[0][0])

    return num_police, num_medics, observations, queries_list, num_of_rows, num_of_cols


# add assumptions to the assumption list, if they are known for a fact
def update_assumptions_counter(pred_counter, assumptions, value):
    pred_counter[0] += 1
    if value == unknown:
        return
    if value == true:
        assumptions.append(pred_counter[0])
    elif value == false:
        assumptions.append(-pred_counter[0])


# initializes the turns map for the problem, sets the assumptions according to what is seen and certain
def turn_board_init(observations, rows, columns, pred_counter, assumptions, teams_dict, KB):
    states_dict = {}
    actions_dict = {}
    scenarios_dict = {}
    state_list = ['H', 'S', 'U']
    actions_list = ['turn healthy', 'turn sick', 'turn unpopulated']
    if teams_dict['police']:
        actions_list.extend(['turn quarantined', 'remain quarantined'])
        state_list.append('Q')
    if teams_dict['medics']:
        actions_list.extend(['turn immune', 'remain immune'])
        state_list.append('I')
    for turn, board in enumerate(observations):
        board_dict = {}
        board_action = {}
        scenario_turn_dict = {'sick_tiles': [], 'healthy_tiles': [], 'unknown_tiles': []}
        for i in range(rows):
            for j in range(columns):
                tile_dict = {}
                if board[i][j] == '?':
                    for state in state_list:
                        if turn == 0 and (state == 'Q' or state == 'I'):
                            update_assumptions_counter(pred_counter, assumptions, false)
                            tile_dict[state] = pred_counter[0]
                        else:
                            update_assumptions_counter(pred_counter, assumptions, unknown)
                            tile_dict[state] = pred_counter[0]
                    scenario_turn_dict['unknown_tiles'].append((i, j))
                # Case The tile is not "?":
                else:
                    if board[i][j] == 'H':
                        scenario_turn_dict['healthy_tiles'].append((i, j))
                    elif board[i][j] == 'S':
                        scenario_turn_dict['sick_tiles'].append((i, j))
                    for state in state_list:
                        if state == board[i][j]:
                            update_assumptions_counter(pred_counter, assumptions, true)
                            tile_dict[state] = pred_counter[0]
                        else:
                            update_assumptions_counter(pred_counter, assumptions, unknown)
                            tile_dict[state] = pred_counter[0]

                if turn > 0:
                    tile_actions_dict = {}
                    # create action predicates
                    for action in actions_list:
                        update_assumptions_counter(pred_counter, assumptions, unknown)
                        tile_actions_dict[action] = pred_counter[0]
                    board_action[(i, j)] = tile_actions_dict
                    KB.extend(only_one_state_per_tile(list(tile_actions_dict.values())))
                board_dict[(i, j)] = tile_dict
                KB.extend(only_one_state_per_tile(list(tile_dict.values())))
        states_dict[turn] = board_dict
        scenarios_dict[turn] = scenario_turn_dict
        if turn > 0:
            actions_dict[turn] = board_action
            if teams_dict['police']:
                q_scenarios = teams_scenarios(states_dict[turn-1], board_action, teams_dict['police'], scenarios_dict[turn-1]['sick_tiles'], scenarios_dict[turn-1]['unknown_tiles'], 'turn quarantined', 'S')
                only_one_scenario_per_turn(q_scenarios, pred_counter, KB)
            if teams_dict['medics']:
                i_scenarios = teams_scenarios(states_dict[turn-1], board_action, teams_dict['medics'], scenarios_dict[turn-1]['healthy_tiles'], scenarios_dict[turn-1]['unknown_tiles'], 'turn immune', 'H')
                only_one_scenario_per_turn(i_scenarios, pred_counter, KB)

    return states_dict, actions_dict


# translate the clause for "only one state at a time"
def only_one_state_per_tile(only_one_at_time_preds):
    clauses = [only_one_at_time_preds]
    for pred_1 in only_one_at_time_preds:
        for pred_2 in only_one_at_time_preds:
            if pred_1 > pred_2:
                clauses.append([-pred_1, -pred_2])
    return clauses


############################################# Actions #############################################


def action_translator(states_dict, actions_dict, rows, columns, predicate_counter, last_turn, KB, teams_dict):
    for turn, board in actions_dict.items():
        for tile, actions in board.items():
            for action, pred in actions.items():
                if action == 'turn sick':
                    KB.extend(turn_sick(states_dict, actions_dict, tile, turn, predicate_counter, KB, rows, columns, teams_dict['police']))
                elif action == 'turn healthy':
                    KB.extend(turn_healthy(states_dict, actions_dict, tile, turn, predicate_counter, KB, rows, columns, teams_dict['police']))
                elif action == 'turn unpopulated':
                    KB.extend(turn_unpopulated(states_dict, actions_dict, tile, turn, last_turn))
                elif action == 'turn quarantined':
                    KB.extend(turn_quarantined(states_dict, actions_dict, tile, turn))
                elif action == 'remain quarantined':
                    KB.extend(remain_quarantined(states_dict, actions_dict, tile, turn))
                elif action == 'turn immune':
                    KB.extend(turn_immune(states_dict, actions_dict, tile, turn, last_turn))
                elif action == 'remain immune':
                    KB.extend(remain_immune(states_dict, actions_dict, tile, turn))
                

# returns relevant tiles that may infect
def look_around(tile, rows, columns):
    relevant_tiles = []
    i, j = tile
    if i+1 < rows:
        relevant_tiles.append((i+1, j))
    if i-1 >= 0:
        relevant_tiles.append((i-1, j))
    if j+1 < columns:
        relevant_tiles.append((i, j+1))
    if j-1 >= 0:
        relevant_tiles.append((i, j-1))

    return relevant_tiles


def turn_sick(states_dict, actions_dict, tile, turn, predicate_counter, KB, rows, columns, are_police):
    # preconditions:
    precond_statement = [[-actions_dict[turn][tile]['turn sick']]]
    tiles_in_the_area = [rlud_tile for rlud_tile in look_around(tile, rows, columns)]
    # up to four neighbours that were sick last turn but not quarantined in the next, and last turn the tile was healthy
    sick_not_quarantined_flag = sick_not_quarantined(tiles_in_the_area, states_dict, turn, predicate_counter, KB, are_police)
    precond_statement.extend([[states_dict[turn-1][tile]['H'], sick_not_quarantined_flag]])
    if turn == 1:
        precond_statement.extend([[states_dict[turn-1][tile]['S']]])
    if turn == 2:  # another two options: last two turns were sick or last turn sick and one before healthy
        precond_statement.extend(
            [[states_dict[turn-1][tile]['S'], states_dict[turn-2][tile]['S']]])
    if turn >= 2:   
        precond_statement.extend(
            [[states_dict[turn-1][tile]['S'], states_dict[turn-2][tile]['H']]])
    if turn >= 3:
        precond_statement.extend(
            [[states_dict[turn-1][tile]['S'], states_dict[turn-2][tile]['S'], states_dict[turn-3][tile]['H']]])
    # create the right clauses for the KB
    precond_clauses = [list(clause_tuple) for clause_tuple in product(*precond_statement)]
    # add effects: the tile in the current turn is sick and isn't quarantined
    add_effect_clauses = [[-actions_dict[turn][tile]['turn sick'], states_dict[turn][tile]['S']]]
    # return all the created clauses
    precond_clauses.extend(add_effect_clauses)
    return precond_clauses


def turn_healthy(states_dict, actions_dict, tile, turn, predicate_counter, KB, rows, columns, are_police):
    # preconditions:
    precond_statement = [[-actions_dict[turn][tile]['turn healthy']]]
    tiles_in_the_area = [rlud_tile for rlud_tile in look_around(tile, rows, columns)]
    # last turn the tile itself was healthy ->
    # up to four neighbours that last turn were sick but got quarantined in the next turn
    sick_not_quarantined_flag = sick_not_quarantined(tiles_in_the_area, states_dict, turn, predicate_counter, KB, are_police)
    precond_statement.extend([[states_dict[turn-1][tile]['H'], -sick_not_quarantined_flag]])
    # last turn the tile itself was healthy, up to four neighbours that weren't sick last turn
    precond_statement.extend(
        [[states_dict[turn-1][tile]['H']] + [-states_dict[turn-1][rlud_tile]['S'] for rlud_tile in
         tiles_in_the_area]])
    if turn >= 2 and are_police:  # last two turns was quarantined, now healthy
        precond_statement.extend([[states_dict[turn-1][tile]['Q'], states_dict[turn-2][tile]['Q']]])
    if turn >= 3:  # last three turns was sick, now healthy
        precond_statement.extend(
            [[states_dict[turn-1][tile]['S'], states_dict[turn-2][tile]['S'],
              states_dict[turn-3][tile]['S']]])
    precond_clauses = [list(clause_tuple) for clause_tuple in product(*precond_statement)]
    # add effects: the current tile is healthy
    add_effect_clauses = [[-actions_dict[turn][tile]['turn healthy'], states_dict[turn][tile]['H']]]
    # return all the created clauses
    precond_clauses.extend(add_effect_clauses)
    return precond_clauses


def sick_not_quarantined(tiles_list, states_dict, turn, predicate_counter, KB, are_police):
    predicate_counter[0] += 1
    flag = predicate_counter[0]
    if are_police:
        list_of_l_preds = [[states_dict[turn-1][tile]['S'], -states_dict[turn][tile]['Q']] for tile in tiles_list]
        to_KB = [[flag, -pred1, -pred2] for pred1, pred2 in list_of_l_preds]
    else:
        list_of_l_preds = [[states_dict[turn-1][tile]['S']] for tile in tiles_list]
        to_KB = [[flag, -pred[0]] for pred in list_of_l_preds]
    to_KB.extend([list(clause_tuple) for clause_tuple in product([-flag], *list_of_l_preds)])
    KB.extend(to_KB)
    return flag


def turn_unpopulated(states_dict, actions_dict, tile, turn, last_turn):
    # the assumption part takes care that each U tile will be U in each and every turn
    precond_clause = [[-actions_dict[turn][tile]['turn unpopulated'], states_dict[turn-1][tile]['U']]]
    add_effect_statement = [[-actions_dict[turn][tile]['turn unpopulated']], [states_dict[t][tile]['U'] for t in range(last_turn+1)]]
    precond_clause.extend([list(clause_tuple) for clause_tuple in product(*add_effect_statement)])
    return precond_clause


def turn_quarantined(states_dict, actions_dict, tile, turn):
    # first is the precondition, second is the add effect
    return [[-actions_dict[turn][tile]['turn quarantined'], states_dict[turn-1][tile]['S']],
            [-actions_dict[turn][tile]['turn quarantined'], states_dict[turn][tile]['Q']]]


def remain_quarantined(states_dict, actions_dict, tile, turn):
    # preconditions:
    precond_statement = [[-actions_dict[turn][tile]['remain quarantined']]]
    if turn == 1:
         precond_statement.extend([[states_dict[turn-1][tile]['Q']]])
    if turn >= 2:  # another two options: last two turns were sick or last turn sick and one before healthy
        precond_statement.extend([[states_dict[turn-1][tile]['Q'], states_dict[turn-2][tile]['S']]])
    # create the right clauses for the KB
    precond_clauses = [list(clause_tuple) for clause_tuple in product(*precond_statement)]
    # add effects: the tile in the current turn is sick and isn't quarantined
    add_effect_clauses = [[-actions_dict[turn][tile]['remain quarantined'], states_dict[turn][tile]['Q']]]
    # return all the created clauses
    precond_clauses.extend(add_effect_clauses)
    return precond_clauses


def turn_immune(states_dict, actions_dict, tile, turn, last_turn):
    precond_clause = [[-actions_dict[turn][tile]['turn immune'], states_dict[turn-1][tile]['H']]]
    add_statements = [[-actions_dict[turn][tile]['turn immune']], [states_dict[future_turn][tile]['I'] for future_turn in range(turn, last_turn+1)]]
    precond_clause.extend([list(clause_tuple) for clause_tuple in product(*add_statements)])
    return precond_clause


def remain_immune(states_dict, actions_dict, tile, turn):
    # precondition
    return [[-actions_dict[turn][tile]['remain immune'], states_dict[turn-1][tile]['I']]]
    # add effects are already filled by "turn immune"


# takes a look at the given boards and tells whether certain actions were taken
def actions_identifier(observations, actions_dict, assumptions, rows, columns):
    for turn, obsrv in enumerate(observations):
        if turn == 0:
            continue
        for i in range(rows):
            for j in range(columns):
                current_tile = obsrv[i][j]
                previous_tile = observations[turn-1][i][j]
                if current_tile == 'S' and (previous_tile == 'H' or previous_tile == 'S'):
                    assumptions.append(actions_dict[turn][(i, j)]['turn sick'])
                elif current_tile == 'H' and (previous_tile == 'Q' or previous_tile == 'S' or previous_tile == 'H'):
                    assumptions.append(actions_dict[turn][(i, j)]['turn healthy'])
                elif current_tile == 'I' and previous_tile == 'H':
                    assumptions.append(actions_dict[turn][(i, j)]['turn immune'])
                elif current_tile == 'I' and previous_tile == 'I':
                    assumptions.append(actions_dict[turn][(i, j)]['remain immune'])
                elif current_tile == 'Q' and previous_tile == 'S':
                    assumptions.append(actions_dict[turn][(i, j)]['turn quarantined'])
                elif current_tile == 'Q' and previous_tile == 'Q':
                    assumptions.append(actions_dict[turn][(i, j)]['remain quarantined'])


############################################# Logic #############################################


def teams_scenarios(states_in_last_turn_dict, actions_in_turn_dict, num_of_teams, known_tiles, unknown_tiles, action, state):
    adressed_tiles_list = known_tiles + unknown_tiles
    scenarios_list = []
    for patients_num in range(len(unknown_tiles)+1):
        pateints_comb = list(combinations(unknown_tiles, patients_num))
        for unknown_tiles_set in pateints_comb:
            chosen_patients = known_tiles + list(unknown_tiles_set)  # these are the only patients, all the rest aren't
            treated_patients_comb = list(combinations(chosen_patients, num_of_teams))
            for treated_tiles in treated_patients_comb:
                scenario = []
                for tile in adressed_tiles_list:
                    if tile in treated_tiles:
                        scenario.append(states_in_last_turn_dict[tile][state])
                        scenario.append(actions_in_turn_dict[tile][action])
                    elif tile in chosen_patients:
                        scenario.append(states_in_last_turn_dict[tile][state])
                        scenario.append(-actions_in_turn_dict[tile][action])
                    else:
                        scenario.append(-states_in_last_turn_dict[tile][state])
                        scenario.append(-actions_in_turn_dict[tile][action])
                scenarios_list.append(scenario)

    return scenarios_list


# sets a flag for a clause with preds with ands between them
def iff_setter(list_of_predicates, flag):
    if list_of_predicates:
        ret_cnf_expr = [list(clause_tuple) for clause_tuple in product([-flag], list_of_predicates)]
        last_clause = [-pred for pred in list_of_predicates]
        last_clause.append(flag)
        ret_cnf_expr.append(last_clause)
        return ret_cnf_expr


def only_one_scenario_per_turn(list_of_scenarios, pred_counter, KB):
    flag_list = []
    for scenario in list_of_scenarios:
        pred_counter[0] += 1
        KB.extend(iff_setter(scenario, pred_counter[0]))
        flag_list.append(pred_counter[0])
    KB.extend(only_one_state_per_tile(flag_list))


def query_solver(queries_list, states_dict, KB, assumptions, actions_dict):
    if assumptions:
        assumptions.pop(0)
    answer_dict = {}
    solver = Glucose4()
    solver.append_formula(KB)
    for query in queries_list:
        tile = query['tile']
        turn = query['turn']
        state = query['question']
        pred = states_dict[turn][tile][state]
        if not solver.solve(assumptions=assumptions+[pred]):
            answer_dict[(tile, turn, state)] = 'F'
        elif solver.solve(assumptions=assumptions+[pred]) and not solver.solve(assumptions=assumptions+[-pred]):
            answer_dict[(tile, turn, state)] = 'T'
        elif solver.solve(assumptions=assumptions+[pred]) and solver.solve(assumptions=assumptions+[-pred]):
            answer_dict[(tile, turn, state)] = '?'

    return answer_dict


def solve_problem(input):
    KB = []
    num_police, num_medics, observations, queries_list, num_of_rows, num_of_columns = input_parser(input)
    teams_dict = {'police': num_police, 'medics': num_medics}
    last_turn = len(observations)-1
    predicate_counter = [0]
    assumptions = [0]
    states_dict, actions_dict = turn_board_init(observations, num_of_rows, num_of_columns, predicate_counter,
                                                         assumptions, teams_dict, KB)
    action_translator(states_dict, actions_dict, num_of_rows, num_of_columns, predicate_counter, last_turn, KB, teams_dict)
    actions_identifier(observations, actions_dict, assumptions, num_of_rows, num_of_columns)
    return query_solver(queries_list, states_dict, KB, assumptions, actions_dict)
