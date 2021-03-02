from pysat.card import *
from pysat.solvers import Glucose4
from itertools import combinations
import copy as cp

ids = ['311281190', '203371034']


def solve_problem(input):

    policeNum = input['police']
    medicsNum = input['medics']
    observed_map = input['observations']
    queries = input['queries']
    turnsNum = len(observed_map)
    rowsNum = len(observed_map[0])
    columnsNum = len(observed_map[0][0])
    g = Glucose4()
    queries_dict = {}

    rows_cols_turns = [rowsNum, columnsNum, turnsNum]

    knowledgeBase = []
    actions, pos_states, days = action_treatment(policeNum, medicsNum, rows_cols_turns)
    clauses = only_one_per_position(actions)
    knowledgeBase += clauses
    clauses = S_treatment(actions, rows_cols_turns, days, policeNum)
    knowledgeBase += clauses

    if policeNum > 0:
        clauses = Q_treatment(actions, rows_cols_turns, days, policeNum)
        knowledgeBase += clauses

    if medicsNum > 0:
        clauses = I_treatment(actions, rows_cols_turns, days, medicsNum)
        knowledgeBase += clauses

    clauses = H_treatment(actions, rows_cols_turns, days, policeNum, medicsNum)
    knowledgeBase += clauses

    clauses = U_treatment(actions, rows_cols_turns, days)
    knowledgeBase += clauses

    clauses = infect(actions, rows_cols_turns, days, policeNum)
    knowledgeBase += clauses

    clauses = Initial(observed_map, actions, days)
    knowledgeBase += clauses

    for q in queries:
        query_dict = query_treatment(q, actions, days, knowledgeBase, g, medicsNum, policeNum)
        queries_dict.update(query_dict)

    return queries_dict


def action_treatment(policeNum, medicsNum, rows_cols_turns):
    allPossibleStatesDictID = {('H', None): 0, ('S', 0): 1, ('S', 1): 2, ('S', 2): 3, ('Q', 0): 4, ('Q', 1): 5, ('U', None): 6, ('I', None): 7}
    actions = {}
    rowsNum, columnsNum, turnsNum = [i for i in rows_cols_turns]

    # day zero
    dayZeroIdList = [0, 1, 6]
    dayZeroIdDict = {('H', None, 0): 0, ('S', 0, 0): 1, ('U', None, 0): 2}

    # no police and no medics
    if policeNum == 0 and medicsNum == 0:
        dayOneIdList = [0, 1, 2, 6]
        dayOneIdDict = {('H', None, 1): 0, ('S', 0, 1): 1, ('S', 1, 1): 2, ('U', None, 1): 3}

        dayTwoIdList = [0, 1, 2, 3, 6]
        dayTwoIdDict = {('H', None, 2): 0, ('S', 0, 2): 1, ('S', 1, 2): 2, ('S', 2, 2): 3, ('U', None, 2): 4}

    # only medics
    elif medicsNum > 0 and policeNum == 0 :

        dayOneIdList = [0, 1, 2, 6, 7]
        dayOneIdDict = {('H', None, 1): 0, ('S', 0, 1): 1, ('S', 1, 1): 2, ('U', None, 1): 3, ('I', None, 1): 4}

        dayTwoIdList = [0, 1, 2, 3, 6, 7]
        dayTwoIdDict = {('H', None, 2): 0, ('S', 0, 2): 1, ('S', 1, 2): 2, ('S', 2, 2): 3, ('U', None, 2): 4, ('I', None, 2): 5}

    # only police
    elif policeNum > 0 and medicsNum == 0:

        dayOneIdList = [0, 1, 2, 4, 6]
        dayOneIdDict = {('H', None, 1): 0, ('S', 0, 1): 1, ('S', 1, 1): 2, ('Q', 0, 1): 3, ('U', None, 1): 4}

        dayTwoIdList = [0, 1, 2, 3, 4, 5, 6]
        dayTwoIdDict = {('H', None, 2): 0, ('S', 0, 2): 1, ('S', 1, 2): 2, ('S', 2, 2): 3, ('Q', 0, 2): 4, ('Q', 1, 2): 5, ('U', None, 2): 6}

    # with police and medics
    else:

        dayOneIdList = [0, 1, 2, 4, 6, 7]
        dayOneIdDict = {('H', None, 1): 0, ('S', 0, 1): 1, ('S', 1, 1): 2, ('Q', 0, 1): 3, ('U', None, 1): 4, ('I', None, 1): 5}

        dayTwoIdList = [0, 1, 2, 3, 4, 5, 6, 7]
        dayTwoIdDict = {('H', None, 2): 0, ('S', 0, 2): 1, ('S', 1, 2): 2, ('S', 2, 2): 3, ('Q', 0, 2): 4, ('Q', 1, 2): 5, ('U', None, 2): 6, ('I', None, 2): 7}

    stateId = 1
    for i in range(rowsNum):
        for j in range(columnsNum):
            actionsList = []

            zeroList = []
            for k in range(len(dayZeroIdList)):
                zeroList.append(stateId)
                stateId = stateId + 1
            actionsList.append(zeroList)

            if turnsNum >= 2:
                oneList = []
                for k in range(len(dayOneIdList)):
                    oneList.append(stateId)
                    stateId = stateId + 1
                actionsList.append(oneList)

            if turnsNum >= 3:
                twoList = []
                for k in range(len(dayTwoIdList)):
                    twoList.append(stateId)
                    stateId = stateId + 1

                actionsList.append(twoList)

                for k in range(turnsNum - 3):
                    additionalList = []
                    for kk in range(len(dayTwoIdList)):
                        additionalList.append(stateId)
                        stateId += 1
                    actionsList.append(additionalList)

            actions[(i, j)] = actionsList

    if turnsNum >= 3:
        days = {**dayZeroIdDict, **dayOneIdDict}
        days.update(dayTwoIdDict)
        for t in range(3, turnsNum):
            new_day = make_new_dict(dayTwoIdDict, t)
            days.update(new_day)

    elif turnsNum <= 2:
        days = {**dayZeroIdDict, **dayOneIdDict}

    else:
        days = dayZeroIdDict

    return actions, allPossibleStatesDictID, days


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


