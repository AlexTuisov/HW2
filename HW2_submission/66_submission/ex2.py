import copy as cp
from pysat.solvers import Glucose4
from itertools import combinations

ids = ['318864436', '205704752']


def solve_problem(input):
    g_solver = Glucose4()
    police = input['police']
    medics = input['medics']
    observations = input['observations']
    queries = input['queries']

    queries_answers = dict()
    turns = 0
    for turn in observations:
        rows = 0
        for line in turn:
            cols = 0
            for var in line:
                cols += 1
            rows += 1
        turns += 1

    basics = [rows, cols, turns]

    known_base = list()
    actions, pos_states, days = action_treatment(police, medics, basics)
    clauses = negative_options(actions)
    known_base += clauses
    clauses = S_treatment(actions, basics, days, police)
    known_base += clauses

    if medics > 0:
        clauses = I_treatment(actions, basics, days, medics)
        known_base += clauses

    if police > 0:
        clauses = Q_treatment(actions, basics, days, police)
        known_base += clauses

    clauses = U_treatment(actions, basics, days)
    known_base += clauses

    clauses = H_treatment(actions, basics, days, police, medics)
    known_base += clauses

    clauses = infect(actions, basics, days, police)
    known_base += clauses

    clauses = initial(observations, actions, days)
    known_base += clauses

    for q in queries:
        query_answer = query_treatment(q, actions, days, known_base, g_solver, medics, police)
        queries_answers = merge_ans(queries_answers, query_answer)

    return queries_answers


def initial(observations, actions, possible_for_q):
    """
    :param observations: list of tuples -> our world
                        -> [(('H', '?'), ('H', 'H')), (('S', '?'), ('?', 'S'))]
    :param actions: dict of list -> key=tile, value= list of possible true actions on a tile organized by days
                        -> {(0, 0): [[1, 2, 3], [4, 5, 6, 7]], (0, 1): [[8, 9, 10], [11, 12, 13, 14]]}
    :param possible_for_q: the possible inputs for the '?' tile
    :return: all_clauses -> all only true statements about our world -> the initial state of the world in turn 0
    """
    all_clauses = list()

    current_turn = 0
    for turn in observations:
        row = 0
        for line in turn:
            col = 0
            for state in line:
                if state == '?':
                    col += 1
                    continue

                clause = []
                lst = actions[row, col]
                if state == 'S':
                    clause.append(lst[current_turn][possible_for_q[state, 0, current_turn]])
                    if current_turn > 0:
                        clause.append(lst[current_turn][possible_for_q[state, 1, current_turn]])
                    if current_turn > 1:
                        clause.append(lst[current_turn][possible_for_q[state, 2, current_turn]])
                    all_clauses.append(clause)

                elif state == 'Q':
                    clause.append(lst[current_turn][possible_for_q[state, 0, current_turn]])
                    if current_turn > 1:
                        clause.append(lst[current_turn][possible_for_q[state, 1, current_turn]])
                    all_clauses.append(clause)

                else:
                    all_clauses.append([lst[current_turn][possible_for_q[state, None, current_turn]]])

                col += 1
            row += 1
        current_turn += 1

    return all_clauses


