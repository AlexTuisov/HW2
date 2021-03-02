from pysat import solvers
# import sympy
from itertools import combinations


ids = ['312546609', '206851164']

"""
states:
'H' = 1
'S' = 2
'U' = 3
'I' = 4
'Q' = 5

actions:
'no action' = 0
'action applied' = 1

easy game clause = state turn row col
hard game clause = state turn row col action timeInState
"""


# region main func of solving problem

def solve_problem(input):
    medics = input['medics']
    police = input['police']
    observations_raw = input['observations']
    observations = []
    for mat in observations_raw:
        observations.append([list(row) for row in mat])
    queries = input['queries']

    easy_game = medics == 0 and police == 0
    knowledge_base = set()
    if easy_game:
        get_known_clauses(observations, knowledge_base)
        s = solvers.Glucose3(bootstrap_with=knowledge_base)
        results = answer_queries(queries, s)
        s.delete()
        return results

    else:
        # just_for_my_test_CNF()
        define_policy(observations, knowledge_base, medics, police)
        s = solvers.Glucose3(bootstrap_with=knowledge_base)
        results = answer_queries_hard_game(queries, s, medics, police)
        s.delete()
        return results

# endregion

# region easy game
def get_known_clauses(observations, knowledge_base):
    end_turn = len(observations) - 1
    push_red_button = True
    while push_red_button:
        push_red_button = False
        turn = 0
        for observation in observations:
            for row in range(len(observation)):
                for col in range(len(observation[0])):
                    state = ''
                    if observation[row][col] == 'H':
                        state = '1'
                        if turn != 0:
                            if check_h_prev_observation(observations[turn - 1], row, col, turn, knowledge_base):
                                push_red_button = True

                    elif observation[row][col] == 'S':
                        state = '2'
                        adjust_neighbors(row, col, observation, turn, knowledge_base, end_turn, observations)
                        if turn != 0:
                            if update_KB_if_one_question_mark_made_me_sick(turn - 1, observations[turn - 1], row, col, knowledge_base):
                                push_red_button = True

                            if need_x2_sick_and_recover(observations[turn - 1], row, col, turn - 1, knowledge_base):
                                sick_x2_and_recover(state, row, col, turn - 1, knowledge_base, end_turn, observations)
                                push_red_button = True
                        else:
                            sick_x2_and_recover(state, row, col, turn, knowledge_base, end_turn, observations)

                    elif observation[row][col] == 'U':
                        state = '3'

                    elif observation[row][col] == '?':
                        take_care_of_question_mark(turn, row, col, knowledge_base)
                        if turn != 0:
                            if fix_h_situation_in_prev_question_mark(turn, observations, row, col, knowledge_base):
                                push_red_button = True

                    # insert the current square to KB
                    if state != '':
                        clause_str = state + str(turn) + str(row) + str(col)
                        clause_num = int(clause_str)
                        knowledge_base.add((clause_num,))

                        fix_only_one_state_at_each_turn(state, knowledge_base, clause_num)

                        if state == '3':
                            if state_live_forever(knowledge_base, clause_num, end_turn, turn,observations, row, col):
                                push_red_button = True
            turn += 1


def adjust_neighbors(row, col, observation, turn, knowledge_base, end_turn, observations):
    # check & fix above
    if row != 0 and observation[row - 1][col] == 'H':
        sick_x3_and_recover(row - 1, col, turn, knowledge_base, end_turn, observations)

    # check & fix bellow
    if row != len(observation) - 1 and observation[row + 1][col] == 'H':
        sick_x3_and_recover(row + 1, col, turn, knowledge_base, end_turn, observations)

    # check & fix left
    if col != 0 and observation[row][col - 1] == 'H':
        sick_x3_and_recover(row, col - 1, turn, knowledge_base, end_turn, observations)

    # check & fix right
    if col != len(observation[0]) - 1 and observation[row][col + 1] == 'H':
        sick_x3_and_recover(row, col + 1, turn, knowledge_base, end_turn, observations)


def sick_x3_and_recover(row, col, turn, knowledge_base, end_turn, observations):
    if turn + 1 <= end_turn:
        clause_str1 = '2' + str(turn + 1) + str(row) + str(col)
        clause_num = int(clause_str1)
        knowledge_base.add((clause_num,))
        observations[turn + 1][row][col] = 'S'
    if turn + 2 <= end_turn:
        clause_str2 = '2' + str(turn + 2) + str(row) + str(col)
        clause_num = int(clause_str2)
        knowledge_base.add((clause_num,))
        observations[turn + 2][row][col] = 'S'
    if turn + 3 <= end_turn:
        clause_str3 = '2' + str(turn + 3) + str(row) + str(col)
        clause_num = int(clause_str3)
        knowledge_base.add((clause_num,))
        observations[turn + 3][row][col] = 'S'
    if turn + 4 <= end_turn:
        clause_str4 = '1' + str(turn + 4) + str(row) + str(col)
        clause_num = int(clause_str4)
        knowledge_base.add((clause_num,))
        observations[turn + 4][row][col] = 'H'


def sick_x2_and_recover(state, row, col, turn, knowledge_base, end_turn, observations):
    if turn + 1 <= end_turn:
        clause_str = state + str(turn + 1) + str(row) + str(col)
        clause_num = int(clause_str)
        knowledge_base.add((clause_num,))
        observations[turn + 1][row][col] = 'S'
    if turn + 2 <= end_turn:
        clause_str = state + str(turn + 2) + str(row) + str(col)
        clause_num = int(clause_str)
        knowledge_base.add((clause_num,))
        observations[turn + 2][row][col] = 'S'
    if turn + 3 <= end_turn:
        clause_str = '1' + str(turn + 3) + str(row) + str(col)
        clause_num = int(clause_str)
        knowledge_base.add((clause_num,))
        observations[turn + 3][row][col] = 'H'


