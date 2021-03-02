import random

ids = ['312132640', '311445639']
from pysat.solvers import Glucose4, Solver
from itertools import combinations



    # possible conditions:
#     '''
#     Cell options:
#         1. Cell can be: S0, S1, S2, H, Q0, Q1, I, U:
#             create map of all cell options
#             iterate over observations, for each cell insert all possible option (at least one possible state = [1000,2000,3000.....] and at most one possible state = [[-1000, -2000]....[-2000,-3000].....] = python func = from itertools import combinations (arr, size) returns all possible combinations
#
#
#
#
#     World actions:
#         2. if S, all neighboring H cells will be S in next turn
#         3. S stays S for 3 turns, then in turn 4 its H
#
#             H->S1      (pre: cell is H in previous turn and one of the neighbors is S in previous turn)
#             S1->S2     (pre: cell is S1 in previous turn)
#             S2->S3     (pre: cell is S2 in previous turn)
#             S3->H      (pre: cell is S3 in previous turn)
#             noop
#
#             create map of all possible world actions
#             iterate over observations, for each cell insert all possible actions (at least one possible action = [1000,2000,3000.....] and at most one possible action = [[-1000, -2000]....[-2000,-3000].....] = python func = from itertools import combinations (arr, size) returns all possible combinations
#
#
#     User action:
#         4. Q stays Q for 2 turns, then in turn 3 its H
#         5. if S, and police > 1, can put in Q
#         6. if H, and medics > 1, can vaccinate and turn to I forever
#         7. More than 1 of each team
# '''

def add_restrictions(g_array, observations):
    # turn 0
    i = 0
    for k in range(len(observations[i])):
        for j in range(len(observations[i][k])):
            first_restrictions = [21000, 22000, 30000, 50000, 51000]
            #print('zero_turn_restricions')
            for t in range(len(first_restrictions)):
                first_turn_restricions = (-1) * (first_restrictions[t] + (100 * i) + (10 * k) + j)
                #print([first_turn_restricions])
                g_array.append([first_turn_restricions])

    # #turn 1
    # i = 1
    # for k in range(len(observations)):
    #     for j in range(len(observations[k])):
    #         first_restrictions = [20000, 22000]
    #         print('first_turn_restricions')
    #         for t in range(len(first_restrictions)):
    #             first_turn_restricions = (-1) * (first_restrictions[t] + (100 * i) + (10 * k) + j)
    #             print([first_turn_restricions])
    #             g_array.append([first_turn_restricions])

def create_cell_options(meaningful_cell_numbers, observations, g_array):
    #print('cell options')
    for i in range(len(observations)):
        turn = i
        at_least_one_state = []

        for k in range(len(observations[i])):
            for j in range(len(observations[i][k])):
                for y in range(len(meaningful_cell_numbers)):
                    # if (not(k == 0 and meaningful_cell_numbers[y] in [21000, 22000, 50000, 51000])):
                    updated_turn = meaningful_cell_numbers[y] + (100 * turn) + (10 * k) + j
                    at_least_one_state.append(updated_turn)
                    if (y == len(meaningful_cell_numbers) - 1):
                        at_most_one_state = list(combinations(at_least_one_state, 2))
                        #print(at_least_one_state)
                        g_array.append(at_least_one_state)
                        for j in range(len(at_most_one_state)):
                            temp1 = (-1) * at_most_one_state[j][0]
                            temp2 = (-1) * at_most_one_state[j][1]
                            #print([temp1, temp2])
                            g_array.append([temp1,temp2])
                            # and when creating the observation itself, we will add the one true statment about each cell
                        at_least_one_state = []



def actions_precondition(actions_map, states_dic, y, i, k, j, cell_g_array):
    #print('precondition')
    updated_action = actions_map[y][2] + (100 * i) + (10 * k) + j
    updated_pre_condition = states_dic[actions_map[y][0]] + (100 * i) + (10 * k) + j
    #print([-updated_action, updated_pre_condition])
    #print([updated_action, -updated_pre_condition])
    cell_g_array.append([-updated_action, updated_pre_condition])
    cell_g_array.append([updated_action, -updated_pre_condition])

def action_effect_clauses(actions_map, states_dic, y, i, k, j, cell_g_array):
    #print('effect')
    updated_action = actions_map[y][2] + (100 * i) + (10 * k) + j
    updated_add_condition = states_dic[actions_map[y][1]] + (100 * (i + 1)) + (10 * k) + j
    updated_del_condition = states_dic[actions_map[y][0]] + (100 * (i + 1)) + (10 * k) + j

    #print([-updated_action, updated_add_condition])  #add
    #print([-updated_action, -updated_del_condition])  #del
    cell_g_array.append([-updated_action, updated_add_condition])
    cell_g_array.append([-updated_action, -updated_del_condition])

