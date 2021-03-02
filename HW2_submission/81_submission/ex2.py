import copy as cp
from pysat.solvers import Glucose4
from pysat.card import *
from itertools import combinations
import math


def merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res


ids = ['311156327', '204585301']


def solve_problem(input):
    g = Glucose4()
    police = input['police']
    medics = input['medics']
    obs_map = input['observations']
    queries = input['queries']

    queries_dict = {}
    m = 0
    for turn in obs_map:
        i = 0
        for line in turn:
            j = 0
            for var in line:
                j += 1
            i += 1
        m += 1

    rows = i
    columns = j
    turns = m

    info = [rows, columns, turns]

    kb = []
    actions, pos_states, days = action_treatment(police, medics, info)
    # print('actions!',actions)
    clauses = only_one_per_position(actions)
    kb += clauses
    # print(kb)
    clauses = S_treatment(actions, pos_states, info, days, police, medics)
    kb += clauses

    if police > 0:
        clauses = Q_treatment(actions, pos_states, info, days, police)
        # print('p',clauses)
        kb += clauses

    if medics > 0:
        clauses = I_treatment(actions, pos_states, info, days, medics)
        # print('m',clauses)
        kb += clauses

    clauses = H_treatment(actions, pos_states, info, days, police, medics)
    # print('h',clauses)
    kb += clauses

    clauses = U_treatment(actions, pos_states, info, days)
    # print('u',clauses)
    kb += clauses

    clauses = infect(actions, info, days, police)
    # print('days',days)
    # print('infect',clauses)
    kb += clauses

    clauses = Initial(obs_map, actions, info, days)
    kb += clauses

    for q in queries:
        query_dict = query_treatment(q, actions, info, days, kb, g, medics, police)
        queries_dict = merge(queries_dict, query_dict)

    return queries_dict


def action_treatment(police, medics, info):
    pos_states = {('H', None): 0, ('S', 0): 1, ('S', 1): 2, ('S', 2): 3, ('Q', 0): 4, ('Q', 1): 5, ('U', None): 6,
                  ('I', None): 7}
    actions = {}
    rows, columns, turns = [i for i in info]
    # print (rows,columns,turns)
    days = {}
    # general
    day_zero = [0, 1, 6]
    day_zero_dict = {('H', None, 0): 0, ('S', 0, 0): 1, ('U', None, 0): 2}
    if police == 0 and medics == 0:
        # no police and no medics
        day_one = [0, 1, 2, 6]
        day_two = [0, 1, 2, 3, 6]
        day_one_dict = {('H', None, 1): 0, ('S', 0, 1): 1, ('S', 1, 1): 2, ('U', None, 1): 3}
        day_two_dict = {('H', None, 2): 0, ('S', 0, 2): 1, ('S', 1, 2): 2, ('S', 2, 2): 3, ('U', None, 2): 4}

    elif medics == 0:
        # no medics
        day_one = [0, 1, 2, 4, 6]
        day_two = [0, 1, 2, 3, 4, 5, 6]
        day_one_dict = {('H', None, 1): 0, ('S', 0, 1): 1, ('S', 1, 1): 2, ('Q', 0, 1): 3, ('U', None, 1): 4}
        day_two_dict = {('H', None, 2): 0, ('S', 0, 2): 1, ('S', 1, 2): 2, ('S', 2, 2): 3, ('Q', 0, 2): 4,
                        ('Q', 1, 2): 5, ('U', None, 2): 6}

    elif police == 0:
        # no police
        day_one = [0, 1, 2, 6, 7]
        day_two = [0, 1, 2, 3, 6, 7]
        day_one_dict = {('H', None, 1): 0, ('S', 0, 1): 1, ('S', 1, 1): 2, ('U', None, 1): 3, ('I', None, 1): 4}
        day_two_dict = {('H', None, 2): 0, ('S', 0, 2): 1, ('S', 1, 2): 2, ('S', 2, 2): 3, ('U', None, 2): 4,
                        ('I', None, 2): 5}

    else:
        # all
        day_one = [0, 1, 2, 4, 6, 7]
        day_two = [0, 1, 2, 3, 4, 5, 6, 7]
        day_one_dict = {('H', None, 1): 0, ('S', 0, 1): 1, ('S', 1, 1): 2, ('Q', 0, 1): 3, ('U', None, 1): 4,
                        ('I', None, 1): 5}
        day_two_dict = {('H', None, 2): 0, ('S', 0, 2): 1, ('S', 1, 2): 2, ('S', 2, 2): 3, ('Q', 0, 2): 4,
                        ('Q', 1, 2): 5, ('U', None, 2): 6, ('I', None, 2): 7}
    action_dict = {}

    # action_dict = {(0,0): [1,2,3] ,(0,1):[4,5,6] ,(1,0):[7,8,9] ,(1,1):[10,11,12]}
    # {(0,0): [1,2,3],[13,14,15,16],(0,1):[4,5,6],[17,18,19,20] ,(1,0):[7,8,9],[21,22,23,24] ,(1,1):[10,11,12],[25,26,27,28]}
    # mix ((i,j)[1]) -> [-1,-2] ,[-2,-3],[-1,-3]
    dict10 = dict()
    '''
  for i in range(4):
    temp = '{}'.format(i)
    dict10[('H',temp)] = ('H',temp)
  print('this is my dict bbbbb', dict10)
  '''
    id = 1

    for i in range(rows):
        for j in range(columns):
            action_lst = []
            zero_len = len(day_zero)
            one_len = len(day_one)
            two_len = len(day_two)

            zero_lst = []
            for n in range(zero_len):
                zero_lst.append(id)
                id += 1
            action_lst.append(zero_lst)

            if turns > 1:
                one_lst = []
                for n in range(one_len):
                    one_lst.append(id)
                    id += 1
                action_lst.append(one_lst)

            if turns > 2:
                two_lst = []
                for n in range(two_len):
                    two_lst.append(id)
                    id += 1
                action_lst.append(two_lst)

                for n in range(turns - 3):
                    more_lst = []
                    for m in range(two_len):
                        more_lst.append(id)
                        id += 1
                    action_lst.append(more_lst)

            actions[(i, j)] = action_lst

    if turns > 2:
        days = merge(day_zero_dict, day_one_dict)
        days = merge(days, day_two_dict)
        for i in range(3, turns):
            new_day = make_new_dict(day_two_dict, i)
            # print("new_day",new_day)
            # print("day_two_dict",day_two_dict)
            days = merge(days, new_day)
            # print(days)
    elif turns > 1:
        days = merge(day_zero_dict, day_one_dict)
    else:
        days = day_zero_dict

    return actions, pos_states, days