def action_treatment(police, medics, basics):
    """
    :param police: number of police teams -> one police team will turn one S tile to Q
    :param medics: number of medics teams -> one medics team will turn one H tile to I
    :param basics: basics = [rows, cols, turns] -> basic information about our given observations
    :return: returns all possible actions on every given turn, on every tile
    """

    possible = {('H', None): 0, ('S', 0): 1, ('S', 1): 2, ('S', 2): 3, ('Q', 0): 4, ('Q', 1): 5, ('U', None): 6,
                  ('I', None): 7}

    actions = {}
    rows, cols, turns = [x for x in basics]
    # print (rows,columns,turns)
    first_turns = {}

    # all possible states on the initial turn
    day0 = [0, 1, 6] #0=H, 1=S0, 6=U
    dict0 = {('H', None, 0): 0, ('S', 0, 0): 1, ('U', None, 0): 2}

    # the possible states -> after turn 0
    day1, day2, dict1, dict2= possible_states(medics,police)

    # we're giving a special id for every possible action on every tile
    id = 1

    for i in range(rows):
        for j in range(cols):
            action_lst = []
            len0, len1, len2 = len(day0),len(day1),len(day2)

            zero_lst = list()
            for n in range(len0):
                zero_lst.append(id)
                id += 1
            action_lst.append(zero_lst)

            if turns > 1:
                one_lst = list()
                for n in range(len1):
                    one_lst.append(id)
                    id += 1
                action_lst.append(one_lst)

            if turns > 2:
                two_lst = list()
                for n in range(len2):
                    two_lst.append(id)
                    id += 1
                action_lst.append(two_lst)

                # after the second turn the lists are repeating themselves
                for n in range(turns - 3):
                    more_lst = []
                    for m in range(len2):
                        more_lst.append(id)
                        id += 1
                    action_lst.append(more_lst)

            actions[(i, j)] = action_lst

    #merging all dicts of possible states
    if turns > 2:
        first_turns = merge_ans(dict0, dict1) #turn 0 and turn 1
        first_turns = merge_ans(first_turns, dict2) #turn 0 and turn 1 and turn 2
        for i in range(3, turns):
            after_second_turn = after2_dict(dict2, i)
            first_turns = merge_ans(first_turns, after_second_turn)
    #turn 0 and turn 1 only
    elif turns ==2:
        first_turns = merge_ans(dict0, dict1)
    #turn 0 only
    else:
        first_turns = dict0

    return actions, possible, first_turns

def possible_states(medics, police):
    """
    :param medics: number of medics teams -> one medics team will turn one H tile to I
    :param police: number of police teams -> one police team will turn one S tile to Q
    :return: possible states for the first turn (day1 and dict1), and for the second turn (day2 and dict2)
    """

    #the case where we have no police or medics
    if police == 0 and medics == 0:
        # no police and no medics
        day1 = [0, 1, 2, 6]
        dict1 = {('H', None, 1): 0, ('S', 0, 1): 1, ('S', 1, 1): 2, ('U', None, 1): 3}
        day2 = [0, 1, 2, 3, 6]
        dict2 = {('H', None, 2): 0, ('S', 0, 2): 1, ('S', 1, 2): 2, ('S', 2, 2): 3, ('U', None, 2): 4}

    # the case where we have no medics but we have police teams
    elif medics == 0:
        day1 = [0, 1, 2, 4, 6]
        dict1 = {('H', None, 1): 0, ('S', 0, 1): 1, ('S', 1, 1): 2, ('Q', 0, 1): 3, ('U', None, 1): 4}
        day2 = [0, 1, 2, 3, 4, 5, 6]
        dict2 = {('H', None, 2): 0, ('S', 0, 2): 1, ('S', 1, 2): 2, ('S', 2, 2): 3, ('Q', 0, 2): 4,
                        ('Q', 1, 2): 5, ('U', None, 2): 6}

    # the case where we have no police but we have medics teams
    elif police == 0:
        day1 = [0, 1, 2, 6, 7]
        dict1 = {('H', None, 1): 0, ('S', 0, 1): 1, ('S', 1, 1): 2, ('U', None, 1): 3, ('I', None, 1): 4}
        day2 = [0, 1, 2, 3, 6, 7]
        dict2 = {('H', None, 2): 0, ('S', 0, 2): 1, ('S', 1, 2): 2, ('S', 2, 2): 3, ('U', None, 2): 4, ('I', None, 2): 5}

    # the case where we have both medics and police teams
    else:
        day1 = [0, 1, 2, 4, 6, 7]
        dict1 = {('H', None, 1): 0, ('S', 0, 1): 1, ('S', 1, 1): 2, ('Q', 0, 1): 3, ('U', None, 1): 4, ('I', None, 1): 5}
        day2 = [0, 1, 2, 3, 4, 5, 6, 7]
        dict2 = {('H', None, 2): 0, ('S', 0, 2): 1, ('S', 1, 2): 2, ('S', 2, 2): 3, ('Q', 0, 2): 4, ('Q', 1, 2): 5, ('U', None, 2): 6, ('I', None, 2): 7}

    return day1, day2, dict1, dict2


