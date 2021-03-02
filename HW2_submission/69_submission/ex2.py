from sympy import *
from sympy.logic.inference import satisfiable
import pysat
import itertools as it

ids = ['211821111', '312441157']


def solve_problem(input):
    med_num = input["medics"]
    police_num = input["police"]
    answer_dict = {}
    observations = input['observations']
    num_turns = len(observations)
    col_len = len(observations[0])
    row_len = len(observations[0][0])
    states = ['U', 'H', 'S']
    action_types = ['noopH', 'noopS', 'noopU', 'heal', 'free', 'infect', 'infected']
    if med_num:
        action_types.append('noopI')
        action_types.append('Vac')
        states.append('I')
    if police_num:
        action_types.append('noopQ')
        action_types.append('Qua')
        states.append('Q')

    pred, action_pred = create_predictors(num_turns, col_len, row_len, states, action_types)
    initial = get_initial(pred, observations, col_len, row_len)
    actions = get_action_verses(med_num, police_num, col_len, row_len, num_turns,
                                pred, action_pred, observations, states)
    terms = initial & actions
    for query in input["queries"]:
        # check of easily determined statements
        if (police_num == 0 and query[2] == 'Q') or (med_num == 0 and query[2] == 'I'):
            answer_dict[query] = 'F'
        for state_map in observations:
            curr_val = state_map[query[0][0]][query[0][1]]
            if query[2] == 'U':
                if curr_val == 'U':
                    answer_dict[query] = 'T'
                if curr_val != 'U' and curr_val != '?':
                    answer_dict[query] = 'F'
            else:
                if curr_val == 'U':
                    answer_dict[query] = 'F'
        answer_dict[query] = answer_to_query(query, terms, pred, states)
    return answer_dict


#  creates action and state predictors using sympy
def create_predictors(num_turns, col_len, row_len, states, action_types):
    action_pred = {}
    pred = {}
    for turn in range(num_turns):
        for i in range(row_len):
            for j in range(col_len):
                loc = str(turn) + '(' + str(i) + str(j) + ')'
                # state predictors
                for state in states:
                    pre = state + loc
                    pred[pre] = symbols(pre)
                    for val in states:
                        if val != state:
                            false_val = val + loc
                            false_val = symbols(false_val)
                            pred[pre] = pred[pre] & ~false_val
                # action predictors
                for action in action_types:
                    if turn < 2 and action in ['heal', 'free']:
                        continue
                    curr_action = action + loc
                    action_pred[action + loc] = symbols(curr_action)
                    for act in action_types:
                        if act != action:
                            conflicted_action = act + loc
                            action_pred[action + loc] = action_pred[action + loc] & ~symbols(conflicted_action)
    return pred, action_pred


# gets the verse for the initial true predictors
def get_initial(pred, observations, col_len, row_len):
    initial_state = True
    num_turns = len(observations)
    for turn in range(num_turns):
        for i in range(col_len):
            for j in range(row_len):
                val = observations[turn][i][j]
                loc = str(turn) + '(' + str(i) + str(j) + ')'
                if val != '?':
                    initial_state = initial_state & pred[val + loc]
    return initial_state


# calls all the action verses and combines them with & clauses
def get_action_verses(med_num, police_num, col_len, row_len, num_turns, pred, action_pred, observations, states):
    verse1 = get_infect_infected_and_noop_verses(col_len, row_len, num_turns, pred,
                                                 action_pred, states, med_num, police_num)
    verse2 = get_team_verses("medic", med_num, col_len, row_len, num_turns, pred, action_pred, observations)
    verse3 = get_team_verses("police", police_num, col_len, row_len, num_turns, pred, action_pred, observations)
    verse4 = get_achievement_clauses(pred, action_pred, num_turns, col_len, row_len, states)
    return verse1 & verse2 & verse3 & verse4