def make_new_dict(day_two_dict, turn):
    new_dict = {}
    for key, value in day_two_dict.items():
        i, j, n = [k for k in key]
        new_key = (i, j, turn)
        new_dict[new_key] = value
    return new_dict


def only_one_per_position(actions):
    clauses = []
    for key, value in actions.items():
        for i in value:
            a = cp.deepcopy(i)
            a[:] = [-1 * x for x in a]
            for x in combinations(a, 2):
                clauses.append(list(x))
    return clauses


def S_treatment(actions, pos_states, info, days, police, medics):
    clauses = []
    rows, columns, turns = [i for i in info]
    if turns == 1:
        return clauses

    for key, value in actions.items():
        iterval = iter(value)
        next(iterval)  # skip first turn
        m = 1
        for val in iterval:  # run on days
            clause = []
            clause.append(-1 * val[days['S', 0, m]])
            # print(val[pos_states['S',0]])
            up_check, down_check, left_check, right_check = is_nbrs(info, key)
            if m >= 3:
                clauses.append(today_yesterday(val, pos_states, actions, key, 'S', 0, m, days, 'H', None))
                clauses.append(today_yesterday(val, pos_states, actions, key, 'S', 1, m, days, 'S', 0))
                clauses.append(today_yesterday(val, pos_states, actions, key, 'S', 2, m, days, 'S', 1))

                if police == 0:
                    clauses.append(today_tomorrow(val, pos_states, actions, key, 'S', 1, m, days, 'S', 0))
                    clauses.append(today_tomorrow(val, pos_states, actions, key, 'S', 2, m, days, 'S', 1))
                    clauses.append(today_tomorrow(val, pos_states, actions, key, 'H', None, m, days, 'S', 2))

            elif m == 2:
                clauses.append(today_yesterday(val, pos_states, actions, key, 'S', 0, m, days, 'H', None))
                clauses.append(today_yesterday(val, pos_states, actions, key, 'S', 1, m, days, 'S', 0))
                clauses.append(today_yesterday(val, pos_states, actions, key, 'S', 2, m, days, 'S', 1))
                if police == 0:
                    clauses.append(today_tomorrow(val, pos_states, actions, key, 'S', 1, m, days, 'S', 0))
                    clauses.append(today_tomorrow(val, pos_states, actions, key, 'S', 2, m, days, 'S', 1))

            elif m == 1:
                clauses.append(today_yesterday(val, pos_states, actions, key, 'S', 0, m, days, 'H', None))
                clauses.append(today_yesterday(val, pos_states, actions, key, 'S', 1, m, days, 'S', 0))
                if police == 0:
                    clauses.append(today_tomorrow(val, pos_states, actions, key, 'S', 1, m, days, 'S', 0))

            if up_check:
                up_lst = actions[up(key)]
                clause.append(up_lst[m - 1][days[('S', 0, m - 1)]])
                if m > 1:
                    clause.append(up_lst[m - 1][days[('S', 1, m - 1)]])
                if m > 2:
                    clause.append(up_lst[m - 1][days[('S', 2, m - 1)]])

            if down_check:
                down_lst = actions[down(key)]
                clause.append(down_lst[m - 1][days[('S', 0, m - 1)]])
                if m > 1:
                    clause.append(down_lst[m - 1][days[('S', 1, m - 1)]])
                if m > 2:
                    clause.append(down_lst[m - 1][days[('S', 2, m - 1)]])
            if left_check:
                left_lst = actions[left(key)]
                clause.append(left_lst[m - 1][days[('S', 0, m - 1)]])
                if m > 1:
                    clause.append(left_lst[m - 1][days[('S', 1, m - 1)]])
                if m > 2:
                    clause.append(left_lst[m - 1][days[('S', 2, m - 1)]])
            if right_check:
                right_lst = actions[right(key)]
                clause.append(right_lst[m - 1][days[('S', 0, m - 1)]])
                if m > 1:
                    clause.append(right_lst[m - 1][days[('S', 1, m - 1)]])
                if m > 2:
                    clause.append(right_lst[m - 1][days[('S', 2, m - 1)]])

            clauses.append(clause)
            m += 1

    return clauses


