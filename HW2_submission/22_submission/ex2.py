import pysat
from pysat.solvers import Glucose3, Solver
import sympy
import re
import copy

ids = ['311127245', '315816157']


def symbol_to_int(num_of_observations, row_num, col_num, possible_states):
    symb_dict = {}
    counter = 1
    for i in range(row_num):
        for j in range(col_num):
            symb = '{}_{}_'.format(i,j)
            for n in range(num_of_observations):
                symb_n = symb + str(n) + '_'
                for s in possible_states:
                    symb_s = symb_n + s
                    symb_dict[symb_s] = counter
                    counter += 1
    return symb_dict


# symbol: row_col_obsNum_state
# KB : transforms the observations we receive into knowledge base.
def KB(observations,possible_states):
    # kb : list of strings defining states in observations
    kb = []
    kb_not = []
    # undefined : list of unknown states defined by strings of row_col_obsNum
    undefined = []
    # U : list of tuples (row,col) where there is U, at any observation
    U = []
    for item in enumerate(observations):
        obsNum = item[0]
        obs = item[1]
        for i in range(len(obs)):
            for j in range(len(obs[0])):
                state = obs[i][j]
                if state == '?':
                    undefined.append('{}_{}_{}'.format(i, j, obsNum))
                else:
                    kb.append('{}_{}_{}_{}'.format(i, j, obsNum, state))
                    for s in possible_states:
                        if s != state:
                            kb_not.append('~{}_{}_{}_{}'.format(i, j, obsNum, s))
                    if state == 'U':
                        U.append((i, j))
    kb_symbols = 1
    # transform strings to symbols
    # kb_symbols : expression of all strings in KB with & operator between them
    for symbol in kb:
        symbol = sympy.symbols(symbol)
        kb_symbols = sympy.And(kb_symbols, symbol)
    for symbol_n in kb_not:
        symbol_n = symbol_n[1:]
        symbol_n = sympy.symbols(symbol_n)
        kb_symbols = sympy.And(kb_symbols, ~symbol_n)
    return kb_symbols, undefined, U, kb, kb_not


# update_U : checks if there are places in any observation known to be U. If so, update all needed undefined places.
# updates kb_symbols and undefined, and returns a new list of data_q
def update_U(kb_symbols, undefined, U, possible_states, kb, data_q):
    # data_q : a list containing strings of row_col_obsNum_state there were changed during running
    U_set = set(U)
    del_U = []
    for place in U_set:
        i, j = place
        pattern = '{}_{}_*'.format(i, j)
        for state in undefined:
            # check if there is an undefined place in any observation, which is certainly Unpopulated
            # (if we know it is U at nay time, it is certainly U at all times)
            if re.match(pattern, state):
                new_symbol = state + '_U'
                data_q.append(new_symbol)
                kb.append(new_symbol)
                new_symbol = sympy.symbols(new_symbol)
                # add the new known state to KB
                kb_symbols = sympy.And(kb_symbols, new_symbol)
                del_U.append(state)
                for p in possible_states:
                    if p != 'U':
                        not_symbol = state + '_' + p
                        data_q.append('~' + not_symbol)
                        not_symbol = sympy.symbols(not_symbol)
                        kb_symbols = sympy.And(kb_symbols, ~not_symbol)
    undefined = [ele for ele in undefined if ele not in del_U]
    for und in undefined:
        row, col, obsNum = und.split(sep='_')
        row, col, obsNum = int(row), int(col), int(obsNum)
        pattern = '{}_{}_*'.format(row, col)
        for defined in kb:
            if re.match(pattern, defined):
                symbol = '{}_{}_{}_U'.format(row, col, obsNum)
                data_q.append('~' + symbol)
                symbol = sympy.symbols(symbol)
                kb_symbols = sympy.And(kb_symbols, ~symbol)
                break
    return kb_symbols, undefined


def update_I(kb, kb_symbols, data_q, undefined, possible_states):
    del_I = []
    for place in kb:
        i, j, n, s = place.split(sep='_')
        if s == 'I':
            i, j, n = int(i), int(j), int(n)
            pattern = '{}_{}_*'.format(i, j)
            for state in undefined:
                if re.match(pattern, state):
                    i_s, j_s, n_s = state.split(sep='_')
                    if int(n_s) > n:
                        del_I.append(state)
                        new_symbol = state + '_I'
                        data_q.append(new_symbol)
                        kb.append(new_symbol)
                        new_symbol = sympy.symbols(new_symbol)
                        kb_symbols = sympy.And(kb_symbols, new_symbol)
                        for p in possible_states:
                            if p != 'I':
                                not_symbol = state + '_' + p
                                data_q.append('~' + not_symbol)
                                not_symbol = sympy.symbols(not_symbol)
                                kb_symbols = sympy.And(kb_symbols, ~not_symbol)
    undefined = [ele for ele in undefined if ele not in del_I]
    return kb_symbols, undefined


def not_Q(kb, kb_symbols, data_q, undefined, police_num, num_of_observations):
    Q_changes = [0]*num_of_observations
    Q_total = [0]*num_of_observations
    for item in kb:
        row, col, obsNum, state = item.split(sep='_')
        obsNum = int(obsNum)
        if state == 'Q':
            Q_total[obsNum] += 1
            if '{}_{}_{}_S'.format(row, col, obsNum - 1) in kb:
                Q_changes[obsNum] += 1
    for item2 in undefined:
        row, col, obsNum = item2.split(sep='_')
        obsNum = int(obsNum)
        prev_Q = '{}_{}_{}_Q'.format(row, col, obsNum-1)
        if (obsNum == 0 or Q_changes[obsNum] == police_num or (Q_total[obsNum] == police_num and obsNum == 1) or (Q_total[obsNum] == 2*police_num and obsNum > 1)) and prev_Q not in kb:
            notq = item2 + '_Q'
            data_q.append('~' + notq)
            notq = sympy.symbols(notq)
            kb_symbols = sympy.And(kb_symbols, ~notq)
    return kb_symbols