def update_KB_if_one_question_mark_made_me_sick(turn, prev_observation, row, col, knowledge_base):
    question_mark_counter = 0
    potential_sick = ''
    if prev_observation[row][col] == 'H':
        # check & fix above
        if row != 0:
            if prev_observation[row - 1][col] == 'S':
                return False
            elif prev_observation[row - 1][col] == '?':
                question_mark_counter += 1
                potential_sick = '2' + str(turn) + str(row - 1) + str(col)

        # check & fix bellow
        if row != len(prev_observation) - 1:
            if prev_observation[row + 1][col] == 'S':
                return False
            elif prev_observation[row + 1][col] == '?':
                question_mark_counter += 1
                potential_sick = '2' + str(turn) + str(row + 1) + str(col)

        # check & fix left
        if col != 0:
            if prev_observation[row][col - 1] == 'S':
                return False
            elif prev_observation[row][col - 1] == '?':
                question_mark_counter += 1
                potential_sick = '2' + str(turn) + str(row) + str(col - 1)

        # check & fix right
        if col != len(prev_observation[0]) - 1:
            if prev_observation[row][col + 1] == 'S':
                return False
            elif prev_observation[row][col + 1] == '?':
                question_mark_counter += 1
                potential_sick = '2' + str(turn) + str(row) + str(col + 1)

        if question_mark_counter == 1:
            potential_sick_num = int(potential_sick)
            knowledge_base.add((potential_sick_num,))
            sick_row = int(potential_sick[2])
            sick_col = int(potential_sick[3])
            prev_observation[sick_row][sick_col] = 'S'
            return True
            # we dont need because we now using push red button system
            # adjust_neighbors(sick_row, sick_col, prev_observation, turn, knowledge_base)


def fix_only_one_state_at_each_turn(state, knowledge_base, clause_num):
    if state == '1':
        knowledge_base.add((-clause_num, -(clause_num + 1000)))
        knowledge_base.add((-clause_num, -(clause_num + 2000)))
    elif state == '2':
        knowledge_base.add((-clause_num, -(clause_num - 1000)))
        knowledge_base.add((-clause_num, -(clause_num + 1000)))
    elif state == '3':
        knowledge_base.add((-clause_num, -(clause_num - 2000)))
        knowledge_base.add((-clause_num, -(clause_num - 1000)))


def state_live_forever(knowledge_base, clause_num, turn, end_turn, observations, row, col):
    flag_u = False
    for i in range(turn + 1):
        knowledge_base.add((clause_num - 100*i,))
        if observations[i][row][col] == '?':
            flag_u = True
        observations[i][row][col] = 'U'

    for i in range(1, end_turn - turn + 1):
        knowledge_base.add((clause_num + 100*i,))
        observations[i + turn][row][col] = 'U'

    return flag_u

def take_care_of_question_mark(turn, row, col, knowledge_base):
    cluase_str_H = '1' + str(turn) + str(row) + str(col)
    cluase_str_S = '2' + str(turn) + str(row) + str(col)
    cluase_str_U = '3' + str(turn) + str(row) + str(col)

    cluase_num_H = int(cluase_str_H)
    cluase_num_S = int(cluase_str_S)
    cluase_num_U = int(cluase_str_U)

    knowledge_base.add((-cluase_num_H, -cluase_num_S))
    knowledge_base.add((-cluase_num_H, -cluase_num_U))
    knowledge_base.add((-cluase_num_S, -cluase_num_U))

# before 'H' and now '?'
# in this func we only need to check if in the previous turn the question mark was 'H' (other states we already checked)
def fix_h_situation_in_prev_question_mark(turn, observations, row, col, knowledge_base):
    if observations[turn - 1][row][col] == 'H':
        # check & fix above
        if row != 0 and (observations[turn - 1][row - 1][col] == 'S' or observations[turn - 1][row - 1][col] == '?'):
            return False

        # check & fix bellow
        if row != len(observations[0]) - 1 and (observations[turn - 1][row + 1][col] == 'S' or observations[turn - 1][row + 1][col] == '?'):
            return False

        # check & fix left
        if col != 0 and (observations[turn - 1][row][col - 1] == 'S' or observations[turn - 1][row][col - 1] == '?'):
            return False

        # check & fix right
        if col != len(observations[0][0]) - 1 and (observations[turn - 1][row][col + 1] == 'S' or observations[turn - 1][row][col + 1] == '?'):
            return False

        cluase_str = '1' + str(turn) + str(row) + str(col)
        cluase_num = int(cluase_str)
        knowledge_base.add((cluase_num,))
        observations[turn][row][col] = 'H'
        return True