def infect(actions, info, days, police):
    rows, columns, turns = [i for i in info]
    clauses = []
    if turns == 1:
        return clauses

    for key, value in actions.items():
        up_check, down_check, left_check, right_check = is_nbrs(info, key)
        m = 0
        for val in value[:-1]:  # run on days
            if up_check:
                up_lst = actions[up(key)]
                clauses += infect_helper(up_lst, key, m, days, val, police)

            if down_check:
                down_lst = actions[down(key)]
                clauses += infect_helper(down_lst, key, m, days, val, police)

            if left_check:
                left_lst = actions[left(key)]
                clauses += infect_helper(left_lst, key, m, days, val, police)

            if right_check:
                right_lst = actions[right(key)]
                clauses += infect_helper(right_lst, key, m, days, val, police)

            m += 1

    return clauses


def infect_helper(direction, key, m, days, val, police):
    clauses = []
    if m == 0:
        clauses.append([-1 * val[days['S', 0, m]], -1 * direction[m + 1][days['H', None, m + 1]]])
    elif m == 1:
        clauses.append([-1 * val[days['S', 0, m]], -1 * direction[m + 1][days['H', None, m + 1]]])
        clauses.append([-1 * val[days['S', 1, m]], -1 * direction[m + 1][days['H', None, m + 1]]])
    elif m >= 2:
        if police == 0:
            clauses.append([-1 * val[days['S', 0, m]], -1 * direction[m + 1][days['H', None, m + 1]],
                            direction[m][days['S', 2, m]]])
            clauses.append([-1 * val[days['S', 1, m]], -1 * direction[m + 1][days['H', None, m + 1]],
                            direction[m][days['S', 2, m]]])
            clauses.append([-1 * val[days['S', 2, m]], -1 * direction[m + 1][days['H', None, m + 1]],
                            direction[m][days['S', 2, m]]])
        else:
            clauses.append([-1 * val[days['S', 0, m]], -1 * direction[m + 1][days['H', None, m + 1]],
                            direction[m][days['S', 2, m]], direction[m][days['Q', 1, m]]])
            clauses.append([-1 * val[days['S', 1, m]], -1 * direction[m + 1][days['H', None, m + 1]],
                            direction[m][days['S', 2, m]], direction[m][days['Q', 1, m]]])
            clauses.append([-1 * val[days['S', 2, m]], -1 * direction[m + 1][days['H', None, m + 1]],
                            direction[m][days['S', 2, m]], direction[m][days['Q', 1, m]]])
    return clauses