def expr_defined_by_limit(func, row_num, col_num, state, obsNum_finite, expr, row, col, NOT, SECOND=False, state2='A', NOT2=False, obsNum_finite2 = 0):
    if row > 0:
        c = '{}_{}_{}_{}'.format(row - 1, col, obsNum_finite, state)
        c = sympy.symbols(c)
        if NOT:
            c = ~c
        if SECOND:
            c2 = '{}_{}_{}_{}'.format(row - 1, col, obsNum_finite2, state2)
            c2 = sympy.symbols(c2)
            if NOT2:
                c2 = ~c2
            c = sympy.And(c,c2)
        expr = func(expr, c)
    if row < row_num - 1:
        c = '{}_{}_{}_{}'.format(row + 1, col, obsNum_finite, state)
        c = sympy.symbols(c)
        if NOT:
            c = ~c
        if SECOND:
            c2 = '{}_{}_{}_{}'.format(row + 1, col, obsNum_finite2, state2)
            c2 = sympy.symbols(c2)
            if NOT2:
                c2 = ~c2
            c = sympy.And(c,c2)
        expr = func(expr, c)
    if col > 0:
        c = '{}_{}_{}_{}'.format(row, col - 1, obsNum_finite, state)
        c = sympy.symbols(c)
        if NOT:
            c = ~c
        if SECOND:
            c2 = '{}_{}_{}_{}'.format(row, col - 1, obsNum_finite2, state2)
            c2 = sympy.symbols(c2)
            if NOT2:
                c2 = ~c2
            c = sympy.And(c,c2)
        expr = func(expr, c)
    if col < col_num - 1:
        c = '{}_{}_{}_{}'.format(row, col + 1, obsNum_finite, state)
        c = sympy.symbols(c)
        if NOT:
            c = ~c
        if SECOND:
            c2 = '{}_{}_{}_{}'.format(row, col + 1, obsNum_finite2, state2)
            c2 = sympy.symbols(c2)
            if NOT2:
                c2 = ~c2
            c = sympy.And(c, c2)
        expr = func(expr, c)
    return expr


def spreader(kb_symbols, undefined, kb, row_num, col_num, data_q, possible_states, police_num):
    undefined_sort = sorted(undefined)
    for u in range(len(undefined_sort)-1):
        i, j, n = undefined_sort[u].split(sep='_')
        i, j, n = int(i), int(j), int(n)
        pattern = '{}_{}_{}'.format(i, j, n+1)
        if undefined_sort[u+1] == pattern:
            infected_by_u = False
            if i > 0:
                infected_by_u = neigh_by_neigh(kb, i-1, j, n + 1, 'down', police_num, row_num, col_num, undefined)
            if not infected_by_u and i < row_num - 1:
                infected_by_u = neigh_by_neigh(kb, i+1, j, n + 1, 'up', police_num, row_num, col_num, undefined)
            if not infected_by_u and j > 0:
                infected_by_u = neigh_by_neigh(kb, i, j-1, n + 1, 'left', police_num, row_num, col_num, undefined)
            if not infected_by_u and j < col_num - 1:
                infected_by_u = neigh_by_neigh(kb, i, j + 1, n + 1, 'right', police_num, row_num, col_num, undefined)
            if infected_by_u:
                symbol = undefined_sort[u] + '_S'
                undefined.remove(undefined_sort[u])
                data_q.append(symbol)
                kb.append(symbol)
                symbol = sympy.symbols(symbol)
                kb_symbols = sympy.And(kb_symbols, symbol)
                if police_num > 0:
                    notq = undefined_sort[u+1] + '_Q'
                    data_q.append('~' + notq)
                    notq = sympy.symbols(notq)
                    kb_symbols = sympy.And(kb_symbols, ~notq)
                for p in possible_states:
                    if p != 'S':
                        not_symbol = undefined_sort[u] + '_' + p
                        data_q.append('~' + not_symbol)
                        not_symbol = sympy.symbols(not_symbol)
                        kb_symbols = sympy.And(kb_symbols, ~not_symbol)
    return kb_symbols