def handle_noop(i, k, j, states_dic, cell_g_array, noop_state):
    #print('noop')
    updated_noop = noop_state[2] + (100 * i) + (10 * k) + j
    updated_noop_pre_condition = states_dic[noop_state[1]] + (100 * i) + (10 * k) + j
    update_noop_effect = states_dic[noop_state[1]] + (100 * (i + 1)) + (10 * k) + j
    cell_g_array.append([-updated_noop, updated_noop_pre_condition])
    cell_g_array.append([-updated_noop, update_noop_effect])
    #print([-updated_noop, updated_noop_pre_condition]) # pre
    #print([-updated_noop, update_noop_effect])  # add


def handle_teams(actions_map, states_dic, y, i, k, j, cell_g_array, team):
    #print('team pre')
    updated_action = actions_map[y][2] + (100 * i) + (10 * k) + j
    updated_pre_state = states_dic[actions_map[y][0]] + (100 * i) + (10 * k) + j
    updated_pre_teams = team
    cell_g_array.append([-updated_action, updated_pre_state])
    cell_g_array.append([-updated_action, updated_pre_teams])
    #print([-updated_action, updated_pre_state])
    #print([-updated_action, updated_pre_teams])

    #print('team effect')
    updated_add_condition = states_dic[actions_map[y][1]] + (100 * (i + 1)) + (10 * k) + j
    updated_del_condition = states_dic[actions_map[y][0]] + (100 * (i + 1)) + (10 * k) + j
    cell_g_array.append([-updated_action, updated_add_condition])
    cell_g_array.append([-updated_action, -updated_del_condition])
    #print([-updated_action, updated_add_condition])  #add
    #print([-updated_action, -updated_del_condition])  #del



def find_neighbors(observation,i,j):
    neighbors = []
    #temp = []
    max_i = len(observation[0]) - 1
    max_j = len(observation[0][0]) - 1
    if i + 1 <= max_i:
        neighbors.append((i + 1, j))
    if j + 1 <= max_j:
        neighbors.append((i, j + 1))
    if i - 1 >= 0:
        neighbors.append((i - 1, j))
    if j - 1 >= 0:
        neighbors.append((i, j - 1))


    return neighbors

def general_infection_preconditions(cell_g_array,observations,i,k,j):
    neighbors = find_neighbors(observations,k,j)
    action_positive = 60000 + (100 * i) + (10 * k) + j
    immune_action = (72000 + (100 * i) + (10 * k) + j)
    action_negative = (-1) * action_positive
    state_precondition_positive = 10000 + (100*i) + (10 * k) + j
    state_precondition_negative = (-1) * state_precondition_positive
    sick_arr = [20000, 21000, 22000]
    sick_neighbors = [-action_positive]
    #print('infection caluses:')
    #print([action_negative, state_precondition_positive])
    cell_g_array.append([action_negative, state_precondition_positive])
    # print([action_negative, immune_action])
    # cell_g_array.append([action_negative, immune_action])
    for x in range(len(neighbors)):
        state_sick_precondition_positive_0 = 20000 + (100 * i) + (neighbors[x][0] * 10) + neighbors[x][1]
        state_sick_precondition_positive_1 = 21000 + (100 * i) + (neighbors[x][0] * 10) + neighbors[x][1]
        state_sick_precondition_positive_2 = 22000 + (100 * i) + (neighbors[x][0] * 10) + neighbors[x][1]
        state_sick_precondition_negative_0 = (-1) * state_sick_precondition_positive_0
        state_sick_precondition_negative_1 = (-1) * state_sick_precondition_positive_1
        state_sick_precondition_negative_2 = (-1) * state_sick_precondition_positive_2
        #print([action_positive,immune_action, state_precondition_negative, state_sick_precondition_negative_0])
        cell_g_array.append( [action_positive, immune_action, state_precondition_negative, state_sick_precondition_negative_0])
        #print([action_positive, immune_action, state_precondition_negative, state_sick_precondition_negative_1])
        cell_g_array.append( [action_positive, immune_action,  state_precondition_negative, state_sick_precondition_negative_1])
        #
        #
        #print([action_positive,immune_action, state_precondition_negative, state_sick_precondition_negative_2])
        cell_g_array.append( [action_positive, immune_action, state_precondition_negative, state_sick_precondition_negative_2])
        for z in range(len(sick_arr)):
            sick_neighbors.append(sick_arr[z] + (100 * i) + (neighbors[x][0] * 10) + neighbors[x][1])
    #print([sick_neighbors])
    cell_g_array.append(sick_neighbors)