def need_x2_sick_and_recover(previous_observation, row, col, prev_turn, knowledge_base):
    # already took cared
    if previous_observation[row][col] == 'S' or previous_observation[row][col] == 'H':
        return False
    elif previous_observation[row][col] == '?':
        # check above
        if row != 0 and previous_observation[row - 1][col] != 'H' and previous_observation[row - 1][col] != 'U':
            return False

        # check & fix bellow
        if row != len(previous_observation) - 1 and previous_observation[row + 1][col] != 'H' and previous_observation[row + 1][col] != 'U':
            return False

        # check & fix left
        if col != 0 and previous_observation[row][col - 1] != 'H' and previous_observation[row][col - 1] != 'U':
            return False

        # check & fix right
        if col != len(previous_observation[0]) - 1 and previous_observation[row][col + 1] != 'H' and previous_observation[row][col + 1] != 'U':
            return False

        previous_observation[row][col] = 'S'
        clause_str = '2' + str(prev_turn) + str(row) + str(col)
        clause_num = int(clause_str)
        knowledge_base.add((clause_num,))

    return True

# before '?' and now 'H'
def check_h_prev_observation(previous_observation, row, col, turn, knowledge_base):
    if previous_observation[row][col] == '?' and turn < 3:
        previous_observation[row][col] = 'H'
        clause_str = '1' + str(turn - 1) + str(row) + str(col)
        clause_num = int(clause_str)
        knowledge_base.add((clause_num,))
        return True

    return False


# region queries handling

def answer_queries(queries, s):
    results = dict()
    for query in queries:
        row = query[0][0]
        col = query[0][1]
        turn = query[1]
        state_str = query[2]
        if state_str == 'H':
            state = 1
        elif state_str == 'S':
            state = 2
        elif state_str == 'U':
            state = 3
        else:
            results[query] = 'F'
            continue

        assumption_str_me = str(state) + str(turn) + str(row) + str(col)
        other_assumptions = get_all_other_states_assumptions(turn, row, col, assumption_str_me)
        assumption_num_me = int(assumption_str_me)
        result = infer_result(other_assumptions, assumption_num_me, s)
        results[query] = result
    return results


def get_all_other_states_assumptions(turn, row, col, assumption_str_me):
    assumption_str_h = '1' + str(turn) + str(row) + str(col)
    assumption_str_s = '2' + str(turn) + str(row) + str(col)
    assumption_str_u = '3' + str(turn) + str(row) + str(col)
    if assumption_str_me == assumption_str_h:
        return [int(assumption_str_s), int(assumption_str_u)]
    elif assumption_str_me == assumption_str_s:
        return [int(assumption_str_h), int(assumption_str_u)]
    else:
        return [int(assumption_str_h), int(assumption_str_s)]


def infer_result(other_assumptions, assumption_num_me, s):
    result = s.solve(assumptions=(assumption_num_me,))
    if not result:
        result = s.solve()
        return 'F'
    else:
        for assumption in other_assumptions:
            result = s.solve(assumptions=(assumption,))
            if result:
                return '?'

        return 'T'

# endregion


# endregion

# region hard game


def define_policy(observations, knowledge_base, medics, police):
    end_turn = len(observations) - 1
    push_red_button = True
    while push_red_button:
        push_red_button = False
        turn = 0
        for observation in observations:
            possibale_vac = []
            possibale_quar = []
            for row in range(len(observation)):
                for col in range(len(observation[0])):
                    if observation[row][col] == 'H':
                        possibale_vac.append(translate_to_clause(1, turn, row, col, 1, 0))
                        handle_h(turn, row, col, knowledge_base, end_turn, medics, police)
                        if turn > 0:
                             if check_h_prev_observation_hard_game(observations[turn - 1], row, col, turn, knowledge_base):
                                 push_red_button = True
                    elif observation[row][col] == 'S':
                        possibale_quar.append(translate_to_clause(2, turn, row, col, 1, 1))
                        possibale_quar.append(translate_to_clause(2, turn, row, col, 1, 2))
                        possibale_quar.append(translate_to_clause(2, turn, row, col, 1, 3))
                        if turn > 0:
                            if update_KB_if_one_question_mark_made_me_sick_hard_game(turn - 1, observations[turn - 1], row, col, knowledge_base):
                                push_red_button = True

                            if need_x2_sick_and_recover_hard_game(observations[turn - 1], row, col, turn - 1, knowledge_base):
                                push_red_button = True
                        handle_s(turn, row, col, knowledge_base, end_turn, medics, police)
                        if turn < end_turn:
                            adjust_neighbors_hard_game(row, col, observation, turn, knowledge_base, police)
                    elif observation[row][col] == 'U':
                        if handle_u(turn, row, col, knowledge_base, end_turn, observations):
                            push_red_button = True
                    elif observation[row][col] == 'I':
                        handle_i(turn, row, col, knowledge_base, end_turn, observations)
                    elif observation[row][col] == 'Q':
                        handle_q(turn, row, col, knowledge_base, end_turn, medics)
                    else:
                        if fix_h_situation_in_prev_question_mark_hard_game(turn, observations, row, col, knowledge_base, medics):
                            push_red_button = True

                    handle_no_duplicates(turn, row, col, knowledge_base, medics, police)

            if medics != 0:
                if len(possibale_vac) <= medics:
                    for action in possibale_vac:
                        knowledge_base.add((action,))
                else:
                    combi_vac = set(combinations(possibale_vac, medics))
                    for single_combi in combi_vac:
                        final_list = []
                        for item in single_combi:
                            final_list.append(-item)
                        for other_act in possibale_vac:
                            if other_act not in single_combi:
                                final_list.append(-other_act)
                                tuple_test = tuple(final_list)
                                knowledge_base.add(tuple_test)
                                final_list.remove(-other_act)

            if police != 0:
                if len(possibale_quar) <= police:
                    for action in possibale_quar:
                        knowledge_base.add((action,))
                else:
                    combi_quar = set(combinations(possibale_quar, police))
                    for single_combi in combi_quar:
                        final_list = []
                        for item in single_combi:
                            final_list.append(-item)
                        for other_act in possibale_quar:
                            if other_act not in single_combi:
                                final_list.append(-other_act)
                                tuple_test = tuple(final_list)
                                knowledge_base.add(tuple_test)
                                final_list.remove(-other_act)

            turn += 1