def after2_dict(dict2, turn):
    res = dict()
    for key in dict2.keys():
        i, j, n = [k for k in key] # we don't need the 'n' variable
        res[(i, j, turn)] = dict2[key]
    return res


def negative_options(actions):
    """
    :param actions: dict of list of lists -> all possible true actions on every tile
                        --> {(0, 0): [[1, 2, 3], [4, 5, 6, 7]], (0, 1): [[8, 9, 10], [11, 12, 13, 14]]}
    :returns: neg_clauses -> list of every negative options (what will not happen)
                    --> [[-1, -2], [-1, -3], [-2, -3], [-4, -5], [-4, -6], [-4, -7], [-5, -6], [-5, -7], [-6, -7],
                                [-8, -9], [-8, -10],[-9, -10], [-11, -12], [-11, -13], [-11, -14], [-12, -13],
                                [-12, -14], [-13, -14]]
    """

    neg_clauses = list()
    for value in actions.values():
        for i in value:
            a = cp.deepcopy(i)
            a[:] = [-1 * x for x in a]

            # we want combinations of 2
            for x in combinations(a, 2):
                neg_clauses.append(list(x))
    return neg_clauses


def S_treatment(actions, basics, possible_for_q, police):
    """
    :param actions: dict of list -> key=tile, value= list of possible true actions on a tile organized by days
                    --> {(0, 0): [[1, 2, 3], [4, 5, 6, 7]], (0, 1): [[8, 9, 10], [11, 12, 13, 14]]}
    :param pos_states: possible states for a tile
    :param basics: [row,cols,turns] -> we will need only the turns value
    :param possible_for_q: the possible inputs for the '?' tile
    :param police: number of police teams
    :return: clauses (list of lists) -> possible answers for what should the '?' tile be
    """

    res_clauses = list()
    turns=basics[2] #how many turns we have on a query

    if turns == 1: # only turn 0
        return res_clauses

    for key in actions.keys():
        #print('val',key)
        iterval = iter(actions[key]) # all possible actions on specific tile organized by days
        next(iterval)  # skipping turn 0
        current_turn = 1
        for val in iterval:  # running on the number of turns
            one_neg = []
            one_neg.append(-1 * val[possible_for_q['S', 0, current_turn]])

            # checking all S neighbors
            up_check, down_check, left_check, right_check = neighbors_of_tile(basics, key)
            if current_turn == 1:
                res_clauses.append(day_handler(val, actions, key, 'S', 0, current_turn, possible_for_q, 'H', None, 'yesterday'))
                res_clauses.append(day_handler(val, actions, key, 'S', 1, current_turn, possible_for_q, 'S', 0, 'yesterday'))
                if police == 0:
                    res_clauses.append(day_handler(val, actions, key, 'S', 1, current_turn, possible_for_q, 'S', 0, 'tomorrow'))

            elif current_turn == 2:
                res_clauses.append(day_handler(val, actions, key, 'S', 0, current_turn, possible_for_q, 'H', None, 'yesterday'))
                res_clauses.append(day_handler(val, actions, key, 'S', 1, current_turn, possible_for_q, 'S', 0, 'yesterday'))
                res_clauses.append(day_handler(val, actions, key, 'S', 2, current_turn, possible_for_q, 'S', 1, 'yesterday'))
                if police == 0:
                    res_clauses.append(day_handler(val, actions, key, 'S', 1, current_turn, possible_for_q, 'S', 0, 'tomorrow'))
                    res_clauses.append(day_handler(val, actions, key, 'S', 2, current_turn, possible_for_q, 'S', 1, 'tomorrow'))

            elif current_turn >= 3:
                res_clauses.append(day_handler(val, actions, key, 'S', 0, current_turn, possible_for_q, 'H', None, 'yesterday'))
                res_clauses.append(day_handler(val, actions, key, 'S', 1, current_turn, possible_for_q, 'S', 0, 'yesterday'))
                res_clauses.append(day_handler(val, actions, key, 'S', 2, current_turn, possible_for_q, 'S', 1, 'yesterday'))

                if police == 0:
                    res_clauses.append(day_handler(val, actions, key, 'S', 1, current_turn, possible_for_q, 'S', 0, 'tomorrow'))
                    res_clauses.append(day_handler(val, actions, key, 'S', 2, current_turn, possible_for_q, 'S', 1, 'tomorrow'))
                    res_clauses.append(day_handler(val, actions, key, 'H', None, current_turn, possible_for_q, 'S', 2, 'tomorrow'))

            if right_check: # there is a neighbor to the right
                right_lst = actions[(key[0], key[1] + 1)]
                one_neg.append(right_lst[current_turn - 1][possible_for_q[('S', 0, current_turn - 1)]])
                if current_turn > 1:
                    one_neg.append(right_lst[current_turn - 1][possible_for_q[('S', 1, current_turn - 1)]])
                if current_turn > 2:
                    one_neg.append(right_lst[current_turn - 1][possible_for_q[('S', 2, current_turn - 1)]])

            if left_check: # there is a neighbor to the left
                left_lst = actions[(key[0], key[1] - 1)]
                one_neg.append(left_lst[current_turn - 1][possible_for_q[('S', 0, current_turn - 1)]])
                if current_turn > 1:
                    one_neg.append(left_lst[current_turn - 1][possible_for_q[('S', 1, current_turn - 1)]])
                if current_turn > 2:
                    one_neg.append(left_lst[current_turn - 1][possible_for_q[('S', 2, current_turn - 1)]])

            if up_check: # there is a neighbor upside
                up_lst = actions[(key[0] - 1, key[1])]
                one_neg.append(up_lst[current_turn - 1][possible_for_q[('S', 0, current_turn - 1)]])
                if current_turn > 1:
                    one_neg.append(up_lst[current_turn - 1][possible_for_q[('S', 1, current_turn - 1)]])
                if current_turn > 2:
                    one_neg.append(up_lst[current_turn - 1][possible_for_q[('S', 2, current_turn - 1)]])

            if down_check: # there is a neighbor downside
                down_lst = actions[(key[0] + 1, key[1])]
                one_neg.append(down_lst[current_turn - 1][possible_for_q[('S', 0, current_turn - 1)]])
                if current_turn > 1:
                    one_neg.append(down_lst[current_turn - 1][possible_for_q[('S', 1, current_turn - 1)]])
                if current_turn > 2:
                    one_neg.append(down_lst[current_turn - 1][possible_for_q[('S', 2, current_turn - 1)]])

            res_clauses.append(one_neg)
            current_turn += 1

    return res_clauses