def neigh_by_neigh(kb, i_n, j_n, n, flag, police_num, row_num, col_num, undefined):
    neigh_is_H = '{}_{}_{}_H'.format(i_n, j_n, n - 1)
    neigh_will_be_S = '{}_{}_{}_S'.format(i_n, j_n, n)
    infected_by_u = False
    if neigh_is_H in kb:
        if neigh_will_be_S in kb:
            neigh_infected_by_neigh = False
            if i_n > 0 and flag != 'up':
                neigh_neigh = '{}_{}_{}_S'.format(i_n - 1, j_n, n - 1)
                un_neigh_neigh = '{}_{}_{}'.format(i_n - 1, j_n, n - 1)
                if police_num > 0:
                    neigh_neigh_next = '{}_{}_{}_Q'.format(i_n - 1, j_n, n)
                    if (neigh_neigh in kb and neigh_neigh_next not in kb) or un_neigh_neigh in undefined:
                        neigh_infected_by_neigh = True
                elif neigh_neigh in kb or un_neigh_neigh in undefined:
                    neigh_infected_by_neigh = True
            if i_n < row_num - 1 and flag != 'down':
                neigh_neigh = '{}_{}_{}_S'.format(i_n + 1, j_n, n - 1)
                un_neigh_neigh = '{}_{}_{}'.format(i_n + 1, j_n, n - 1)
                if police_num > 0:
                    neigh_neigh_next = '{}_{}_{}_Q'.format(i_n + 1, j_n, n)
                    if (neigh_neigh in kb and neigh_neigh_next not in kb) or un_neigh_neigh in undefined:
                        neigh_infected_by_neigh = True
                elif neigh_neigh in kb or un_neigh_neigh in undefined:
                    neigh_infected_by_neigh = True
            if j_n > 0 and flag != 'right':
                neigh_neigh = '{}_{}_{}_S'.format(i_n, j_n - 1, n - 1)
                un_neigh_neigh = '{}_{}_{}'.format(i_n, j_n - 1, n - 1)
                if police_num > 0:
                    neigh_neigh_next = '{}_{}_{}_Q'.format(i_n, j_n - 1, n)
                    if (neigh_neigh in kb and neigh_neigh_next not in kb) or un_neigh_neigh in undefined:
                        neigh_infected_by_neigh = True
                elif neigh_neigh in kb or un_neigh_neigh in undefined:
                    neigh_infected_by_neigh = True
            if j_n < col_num - 1 and flag != 'left':
                neigh_neigh = '{}_{}_{}_S'.format(i_n, j_n + 1, n - 1)
                un_neigh_neigh = '{}_{}_{}'.format(i_n, j_n + 1, n - 1)
                if police_num > 0:
                    neigh_neigh_next = '{}_{}_{}_Q'.format(i_n, j_n + 1, n)
                    if (neigh_neigh in kb and neigh_neigh_next not in kb) or un_neigh_neigh in undefined:
                        neigh_infected_by_neigh = True
                elif neigh_neigh in kb or un_neigh_neigh in undefined:
                    neigh_infected_by_neigh = True
            if not neigh_infected_by_neigh:
                infected_by_u = True
    return infected_by_u


# in current round
def quarantine(kb, kb_symbols, data_q, undefined, police_num, num_of_observations, possible_states):
    Q_changes = [0] * num_of_observations # for each obs count the number on new Q
    S_to_undefined = {k: [] for k in range(num_of_observations)} # for each obs count the number of s to undefined
    S_count = [0] * num_of_observations
    H_to_S = [0] * num_of_observations
    undefined_current = {k: [] for k in range(num_of_observations)} #undefined in round
    undefined_count = [0] * num_of_observations #undefined stay undefined
    for item in kb:
        row, col, obsNum, state = item.split(sep='_')
        obsNum = int(obsNum)
        if state == 'Q' and '{}_{}_{}_S'.format(row, col, obsNum - 1) in kb:
            Q_changes[obsNum] += 1
        if state == 'S':
            S_count[obsNum] += 1
            if '{}_{}_{}'.format(row, col, obsNum + 1) in undefined:
                S_to_undefined[obsNum + 1].append((row, col))
            if '{}_{}_{}_H'.format(row, col, obsNum - 1) in kb:
                H_to_S[obsNum - 1] += 1 #the H in round obsNum-1 became S in the next round
    for item1 in undefined:
        row, col, obsNum = item1.split(sep='_')
        obsNum = int(obsNum)
        undefined_current[obsNum].append((row,col))
        if '{}_{}_{}'.format(row, col, obsNum + 1) in undefined:
            undefined_count[obsNum + 1] += 1

    for i in range(1,num_of_observations):
        if len(S_to_undefined[i]) + undefined_count[i] <= (police_num - Q_changes[i]):
            for row,col in S_to_undefined[i]:
                symbol = '{}_{}_{}_Q'.format(row, col, i)
                data_q.append(symbol)
                kb.append(symbol)
                undefined.remove('{}_{}_{}'.format(row, col, i))
                symbol = sympy.symbols(symbol)
                kb_symbols = sympy.And(kb_symbols, symbol)
                for p in possible_states:
                    if p != 'Q':
                        not_symbol = '{}_{}_{}_{}'.format(row, col, i, p)
                        data_q.append('~' + not_symbol)
                        not_symbol = sympy.symbols(not_symbol)
                        kb_symbols = sympy.And(kb_symbols, ~not_symbol)
    for i in range(num_of_observations):
        if S_count[i] + len(undefined_current[i]) == police_num + 1 and H_to_S[i]:
            for row,col in undefined_current[i]:
                new_s = '{}_{}_{}'.format(row, col, i)
                undefined.remove(new_s)
                new_s = new_s +'_S'
                data_q.append(new_s)
                kb.append(new_s)
                new_s = sympy.symbols(new_s)
                kb_symbols = sympy.And(kb_symbols, new_s)
                for p in possible_states:
                    if p != 'S':
                        not_symbol = '{}_{}_{}_{}'.format(row, col, i, p)
                        data_q.append('~' + not_symbol)
                        not_symbol = sympy.symbols(not_symbol)
                        kb_symbols = sympy.And(kb_symbols, ~not_symbol)
        if S_count[i] + len(undefined_current[i]) <= police_num:
            if i < num_of_observations - 1:
                for row, col in undefined_current[i+1]:
                    new_s = '{}_{}_{}_S'.format(row, col, i+1)
                    data_q.append('~' + new_s)
                    new_s = sympy.symbols(new_s)
                    kb_symbols = sympy.And(kb_symbols, ~new_s)
    return kb_symbols