def now_before(val, actions, key, state_1, count_1, turn, days, state_2, count_2):
    current = actions[key]
    return [-1 * val[days[state_1, count_1, turn]], current[turn - 1][days[(state_2, count_2, turn - 1)]]]


def now_after(val, actions, key, state_1, count_1, turn, days, state_2, count_2):
    current = actions[key]
    return [val[days[state_1, count_1, turn]], -1 * current[turn - 1][days[(state_2, count_2, turn - 1)]]]


def S_treatment(actions, rows_cols_turns, days, police):
    clauses = []
    rows, columns, turns = [i for i in rows_cols_turns]
    if turns == 1:
        return clauses

    for key, value in actions.items():
        iterVal = iter(value)
        next(iterVal)
        m = 1
        for val in iterVal:
            clause = [-1 * val[days['S', 0, m]]]
            upNeighbor, downNeighbor, leftNeighbor, rightNeighbor = is_neighbor(rows_cols_turns, key)
            if m >= 2:
                clauses.append(now_before(val, actions, key, 'S', 0, m, days, 'H', None))
                clauses.append(now_before(val, actions, key, 'S', 1, m, days, 'S', 0))
                clauses.append(now_before(val, actions, key, 'S', 2, m, days, 'S', 1))

                if police == 0:
                    clauses.append(now_after(val, actions, key, 'S', 1, m, days, 'S', 0))
                    clauses.append(now_after(val, actions, key, 'S', 2, m, days, 'S', 1))
                    if m >= 3:
                        clauses.append(now_after(val, actions, key, 'H', None, m, days, 'S', 2))

            elif m == 1:
                clauses.append(now_before(val, actions, key, 'S', 0, m, days, 'H', None))
                clauses.append(now_before(val, actions, key, 'S', 1, m, days, 'S', 0))
                if police == 0:
                    clauses.append(now_after(val, actions, key, 'S', 1, m, days, 'S', 0))

            if upNeighbor:
                upList = actions[go_up(key)]
                clause.append(upList[m - 1][days[('S', 0, m - 1)]])
                if m > 1:
                    clause.append(upList[m - 1][days[('S', 1, m - 1)]])
                if m > 2:
                    clause.append(upList[m - 1][days[('S', 2, m - 1)]])

            if downNeighbor:
                downList = actions[go_down(key)]
                clause.append(downList[m - 1][days[('S', 0, m - 1)]])
                if m > 1:
                    clause.append(downList[m - 1][days[('S', 1, m - 1)]])
                if m > 2:
                    clause.append(downList[m - 1][days[('S', 2, m - 1)]])

            if leftNeighbor:
                leftList = actions[go_left(key)]
                clause.append(leftList[m - 1][days[('S', 0, m - 1)]])
                if m > 1:
                    clause.append(leftList[m - 1][days[('S', 1, m - 1)]])
                if m > 2:
                    clause.append(leftList[m - 1][days[('S', 2, m - 1)]])

            if rightNeighbor:
                rightList = actions[go_right(key)]
                clause.append(rightList[m - 1][days[('S', 0, m - 1)]])
                if m > 1:
                    clause.append(rightList[m - 1][days[('S', 1, m - 1)]])
                if m > 2:
                    clause.append(rightList[m - 1][days[('S', 2, m - 1)]])

            clauses.append(clause)
            m += 1

    return clauses