def day_handler(val, actions, key, s1, c1, turn, days, s2, c2, what_day):
    current = actions[key]
    if what_day=='yesterday':
        return [-1 * val[days[s1, c1, turn]], current[turn - 1][days[(s2, c2, turn - 1)]]]
    elif what_day=='tomorrow':
        return [val[days[s1, c1, turn]], -1 * current[turn - 1][days[(s2, c2, turn - 1)]]]



def neighbors_of_tile(basics, position):
    """
        :param basics: [rows,cols,turns]
        :param position: the tile (row,col)
        :return: up -> if there is a neighbor upside
                down -> if there is a neighbor downside
                left -> if there is a neighbor to the left
                right -> if there is a neighbor to the right
    """
    up, down, left, right = False, False, False, False
    row_num, column_num, turns = [i for i in basics]
    row, col = position[0], position[1]
    if row + 1 < row_num:
        down = True
    if row > 0:
        up = True
    if col + 1 < column_num:
        right = True
    if col > 0:
        left = True
    return up, down, left, right


def infect(actions, basics, possible_for_q, police):
    """
    :param actions: dict of list -> key=tile, value= list of possible true actions on a tile organized by days
                    --> {(0, 0): [[1, 2, 3], [4, 5, 6, 7]], (0, 1): [[8, 9, 10], [11, 12, 13, 14]]}
    :param basics: [row,cols,turns] -> we will need only the turns value
    :param possible_for_q: the possible inputs for the '?' tile
    :param police: number of police teams
    :return: clauses (list of lists) -> possible answers for what should the '?' tile be
    """
    rows, columns, turns = [i for i in basics]
    clauses = []
    if turns == 1:
        return clauses

    for key, value in actions.items():
        up_check, down_check, left_check, right_check = neighbors_of_tile(basics, key)
        current_turn = 0
        for val in value[:-1]:  # run on days
            if up_check:
                up_lst = actions[(key[0] - 1, key[1])]
                clauses += infect_for_neighbor_x(up_lst, current_turn, possible_for_q, val, police)

            if down_check:
                down_lst = actions[(key[0] + 1, key[1])]
                clauses += infect_for_neighbor_x(down_lst, current_turn, possible_for_q, val, police)

            if left_check:
                left_lst = actions[(key[0], key[1] - 1)]
                clauses += infect_for_neighbor_x(left_lst, current_turn, possible_for_q, val, police)

            if right_check:
                right_lst = actions[(key[0], key[1] + 1)]
                clauses += infect_for_neighbor_x(right_lst, current_turn, possible_for_q, val, police)

            current_turn += 1

    return clauses