# returns the verses for infection and noop actions
def get_infect_infected_and_noop_verses(col_len, row_len, num_turns, pred, action_pred, states, med_num, police_num):
    directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    verse = True

    for turn in range(num_turns - 1):
        for i in range(col_len):
            for j in range(row_len):
                infect_verse = True
                infected_verse = True
                noop_action_pred = True
                loc = '(' + str(i) + str(j) + ')'

                # loop for noop actions
                for state in states:
                    pre_noop = get_noop_pre_cond(state, i, j, turn, col_len, row_len, pred)
                    # stays the same
                    add_noop = pred[state + str(turn + 1) + loc]
                    this_noop = 'noop' + state + str(turn) + loc
                    noop_action_pred = noop_action_pred & (~action_pred[this_noop] | (pre_noop & add_noop))

                # infect variables
                infect_ij = 'infect' + str(turn) + '(' + str(i) + str(j) + ')'
                pre_infect = get_infect_pre_cond(pred, turn, loc, police_num)
                add_infect = True

                # infected variables
                infected_ij = 'infected' + str(turn) + loc
                pre_infected = get_infected_pre_cond(pred, turn, loc, med_num)
                can_inf = False
                add_infected = True

                for move in directions:
                    loc2 = '(' + str(i + move[0]) + str(j + move[1]) + ')'
                    if 0 <= i + move[0] < col_len and 0 <= j + move[1] < row_len:
                        # add effect for infect
                        add_infect = add_infect & (~pred['H' + str(turn) + loc2] | pred['S' + str(turn + 1) + loc2])
                        # terms and add effect for infected
                        can_inf = can_inf | get_can_infect_cond(pred, turn, loc2, police_num)
                        add_infected = pred['S' + str(turn + 1) + loc]

                infected_verse = infected_verse & (~action_pred[infected_ij] | (pre_infected & add_infected & can_inf))
                infect_verse = infect_verse & (~action_pred[infect_ij] | (pre_infect & add_infect))

                verse = verse & infected_verse & infect_verse & noop_action_pred
    return verse


# returns the pre conditions for each noop action
def get_noop_pre_cond(state, i, j, turn, col_len, row_len, pred):
    loc = '(' + str(i) + str(j) + ')'
    cond = pred[state + str(turn) + loc]

    if state == 'H':
        for move in [[1, 0], [0, 1], [-1, 0], [0, -1]]:
            if 0 <= i + move[0] < col_len and 0 <= j + move[1] < row_len:
                cond = cond & ~pred['S' + str(turn) + '(' + str(i + move[0]) + str(j + move[1]) + ')']
        return cond

    if state == 'S':
        if turn >= 2:
            return (~pred[state + str(turn - 2) + loc] | ~pred[state + str(turn - 1) + loc]) & cond
        return cond

    if state == 'U':
        return cond

    if state == 'I':
        if turn == 0:
            return False
        return cond

    if state == 'Q':
        if turn == 0:
            return False
        return ~pred[state + str(turn - 1) + loc] & cond


# get pre cond for a spot to be able to infect others
def get_infect_pre_cond(pred, turn, loc, police_num):
    pre_cond = pred['S' + str(turn) + loc]
    if police_num > 0:
        pre_cond = pre_cond & ~pred['Q' + str(turn + 1) + loc]
    return pre_cond


# gets pre conditions for a spot to be infected
def get_infected_pre_cond(pred, turn, loc, med_num):
    pre_cond = pred['H' + str(turn) + loc]
    if med_num > 0:
        pre_cond = pre_cond & ~pred['I' + str(turn + 1) + loc]
    return pre_cond


# gets terms for a spots to be able to infect others this turn
def get_can_infect_cond(pred, turn, loc2, police_num):
    cond = pred['S' + str(turn) + loc2]
    if police_num > 0:
        cond = cond & ~pred['Q' + str(turn + 1) + loc2]
    return cond