def adjust_neighbors_hard_game(row, col, observation, turn, knowledge_base, police):

    clause_s1 = translate_to_clause(2, turn, row, col, 0, 1)
    clause_s2 = translate_to_clause(2, turn, row, col, 0, 2)
    clause_s3 = translate_to_clause(2, turn, row, col, 0, 3)

    # check & fix above
    if row != 0 and (observation[row - 1][col] == 'H' or observation[row - 1][col] == '?'):
        # ( h_n & (s1 | s2 | s3) ) => (next_s1_n | next_s1_act_n) =  (4 | 5 | ~1 | ~10) & (4 | 5 | ~10 | ~2) & (4 | 5 | ~10 | ~3)
        neighbor_h = translate_to_clause(1, turn, row - 1, col, 0, 0)
        next_turn_become_s1 = translate_to_clause(2, turn + 1, row - 1, col, 0, 1)
        if police != 0:
            next_turn_become_s1_act = translate_to_clause(2, turn + 1, row - 1, col, 1, 1)
            knowledge_base.add((-neighbor_h, -clause_s1, next_turn_become_s1, next_turn_become_s1_act))
            knowledge_base.add((-neighbor_h, -clause_s2, next_turn_become_s1, next_turn_become_s1_act))
            knowledge_base.add((-neighbor_h, -clause_s3, next_turn_become_s1, next_turn_become_s1_act))
        else:
            knowledge_base.add((-neighbor_h, -clause_s1, next_turn_become_s1))
            knowledge_base.add((-neighbor_h, -clause_s2, next_turn_become_s1))
            knowledge_base.add((-neighbor_h, -clause_s3, next_turn_become_s1))

    # check & fix bellow
    if row != len(observation) - 1 and (observation[row + 1][col] == 'H' or observation[row + 1][col] == '?'):
        neighbor_h = translate_to_clause(1, turn, row + 1, col, 0, 0)
        next_turn_become_s1 = translate_to_clause(2, turn + 1, row + 1, col, 0, 1)
        if police != 0:
            next_turn_become_s1_act = translate_to_clause(2, turn + 1, row + 1, col, 1, 1)
            knowledge_base.add((-neighbor_h, -clause_s1, next_turn_become_s1, next_turn_become_s1_act))
            knowledge_base.add((-neighbor_h, -clause_s2, next_turn_become_s1, next_turn_become_s1_act))
            knowledge_base.add((-neighbor_h, -clause_s3, next_turn_become_s1, next_turn_become_s1_act))
        else:
            knowledge_base.add((-neighbor_h, -clause_s1, next_turn_become_s1))
            knowledge_base.add((-neighbor_h, -clause_s2, next_turn_become_s1))
            knowledge_base.add((-neighbor_h, -clause_s3, next_turn_become_s1))

    # check & fix left
    if col != 0 and (observation[row][col - 1] == 'H' or observation[row][col - 1] == '?'):
        neighbor_h = translate_to_clause(1, turn, row, col - 1, 0, 0)
        next_turn_become_s1 = translate_to_clause(2, turn + 1, row, col - 1, 0, 1)
        if police != 0:
            next_turn_become_s1_act = translate_to_clause(2, turn + 1, row, col - 1, 1, 1)
            knowledge_base.add((-neighbor_h, -clause_s1, next_turn_become_s1, next_turn_become_s1_act))
            knowledge_base.add((-neighbor_h, -clause_s2, next_turn_become_s1, next_turn_become_s1_act))
            knowledge_base.add((-neighbor_h, -clause_s3, next_turn_become_s1, next_turn_become_s1_act))
        else:
            knowledge_base.add((-neighbor_h, -clause_s1, next_turn_become_s1))
            knowledge_base.add((-neighbor_h, -clause_s2, next_turn_become_s1))
            knowledge_base.add((-neighbor_h, -clause_s3, next_turn_become_s1))

    # check & fix right
    if col != len(observation[0]) - 1 and (observation[row][col + 1] == 'H' or observation[row][col + 1] == '?'):
        neighbor_h = translate_to_clause(1, turn, row, col + 1, 0, 0)
        next_turn_become_s1 = translate_to_clause(2, turn + 1, row, col + 1, 0, 1)
        if police != 0:
            next_turn_become_s1_act = translate_to_clause(2, turn + 1, row, col + 1, 1, 1)
            knowledge_base.add((-neighbor_h, -clause_s1, next_turn_become_s1, next_turn_become_s1_act))
            knowledge_base.add((-neighbor_h, -clause_s2, next_turn_become_s1, next_turn_become_s1_act))
            knowledge_base.add((-neighbor_h, -clause_s3, next_turn_become_s1, next_turn_become_s1_act))
        else:
            knowledge_base.add((-neighbor_h, -clause_s1, next_turn_become_s1))
            knowledge_base.add((-neighbor_h, -clause_s2, next_turn_become_s1))
            knowledge_base.add((-neighbor_h, -clause_s3, next_turn_become_s1))


# before '?' and now 'H'
def check_h_prev_observation_hard_game(previous_observation, row, col, turn, knowledge_base):
    if previous_observation[row][col] == '?' and turn < 3:
        previous_observation[row][col] = 'H'
        clause_h = translate_to_clause(1, turn - 1, row, col, 0, 0)
        knowledge_base.add((clause_h,))
        return True

    return False