def not_I(kb, kb_symbols, data_q, undefined):
    for und in undefined:
        row, col, obsNum = und.split(sep='_')
        row, col, obsNum = int(row), int(col), int(obsNum)
        pattern = '{}_{}_*'.format(row, col)
        if obsNum == 0:
            symbol = '{}_{}_0_I'.format(row, col)
            data_q.append('~' + symbol)
            symbol = sympy.symbols(symbol)
            kb_symbols = sympy.And(kb_symbols, ~symbol)
            continue
        for defined in kb:
            if re.match(pattern, defined):
                row1, col1, obsNum1, state1 = defined.split(sep='_')
                if (int(obsNum1) == obsNum-1 and (state1 == 'S' or state1 == 'Q')) or (int(obsNum1) > obsNum and state1 != 'I'):
                    symbol = '{}_{}_{}_I'.format(row, col, obsNum)
                    data_q.append('~' + symbol)
                    symbol =sympy.symbols(symbol)
                    kb_symbols = sympy.And(kb_symbols, ~symbol)
                    break
    return kb_symbols


def vaccine(kb, kb_symbols, data_q, undefined, medic_num, num_of_observations, possible_states):
    I_changes = [0] * num_of_observations # for each obs count the number on new I
    H_to_undefined = {k: [] for k in range(num_of_observations)} # for each obs count the number of h to undrfinrd
    H_count = [0] * num_of_observations
    undefined_count = [0] * num_of_observations
    undefined_current = {k: [] for k in range(num_of_observations)}
    for item in kb:
        row, col, obsNum, state = item.split(sep='_')
        obsNum = int(obsNum)
        if state == 'I' and '{}_{}_{}_H'.format(row, col, obsNum - 1) in kb:
            I_changes[obsNum] += 1
        if state == 'H':
            H_count[obsNum] += 1
            if '{}_{}_{}'.format(row, col, obsNum + 1) in undefined:
                H_to_undefined[obsNum + 1].append((row, col))
    for item1 in undefined:
        row, col, obsNum = item1.split(sep='_')
        obsNum = int(obsNum)
        undefined_current[obsNum].append((row,col))
        if '{}_{}_{}'.format(row, col, obsNum + 1) in undefined:
            undefined_count[obsNum + 1] += 1

    for i in range(1,num_of_observations):
        if len(H_to_undefined[i]) + undefined_count[i] <= (medic_num - I_changes[i]):
            for row, col in H_to_undefined[i]:
                symbol = '{}_{}_{}_I'.format(row, col, i)
                data_q.append(symbol)
                kb.append(symbol)
                undefined.remove('{}_{}_{}'.format(row, col, i))
                symbol = sympy.symbols(symbol)
                kb_symbols = sympy.And(kb_symbols, symbol)
                for p in possible_states:
                    if p != 'I':
                        not_symbol = '{}_{}_{}_{}'.format(row, col, i, p)
                        data_q.append('~' + not_symbol)
                        not_symbol = sympy.symbols(not_symbol)
                        kb_symbols = sympy.And(kb_symbols,~not_symbol)
    for i in range(num_of_observations):
        if H_count[i] + len((undefined_current[i])) <= medic_num:
            if i < num_of_observations - 1:
                for row, col in undefined_current[i+1]:
                    new_H = '{}_{}_{}_H'.format(row, col, i+1)
                    data_q.append('~' + new_H)
                    new_H = sympy.symbols(new_H)
                    kb_symbols = sympy.And(kb_symbols, ~new_H)
        if I_changes[i] == medic_num:
            for row, col in undefined_current[i]:
                new_I = '{}_{}_{}_I'.format(row, col, i)
                data_q.append('~' + new_I)
                new_I = sympy.symbols(new_I)
                kb_symbols = sympy.And(kb_symbols, ~new_I)

    return kb_symbols


def is_S(undefined_state, row_num, col_num, num_of_observations):
    row, col, obsNum = undefined_state.split(sep='_')
    row, col, obsNum = int(row), int(col), int(obsNum)
    expr0, expr1, expr2, expr3, expr = 1, 1, 1, 0, 0
    # if at this turn all of my neighbors are not sick and at the next turn im sick, im certainly sick at this turn.
    if obsNum < num_of_observations - 1:
        c0 = '{}_{}_{}_S'.format(row, col, obsNum+1)
        c0 = sympy.symbols(c0)
        expr0 = expr_defined_by_limit(sympy.And, row_num, col_num, 'S', obsNum, expr0, row, col, True)
        expr0 = sympy.And(c0, expr0)
        expr = sympy.Or(expr, expr0)
    if obsNum > 0:
        # checks of number of turns i was sick
        c = '{}_{}_{}_S'.format(row, col, obsNum-1)
        c = sympy.symbols(c)
        expr1 = sympy.And(expr1, c)
        expr2 = sympy.And(expr2, c)
        if obsNum > 1:
            c1 = '{}_{}_{}_S'.format(row, col, obsNum-2)
            c1 = sympy.symbols(c1)
            expr2 = sympy.And(expr2, c1)
            expr1 = sympy.And(expr1, ~c1)
            if obsNum > 2:
                c2 = '{}_{}_{}_S'.format(row, col, obsNum - 3)
                c2 = sympy.symbols(c2)
                expr2 = sympy.And(expr2, ~c2)
        expr3 = expr_defined_by_limit(sympy.Or, row_num, col_num, 'S', obsNum-1, expr3, row, col, False)
        c3 = '{}_{}_{}_H'.format(row, col, obsNum - 1)
        c3 = sympy.symbols(c3)
        expr3 = sympy.And(expr3, c3)
        expr = sympy.Or(expr1, expr2, expr3)
    return expr


