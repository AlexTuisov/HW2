import itertools
import copy
import sympy.logic.algorithms.dpll as dpll_alg
from sympy.core import symbols
from functools import reduce

ids = ['201209020', '308869700']


def find_initial_list_tile_letter(tile, turn):
    """
    this function transfers a letter to a tile state.
    tile state location info:
    [H, U, I, Q0, Q1, S0, S1, S2]

    :param tile: a letter from the user.
    :type tile: str
    :param turn: the turn which the tile is related.
    :type turn: int
    :return: tile_state_list: tile state as a list, gives a True or False list with the number as True
    and others as False
    :type return list
    """
    tile_state_list = [False for i in range(8)]
    if turn == 0:
        if tile == 'H':
            tile_state_list[0] = True
        elif tile == 'U':
            tile_state_list[1] = True
        elif tile == 'I':
            tile_state_list[2] = True
        elif tile == 'Q':
            tile_state_list[3] = True
        elif tile == 'S':
            tile_state_list[5] = True
        else:
            tile_state_list = [True for i in range(8)]

    elif turn == 1:
        if tile == 'H':
            tile_state_list[0] = True
        elif tile == 'U':
            tile_state_list[1] = True
        elif tile == 'I':
            tile_state_list[2] = True
        elif tile == 'Q':
            tile_state_list[3] = True
            tile_state_list[4] = True
        elif tile == 'S':
            tile_state_list[5] = True
            tile_state_list[6] = True
        else:
            tile_state_list = [True for i in range(8)]

    else:
        if tile == 'H':
            tile_state_list[0] = True
        elif tile == 'U':
            tile_state_list[1] = True
        elif tile == 'I':
            tile_state_list[2] = True
        elif tile == 'Q':
            tile_state_list[3] = True
            tile_state_list[4] = True
        elif tile == 'S':
            tile_state_list[5] = True
            tile_state_list[6] = True
            tile_state_list[7] = True
        else:
            tile_state_list = [True for i in range(8)]

    return tile_state_list


def convert_tile_to_symbolic_clause(tile):
    """
    this function transfers a tile (given as a list of True-False) to a  clause.

    :param tile: True - False list
    :type tile: list
    :return: clause:
    :type return:
    """
    h, u, i, q0, q1, s0, s1, s2 = symbols('h, u, i, q0, q1, s0, s1, s2')

    if tile[0]:
        clause = h
    else:
        clause = ~h

    if tile[1]:
        clause = clause & u
    else:
        clause = clause & ~u

    if tile[2]:
        clause = clause & i
    else:
        clause = clause & ~i

    if tile[3] and not tile[4]:
        clause = clause & q0 & ~q1
    elif tile[4] and not tile[3]:
        clause = clause & q1 & ~q0
    elif not tile[3] and not tile[4]:
        clause = clause & ~q0 & ~q1
    else:
        clause = clause & (q0 | q1)

    if tile[5] and not tile[6]:
        clause = clause & s0 & ~s1 & ~s2
    elif tile[5] and tile[6] and not tile[7]:
        clause = clause & (s0 | s1) & ~s2
    elif tile[6] and not tile[5]:
        clause = clause & s1 & ~s0 & ~s2
    elif tile[7] and not tile[6]:
        clause = clause & s2 & ~s0 & ~s1
    elif not tile[5] and not tile[6] and not tile[7]:
        clause = clause & ~s0 & ~s1 & ~s2
    else:
        clause = clause & (s0 | s1 | s2)

    if reduce((lambda x, y: x and y), tile):  # question mark
        clause = h | u | i | q0 | q1 | s0 | s1 | s2

    return clause