def handle_h(turn, row, col, knowledge_base, end_turn, medics, police):
    # handle_h_present
    clause_h = translate_to_clause(1, turn, row, col, 0, 0)
    if medics > 0:
        clause_h_act = translate_to_clause(1, turn, row, col, 1, 0)
        knowledge_base.add((clause_h, clause_h_act))
    else:
        knowledge_base.add((clause_h,))
    # fix_only_one_state_at_each_turn_hard_game('1', knowledge_base, clause_h)

    # handle_h_future
    if turn < end_turn:
        # H -> H or H_act or S
        # H
        next_turn_h = translate_to_clause(1, turn + 1, row, col, 0, 0)
        # S
        next_turn_s_after_infected = translate_to_clause(2, turn + 1, row, col, 0, 1)
        if police != 0:
            # S_act
            next_turn_s_act_after_infected = translate_to_clause(2, turn + 1, row, col, 1, 1)

        # H_act -> I
        if medics != 0:
            next_turn_h_act = translate_to_clause(1, turn + 1, row, col, 1, 0)
            next_turn_i_after_act = translate_to_clause(4, turn + 1, row, col, 0, 0)
            knowledge_base.add((-clause_h_act, next_turn_i_after_act))
            if police != 0:
                knowledge_base.add((-clause_h, next_turn_h, next_turn_h_act, next_turn_s_after_infected, next_turn_s_act_after_infected))
            else:
                knowledge_base.add((-clause_h, next_turn_h, next_turn_h_act, next_turn_s_after_infected))
        else:
            # TODO : add adjust neigbhors in new func because we solve the next_turn_s_after_infected problem
            if police != 0:
                knowledge_base.add((-clause_h, next_turn_h, next_turn_s_after_infected, next_turn_s_act_after_infected))
            else:
                knowledge_base.add((-clause_h, next_turn_h, next_turn_s_after_infected))


def update_KB_if_one_question_mark_made_me_sick_hard_game(prev_turn, prev_observation, row, col, knowledge_base):
    question_mark_counter = 0
    if prev_observation[row][col] == 'H':
        # check & fix above
        if row != 0:
            if prev_observation[row - 1][col] == 'S':
                return False
            elif prev_observation[row - 1][col] == '?':
                question_mark_counter += 1
                potential_sick1 = translate_to_clause(2, prev_turn, row - 1, col, 0, 1)
                potential_sick2 = translate_to_clause(2, prev_turn, row - 1, col, 0, 2)
                potential_sick3 = translate_to_clause(2, prev_turn, row - 1, col, 0, 3)

        # check & fix bellow
        if row != len(prev_observation) - 1:
            if prev_observation[row + 1][col] == 'S':
                return False
            elif prev_observation[row + 1][col] == '?':
                question_mark_counter += 1
                potential_sick1 = translate_to_clause(2, prev_turn, row + 1, col, 0, 1)
                potential_sick2 = translate_to_clause(2, prev_turn, row + 1, col, 0, 2)
                potential_sick3 = translate_to_clause(2, prev_turn, row + 1, col, 0, 3)

        # check & fix left
        if col != 0:
            if prev_observation[row][col - 1] == 'S':
                return False
            elif prev_observation[row][col - 1] == '?':
                question_mark_counter += 1
                potential_sick1 = translate_to_clause(2, prev_turn, row, col - 1, 0, 1)
                potential_sick2 = translate_to_clause(2, prev_turn, row, col - 1, 0, 2)
                potential_sick3 = translate_to_clause(2, prev_turn, row, col - 1, 0, 3)

        # check & fix right
        if col != len(prev_observation[0]) - 1:
            if prev_observation[row][col + 1] == 'S':
                return False
            elif prev_observation[row][col + 1] == '?':
                question_mark_counter += 1
                potential_sick1 = translate_to_clause(2, prev_turn, row, col + 1, 0, 1)
                potential_sick2 = translate_to_clause(2, prev_turn, row, col + 1, 0, 2)
                potential_sick3 = translate_to_clause(2, prev_turn, row, col + 1, 0, 3)

        if question_mark_counter == 1:
            knowledge_base.add((potential_sick1, potential_sick2, potential_sick3))
            sick_row = int(str(potential_sick1)[2])
            sick_col = int(str(potential_sick1)[3])
            prev_observation[sick_row][sick_col] = 'S'
            return True
            # we dont need because we now using push red button system
            # adjust_neighbors(sick_row, sick_col, prev_observation, turn, knowledge_base)


def need_x2_sick_and_recover_hard_game(previous_observation, row, col, prev_turn, knowledge_base):
    # already took cared
    if previous_observation[row][col] == 'S' or previous_observation[row][col] == 'H':
        return False
    elif previous_observation[row][col] == '?':
        # check above
        if row != 0 and previous_observation[row - 1][col] != 'H' and previous_observation[row - 1][col] != 'U':
            return False

        # check & fix bellow
        if row != len(previous_observation) - 1 and previous_observation[row + 1][col] != 'H' and previous_observation[row + 1][col] != 'U':
            return False

        # check & fix left
        if col != 0 and previous_observation[row][col - 1] != 'H' and previous_observation[row][col - 1] != 'U':
            return False

        # check & fix right
        if col != len(previous_observation[0]) - 1 and previous_observation[row][col + 1] != 'H' and previous_observation[row][col + 1] != 'U':
            return False

        previous_observation[row][col] = 'S'
        clause_s1 = translate_to_clause(2, prev_turn, row, col, 0, 1)
        clause_s2 = translate_to_clause(2, prev_turn, row, col, 0, 2)
        knowledge_base.add((clause_s1, clause_s2))

    return True