def infect_for_neighbor_x(direction, current_turn, possible_for_q, val, police):
    """
    helper function to infect function
    """
    res = list()
    if current_turn == 0:
        res.append([-1 * val[possible_for_q['S', 0, current_turn]], -1 * direction[current_turn + 1][possible_for_q['H', None, current_turn + 1]]])
    elif current_turn == 1:
        res.append([-1 * val[possible_for_q['S', 0, current_turn]], -1 * direction[current_turn + 1][possible_for_q['H', None, current_turn + 1]]])
        res.append([-1 * val[possible_for_q['S', 1, current_turn]], -1 * direction[current_turn + 1][possible_for_q['H', None, current_turn + 1]]])
    elif current_turn >1:
        if police == 0:
            res.append([-1 * val[possible_for_q['S', 0, current_turn]], -1 * direction[current_turn + 1][possible_for_q['H', None, current_turn + 1]],
                        direction[current_turn][possible_for_q['S', 2, current_turn]]])
            res.append([-1 * val[possible_for_q['S', 1, current_turn]], -1 * direction[current_turn + 1][possible_for_q['H', None, current_turn + 1]],
                        direction[current_turn][possible_for_q['S', 2, current_turn]]])
            res.append([-1 * val[possible_for_q['S', 2, current_turn]], -1 * direction[current_turn + 1][possible_for_q['H', None, current_turn + 1]],
                        direction[current_turn][possible_for_q['S', 2, current_turn]]])
        else:
            res.append([-1 * val[possible_for_q['S', 0, current_turn]], -1 * direction[current_turn + 1][possible_for_q['H', None, current_turn + 1]],
                        direction[current_turn][possible_for_q['S', 2, current_turn]], direction[current_turn][possible_for_q['Q', 1, current_turn]]])
            res.append([-1 * val[possible_for_q['S', 1, current_turn]], -1 * direction[current_turn + 1][possible_for_q['H', None, current_turn + 1]],
                        direction[current_turn][possible_for_q['S', 2, current_turn]], direction[current_turn][possible_for_q['Q', 1, current_turn]]])
            res.append([-1 * val[possible_for_q['S', 2, current_turn]], -1 * direction[current_turn + 1][possible_for_q['H', None, current_turn + 1]],
                        direction[current_turn][possible_for_q['S', 2, current_turn]], direction[current_turn][possible_for_q['Q', 1, current_turn]]])
    return res

def I_treatment(actions, basics, possible_for_q, medics):
    """
    :param actions: dict of list -> key=tile, value= list of possible true actions on a tile organized by days
                            --> {(0, 0): [[1, 2, 3], [4, 5, 6, 7]], (0, 1): [[8, 9, 10], [11, 12, 13, 14]]}
    :param basics: [row,cols,turns] -> we will need only the turns value
    :param possible_for_q: the possible inputs for the '?' tile
    :param medics: number of medics teams
    :return: all_clauses (list of lists) -> possible answers for what should the '?' tile be
    """

    turns = basics[2]
    all_clauses = []
    if turns == 1:
        return all_clauses
    for key in actions.keys():
        cur = actions[key]
        interval = iter(cur)
        next(interval)
        current_turn = 1
        for val in interval:
            c1 = []
            c1.append(cur[current_turn - 1][possible_for_q[('H', None, current_turn - 1)]])
            c1.append(-1 * val[possible_for_q['I', None, current_turn]])

            if current_turn >= 2:
                c1.append(cur[current_turn - 1][possible_for_q[('I', None, current_turn - 1)]])
            current_turn += 1

            all_clauses.append(c1)
    if medics >= 1:
        tmp = list()
        for turn in range(1, turns):
            I_list = list()
            for key, val in actions.items():
                I_list.append(val[turn][possible_for_q[('I', None, turn)]])
            I_list = [(-1) * x for x in I_list]
            comb = combinations(I_list, 2 + (turn - 1) * medics)
            tmp += [list(i) for i in comb]
        all_clauses += tmp

    return all_clauses