def infect(actions, rows_cols_turns, days, police):
    rows, columns, turns = [i for i in rows_cols_turns]
    clauses = []
    if turns == 1:
        return clauses

    for key, value in actions.items():
        up_check, down_check, left_check, right_check = is_neighbor(rows_cols_turns, key)
        m = 0
        for val in value[:-1]:
            if up_check:
                up_lst = actions[go_up(key)]
                clauses += infect_handler(up_lst, m, days, val, police)

            if down_check:
                down_lst = actions[go_down(key)]
                clauses += infect_handler(down_lst, m, days, val, police)

            if left_check:
                left_lst = actions[go_left(key)]
                clauses += infect_handler(left_lst, m, days, val, police)

            if right_check:
                right_lst = actions[go_right(key)]
                clauses += infect_handler(right_lst, m, days, val, police)

            m += 1

    return clauses


def infect_handler(direction, m, days, val, police):
    clauses = []
    if m == 0:
        clauses.append([-1 * val[days['S', 0, m]], -1 * direction[m + 1][days['H', None, m + 1]]])
    elif m == 1:
        clauses.append([-1 * val[days['S', 0, m]], -1 * direction[m + 1][days['H', None, m + 1]]])
        clauses.append([-1 * val[days['S', 1, m]], -1 * direction[m + 1][days['H', None, m + 1]]])
    elif m >= 2:
        if police == 0:
            clauses.append([-1 * val[days['S', 0, m]], -1 * direction[m + 1][days['H', None, m + 1]], direction[m][days['S', 2, m]]])
            clauses.append([-1 * val[days['S', 1, m]], -1 * direction[m + 1][days['H', None, m + 1]], direction[m][days['S', 2, m]]])
            clauses.append([-1 * val[days['S', 2, m]], -1 * direction[m + 1][days['H', None, m + 1]], direction[m][days['S', 2, m]]])
        else:
            clauses.append([-1 * val[days['S', 0, m]], -1 * direction[m + 1][days['H', None, m + 1]], direction[m][days['S', 2, m]], direction[m][days['Q', 1, m]]])
            clauses.append([-1 * val[days['S', 1, m]], -1 * direction[m + 1][days['H', None, m + 1]], direction[m][days['S', 2, m]], direction[m][days['Q', 1, m]]])
            clauses.append([-1 * val[days['S', 2, m]], -1 * direction[m + 1][days['H', None, m + 1]], direction[m][days['S', 2, m]], direction[m][days['Q', 1, m]]])
    return clauses


def Q_treatment(actions, rows_cols_turns, days, police):
    rows, columns, turns = [i for i in rows_cols_turns]
    clauses = []
    if turns == 1:
        return clauses

    for key, value in actions.items():
        current = actions[key]
        iterVal = iter(value)
        next(iterVal)
        m = 1
        for val in iterVal:
            clause = [-1 * val[days[('Q', 0, m)]], current[m - 1][days[('S', 0, m - 1)]]]
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
                queue_lst.append(value[turn][days[('Q', 0, turn)]])
            queues.append(queue_lst)
            queue_lst = [-1 * x for x in queue_lst]
            comb = combinations(queue_lst, 2 + (turn - 1) * police)
            queues += [list(i) for i in comb]

        clauses += queues
    return clauses


def I_treatment(actions, rows_cols_turns, days, medics):
    rows, columns, turns = [i for i in rows_cols_turns]
    clauses = []
    if turns == 1:
        return clauses

    for key, value in actions.items():
        current = actions[key]
        iterVal = iter(value)
        next(iterVal)
        m = 1
        for val in iterVal:
            clause = [-1 * val[days['I', None, m]], current[m - 1][days[('H', None, m - 1)]]]
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