def handle_s(turn, row, col, knowledge_base, end_turn, medics, police):
    # handle_s_present
    clause_s1 = translate_to_clause(2, turn, row, col, 0, 1)
    clause_s2 = translate_to_clause(2, turn, row, col, 0, 2)
    clause_s3 = translate_to_clause(2, turn, row, col, 0, 3)
    if police != 0:
        clause_s1_act = translate_to_clause(2, turn, row, col, 1, 1)
        clause_s2_act = translate_to_clause(2, turn, row, col, 1, 2)
        clause_s3_act = translate_to_clause(2, turn, row, col, 1, 3)
        if turn == 0:
            knowledge_base.add((clause_s1, clause_s1_act))
        elif turn == 1:
            knowledge_base.add((clause_s1, clause_s2, clause_s1_act, clause_s2_act))
        else:
            knowledge_base.add((clause_s1, clause_s2, clause_s3, clause_s1_act, clause_s2_act, clause_s3_act))
    else:
        if turn == 0:
            knowledge_base.add((clause_s1,))
        elif turn == 1:
            knowledge_base.add((clause_s1, clause_s2))
        else:
            knowledge_base.add((clause_s1, clause_s2, clause_s3))


    # handle_s_future
    if turn < end_turn:
        next_turn_clause_s2 = translate_to_clause(2, turn + 1, row, col, 0, 2)
        next_turn_clause_s3 = translate_to_clause(2, turn + 1, row, col, 0, 3)
        if police != 0:
            # act quarantine
            next_turn_q_after_act = translate_to_clause(5, turn + 1, row, col, 0, 1)
            knowledge_base.add((-clause_s1_act, next_turn_q_after_act))
            knowledge_base.add((-clause_s2_act, next_turn_q_after_act))
            knowledge_base.add((-clause_s3_act, next_turn_q_after_act))
            # s1 -> s2 | s2_act (next turn)
            next_turn_clause_s2_act = translate_to_clause(2, turn + 1, row, col, 1, 2)
            knowledge_base.add((-clause_s1, next_turn_clause_s2, next_turn_clause_s2_act))
            # s2 -> s3 | s3_act (next turn)
            next_turn_clause_s3_act = translate_to_clause(2, turn + 1, row, col, 1, 3)
            knowledge_base.add((-clause_s2, next_turn_clause_s3, next_turn_clause_s3_act))
        else:
            # s1 -> s2 (next turn)
            knowledge_base.add((-clause_s1, next_turn_clause_s2))
            # s2 -> s3 (next turn)
            knowledge_base.add((-clause_s2, next_turn_clause_s3))

        next_turn_h_after_3_sick = translate_to_clause(1, turn + 1, row, col, 0, 0)
        if medics != 0:
            # s3 -> H | H_act (next turn)
            next_turn_h_act_after_3_sick = translate_to_clause(1, turn + 1, row, col, 1, 0)
            knowledge_base.add((-clause_s3, next_turn_h_after_3_sick, next_turn_h_act_after_3_sick))
        else:
            knowledge_base.add((-clause_s3, next_turn_h_after_3_sick))


def handle_u(turn, row, col, knowledge_base, end_turn, observations):
    flag_u = False
    current_clause = translate_to_clause(3, turn, row, col, 0, 0)
    # taking care of the past
    for i in range(turn):
        knowledge_base.add((current_clause - 10000 * i,))
        if observations[i][row][col] == '?':
            observations[i][row][col] = 'U'
            flag_u = True

    # taking care of the future
    for i in range(end_turn - turn + 1):
        knowledge_base.add((current_clause + 10000 * i,))
        observations[i + turn][row][col] = 'U'

    return flag_u


def handle_i(turn, row, col, knowledge_base, end_turn, observations):
    # handle history
    prev_turn_h_act = translate_to_clause(1, turn - 1, row, col, 1, 0)
    prev_turn_i = translate_to_clause(4, turn - 1, row, col, 0, 0)
    knowledge_base.add((prev_turn_h_act, prev_turn_i))

    # handle future
    current_clause = translate_to_clause(4, turn, row, col, 0, 0)
    for i in range(end_turn - turn + 1):
        knowledge_base.add((current_clause + 10000 * i,))
        observations[i + turn][row][col] = 'I'