def Q_treatment(actions, basics, possible_for_q, police):
    """
        :param actions: dict of list -> key=tile, value= list of possible true actions on a tile organized by days
                        --> {(0, 0): [[1, 2, 3], [4, 5, 6, 7]], (0, 1): [[8, 9, 10], [11, 12, 13, 14]]}
        :param basics: [row,cols,turns] -> we will need only the turns value
        :param possible_for_q: the possible inputs for the '?' tile
        :param police: number of police teams
        :return: all_clauses (list of lists) -> possible answers for what should the '?' tile be
    """

    #inf = [i for i in info]
    turns = basics[2]
    all_clauses = list()
    if turns == 1:
        return all_clauses
    for key, val in actions.items():
        cur = actions[key]
        interval = iter(val)
        next(interval) # starts on turn 1
        clause = list()
        current_turn = 1
        for val in interval:
            clause.append(cur[current_turn - 1][possible_for_q[('S', 0, current_turn - 1)]])
            clause.append(-1 * val[possible_for_q[('Q', 0, current_turn)]])

            if current_turn >= 3:
                clause.append(cur[current_turn - 1][possible_for_q[('S', 2, current_turn - 1)]])

            if current_turn >= 2:
                all_clauses.append([-1 * val[possible_for_q[('Q', 1, current_turn)]], cur[current_turn - 1][possible_for_q[('Q', 0, current_turn - 1)]]])
                clause.append(cur[current_turn - 1][possible_for_q[('S', 1, current_turn - 1)]])

            all_clauses.append(clause)
            current_turn += 1
    q = list()
    if police >= 1:
        q_list = list()
        for turn in range(1, turns):
            for key, val in actions.items():
                q_list.append(val[turn][possible_for_q[('Q', 0, turn)]])
            q.append(q_list)
            q_list = [-1 * i for i in q_list]
            comb = combinations(q_list, 2 + (turn - 1) * police)
            q += [list(i) for i in comb]

        all_clauses += q
    return all_clauses



def H_treatment(actions, basics, possible_for_q, police, medics):
    """
    :param actions: dict of list -> key=tile, value= list of possible true actions on a tile organized by days
                    --> {(0, 0): [[1, 2, 3], [4, 5, 6, 7]], (0, 1): [[8, 9, 10], [11, 12, 13, 14]]}
    :param basics: [row,cols,turns] -> we will need only the turns value
    :param possible_for_q: the possible inputs for the '?' tile
    :param police: number of police teams
    :param medics: number of medics teams
    :return: clauses (list of lists) -> possible answers for what should the '?' tile be
    """
    clauses = list()
    turns=basics[2]
    if turns == 1:
        return clauses

    for key in actions.keys():
        iterval = iter(actions[key])
        next(iterval)  # starts with turn 1
        current_turn = 1
        for val in iterval:  # running on days
            c1, c2 = list(), list()
            current = actions[key]

            c1.append(-1 * val[possible_for_q['H', None, current_turn]])  # if you're H now, you were H or S2 on the previous turn
            c1.append(current[current_turn - 1][possible_for_q[('H', None, current_turn - 1)]])

            c2.append(-1 * current[current_turn - 1][possible_for_q[('H', None, current_turn - 1)]])
            c2.append(val[possible_for_q[('H', None, current_turn)]])
            c2.append(val[possible_for_q[('S', 0, current_turn)]])
            if current_turn > 2:
                c1.append(current[current_turn - 1][possible_for_q[('S', 2, current_turn - 1)]])
                if police > 0:
                    c1.append(current[current_turn - 1][possible_for_q[('Q', 1, current_turn - 1)]])
            if medics > 0:
                c2.append(val[possible_for_q[('I', None, current_turn)]])
            current_turn += 1

            clauses.append(c1)
            clauses.append(c2)
    return clauses