def is_S_with_police(undefined_state, row_num, col_num, num_of_observations):
    row, col, obsNum = undefined_state.split(sep='_')
    row, col, obsNum = int(row), int(col), int(obsNum)
    expr1, expr2 = 0, 0
    if obsNum + 2 < num_of_observations:
        temp1 = '{}_{}_{}_Q'.format(row, col, obsNum + 1)
        temp1 = sympy.symbols(temp1)
        temp2 = '{}_{}_{}_Q'.format(row, col, obsNum + 2)
        temp2 = sympy.symbols(temp2)
        expr1 = sympy.And(temp1, temp2)
    if obsNum > 0:
        temp = '{}_{}_{}_H'.format(row, col, obsNum - 1)
        temp = sympy.symbols(temp)
        expr2 = expr_defined_by_limit(sympy.Or, row_num, col_num, 'S', obsNum - 1, expr2, row, col, False, SECOND=True,
                                      state2='Q', NOT2=True, obsNum_finite2=obsNum)
        expr2 = sympy.And(expr2, temp)
    return sympy.Or(expr1, expr2)



def is_H(undefined_state, row_num, col_num, police_num, medic_num, num_of_observations):
    row, col, obsNum = undefined_state.split(sep='_')
    row, col, obsNum = int(row), int(col), int(obsNum)
    if obsNum == 0:
        expr = '{}_{}_{}_H'.format(row, col, obsNum + 1)
        expr = sympy.symbols(expr)
        if medic_num > 0:
            temp = '{}_{}_{}_I'.format(row, col, obsNum + 1)
            temp = sympy.symbols(temp)
            expr = sympy.Or(expr, temp)
        return expr
    else:
        expr1, expr2, expr3, expr4, expr5 = 0, 0, 0, 0, 0
        if obsNum >= 3:
            expr1 = '{}_{}_{}_S'.format(row, col, obsNum - 3)
            expr1 = sympy.symbols(expr1)
            temp = '{}_{}_{}_S'.format(row, col, obsNum - 2)
            temp = sympy.symbols(temp)
            expr1 = sympy.And(expr1, temp)
            temp1 = '{}_{}_{}_S'.format(row, col, obsNum - 1)
            temp1 = sympy.symbols(temp1)
            expr1 = sympy.And(expr1, temp1)
        if medic_num > 0 and obsNum + 1 < num_of_observations:
            expr2 = '{}_{}_{}_I'.format(row, col, obsNum + 1)
            expr2 = sympy.symbols(expr2)
            temp = '{}_{}_{}_S'.format(row, col, obsNum - 1)
            temp = sympy.symbols(temp)
            if police_num > 0:
                temp1 = '{}_{}_{}_Q'.format(row, col, obsNum - 1)
                temp1 = sympy.symbols(temp1)
                temp = sympy.Or(temp, temp1)
            expr2 = sympy.And(expr2, temp)
        if medic_num == 0:
            expr3 = '{}_{}_{}_H'.format(row, col, obsNum - 1)
            expr3 = sympy.symbols(expr3)
            expr3 = expr_defined_by_limit(sympy.And, row_num, col_num, 'S', obsNum - 1, expr3, row, col, True)
        if police_num > 0:
            if obsNum > 2:
                expr4 = '{}_{}_{}_Q'.format(row, col, obsNum - 1)
                expr4 = sympy.symbols(expr4)
                temp = '{}_{}_{}_Q'.format(row, col, obsNum - 2)
                temp = sympy.symbols(temp)
                expr4 = sympy.And(expr4, temp)
                expr5 = '{}_{}_{}_Q'.format(row, col, obsNum - 3)
                expr5 = sympy.symbols(expr5)
                expr5 = sympy.And(~expr5, temp)
        expr = sympy.Or(expr5, expr4, expr3, expr2, expr1)
        return expr


def is_Q(undefined_state, num_of_observations, row_num, col_num):
    row, col, obsNum = undefined_state.split(sep='_')
    row, col, obsNum = int(row), int(col), int(obsNum)
    expr1, expr2, expr3 = 0, 0, 0
    if obsNum > 1:
        temp1 = '{}_{}_{}_Q'.format(row, col, obsNum - 2)
        temp1 = sympy.symbols(temp1)
        temp2 = '{}_{}_{}_Q'.format(row, col, obsNum - 1)
        temp2 = sympy.symbols(temp2)
        expr1 = sympy.And(~temp1, temp2)
    if obsNum + 2 < num_of_observations:
        temp1 = '{}_{}_{}_Q'.format(row, col, obsNum + 1)
        temp1 = sympy.symbols(temp1)
        temp2 = '{}_{}_{}_H'.format(row, col, obsNum + 2)
        temp2 = sympy.symbols(temp2)
        expr2 = sympy.And(temp1, temp2)
    if obsNum > 0:
        temp1 = '{}_{}_{}_S'.format(row, col, obsNum - 1)
        temp1 = sympy.symbols(temp1)
        expr3 = expr_defined_by_limit(sympy.Or, row_num, col_num, 'H', obsNum - 1, expr3, row, col, False, SECOND=True,
                                      state2='H', NOT2=False, obsNum_finite2=obsNum)
        expr3 = sympy.And(expr3, temp1)
        expr3 = sympy.simplify(expr3)
    return sympy.Or(expr1, expr2, expr3)


def one_obs(queries):
    answer = {}
    for quer in queries[0]:
        place, number, s = quer
        if s in ['H', 'U', 'S']:
            answer[quer] = '?'
        else:
            answer[quer] = 'F'
    return answer