def handle_q(turn, row, col, knowledge_base, end_turn, medics):
    # handle_q_present
    # there is no Q in turn 0
    clause_q1 = translate_to_clause(5, turn, row, col, 0, 1)
    clause_q2 = translate_to_clause(5, turn, row, col, 0, 2)
    if turn == 1:
        knowledge_base.add((clause_q1,))
    else:
        knowledge_base.add((clause_q1, clause_q2))

    # handle history
    prev_turn_q1 = translate_to_clause(5, turn - 1, row, col, 0, 1)
    knowledge_base.add((-clause_q2, prev_turn_q1))

    prev_turn_s1_act = translate_to_clause(2, turn - 1, row, col, 1, 1)
    prev_turn_s2_act = translate_to_clause(2, turn - 1, row, col, 1, 2)
    prev_turn_s3_act = translate_to_clause(2, turn - 1, row, col, 1, 3)
    knowledge_base.add((-clause_q1, prev_turn_s1_act, prev_turn_s2_act, prev_turn_s3_act))

    # handle_q_future
    if turn < end_turn:
        # q1 -> q2
        next_turn_q2 = translate_to_clause(5, turn + 1, row, col, 0, 2)
        knowledge_base.add((-clause_q1, next_turn_q2))
        # q2 -> H
        next_turn_h_after_2_quarantine = translate_to_clause(1, turn + 1, row, col, 0, 0)
        if medics != 0:
            next_turn_h_act_after_2_quarantine = translate_to_clause(1, turn + 1, row, col, 1, 0)
            knowledge_base.add((-clause_q2, next_turn_h_after_2_quarantine, next_turn_h_act_after_2_quarantine))
        else:
            knowledge_base.add((-clause_q2, next_turn_h_after_2_quarantine))
        if turn < end_turn - 1:
            next_two_turn_h_after_2_quarantine = translate_to_clause(1, turn + 2, row, col, 0, 0)
            if medics != 0:
                next_two_turn_h_act_after_2_quarantine = translate_to_clause(1, turn + 2, row, col, 1, 0)
                knowledge_base.add((-clause_q1, next_two_turn_h_after_2_quarantine, next_two_turn_h_act_after_2_quarantine))
            else:
                knowledge_base.add((-clause_q1, next_two_turn_h_after_2_quarantine))


# before 'H' and now '?'
# in this func we only need to check if in the previous turn the question mark was 'H' (other states we already checked)
def fix_h_situation_in_prev_question_mark_hard_game(turn, observations, row, col, knowledge_base, medics):
    if observations[turn - 1][row][col] == 'H':
        # check & fix above
        if row != 0 and (observations[turn - 1][row - 1][col] == 'S' or observations[turn - 1][row - 1][col] == '?'):
            if observations[turn][row - 1][col] != 'Q':
                return False

        # check & fix bellow
        if row != len(observations[0]) - 1 and (observations[turn - 1][row + 1][col] == 'S' or observations[turn - 1][row + 1][col] == '?'):
            if observations[turn][row + 1][col] != 'Q':
                return False

        # check & fix left
        if col != 0 and (observations[turn - 1][row][col - 1] == 'S' or observations[turn - 1][row][col - 1] == '?'):
            if observations[turn][row][col - 1] != 'Q':
                return False

        # check & fix right
        if col != len(observations[0][0]) - 1 and (observations[turn - 1][row][col + 1] == 'S' or observations[turn - 1][row][col + 1] == '?'):
            if observations[turn][row][col + 1] != 'Q':
                return False

        cluase_h = translate_to_clause(1, turn, row, col, 0, 0)
        if medics > 0:
            clause_i = translate_to_clause(4, turn, row, col, 0, 0)
            cluase_h_act = translate_to_clause(1, turn, row, col, 1, 0)
            knowledge_base.add((cluase_h, cluase_h_act, clause_i))
            return False
        else:
            knowledge_base.add((cluase_h,))
            observations[turn][row][col] = 'H'
        return True


def handle_no_duplicates(turn, row, col, knowledge_base, medics, police):
    temp_list = []
    cluase_H = translate_to_clause(1, turn, row, col, 0, 0)
    temp_list.append(cluase_H)
    if medics != 0:
        cluase_H_with_act = translate_to_clause(1, turn, row, col, 1, 0)
        temp_list.append(cluase_H_with_act)
        cluase_I = translate_to_clause(4, turn, row, col, 0, 0)
        temp_list.append(cluase_I)
    cluase_S1 = translate_to_clause(2, turn, row, col, 0, 1)
    temp_list.append(cluase_S1)
    cluase_S2 = translate_to_clause(2, turn, row, col, 0, 2)
    temp_list.append(cluase_S2)
    cluase_S3 = translate_to_clause(2, turn, row, col, 0, 3)
    temp_list.append(cluase_S3)
    if police != 0:
        cluase_S1_with_act = translate_to_clause(2, turn, row, col, 1, 1)
        temp_list.append(cluase_S1_with_act)
        cluase_S2_with_act = translate_to_clause(2, turn, row, col, 1, 2)
        temp_list.append(cluase_S2_with_act)
        cluase_S3_with_act = translate_to_clause(2, turn, row, col, 1, 3)
        temp_list.append(cluase_S3_with_act)
        cluase_Q1 = translate_to_clause(5, turn, row, col, 0, 1)
        temp_list.append(cluase_Q1)
        cluase_Q2 = translate_to_clause(5, turn, row, col, 0, 2)
        temp_list.append(cluase_Q2)
    cluase_U = translate_to_clause(3, turn, row, col, 0, 0)
    temp_list.append(cluase_U)

    all_2_combi = set(combinations(temp_list, 2))

    for item in all_2_combi:
        knowledge_base.add((-item[0], -item[1]))


def translate_to_clause(state, turn, row, col, action=0, time_in_state=0):
    clause_str = str(state) + str(turn) + str(row) + str(col) + str(action) + str(time_in_state)
    return int(clause_str)