def U_treatment(actions, basics, possible_for_q):
    """
        :param actions: dict of list -> key=tile, value= list of possible true actions on a tile organized by days
                        --> {(0, 0): [[1, 2, 3], [4, 5, 6, 7]], (0, 1): [[8, 9, 10], [11, 12, 13, 14]]}
        :param basics: [row,cols,turns] -> we will need only the turns value
        :param possible_for_q: the possible inputs for the '?' tile
        :return: all_clauses (list of lists) -> possible answers for what should the '?' tile be
        """

    turns = basics[2]
    all_clauses = list()
    if turns == 1:
        return all_clauses
    for key in actions.keys():
        curr_actions = actions[key]
        interval = iter(curr_actions)
        next(interval)
        current_turn = 1

        for val in interval:
            c1 = list()
            c1.append(curr_actions[current_turn][possible_for_q[('U', None, current_turn)]])
            c1.append(-1 * curr_actions[current_turn - 1][possible_for_q[('U', None, current_turn - 1)]])
            c2 = list()
            c2.append(-1 * curr_actions[current_turn][possible_for_q[('U', None, current_turn)]])
            c2.append(curr_actions[current_turn - 1][possible_for_q[('U', None, current_turn - 1)]])

            current_turn += 1

        all_clauses.append(c1)
        all_clauses.append(c2)
    return all_clauses




def query_treatment(query, actions, days, known_base, g_solver, medics, police):

    query_answers = dict()
    for kb in known_base:
        g_solver.add_clause(kb)

    turn,state = query[1], query[2]
    if state == 'I' or state == 'Q':
        if state=='I':
            if turn == 0 or medics == 0:
                query_answers[query] = 'F'
                return query_answers
        else:
            if turn == 0 or police == 0:
                query_answers[query] = 'F'
                return query_answers

    row,col = query[0][0],query[0][1]
    lst = actions[row, col]
    if state == 'Q':
        stateQ = list()
        question = lst[turn][days[state, 0, turn]]
        answer = check(known_base, question)
        stateQ.append(answer)

        if turn >= 2:
            question = lst[turn][days[state, 1, turn]]
            answer = check(known_base, question)
            stateQ.append(answer)
        for row in stateQ:
            if row == 'T':
                query_answers[query] = 'T'
                return query_answers
        query_answers[query] = '?' if '?' in stateQ else 'F'
        return query_answers

    elif state == 'S':
        stateS = list()
        question = lst[turn][days[state, 0, turn]]
        answer = check(known_base, question)
        stateS.append(answer)

        if turn >=1:
            question = lst[turn][days[state, 1, turn]]
            answer = check(known_base, question)
            stateS.append(answer)
        if turn >=2:
            question = lst[turn][days[state, 2, turn]]
            answer = check(known_base, question)
            stateS.append(answer)

        for row in stateS:
            if row == 'T':
                query_answers[query] = 'T'
                return query_answers

        query_answers[query] = '?' if '?' in stateS else 'F'
        return query_answers

    else:
        question = lst[turn][days[state, None, turn]]
        answer = check(known_base, question)
        query_answers[query] = answer
        return query_answers


def solver(known_base, ask):
    """
    the SAT solver
    """
    g_solver = Glucose4()
    g_solver.add_clause([ask])
    for kb in known_base:
        g_solver.add_clause(kb)

    ans = g_solver.solve()
    g_solver.delete()
    return ans


def check(known_base, ask):
    """
    :param known_base: our world as we know
    :param ask: our question -> we ask if this could happen in our known_base
    :return: 'T' if it can, 'F' if it cannot, '?' if we don't know
    """
    res = solver(known_base, ask)
    if res:
        ask = -1 * ask
        res = solver(known_base, ask)
        if not res:
            return 'T'
        else:
            return '?'
    else:
        return 'F'


#helper function
def merge_ans(dict1, dict2):
    res = {**dict1, **dict2}
    return res