def today_yesterday(val, pos_states, actions, key, state_1, count_1, turn, days, state_2, count_2):
    current = actions[key]
    return [-1 * val[days[state_1, count_1, turn]], current[turn - 1][days[(state_2, count_2, turn - 1)]]]


def today_tomorrow(val, pos_states, actions, key, state_1, count_1, turn, days, state_2, count_2):
    current = actions[key]
    return [val[days[state_1, count_1, turn]], -1 * current[turn - 1][days[(state_2, count_2, turn - 1)]]]


def Q_treatment(actions, pos_states, info, days, police):
    rows, columns, turns = [i for i in info]
    clauses = []
    if turns == 1:
        return clauses
    for key, value in actions.items():
        current = actions[key]
        iterval = iter(value)
        next(iterval)  # skip first turn
        m = 1
        for val in iterval:
            clause = []
            clause.append(-1 * val[days[('Q', 0, m)]])
            clause.append(current[m - 1][days[('S', 0, m - 1)]])
            if m > 1:
                clauses.append([-1 * val[days[('Q', 1, m)]], current[m - 1][days[('Q', 0, m - 1)]]])
                clause.append(current[m - 1][days[('S', 1, m - 1)]])
            if m > 2:
                clause.append(current[m - 1][days[('S', 2, m - 1)]])
            clauses.append(clause)
            m += 1

    if police >= 1:
        queues = []
        for turn in range(1, turns):
            queue_lst = []
            for key, value in actions.items():
                # print("value",value)
                queue_lst.append(value[turn][days[('Q', 0, turn)]])
            queues.append(queue_lst)
            queue_lst = [-1 * x for x in queue_lst]
            comb = combinations(queue_lst, 2 + (turn - 1) * police)
            queues += [list(i) for i in comb]

        clauses += queues
    return clauses


def I_treatment(actions, pos_states, info, days, medics):
    # print("days",days)
    rows, columns, turns = [i for i in info]
    clauses = []
    if turns == 1:
        return clauses
    for key, value in actions.items():
        current = actions[key]
        iterval = iter(value)
        next(iterval)  # skip first turn
        m = 1
        for val in iterval:
            clause = []
            clause.append(-1 * val[days['I', None, m]])
            clause.append(current[m - 1][days[('H', None, m - 1)]])
            if m > 1:
                clause.append(current[m - 1][days[('I', None, m - 1)]])
            m += 1

            clauses.append(clause)
    if medics >= 1:
        queues = []
        for turn in range(1, turns):
            I_lst = []
            for key, value in actions.items():
                I_lst.append(value[turn][days[('I', None, turn)]])
            I_lst = [-1 * x for x in I_lst]
            comb = combinations(I_lst, 2 + (turn - 1) * medics)
            queues += [list(i) for i in comb]
        clauses += queues

    return clauses


def H_treatment(actions, pos_states, info, days, police, medics):
    clauses = []
    rows, columns, turns = [i for i in info]
    if turns == 1:
        return clauses

    for key, value in actions.items():
        iterval = iter(value)
        next(iterval)  # skip first turn
        m = 1
        for val in iterval:  # run on days
            clause = []
            clause1 = []
            current = actions[key]
            clause.append(-1 * val[days['H', None, m]])  # if you're healthy, you were healthy or sick2
            clause.append(current[m - 1][days[('H', None, m - 1)]])

            clause1.append(-1 * current[m - 1][days[('H', None, m - 1)]])
            clause1.append(val[days[('H', None, m)]])
            clause1.append(val[days[('S', 0, m)]])
            if m > 2:
                clause.append(current[m - 1][days[('S', 2, m - 1)]])
                if police > 0:
                    clause.append(current[m - 1][days[('Q', 1, m - 1)]])
            if medics > 0:
                clause1.append(val[days[('I', None, m)]])
            m += 1
            clauses.append(clause)
            clauses.append(clause1)

    return clauses


def U_treatment(actions, pos_states, info, days):
    # print("days",days)
    rows, columns, turns = [i for i in info]
    clauses = []
    if turns == 1:
        return clauses
    for key, value in actions.items():
        current = actions[key]
        iterval = iter(value)
        next(iterval)  # skip first turn
        m = 1
        for val in iterval:
            clause = []
            clause1 = []
            clause.append(-1 * current[m - 1][days[('U', None, m - 1)]])
            clause.append(current[m][days[('U', None, m)]])
            clause1.append(current[m - 1][days[('U', None, m - 1)]])
            clause1.append(-1 * current[m][days[('U', None, m)]])
            m += 1

        clauses.append(clause)
        clauses.append(clause1)
    return clauses