def convert_dpll_satisfiable_answer_to_clause(dpll_dict_ans):
    if not dpll_dict_ans:
        clause = False
    else:
        h, u, i, q0, q1, s0, s1, s2 = symbols('h, u, i, q0, q1, s0, s1, s2')

        if dpll_dict_ans[h]:
            clause = h
        else:
            clause = ~h

        if dpll_dict_ans[u]:
            clause = clause & u
        else:
            clause = clause & ~u

        if dpll_dict_ans[i]:
            clause = clause & i
        else:
            clause = clause & ~i

        if dpll_dict_ans[q0]:
            clause = clause & q0
        else:
            clause = clause & ~q0

        if dpll_dict_ans[q1]:
            clause = clause & q1
        else:
            clause = clause & ~q1

        if dpll_dict_ans[s0]:
            clause = clause & s0
        else:
            clause = clause & ~s0

        if dpll_dict_ans[s1]:
            clause = clause & s1
        else:
            clause = clause & ~s1

        if dpll_dict_ans[s2]:
            clause = clause & s2
        else:
            clause = clause & ~s2

    return clause


def qm_options_generator(optional_qm):
    answer = list(reduce((lambda sqe1, seq2: [[xx, yy] for xx in sqe1 for yy in seq2]), optional_qm))
    final_list = []
    for ans in answer:
        counter = len(optional_qm)
        tempo_list = []
        ans_dcopy = copy.deepcopy(ans)
        while counter > 1:
            if counter == 2:
                tempo_list.append(ans_dcopy[1])
                tempo_list.append(ans_dcopy[0])
            else:
                tempo_list.append(ans_dcopy[1])
                ans_dcopy = ans_dcopy[0]
            counter -= 1
        tempo_list.reverse()
        final_list.append(tempo_list)
    return final_list


def is_question_mark(tile):
    """
    this function returns True if the tile cntains question mark

    :param tile: tile represented as a list of True-False
    :type tile: list
    :return: True or False
    :type return: bool
    """
    return len(list(filter((lambda x: x), tile))) == 8


def find_question_mark_locations(observation):
    """
    this function finds the locations of the '?' in the current observation
    tile state location info:
    [H, U, I, Q0, Q1, S0, S1, S2]

    :param observation: a list that represents the current observation.
    :type observation: list
    :return: question_mark_locations: (x,y) location of all the '?' in the current observation
    :type return: list
    """
    question_mark_locations = []
    for i in range(len(observation)):
        for j in range(len(observation[i])):
            if is_question_mark(observation[i][j]):
                question_mark_locations.append((i, j))
    return question_mark_locations


def number_to_tile_state(num):
    """
    this function transfers a number to a tile state.
    tile state location info:
    [H, U, I, Q0, Q1, S0, S1, S2]

    :param num: a number from the user. the function transfers a number to his tile state.
    :type num: int
    :return: num_in_tile_representation:  tile state as a list, gives a True or False list
     with the number as True and others as False
    :type return: list
    """
    num_in_tile_representation = [False for i in range(8)]
    num_in_tile_representation[num] = True
    return num_in_tile_representation


def tile_to_number(tile):
    for i in range(len(tile)):
        if tile[i]:
            return i


def calc_qm_option_list(possible_observations, qm_location):
    return list(set([tile_to_number(pos_observation[qm_location[0]][qm_location[1]]) for pos_observation
                     in possible_observations]))


def find_sick_location(observation):
    """
    this function finds the locations of the 'S' in the current observation
    tile state location info:
    [H, U, I, Q0, Q1, S0, S1, S2]

    :param observation:
    :type observation: list
    :return: sick_locations
    :type return: list
    """
    sick_locations = []
    for i in range(len(observation)):
        for j in range(len(observation[i])):
            if (observation[i][j])[5] or (observation[i][j])[6] or (observation[i][j])[7] \
                    and not is_question_mark(observation[i][j]):
                sick_locations.append((i, j))
    return sick_locations


def find_healthy_location(observation):
    """
    this function finds the locations of the 'H' in the current observation
    tile state location info:
    [H, U, I, Q0, Q1, S0, S1, S2]

    :param observation: the current observation as a list of lists with True-False.
    :type observation: list
    :return: healthy_locations:
    :type return: list
    """
    healthy_locations = []
    for i in range(len(observation)):
        for j in range(len(observation[i])):
            if (observation[i][j])[0] and not is_question_mark(observation[i][j]):
                healthy_locations.append((i, j))
    return healthy_locations