def solve_problem_no_teams(kb, kb_symbols, data_q, undefined, queries, num_of_observations, row_num, col_num, possible_states):
    answer = {}
    change = True
    police_num, medic_num= 0, 0
    kb_symbols = spreader(kb_symbols, undefined, kb, row_num, col_num, data_q, possible_states, police_num)
    while change:
        undefined_copy = undefined.copy()
        undefined_copy.reverse()
        for und in undefined_copy:
            isS = is_S(und, row_num, col_num, num_of_observations)
            kb_S = sympy.And(~isS, kb_symbols)
            kb_S_cnf = sympy.to_cnf(kb_S)
            res = sympy.satisfiable(kb_S_cnf)
            if not res:
                new_S = und + '_S'
                data_q.append(new_S)
                kb.append(new_S)
                undefined.remove(und)
                new_S = sympy.symbols(new_S)
                kb_symbols = sympy.And(kb_symbols, new_S)
                no_H = und + '_H'
                data_q.append('~' + no_H)
                no_H = sympy.symbols(no_H)
                kb_symbols = sympy.And(kb_symbols, ~no_H)
                no_U = und + '_U'
                if '~' + no_U not in data_q:
                    data_q.append('~' + no_U)
                    no_U = sympy.symbols(no_U)
                    kb_symbols = sympy.And(kb_symbols, ~no_U)
            else:
                isH = is_H(und, row_num, col_num, police_num, medic_num, num_of_observations)
                kb_H = sympy.And(~isH, kb_symbols)
                kb_H_cnf = sympy.to_cnf(kb_H)
                res = sympy.satisfiable(kb_H_cnf)
                if not res:
                    new_H = und + '_H'
                    data_q.append(new_H)
                    kb.append(new_H)
                    undefined.remove(und)
                    new_H = sympy.symbols(new_H)
                    kb_symbols = sympy.And(kb_symbols, new_H)
                    no_S = und + '_S'
                    data_q.append('~' + no_S)
                    no_S = sympy.symbols(no_S)
                    kb_symbols = sympy.And(kb_symbols, ~no_S)
                    no_U = und + '_U'
                    if '~' + no_U not in data_q:
                        data_q.append('~' + no_U)
                        no_U = sympy.symbols(no_U)
                        kb_symbols = sympy.And(kb_symbols, ~no_U)
        kb_symbols = spreader(kb_symbols, undefined, kb, row_num, col_num, data_q, possible_states, police_num)
        if set(undefined_copy) == set(undefined):
            change = False
    for quer in queries:
        place, number, s = quer
        i, j = place
        q = '{}_{}_{}_{}'.format(i, j, number, s)
        if q in data_q:
            answer[quer] = 'T'
        elif '~' + q in data_q:
            answer[quer] = 'F'
        else:
            answer[quer] = '?'
    return answer


def not_H(kb, kb_symbols, data_q, undefined):
    for und in undefined:
        row, col, obsNum = und.split(sep='_')
        row, col, obsNum = int(row), int(col), int(obsNum)
        if obsNum == 1:
            state_k1 = '{}_{}_{}_S'.format(row, col, obsNum - 1)
            if state_k1 in kb:
                state_k = '{}_{}_{}_H'.format(row,col, obsNum)
                data_q.append('~' + state_k)
                state_k = sympy.symbols(state_k)
                kb_symbols = sympy.And(kb_symbols, ~state_k)
        if obsNum > 1:
            state_k2 = '{}_{}_{}_H'.format(row,col, obsNum-2)
            state_k1 = '{}_{}_{}_S'.format(row,col, obsNum -1)
            if state_k1 in kb and state_k2 in kb:
                state_k = '{}_{}_{}_H'.format(row,col, obsNum)
                data_q.append('~' + state_k)
                state_k = sympy.symbols(state_k)
                kb_symbols = sympy.And(kb_symbols, ~state_k)
            if obsNum == 2:
                state_k2 = '{}_{}_{}_S'.format(row, col, obsNum - 2)
                state_k1 = '{}_{}_{}_S'.format(row, col, obsNum - 1)
                if state_k1 in kb and state_k2 in kb:
                    state_k = '{}_{}_{}_H'.format(row, col, obsNum)
                    data_q.append('~' + state_k)
                    state_k = sympy.symbols(state_k)
                    kb_symbols = sympy.And(kb_symbols, ~state_k)
            if obsNum > 2:
                state_k3 = '{}_{}_{}_H'.format(row,col, obsNum-3)
                state_k2 = '{}_{}_{}_S'.format(row,col, obsNum -2)
                state_k1 = '{}_{}_{}_S'.format(row, col, obsNum - 1)
                if state_k1 in kb and state_k2 in kb and state_k3 in kb:
                    state_k = '{}_{}_{}_H'.format(row, col, obsNum)
                    data_q.append('~' + state_k)
                    state_k = sympy.symbols(state_k)
                    kb_symbols = sympy.And(kb_symbols, ~state_k)
        if ('{}_{}_{}_S'.format(row - 1, col, obsNum) in kb and '{}_{}_{}_S'.format(row - 1, col, obsNum - 1) in kb) \
                or ('{}_{}_{}_S'.format(row + 1, col, obsNum) in kb and '{}_{}_{}_S'.format(row + 1, col, obsNum - 1) in kb) \
                or ('{}_{}_{}_S'.format(row, col - 1, obsNum) in kb and '{}_{}_{}_S'.format(row, col - 1, obsNum - 1) in kb) \
                or ('{}_{}_{}_S'.format(row, col + 1, obsNum) in kb and '{}_{}_{}_S'.format(row, col + 1, obsNum - 1) in kb):
            state_k = '{}_{}_{}_H'.format(row, col, obsNum)
            data_q.append('~' + state_k)
            state_k = sympy.symbols(state_k)
            kb_symbols = sympy.And(kb_symbols, ~state_k)
    return kb_symbols