def H_treatment(actions, rows_cols_turns, days, police, medics):
    clauses = []
    rows, columns, turns = [i for i in rows_cols_turns]
    if turns == 1:
        return clauses

    for key, value in actions.items():
        iterVal = iter(value)
        next(iterVal)
        m = 1
        for val in iterVal:
            clause = []
            clause1 = []
            current = actions[key]
            clause.append(-1 * val[days['H', None, m]])
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


def U_treatment(actions, rows_cols_turns, days):
    rows, columns, turns = [i for i in rows_cols_turns]
    clauses = []
    if turns == 1:
        return clauses

    for key, value in actions.items():
        current = actions[key]
        iterVal = iter(value)
        next(iterVal)
        m = 1
        for val in iterVal:
            clause = []
            clause1 = []
            clause.append(-1 * current[m - 1][days[('U', None, m - 1)]])
            clause.append(current[m][days[('U', None, m)]])
            clause1.append(current[m - 1][days[('U', None, m - 1)]])
            clause1.append(-1 * current[m][days[('U', None, m)]])
            m += 1

        clauses.append(clause)
        clauses.append(clause1)

    for key, value in actions.items():
        nextAction = actions[key]
    actionT = [nextAction]

    return clauses


def is_neighbor(rows_cols_turns, pos):
    up, down, left, right = 0, 0, 0, 0
    rows, columns, turns = [i for i in rows_cols_turns]
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


def go_up(pos):
    return pos[0] - 1, pos[1]


def go_down(pos):
    return pos[0] + 1, pos[1]


def go_left(pos):
    return pos[0], pos[1] - 1


def go_right(pos):
    return pos[0], pos[1] + 1


def Initial(observed_map, actions, days):
    clauses = []

    m = 0
    for turn in observed_map:
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
                    if m >= 1:
                        clause.append(lst[m][days[var, 1, m]])
                    if m >= 2:
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


def query_treatment(query, actions, days, knowledgeBase, g, medics, police):

    query_dict = {}
    for i in knowledgeBase:
        g.add_clause(i)
    pos = query[0]
    i = pos[0]
    j = pos[1]
    turn = query[1]
    state = query[2]
    if state == 'Q':
        if turn == 0 or police == 0:
            query_dict[query] = 'F'
            return query_dict
    if state == 'I':
        if turn == 0 or medics == 0:
            query_dict[query] = 'F'
            return query_dict

    lst = actions[i, j]
    if state == 'S':
        lst_s = []
        ask = lst[turn][days[state, 0, turn]]
        ans = check(knowledgeBase, ask)
        lst_s.append(ans)
        if turn > 0:
            ask = lst[turn][days[state, 1, turn]]
            ans = check(knowledgeBase, ask)
            lst_s.append(ans)
        if turn > 1:
            ask = lst[turn][days[state, 2, turn]]
            ans = check(knowledgeBase, ask)
            lst_s.append(ans)
        for i in lst_s:
            if i == 'T':
                query_dict[query] = 'T'
                return query_dict
        if '?' in lst_s:
            query_dict[query] = '?'
            return query_dict
        else:
            query_dict[query] = 'F'
            return query_dict

    elif state == 'Q':
        lst_q = []
        ask = lst[turn][days[state, 0, turn]]
        ans = check(knowledgeBase, ask)
        lst_q.append(ans)
        if turn > 1:
            ask = lst[turn][days[state, 1, turn]]
            ans = check(knowledgeBase, ask)
            lst_q.append(ans)
        for i in lst_q:
            if i == 'T':
                query_dict[query] = 'T'
                return query_dict
        if '?' in lst_q:
            query_dict[query] = '?'
            return query_dict
        else:
            query_dict[query] = 'F'
            return query_dict

    else:
        ask = lst[turn][days[state, None, turn]]
        ans = check(knowledgeBase, ask)
        query_dict[query] = ans
        return query_dict


def solver(knowledgeBase, ask):
    g = Glucose4()
    g.add_clause([ask])
    for i in knowledgeBase:
        g.add_clause(i)

    ans = g.solve()
    g.delete()
    return ans


def check(knowledgeBase, ask):
    ans = solver(knowledgeBase, ask)
    if ans:
        ask = -1 * ask
        ans = solver(knowledgeBase, ask)
        if ans:
            return '?'
        else:
            return 'T'
    else:
        return 'F'