def find_quarantine_location(observation):
    """
    this function finds the locations of the 'Q' in the current observation
    tile state location info:
    [H, U, I, Q0, Q1, S0, S1, S2]

    :param observation: the current observation as a list of lists with True-False.
    :type observation: list
    :return: healthy_locations:
    :type return: list
    """
    quarantine_locations = []
    for i in range(len(observation)):
        for j in range(len(observation[i])):
            if (observation[i][j])[3] and not is_question_mark(observation[i][j]):
                quarantine_locations.append((i, j))
    return quarantine_locations


def find_immune_location(observation):
    """
    this function finds the locations of the 'H' in the current observation
    tile state location info:
    [H, U, I, Q0, Q1, S0, S1, S2]

    :param observation: the current observation as a list of lists with True-False.
    :type observation: list
    :return: healthy_locations:
    :type return: list
    """
    immune_location = []
    for i in range(len(observation)):
        for j in range(len(observation[i])):
            if (observation[i][j])[2] and not is_question_mark(observation[i][j]):
                immune_location.append((i, j))
    return immune_location


def find_unpopulated_location(observation):
    """
    this function finds the locations of the 'U' in the current observation
    tile state location info:
    [H, U, I, Q0, Q1, S0, S1, S2]

    :param observation: the current observation as a list of lists with True-False
    :type observation: list
    :return: unpopulated_locations
    :type return: list
    """
    unpopulated_locations = []
    for i in range(len(observation)):
        for j in range(len(observation[i])):
            if (observation[i][j])[1] and not is_question_mark(observation[i][j]):
                unpopulated_locations.append((i, j))
    return unpopulated_locations


def find_healthy_with_sick_neighbors(healthy, sick):
    """
    this function finds the locations of healthy locations with sick neighbors

    :param healthy: the location of healthy locations in (x,y) coor. of the matrix
    :type healthy: list
    :param sick: the location of sick locations in (x,y) coor. of the matrix
    :type sick: list
    :return: set of tuples that gives the location of healthy with sick neighbors
    :type return: set
    """
    temp = []
    for healthy_spot in healthy:
        for sick_spot in sick:
            if (abs(healthy_spot[0]-sick_spot[0]) == 1 and abs(healthy_spot[1]-sick_spot[1]) == 0) \
                    or (abs(healthy_spot[0]-sick_spot[0]) == 0 and abs(healthy_spot[1]-sick_spot[1]) == 1):
                temp.append(healthy_spot)
    return set(temp)


def actions(state, must_be_actions, qm_locations, police, medics):
    """Returns all the actions that can be executed in the given
    state. The result should be a tuple (or other iterable) of actions
    as defined in the problem description file

    :param state: list of lists
    :type state: list of lists
    :param must_be_actions:
    :type must_be_actions: list of lists
    :param qm_locations:
    :type qm_locations: list of lists
    :param police: .
    :type police: int
    :param medics: .
    :type medics: int
    :return: num_in_tile_representation:  tile state as a list, gives a True or False list
     with the number as True and others as False
    :type return: list
    """
    final_list = []
    temp = must_be_actions.copy()
    sick_location = [loc for loc in find_sick_location(state) if loc in qm_locations]
    healthy_location = [loc for loc in find_healthy_location(state) if loc in qm_locations]

    # combination of valid police locations
    police_comb = list(itertools.combinations(sick_location, min(police, len(sick_location))))
    # combination of valid medic locations
    medics_comb = list(itertools.combinations(healthy_location, min(medics, len(healthy_location))))
    if len(medics_comb) == 0:
        for p_comb1 in police_comb:
            for location in p_comb1:
                temp.append(("quarantine", location))
            final_list.append(tuple(temp))
            temp = must_be_actions.copy()

    elif len(police_comb) == 0:
        for m_comb1 in medics_comb:
            for location in m_comb1:
                temp.append(("vaccinate", location))
            final_list.append(tuple(temp))
            temp = must_be_actions.copy()
    else:
        for p_comb1 in police_comb:
            for m_comb1 in medics_comb:
                for location in p_comb1:
                    temp.append(("quarantine", location))
                for location in m_comb1:
                    temp.append(("vaccinate", location))

                final_list.append(tuple(temp))
                temp = must_be_actions.copy()
    if not final_list:
        return [()]
    else:
        return final_list