def create_world_actions(num_of_cells, meaningful_world_numbers, observations, actions_map, states_dic, meaningful_cell_numbers, cell_g_array):
    #print('world_options')
    create_cell_options(meaningful_world_numbers, observations, cell_g_array) #create for each cell all optional actions in the world

    for i in range(len(observations)):
    # for i in range(1):
        for k in range(len(observations[i])):
        # for k in range(1):
            for j in range(len(observations[i][k])):
           # for j in range(1):
                #print('-----------')
                #print('Timestep {}, Cell {}/{}'.format(i, k, j))
                #print( '-----------')
                for y in range(len(actions_map)):
                    if (actions_map[y][0] in ('S0', 'S1', 'S2', 'Q0', 'Q1')):
                        actions_precondition(actions_map, states_dic, y, i, k, j, cell_g_array)
                        action_effect_clauses(actions_map, states_dic, y, i, k, j, cell_g_array)

                    if (actions_map[y][0] == 'H' and actions_map[y][1] == 'S0'):
                        general_infection_preconditions(cell_g_array,observations,i,k,j)
                        action_effect_clauses(actions_map, states_dic, y, i, k, j, cell_g_array)

                    if(actions_map[y][0] == 'noop'):
                        handle_noop(i, k, j, states_dic, cell_g_array, actions_map[y])

                    # medics: 12, police: 13

                    if ((actions_map[y][0] == 'H' and actions_map[y][1] == 'I')):
                        handle_teams(actions_map, states_dic, y, i, k, j, cell_g_array, 12)

                    # if((actions_map[y][1] == 'Q0')):
                    #     handle_teams(actions_map, states_dic, y, i, k, j, cell_g_array, 13)



def insert_observation(input, world_g_array,meaningful_cell_numbers):
    state_len = len( input["observations"] )
    state = input["observations"]
    #print( 'inserting current observastion to g: ' )
    s_arr = [20000, 21000, 22000]
    for k in range(state_len):
        for i in range(len(state[k])):
            for j in range(len(state[k][i])):
                temp = 0
                if state[k][i][j] == 'H':
                    temp = 10000 + (k * 100) + (i * 10) + j
                    #print([temp])
                    world_g_array.append( [temp] )
                    continue
                if state[k][i][j] == 'S':
                    temp_s_arr = []
                    for s in range(len(s_arr)):
                        temp_s_arr.append(s_arr[s] + (k * 100) + (i * 10) + j)
                    world_g_array.append(temp_s_arr)
                    #print(temp_s_arr)
                    continue
                if state[k][i][j] == 'I':
                    #print( [temp] )
                    temp = 30000 + (k * 100) + (i * 10) + j
                    world_g_array.append( [temp] )
                    continue
                if state[k][i][j] == 'U':
                    #print( [temp] )
                    temp = 40000 + (k * 100) + (i * 10) + j
                    world_g_array.append( [temp] )
                    continue
                if state[k][i][j] == 'Q':
                    if (k - 1) >= 0:
                        if state[k - 1][i][j] == 'Q':
                            temp = 51000 + (k * 100) + (i * 10) + j
                            #print( [temp] )
                            world_g_array.append( [temp] )
                            continue
                    else:
                        temp = 50000 + (k * 100) + (i * 10) + j
                        #print( [temp] )
                        world_g_array.append( [temp] )
                    continue


def limit_teams_actions(observations, g_array):
    #print('limit team action per cell')
    teams_numbers = [72000]
    for y in range(len(teams_numbers)):
        for i in range(len(observations)):
            all_cells = []
            for k in range(len(observations[i])):
                for j in range(len(observations[i][k])):
                    action_per_cell = (-1) * (teams_numbers[y] + (100 * i) + (10 * k) + j)
                    all_cells.append(action_per_cell)
            positive_all_cells = [-i for i in all_cells]
            positive_all_cells.append(-12)
            for turn in range(len(observations)):
                for row in range(len(observations[turn])):
                    for col in range(len(observations[turn][row])):
                        update_turn = (-1) * (60000 + (100 * turn) + (10 * row) + col)
                        add_clause = [*positive_all_cells, update_turn]
                        #print(add_clause)
                        g_array.append(add_clause)
                        # positive_all_cells.pop()

            at_most_one_action = list(combinations(all_cells, 2))
            for x in range(len(at_most_one_action)):
                g_array.append(list(at_most_one_action[x]))
                #print([at_most_one_action[x]])