# heal and free are actions of turning S and Q spots to H when their time is over.
def get_heal_and_free_verses(col_len, row_len, num_turns, pred, action_pred):
    heal_verses = true
    free_verses = true
    if num_turns <= 3:
        return heal_verses
    else:
        for turn in range(2, num_turns - 1):
            for i in range(col_len):
                for j in range(row_len):
                    loc = '(' + str(i) + str(j) + ')'
                    this_heal = 'heal' + str(turn) + loc
                    this_free = 'free' + str(turn) + loc
                    # needs to be Q for the last 2 turns
                    pre_free = pred['Q' + str(turn) + loc] & pred['Q' + str(turn - 1) + loc]
                    # needs to be S for the last 3 turns and not Q in the next
                    pre_heal = pred['S' + str(turn) + loc] & pred['S' + str(turn - 1) + loc]
                    pre_heal = pre_heal & pred['S' + str(turn - 2) + loc] & ~pred['Q' + str(turn + 1) + loc]
                    # both become H
                    add_heal = pred['H' + str(turn + 1) + loc]
                    add_free = pred['H' + str(turn + 1) + loc]

                    heal_verses = heal_verses & (~action_pred[this_heal] | (pre_heal & add_heal))
                    free_verses = free_verses & (~action_pred[this_free] | (pre_free & add_free))
    return heal_verses & free_verses


# gets the verse for a certain type of action: "Vac , Qua" with the input of the team num and type
def get_team_verses(team_type, team_num, col_len, row_len, num_turns, pred, action_pred, observations):
    team_verses = True
    action_list = []

    if team_num == 0:
        return team_verses

    # set needed type
    if team_type == 'police':
        action_type = 'Qua'
        pre_type = 'S'
        add_type = 'Q'
    else:
        action_type = 'Vac'
        pre_type = 'H'
        add_type = 'I'

    for turn in range(num_turns - 1):
        combo_verses = False
        for i in range(col_len):
            for j in range(row_len):
                loc = '(' + str(i) + str(j) + ')'
                # places that the action might be implemented oon
                if observations[turn][i][j] in [pre_type, '?']:
                    pre_cond = pred[pre_type + str(turn) + loc]
                    add_eff = pred[add_type + str(turn + 1) + loc]
                    action = action_type + str(turn) + loc
                    action_list.append(action_pred[action])
                    team_verses = team_verses & (~action_pred[action] | (pre_cond & add_eff))
        # we must have at most team num actions
        for combo in it.combinations(action_list, team_num):
            combo_verse = True
            for act in action_list:
                if act in combo:
                    combo_verse = combo_verse | act
                else:
                    combo_verse = combo_verse & ~act
            combo_verses = combo_verses | combo_verse
        team_verses = team_verses & combo_verses
        action_list = []

    return team_verses


# returns a verse with all the achievement clauses terms for all possible states
def get_achievement_clauses(pred, action_pred, num_turns, col_len, row_len, states):
    verse = True
    for turn in range(num_turns):
        for i in range(col_len):
            for j in range(row_len):
                loc = '(' + str(i) + str(j) + ')'
                for state in states:
                    verse = verse & get_clause_for_state(state, turn, loc, pred, action_pred)
    return verse


# gets the achievement clause for a given state
def get_clause_for_state(state, turn, loc, pred, action_pred):
    if turn == 0:
        return True

    if state == 'H':
        actions = action_pred['noopH' + str(turn - 1) + loc]
        if turn > 2:
            actions = actions | action_pred['free' + str(turn - 1) + loc] | action_pred['heal' + str(turn - 1) + loc]
        return ~pred['H' + str(turn) + loc] | actions

    if state == 'S':
        actions = action_pred['noopS' + str(turn - 1) + loc] | action_pred['infected' + str(turn - 1) + loc]
        return ~pred['S' + str(turn) + loc] | actions

    if state == 'U':
        return ~pred['U' + str(turn) + loc] | action_pred['noopU' + str(turn - 1) + loc]

    if state == 'I':
        actions = action_pred['Vac' + str(turn - 1) + loc] | action_pred['noopI' + str(turn - 1) + loc]
        return ~pred['I' + str(turn) + loc] | actions

    if state == 'Q':
        actions = action_pred['Qua' + str(turn - 1) + loc] | action_pred['noopQ' + str(turn - 1) + loc]
        return ~pred['Q' + str(turn) + loc] | actions


def answer_to_query(query, terms, pred, states):
    loc = str(query[1]) + '(' + str(query[0][0]) + str(query[0][1]) + ')'
    query_pred = pred[query[2] + loc]
    if not satisfiable(terms & query_pred):
        return 'F'
    else:
        for state in states:
            if state != query[2]:
                new_pred = pred[state + loc]
                if satisfiable(terms & new_pred):
                    return '?'
        return 'T'