def generate_new_state(state, action):
    """Return the state that results from executing the given
    action in the given state. The action must be one of
    self.actions(state).

    :param state: the current observation as a list of lists with True-False
    :type state: list
    :param action: the current observation as a list of lists with True-False
    :type action: tuple
    :return: unpopulated_locations
    :type return: list
    """
    new_state = copy.deepcopy(state)
    new_q_locations = []

    # medics and police do their jobs
    for act in action:
        if act[0] == "quarantine":
            new_state[act[1][0]][act[1][1]] = [False, False, False, True, False, False, False, False]  # change S to Q
            new_q_locations.append((act[1][0], act[1][1]))
        elif act[0] == "vaccinate":
            new_state[act[1][0]][act[1][1]] = [False, False, True, False, False, False, False, False]  # change H to I
    # Healthy to sick (because of neighbors)
    # sick = find_sick_location(new_state)
    # healthy = find_healthy_location(new_state)

    h2s = find_healthy_with_sick_neighbors(find_healthy_location(new_state), find_sick_location(new_state))
    # change H to S
    for loc in h2s:
        new_state[loc[0]][loc[1]] = [False, False, False, False, False, True, False, False]
    # dynamics - quarantine and sick
    for i in range(len(new_state)):
        for j in range(len(new_state[i])):
            if new_state[i][j][4]:
                new_state[i][j] = [True, False, False, False, False, False, False, False]
            elif new_state[i][j][3] and (i, j) not in new_q_locations:
                new_state[i][j] = [False, False, False, False, True, False, False, False]
            elif new_state[i][j][7]:
                new_state[i][j] = [True, False, False, False, False, False, False, False]
            elif new_state[i][j][6]:
                new_state[i][j] = [False, False, False, False, False, False, False, True]
            elif new_state[i][j][5] and (i, j) not in h2s:
                new_state[i][j] = [False, False, False, False, False, False, True, False]

    return new_state