def not_S(kb, kb_symbols, data_q, undefined):
    for und in undefined:
        row, col, obsNum = und.split(sep='_')
        row, col, obsNum = int(row), int(col), int(obsNum)
        if obsNum > 1:
            state_k1 = '{}_{}_{}_Q'.format(row,col, obsNum -1)
            if state_k1 in kb:
                state_k = '{}_{}_{}_S'.format(row,col, obsNum)
                data_q.append('~' + state_k)
                state_k = sympy.symbols(state_k)
                kb_symbols = sympy.And(kb_symbols, ~state_k)
        if ('{}_{}_{}_H'.format(row-1, col, obsNum) in kb and '{}_{}_{}_H'.format(row-1, col, obsNum +1) in kb) \
                or ('{}_{}_{}_H'.format(row+1, col, obsNum) in kb and '{}_{}_{}_H'.format(row+1, col, obsNum +1) in kb) \
                or ('{}_{}_{}_H'.format(row , col- 1, obsNum) in kb and '{}_{}_{}_H'.format(row, col- 1, obsNum + 1) in kb) \
                or ('{}_{}_{}_H'.format(row, col + 1, obsNum) in kb and '{}_{}_{}_H'.format(row, col + 1, obsNum + 1) in kb):
            state_k = '{}_{}_{}_S'.format(row, col, obsNum)
            data_q.append('~' + state_k)
            state_k = sympy.symbols(state_k)
            kb_symbols = sympy.And(kb_symbols, ~state_k)

    return kb_symbols


def to_sat_cnf(list_to_change, symb_dict):
    cnf_list = []
    for symbol in list_to_change:
        if symbol[0] == '~':
            symbol_not = symbol[1:]
            symbol_int = symb_dict[symbol_not]
            cnf_list.append([-symbol_int])
        else:
            symbol_int = symb_dict[symbol]
            cnf_list.append([symbol_int])
    return cnf_list


def is_to_sat_cnf(expr_to_change, symb_dict, cnf_list):
    list_expr = str(expr_to_change).split(sep=' & ')
    for expr in list_expr:
        expr = expr.replace(')', '')
        expr = expr.replace('(', '')
        expr_split = expr.split(sep=' | ')
        expr_or = []

        for e in expr_split:
            if e[0] == '~':
                symbol_not = e[1:]
                symbol_int = symb_dict[symbol_not]
                expr_or.append(-symbol_int)
            else:
                symbol_int = symb_dict[e]
                expr_or.append(symbol_int)
        cnf_list.append(expr_or)
    return cnf_list


def exclusive(und, possible_states, symb_dict):
    exclusive_list = []
    exclusive_und = []
    for p1 in range(len(possible_states)):
        temp1 = und + '_' + possible_states[p1]
        temp1_int = symb_dict[temp1]
        exclusive_und.append(temp1_int)
        for p2 in range(p1+1, len(possible_states)):
            temp2 = und + '_' + possible_states[p2]
            temp2_int = symb_dict[temp2]
            exclusive_list.append([-temp1_int, -temp2_int])
    exclusive_list.append(exclusive_und)
    return exclusive_list