def is_nbrs(info, pos):
    up, down, left, right = 0, 0, 0, 0
    rows, columns, turns = [i for i in info]
    i = pos[0]
    j = pos[1]
    if i + 1 < rows:
        down = 1
    if i > 0:
        up = 1
    if j + 1 < columns:
        right = 1
    if j > 0:
        left = 1
    return up, down, left, right


def up(pos):
    return (pos[0] - 1, pos[1])


def down(pos):
    return (pos[0] + 1, pos[1])


def left(pos):
    return (pos[0], pos[1] - 1)


def right(pos):
    return (pos[0], pos[1] + 1)


def Initial(obs_map, actions, info, days):
    clauses = []

    m = 0
    for turn in obs_map:
        i = 0
        for line in turn:
            j = 0
            for var in line:
                if var == '?':
                    j += 1
                    continue

                clause = []
                lst = actions[i, j]
                if var == 'S':
                    clause.append(lst[m][days[var, 0, m]])
                    if m > 0:
                        clause.append(lst[m][days[var, 1, m]])
                    if m > 1:
                        clause.append(lst[m][days[var, 2, m]])
                    clauses.append(clause)

                elif var == 'Q':
                    clause.append(lst[m][days[var, 0, m]])
                    if m > 1:
                        clause.append(lst[m][days[var, 1, m]])
                    clauses.append(clause)

                else:
                    clauses.append([lst[m][days[var, None, m]]])

                j += 1
            i += 1
        m += 1

    return clauses


def query_treatment(query, actions, info, days, kb, g, medics, police):

    query_dict = {}
    for i in kb:
        g.add_clause(i)
    pos = query[0]
    i = pos[0]
    j = pos[1]
    turn = query[1]
    state = query[2]
    if state == 'Q':
        if turn == 0 or police == 0:
            # print('1',query)
            query_dict[query] = 'F'
            return query_dict
    if state == 'I':
        if turn == 0 or medics == 0:
            # print('2',query)
            query_dict[query] = 'F'
            return query_dict

    lst = actions[i, j]
    if state == 'S':
        lst_s = []
        ask = lst[turn][days[state, 0, turn]]
        # ans = solver(kb,ask)
        ans = check(kb, ask)
        lst_s.append(ans)
        if turn > 0:
            # clause.append(lst[turn][days[state,1,turn]])
            ask = lst[turn][days[state, 1, turn]]
            ans = check(kb, ask)
            lst_s.append(ans)
        if turn > 1:
            # clause.append(lst[turn][days[state,2,turn]])
            ask = lst[turn][days[state, 2, turn]]
            ans = check(kb, ask)
            lst_s.append(ans)
        for i in lst_s:
            if i == 'T':
                # print('3',query)
                query_dict[query] = 'T'
                return query_dict
        if '?' in lst_s:
            # print('4',query)
            query_dict[query] = '?'
            return query_dict
        else:
            query_dict[query] = 'F'
            # print('5',query)
            # print('in5',lst_s)
            return query_dict

    elif state == 'Q':
        lst_q = []
        ask = lst[turn][days[state, 0, turn]]
        ans = check(kb, ask)
        lst_q.append(ans)
        # clause.append(lst[turn][days[state,0,turn]])
        if turn > 1:
            ask = lst[turn][days[state, 1, turn]]
            ans = check(kb, ask)
            lst_q.append(ans)
        for i in lst_q:
            if i == 'T':
                # print('6',query)
                query_dict[query] = 'T'
                return query_dict
        if '?' in lst_q:
            # print('7',query)
            query_dict[query] = '?'
            return query_dict
        else:
            # print('8',query)
            query_dict[query] = 'F'
            return query_dict

    else:
        ask = lst[turn][days[state, None, turn]]
        ans = check(kb, ask)
        # print('9',query)
        query_dict[query] = ans
        return query_dict


def solver(kb, ask):
    g = Glucose4()
    g.add_clause([ask])
    for i in kb:
        g.add_clause(i)

    # print("kb",kb,"ask",ask)
    ans = g.solve()
    # print("ans",ans)
    # print("model",g.get_model())
    g.delete()
    return ans


def check(kb, ask):
    ans = solver(kb, ask)
    # print('kb1,ans1',ans,ask,kb)
    if ans == True:
        ask = -1 * ask
        # print('ask',ask)
        ans = solver(kb, ask)
        # print('kb2,ans2',ans,ask,kb)
        if ans == True:
            return '?'
        else:
            return 'T'
    else:
        return 'F'