def solve_problem(input):
    """
    the MAIN function. calls all the other functions
    :param input: 4 keys dict - police(int), medics(int), observations(list), queries(list)
    :type input: dict
    :return: : dict where the keys are the queries and the values are 'T', 'F' or '?'
    :type return: dict
    """
    # put your solution here, remember the format needed

    # tile options:
    # [H, U, I, Q0, Q1, S0, S1, S2]

    police = input["police"]
    medics = input["medics"]
    queries = input["queries"]

    ######################### Step 0.0 - set the given observation into a 'state map' #######################
    state_map = []
    observation_counter = 0

    #### Step 0.1 define the dict that we will return at the end. the dict answer order is as the queries order ###
    queries_answer_dict = {}
    for query in queries:
        queries_answer_dict[query] = '?'

    question_mark_options = []
    question_mark_locations = []

    ### Step 0.2 find the 'U' locations in the future states and implement it in the previous states ###
    unpopulated_location_list = []
    for observation in input["observations"]:
        temp_observation = []
        for row in observation:
            temp_row = []
            for tile in row:
                temp_row.append(find_initial_list_tile_letter(tile, observation_counter))
            temp_observation.append(temp_row)
        state_map.append(temp_observation)
        unpopulated_location_list.extend(find_unpopulated_location(temp_observation))
        observation_counter += 1

    unpopulated_location_list = list(set(unpopulated_location_list))
    for observation in state_map:
        for loc in unpopulated_location_list:
            observation[loc[0]][loc[1]] = number_to_tile_state(1)  # U

    # start going through the solution steps:
    for turn_counter in range(len(state_map)-1):
        if turn_counter == 0:
            ########## step 1 - find all '?' locations and next level combinations taken from all '?' ##########
            state_options = [0, 1, 5]
            question_mark_locations = find_question_mark_locations(state_map[turn_counter])
            question_mark_options = list(
                itertools.combinations_with_replacement(state_options, len(question_mark_locations)))


        ################## step 2.0 - find all possible next level observations ###################
        actual_observation_list = []
        possible_next_observation_list = []

        # Step 3.0 find locations in the next turn that are Q and in this turn are S
        q_location_next_turn = find_quarantine_location(state_map[turn_counter+1])
        s_location = find_sick_location(state_map[turn_counter])
        # in this locations the police must act
        police_action_location = [loc for loc in q_location_next_turn if loc in s_location]

        # Step 3.0 find locations in the next turn that are I and in this turn are H
        i_location_next_turn = find_immune_location(state_map[turn_counter+1])
        h_location = find_healthy_location(state_map[turn_counter])
        # in this locations the medics must act
        medics_action_location = [loc for loc in i_location_next_turn if loc in h_location]

        for qm_option in question_mark_options:
            actual_observation = copy.deepcopy(state_map[turn_counter]) # copy the curent state to 'actual_observation'
            for i in range(len(question_mark_locations)):
                actual_observation[(question_mark_locations[i])[0]][(question_mark_locations[i])[1]] = \
                    number_to_tile_state(qm_option[i])

            ######## step 3.1 - medics, police and system dynamics #######
            # using the data in step 3.0 - earlier we searched for given Q and I locations in next turn and now
            # we want to use this data and append the police and medics actions that are making it happen.
            must_be_actions = []
            for loc in police_action_location:
                must_be_actions.append(("quarantine", loc))
            for loc in medics_action_location:
                must_be_actions.append(("vaccinate", loc))

            # find '?' in the current and the next turn.
            two_turns_question_mark_locations = copy.deepcopy(question_mark_locations)
            two_turns_question_mark_locations.extend(find_question_mark_locations(state_map[turn_counter+1]))
            two_turns_question_mark_locations = list(set(two_turns_question_mark_locations))

            # if there are free police and medics, we will use the 'actions' function to find al the 'possible_actions'.
            if not (len(police_action_location) == police and len(medics_action_location) == medics):
                possible_actions = actions(actual_observation,
                                           must_be_actions, two_turns_question_mark_locations,
                                           police-len(police_action_location),
                                                           medics - len(medics_action_location))
            else:
                possible_actions = [tuple(must_be_actions)]
                if not must_be_actions:
                    possible_actions = [()]

            # go through all the actions and check if they are possible with next known state
            for action in possible_actions:
                # check with DPLL if generate_new_state(actual_observation, action) similar to state(next turn)
                possible_next_observation = generate_new_state(actual_observation, action)

                ### step 4 - DPLL compare next level observations to the known \ given next level observation ###
                break_flag = False
                for row in range(len(possible_next_observation)):
                    for col in range(len(possible_next_observation[row])):
                        possible_next_observation_tile_clause = \
                            convert_tile_to_symbolic_clause(possible_next_observation[row][col])
                        next_observation_tile_clause = \
                            convert_tile_to_symbolic_clause(state_map[turn_counter+1][row][col])
                        if not dpll_alg.dpll_satisfiable(possible_next_observation_tile_clause &
                                                         next_observation_tile_clause):
                            break_flag = True
                            break
                    if break_flag:
                        break

                if not break_flag:
                    actual_observation_list.append(actual_observation)
                    possible_next_observation_list.append(possible_next_observation)

        ##### step 5 - conclusions ####
        # step5.1 - compare current turn\step
        if len(actual_observation_list) == 1:
            # if the len of the current possible observation list is 1, then it is the only possible option.
            state_map[turn_counter] = actual_observation_list[0]
        elif len(actual_observation_list) > 1:
            # if the len of the current possible observation list is greater than 1,
            # then there are several options, and we have to check them using dpll
            for qm_loc in question_mark_locations:
                comparison_break_flag = False
                comparable_observation_tile_clause = \
                    convert_tile_to_symbolic_clause(actual_observation_list[0][qm_loc[0]][qm_loc[1]])
                for act_observation in actual_observation_list:
                    comparison_ans = dpll_alg.dpll_satisfiable(comparable_observation_tile_clause &
                                                               convert_tile_to_symbolic_clause
                                                               (act_observation[qm_loc[0]][qm_loc[1]]))
                    if not comparison_ans:
                        comparison_break_flag = True
                        break

                if not comparison_break_flag:
                    state_map[turn_counter][qm_loc[0]][qm_loc[1]] = actual_observation_list[0][qm_loc[0]][qm_loc[1]]

        question_mark_locations_next_turn = find_question_mark_locations(state_map[turn_counter+1])

        # step5.2 - compare next turn\step
        qm_next_dict = {}
        if len(possible_next_observation_list) == 1:
            state_map[turn_counter + 1] = possible_next_observation_list[0]
        elif len(possible_next_observation_list) > 1:
            for qm_loc in question_mark_locations_next_turn:
                comparison_break_flag = False
                comparable_observation_tile_clause = \
                    convert_tile_to_symbolic_clause(possible_next_observation_list[0][qm_loc[0]][qm_loc[1]])
                for pos_next_observation in possible_next_observation_list:
                    comparison_ans = dpll_alg.dpll_satisfiable(comparable_observation_tile_clause &
                                                               convert_tile_to_symbolic_clause
                                                                   (pos_next_observation[qm_loc[0]][qm_loc[1]]))
                    if not comparison_ans:
                        comparison_break_flag = True
                        break

                if not comparison_break_flag:
                    state_map[turn_counter+1][qm_loc[0]][qm_loc[1]] = \
                        possible_next_observation_list[0][qm_loc[0]][qm_loc[1]]
                else:
                    qm_next_dict[(qm_loc[0], qm_loc[1])] = calc_qm_option_list(possible_next_observation_list, qm_loc)

        question_mark_locations = list(qm_next_dict.keys())
        if question_mark_locations:
            question_mark_options = qm_options_generator([qm_next_dict[key] for key in question_mark_locations])

        # step5.3 - go through the queries and answer them
        query_to_del = copy.deepcopy(queries)
        for query in query_to_del:
            query_answer_list = []
            if query[1] == turn_counter:
                for act_observation in actual_observation_list:
                    query_loc = query[0]
                    query_letter = find_initial_list_tile_letter(query[2], turn_counter)
                    query_letter_clause = convert_tile_to_symbolic_clause(query_letter)
                    act_observation_tile_clause = \
                        convert_tile_to_symbolic_clause(act_observation[query_loc[0]][query_loc[1]])
                    query_answer_list.append(dpll_alg.dpll_satisfiable(query_letter_clause &
                                                                       act_observation_tile_clause))

                if len(list(filter((lambda x: x), query_answer_list))) == len(actual_observation_list) \
                        and len(actual_observation_list) > 0:
                    queries_answer_dict[query] = 'T'
                    queries.remove(query)

                elif len(list(filter((lambda x: x), query_answer_list))) == 0 or len(actual_observation_list) == 0:
                    queries_answer_dict[query] = 'F'
                    queries.remove(query)
                else:
                    queries_answer_dict[query] = '?'

            elif query[1] == turn_counter + 1:
                for pos_observation in possible_next_observation_list:
                    query_loc = query[0]
                    query_letter = find_initial_list_tile_letter(query[2], turn_counter+1)
                    query_letter_clause = convert_tile_to_symbolic_clause(query_letter)
                    pos_observation_tile_clause = \
                        convert_tile_to_symbolic_clause(pos_observation[query_loc[0]][query_loc[1]])
                    query_answer_list.append(dpll_alg.dpll_satisfiable(query_letter_clause &
                                                                       pos_observation_tile_clause))

                if len(list(filter((lambda x: x), query_answer_list))) == len(possible_next_observation_list) \
                        and len(possible_next_observation_list) > 0:
                    queries_answer_dict[query] = 'T'
                    queries.remove(query)
                elif len(list(filter((lambda x: x), query_answer_list))) == 0 \
                        or len(possible_next_observation_list) == 0:
                    queries_answer_dict[query] = 'F'
                    queries.remove(query)
                else:
                    queries_answer_dict[query] = '?'

        if not queries:
            return queries_answer_dict

    return queries_answer_dict