def solve_problem_with_teams(kb, kb_symbols, data_q, undefined, queries, num_of_observations, row_num, col_num,
                             medic_num, police_num, possible_states, symb_dict, kb_list):
    answer = {}
    change = True
    res = False

    while change:
        # global check
        kb_symbols = spreader(kb_symbols, undefined, kb, row_num, col_num, data_q, possible_states, police_num)
        kb_symbols = not_H(kb, kb_symbols, data_q, undefined)
        kb_symbols = not_S(kb, kb_symbols, data_q, undefined)
        if medic_num > 0:
            kb_symbols = not_I(kb, kb_symbols, data_q, undefined)
            kb_symbols, undefined = update_I(kb, kb_symbols, data_q, undefined, possible_states)
            kb_symbols = vaccine(kb, kb_symbols, data_q, undefined, medic_num, num_of_observations, possible_states)
        if police_num > 0:
            kb_symbols = not_Q(kb, kb_symbols, data_q, undefined, police_num, num_of_observations)
            kb_symbols = quarantine(kb, kb_symbols, data_q, undefined, police_num, num_of_observations, possible_states)
        undefined_copy = undefined.copy()
        undefined_copy.reverse()
        for und in undefined_copy:
            ex_list = exclusive(und,possible_states,symb_dict)
            data_q_list = to_sat_cnf(data_q, symb_dict)
            data_q_list.extend(kb_list)
            data_q_list.extend(ex_list)
            if police_num > 0:
                isS = is_S_with_police(und, row_num, col_num, num_of_observations)
            else:
                isS = is_S(und, row_num, col_num, num_of_observations)
            if not isS:
                S_cnf_list = data_q_list.copy()
            else:
                S_cnf = sympy.to_cnf(~isS, simplify=True, force=True)
                S_cnf_list = is_to_sat_cnf(S_cnf, symb_dict, data_q_list.copy())
            solver = pysat.solvers.Solver(name='g3', bootstrap_with=S_cnf_list, with_proof=True)
            res = solver.solve()
            solver.delete()
            if not res:
                new_S = und + '_S'
                data_q.append(new_S)
                kb.append(new_S)
                undefined.remove(und)
                new_S = sympy.symbols(new_S)
                kb_symbols = sympy.And(kb_symbols, new_S)
                for p in possible_states:
                    if p != 'S':
                        not_symbol = und + '_' + p
                        if '~' + not_symbol not in data_q:
                            data_q.append('~' + not_symbol)
                            not_symbol = sympy.symbols(not_symbol)
                            kb_symbols = sympy.And(kb_symbols, ~not_symbol)
            else:
                isH = is_H(und, row_num, col_num, police_num, medic_num, num_of_observations)
                if not isH:
                    H_cnf_list = data_q_list.copy()
                else:
                    H_cnf = sympy.to_cnf(~isH, simplify=True, force=True)
                    H_cnf_list = is_to_sat_cnf(H_cnf, symb_dict, data_q_list.copy())
                solver = pysat.solvers.Solver(name='g3', bootstrap_with=H_cnf_list)
                res = solver.solve()
                solver.delete()
                if not res:
                    new_H = und + '_H'
                    data_q.append(new_H)
                    kb.append(new_H)
                    undefined.remove(und)
                    new_H = sympy.symbols(new_H)
                    kb_symbols = sympy.And(kb_symbols, new_H)
                    for p in possible_states:
                        if p != 'H':
                            not_symbol = und + '_' + p
                            if '~' + not_symbol not in data_q:
                                data_q.append('~' + not_symbol)
                                not_symbol = sympy.symbols(not_symbol)
                                kb_symbols = sympy.And(kb_symbols, ~not_symbol)
                elif police_num > 0:
                    isQ = is_Q(und, num_of_observations, row_num, col_num)
                    if not isQ:
                        Q_cnf_list = data_q_list.copy()
                    else:
                        Q_cnf = sympy.to_cnf(~isQ, simplify=True, force=True)
                        Q_cnf_list = is_to_sat_cnf(Q_cnf, symb_dict, data_q_list.copy())
                    solver = pysat.solvers.Solver(name='g3', bootstrap_with=Q_cnf_list)
                    res = solver.solve()
                    solver.delete()
                    if not res:
                        new_Q = und + '_Q'
                        data_q.append(new_Q)
                        kb.append(new_Q)
                        undefined.remove(und)
                        new_Q = sympy.symbols(new_Q)
                        kb_symbols = sympy.And(kb_symbols, new_Q)
                        for p in possible_states:
                            if p != 'Q':
                                not_symbol = und + '_' + p
                                if '~' + not_symbol not in data_q:
                                    data_q.append('~' + not_symbol)
                                    not_symbol = sympy.symbols(not_symbol)
                                    kb_symbols = sympy.And(kb_symbols, ~not_symbol)
                    else:
                        possible_not_s = len(possible_states) - 1
                        i, j, number = und.split('_')
                        for s in possible_states:
                            find_not_s = []
                            for option in [p for p in possible_states if p != s]:
                                if '~{}_{}_{}_{}'.format(int(i), int(j), int(number), option) in data_q:
                                    find_not_s.append(option)
                            find_not_s = set(find_not_s)
                            if possible_not_s == len(find_not_s):
                                new_state = '{}_{}_{}_{}'.format(int(i), int(j), int(number),s)
                                data_q.append(new_state)
                                kb.append(new_state)
                                new_state = sympy.symbols(new_state)
                                kb_symbols = sympy.And(kb_symbols, new_state)
                                if s == 'U':
                                    kb_symbols, undefined = update_U(kb_symbols, undefined, [(int(i),int(j))], possible_states, kb, data_q)
                                else:
                                 undefined.remove(und)
                else:
                    possible_not_s = len(possible_states) - 1
                    i, j, number = und.split('_')
                    for s in possible_states:
                        find_not_s = []
                        for option in [p for p in possible_states if p != s]:
                            if '~{}_{}_{}_{}'.format(int(i), int(j), int(number), option) in data_q:
                                find_not_s.append(option)
                        find_not_s = set(find_not_s)
                        if possible_not_s == len(find_not_s):
                            new_state = '{}_{}_{}_{}'.format(int(i), int(j), int(number), s)
                            data_q.append(new_state)
                            kb.append(new_state)
                            new_state = sympy.symbols(new_state)
                            kb_symbols = sympy.And(kb_symbols, new_state)
                            if s == 'U':
                                kb_symbols, undefined = update_U(kb_symbols, undefined, [(int(i), int(j))], possible_states,
                                                                 kb, data_q)
                            else:
                                undefined.remove(und)

        if set(undefined_copy) == set(undefined):
            change = False

    for quer in queries:
        place, number, s = quer
        i, j = place
        q = '{}_{}_{}_{}'.format(i, j, number, s)
        if q in data_q:
            answer[quer] = 'T'
        elif '~' + q in data_q:
            answer[quer] = 'F'
        else:
            answer[quer] = '?'
    return answer


def solve_problem(input):
    answer = {}
    # data
    observations = input['observations']
    num_of_observations = len(observations)
    col_num = len(observations[0][0])
    row_num = len(observations[0])
    police_num = input['police']
    medic_num = input['medics']
    queries = input['queries']
    possible_states = ['S', 'U', 'H']
    if police_num > 0:
        possible_states.append('Q')
    if medic_num > 0:
        possible_states.append('I')

    # one observation
    if num_of_observations == 1:
        answer = one_obs(queries)
        return answer
    symb_dict = symbol_to_int(num_of_observations, row_num, col_num, possible_states)
    # knowledge base
    kb_symbols, undefined, U, kb, kb_not = KB(observations, possible_states)
    kb_not.extend(kb)
    kb_list = to_sat_cnf(kb_not, symb_dict)
    data_q = []
    kb_symbols, undefined = update_U(kb_symbols, undefined, U, possible_states, kb, data_q)


    # no police and no medic
    if police_num == 0 and medic_num == 0:
        answer = solve_problem_no_teams(kb, kb_symbols, data_q, undefined, queries, num_of_observations, row_num, col_num,
                                        possible_states)
        return answer

    # with teams
    answer = solve_problem_with_teams(kb, kb_symbols, data_q, undefined, queries, num_of_observations, row_num, col_num,
                                      medic_num, police_num, possible_states, symb_dict, kb_list)
    return answer