# region answer queris hard game
def answer_queries_hard_game(queries, s, medics, police):
    results = dict()
    for query in queries:
        row = query[0][0]
        col = query[0][1]
        turn = query[1]
        state_str = query[2]
        is_legal = True

        assumption_h = int('1' + str(turn) + str(row) + str(col) + '0' + '0')
        assumption_h_act = int('1' + str(turn) + str(row) + str(col) + '1' + '0')
        assumption_s1 = int('2' + str(turn) + str(row) + str(col) + '0' + '1')
        assumption_s2 = int('2' + str(turn) + str(row) + str(col) + '0' + '2')
        assumption_s3 = int('2' + str(turn) + str(row) + str(col) + '0' + '3')
        assumption_s1_act = int('2' + str(turn) + str(row) + str(col) + '1' + '1')
        assumption_s2_act = int('2' + str(turn) + str(row) + str(col) + '1' + '2')
        assumption_s3_act = int('2' + str(turn) + str(row) + str(col) + '1' + '3')
        assumption_u = int('3' + str(turn) + str(row) + str(col) + '0' + '0')
        assumption_i = int('4' + str(turn) + str(row) + str(col) + '0' + '0')
        assumption_q1 = int('5' + str(turn) + str(row) + str(col) + '0' + '1')
        assumption_q2 = int('5' + str(turn) + str(row) + str(col) + '0' + '2')

        my_assumptions = []
        other_assumptions = []

        if state_str == 'H':
            my_assumptions.append(assumption_h)
            other_assumptions.append(assumption_s1)
            other_assumptions.append(assumption_s2)
            other_assumptions.append(assumption_s3)
            other_assumptions.append(assumption_u)
            if medics != 0:
                my_assumptions.append(assumption_h_act)
                other_assumptions.append(assumption_i)

            if police != 0:
                other_assumptions.append(assumption_s1_act)
                other_assumptions.append(assumption_s2_act)
                other_assumptions.append(assumption_s3_act)
                other_assumptions.append(assumption_q1)
                other_assumptions.append(assumption_q2)

        elif state_str == 'S':
            other_assumptions.append(assumption_h)
            my_assumptions.append(assumption_s1)
            my_assumptions.append(assumption_s2)
            my_assumptions.append(assumption_s3)
            other_assumptions.append(assumption_u)

            if police != 0:
                my_assumptions.append(assumption_s1_act)
                my_assumptions.append(assumption_s2_act)
                my_assumptions.append(assumption_s3_act)
                other_assumptions.append(assumption_q1)
                other_assumptions.append(assumption_q2)

            if medics != 0:
                other_assumptions.append(assumption_h_act)
                other_assumptions.append(assumption_i)

        elif state_str == 'U':
            other_assumptions.append(assumption_h)
            other_assumptions.append(assumption_s1)
            other_assumptions.append(assumption_s2)
            other_assumptions.append(assumption_s3)
            my_assumptions.append(assumption_u)

            if medics != 0:
                other_assumptions.append(assumption_h_act)
                other_assumptions.append(assumption_i)

            if police != 0:
                other_assumptions.append(assumption_s1_act)
                other_assumptions.append(assumption_s2_act)
                other_assumptions.append(assumption_s3_act)
                other_assumptions.append(assumption_q1)
                other_assumptions.append(assumption_q2)

        elif state_str == 'I':
            other_assumptions.append(assumption_h)
            other_assumptions.append(assumption_s1)
            other_assumptions.append(assumption_s2)
            other_assumptions.append(assumption_s3)
            other_assumptions.append(assumption_u)
            my_assumptions.append(assumption_i)

            if medics != 0:
                other_assumptions.append(assumption_h_act)
            else:
                is_legal = False

            if police != 0:
                other_assumptions.append(assumption_s1_act)
                other_assumptions.append(assumption_s2_act)
                other_assumptions.append(assumption_s3_act)
                other_assumptions.append(assumption_q1)
                other_assumptions.append(assumption_q2)

        elif state_str == 'Q':
            other_assumptions.append(assumption_h)
            other_assumptions.append(assumption_s1)
            other_assumptions.append(assumption_s2)
            other_assumptions.append(assumption_s3)
            other_assumptions.append(assumption_u)
            my_assumptions.append(assumption_q1)
            my_assumptions.append(assumption_q2)

            if medics != 0:
                other_assumptions.append(assumption_h_act)
                other_assumptions.append(assumption_i)

            if police != 0:
                other_assumptions.append(assumption_s1_act)
                other_assumptions.append(assumption_s2_act)
                other_assumptions.append(assumption_s3_act)
            else:
                is_legal = False

        if turn == 0 and state_str == 'Q':
            is_legal = False

        if turn == 0 and state_str == 'I':
            is_legal = False

        if is_legal:
            result = infer_result_hard_game(other_assumptions, my_assumptions, s)
        else:
            result = 'F'
        results[query] = result
    return results


def infer_result_hard_game(other_assumptions, my_assumptions, s):
    my_flag = False
    results = []
    for assumption in my_assumptions:
        game_result = s.solve(assumptions=(assumption,))
        # game_result = s.solve()
        # test = s.get_core()
        # print(game_result)

        results.append(game_result)
    for result in results:
        if result:
            my_flag = True

    if not my_flag:
        return 'F'
    else:
        for assumption in other_assumptions:
            result = s.solve(assumptions=(assumption,))
            if result:
                return '?'

        return 'T'


# endregion

# endregion


# def just_for_my_test_CNF():
    # ( h_n & (s1 | s2 | s3) ) => (next_s1_n | next_s1_act_n)
    # x1, x2, x3, x4, x5, x6, x7, x8, x9, x10 = sympy.symbols('1,2,3,4,5,6,7,8,9,10')
    # print(sympy.to_cnf((x10 & (x1 | x2 | x3)) >> (x4 | x5))) # = (4 | 5 | ~1 | ~10) & (4 | 5 | ~10 | ~2) & (4 | 5 | ~10 | ~3)