def check_if_unknown(meaningful_cell_numbers, queries, q, g, states_dic):
    curr_state = queries[q][2]
    for state in meaningful_cell_numbers:
        if (curr_state == 'S'):
            temp = 2
        if (curr_state == 'Q'):
            temp = 5
        if (curr_state != 'S' and curr_state != 'Q'):
            temp = (states_dic[curr_state]) / 10000
        temp_dic = state/10000 // 1
        if(temp != temp_dic):
            temp_assump = state + queries[q][1] * 100 + queries[q][0][0] * 10 + queries[q][0][1]
            temp_answer = g.solve(assumptions=[temp_assump])
            if temp_answer == True:
                return ('?')

def hadle_query(queries, q, states_dic, g):
    state = queries[q][2]
    if(state == 'Q'):
        assump_Q0 = [50000 + queries[q][1] * 100 + queries[q][0][0] * 10 + queries[q][0][1]]
        assumption_Q0 = g.solve(assumptions=assump_Q0)
        assump_Q1 = [51000 + queries[q][1] * 100 + queries[q][0][0] * 10 + queries[q][0][1]]
        assumption_Q1 = g.solve(assumptions=assump_Q1)
        if (assumption_Q0 or assumption_Q1):
            return True
        else:
            return False
    if(state == 'S'):
        assump_S0 = [20000 + queries[q][1] * 100 + queries[q][0][0] * 10 + queries[q][0][1]]
        assumption_S0 = g.solve(assumptions=assump_S0)
        assump_S1 = [21000 + queries[q][1] * 100 + queries[q][0][0] * 10 + queries[q][0][1]]
        assumption_S1 = g.solve(assumptions=assump_S1)
        assump_S2 = [22000 + queries[q][1] * 100 + queries[q][0][0] * 10 + queries[q][0][1]]
        assumption_S2 = g.solve(assumptions=assump_S2)
        if (assumption_S0 or assumption_S1 or assumption_S2):
            return True
        else:
            return False

    assump = [states_dic[state] + queries[q][1] * 100 + queries[q][0][0] * 10 + queries[q][0][1]]
    assumption_answer = g.solve(assumptions=assump)
    return assumption_answer

def solve_problem(input):
    g = Glucose4(with_proof=True)
    police_num = input["police"]
    medic_num = input["medics"]
    queries = input["queries"]
    g_array = []
    observations = input['observations']
    num_of_cells = len(observations) * len(observations[0])
    meaningful_cell_numbers = [10000, 20000, 21000, 22000, 30000, 40000, 50000, 51000]
    meaningful_world_numbers = [60000, 61000, 62000, 63000, 64000, 65000, 66000, 70000, 71000, 72000]
    states_dic = {'H': 10000, 'S0': 20000, 'S1': 21000, 'S2': 22000, 'I': 30000, 'U': 40000, 'Q0': 50000, 'Q1': 51000}
    actions_map = [('H', 'S0', 60000), ('S0', 'S1', 61000), ('S1', 'S2', 62000), ('S2', 'H', 63000),
                   ('noop', 'H', 64000), ('noop', 'I', 65000), ('noop', 'U', 66000),
                   ('Q0', 'Q1', 70000), ('Q1', 'H', 71000), ('H', 'I', 72000)]

    ## todo: add S -> Q0, Q0->Q1, Q1->H, H->I
    ## todo: פעולות אפשריות כמספר הצוותים
    ## todo: in H->S0 need to check if S wasn't turned to Q



    add_restrictions(g_array, observations)
    create_cell_options(meaningful_cell_numbers, observations, g_array)
    create_world_actions(num_of_cells, meaningful_world_numbers, observations, actions_map, states_dic, meaningful_cell_numbers, g_array) #todo if bug, check disjunction from presentation
    insert_observation(input, g_array, meaningful_cell_numbers)
    limit_teams_actions(observations, g_array)
    if (input['medics'] > 0):
        g_array.append([12])
    else:
        g_array.append([-12])

    #print('Adding')
    for i in range(len(g_array)):
        #print(g_array[i])
        r = g.add_clause(g_array[i], no_return=True)


    answer_dict = {}
    for q in range(len(queries)):
        assumption_answer = hadle_query(queries, q, states_dic, g)
        if(assumption_answer == True):
            unknown_answer = check_if_unknown(meaningful_cell_numbers, queries, q, g, states_dic)
            if(unknown_answer == '?'):
                answer_dict[queries[q]] = '?'
            else:
                answer_dict[queries[q]] = 'T'
        else:
            answer_dict[queries[q]] = 'F'

    return answer_dict