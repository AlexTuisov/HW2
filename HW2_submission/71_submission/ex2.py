from pysat.solvers import Solver
from itertools import product, combinations

ids = ['312320468', '316552710']


def initial_literals(medics, police, observations):
    dict_of_all = {}
    index = 1

    for turn, observation in enumerate(observations):
        for i, row in enumerate(observation):
            for j, col in enumerate(row):
                add = 0
                dict_of_all[(i, j), turn, 'H'] = index
                dict_of_all[(i, j), turn, 'U'] = index + 1
                dict_of_all[(i, j), turn, 'S'] = index + 2
                if medics != 0:
                    dict_of_all[(i, j), turn, 'I'] = index + 3
                    add += 1
                if police != 0:
                    dict_of_all[(i, j), turn, 'Q'] = index + add + 3
                    add += 1
                index = index + add + 3

    return dict_of_all

def Knowledge_Base(observations, dict_of_all, options):
    kb = []
    clauses = []
    uk_index = []

    for turn, obs in enumerate(observations):
        clauses.append([])
        for i, row in enumerate(obs):
            for j, col in enumerate(row):
                if col != '?':
                    kb.append([dict_of_all[((i, j), turn, col)]])
                    for option in options:
                        if option != col:
                            kb.append([-dict_of_all[((i, j), turn, option)]])
                else:
                    uk_index.append(((i, j), turn))
                clauses[turn].append(((i, j), turn, col))
    return kb, clauses, uk_index


def if_vaccinated(dict_of_all, turn, index, cnf):
    if [dict_of_all[(index, turn, 'H')]] in cnf and \
            [dict_of_all[(index, turn + 1, 'I')]] in cnf:
        return 1
    if [dict_of_all[(index, turn, 'H')]] in cnf and \
            [-dict_of_all[(index, turn + 1, 'I')]] in cnf:
        return 2
    return 0


def if_quarantined(dict_of_all, turn, index, cnf):
    if [dict_of_all[(index, turn, 'S')]] in cnf and \
            [dict_of_all[(index, turn + 1, 'Q')]] in cnf:
        return 1
    if [dict_of_all[(index, turn, 'S')]] in cnf and \
            [-dict_of_all[(index, turn + 1, 'Q')]] in cnf:
        return 2
    return 0


def free_teams(police, medics, check_cnf, kb, obs, dict_of_all):
    police_working = []
    medics_working = []
    police_not_working = []
    medics_not_working = []
    func_list = []
    all = kb + check_cnf

    for turn in range(len(obs) - 1):
        cur_uk = uk_in_turn(obs[turn])
        police_working.append([])
        medics_working.append([])

        police_not_working.append([])
        medics_not_working.append([])
        for i in range(len(obs[0])):
            for j in range(len(obs[0][0])):
                index = (i,j)
                if police > 0:
                    iq_p = if_quarantined(dict_of_all, turn, index, all)
                    if iq_p == 1:
                        police_working[turn].append(index)
                    elif iq_p == 2:
                        police_not_working[turn].append(index)

                if medics > 0:
                    iq_m = if_vaccinated(dict_of_all, turn, index, all)
                    if iq_m == 1:
                        medics_working[turn].append(index)
                    elif iq_m == 2:
                        medics_not_working[turn].append(index)

        if medics != 0:
            if len(medics_working[turn]) == medics and medics:
                for i in range(len(obs[0])):
                    for j in range(len(obs[0][0])):
                        if (i, j) not in medics_working[turn]:
                            index = (i, j)
                            func_list.append([dict_of_all[(index, turn, 'I')], -dict_of_all[(index, turn + 1, 'I')]])

            elif len(medics_not_working[turn]) > 0:
                uses = []
                for uk in cur_uk:
                    temp = [dict_of_all[(uk, turn, 'H')], dict_of_all[(uk, turn + 1, 'I')],
                                 -dict_of_all[(uk, turn, 'I')], -dict_of_all[(uk, turn + 1, 'S')],
                                 -dict_of_all[(uk, turn, 'S')], -dict_of_all[(uk, turn, 'U')],
                                 -dict_of_all[(uk, turn + 1, 'H')], -dict_of_all[(uk, turn + 1, 'U')]]
                    if police > 0:
                        temp.append(-dict_of_all[(uk, turn, 'Q')])
                        temp.append(-dict_of_all[(uk, turn + 1, 'Q')])
                    uses.append(temp)

                x = combinations(uses, min(len(cur_uk), medics - len(medics_working[turn])))
                vaccinated = list(x)
                l = []
                for v in vaccinated:
                    temp = [item for sublist in list(v) for item in sublist]
                    l.append(temp)
                p_cnf = list(product(*l))
                for p in p_cnf:
                    func_list.append(list(p))

        if police != 0:
            if len(police_working[turn]) == police:
                for i in range(len(obs[0])):
                    for j in range(len(obs[0][0])):
                        if (i, j) not in police_working[turn]:
                            func_list.append([-dict_of_all[((i, j), turn + 1, 'Q')], dict_of_all[((i, j), turn, 'Q')]])

            elif len(police_not_working[turn]) > 0:
                uses = []
                for uk in cur_uk:
                    temp = [dict_of_all[(uk, turn, 'S')], dict_of_all[(uk, turn + 1, 'Q')],
                                              -dict_of_all[(uk, turn, 'H')], -dict_of_all[(uk, turn, 'Q')],
                                              -dict_of_all[(uk, turn, 'U')], -dict_of_all[(uk, turn + 1, 'S')],
                                              -dict_of_all[(uk, turn + 1, 'H')], -dict_of_all[(uk, turn + 1, 'U')]]
                    if medics > 0:
                        temp.append(-dict_of_all[(uk, turn, 'I')])
                        temp.append(-dict_of_all[(uk, turn + 1, 'I')])
                    uses.append(temp)

                x = combinations(uses, min(len(cur_uk), police - len(police_working[turn])))
                quarantined = list(x)
                l = []
                for q in quarantined:
                    temp = [item for sublist in list(q) for item in sublist]
                    l.append(temp)

                p_cnf = list(product(*l))
                for p in p_cnf:
                    func_list.append(list(p))

    return func_list


def has_sick_neighbor(location, first_turn,second_turn):
    i, j = location
    if (i - 1 > 0 and first_turn[i - 1][j] == 'S' and second_turn[i - 1][j] != 'Q') or \
            (i + 1 < len(first_turn) and first_turn[i + 1][j] == 'S' and second_turn[i + 1][j] != 'Q') or \
            (j - 1 > 0 and first_turn[i][j - 1] == 'S' and second_turn[i][j - 1] != 'Q') or \
            (j + 1 < len(first_turn[0]) and first_turn[i][j + 1] == 'S' and second_turn[i][j + 1] != 'Q'):
        return True
    return False


def has_uk_neighbor(location, turn):
    i, j = location
    if (i - 1 > 0 and turn[i - 1][j] == '?') or (i + 1 < len(turn) and turn[i + 1][j] == '?') or \
            (j - 1 > 0 and turn[i][j - 1] == '?') or (j + 1 < len(turn[0]) and turn[i][j + 1] == '?'):
        return True
    return False


def find_uk_neighbors(location, turn):
    i, j = location
    uk_neighbors = []
    if i - 1 > 0 and turn[i - 1][j] == '?':
        uk_neighbors.append((i - 1, j))
    if i + 1 < len(turn) and turn[i + 1][j] == '?':
        uk_neighbors.append((i + 1, j))
    if j - 1 > 0 and turn[i][j - 1] == '?':
        uk_neighbors.append((i, j - 1))
    if j + 1 < len(turn[0]) and turn[i][j + 1] == '?':
        uk_neighbors.append((i, j + 1))
    return uk_neighbors


def find_sick_neighbors(location, turn):
    i, j = location
    sick_neighbors = []
    if i - 1 > 0 and turn[i - 1][j] == 'S':
        sick_neighbors.append((i - 1, j))
    if i + 1 < len(turn) and turn[i + 1][j] == 'S':
        sick_neighbors.append((i + 1, j))
    if j - 1 > 0 and turn[i][j - 1] == 'S':
        sick_neighbors.append((i, j - 1))
    if j + 1 < len(turn[0]) and turn[i][j + 1] == 'S':
        sick_neighbors.append((i, j + 1))
    return sick_neighbors


def check_how_many_neighbors(location, turn):
    count = 0
    i, j = location
    if i-1>0:
        count +=1
    if i + 1 < len(turn):
        count += 1
    if j - 1 > 0:
        count += 1
    if j + 1 < len(turn[0]):
        count += 1
    return count


def uk_in_turn(turn):
    list_of_uk = []
    for i in range(len(turn)):
        for j in range(len(turn[0])):
            if turn[i][j] == '?':
                list_of_uk.append((i, j))
    return list_of_uk


def find_h_to_s_nei(location, first_ob, second_ob):
    i, j = location
    li = []
    if (i - 1 > 0 and first_ob[i - 1][j] == 'H' and second_ob[i - 1][j] == 'S'):
        li.append((i-1,j))
    if (i + 1 < len(first_ob) and first_ob[i + 1][j] == 'H' and second_ob[i + 1][j] == 'S'):
        li.append((i+1,j))
    if (j - 1 > 0 and first_ob[i][j - 1] == 'H' and second_ob[i][j - 1] == 'S'):
        li.append((i, j-1))
    if (j + 1 < len(first_ob[0]) and first_ob[i][j + 1] == 'H' and first_ob[i][j + 1] == 'S'):
        li.append((i, j+1))
    return li


def check_if_H_neighbor_didnt_turn_to_S(location, first_ob, second_ob, medics):
    i, j = location
    if medics == 0:
        if (i - 1 > 0 and first_ob[i - 1][j] == 'H' and not second_ob[i - 1][j] == 'S') or \
                (i + 1 < len(first_ob) and first_ob[i + 1][j] == 'H' and not second_ob[i + 1][j] == 'S') or \
                (j - 1 > 0 and first_ob[i][j - 1] == 'H' and not second_ob[i][j - 1] == 'S') or \
                (j + 1 < len(first_ob[0]) and first_ob[i][j + 1] == 'H' and not first_ob[i][j + 1] == 'S'):
            return True
    else:
        if (i - 1 > 0 and first_ob[i - 1][j] == 'H' and not second_ob[i - 1][j] == 'S' and not second_ob[i - 1][
                                                                                                   j] == 'I') or \
                (i + 1 < len(first_ob) and first_ob[i + 1][j] == 'H' and not second_ob[i + 1][j] == 'S' and not
                second_ob[i - 1][j] == 'I') or \
                (j - 1 > 0 and first_ob[i][j - 1] == 'H' and not second_ob[i][j - 1] == 'S' and not second_ob[i - 1][
                                                                                                        j] == 'I') or \
                (j + 1 < len(first_ob[0]) and first_ob[i][j + 1] == 'H' and not first_ob[i][j + 1] == 'S' and not
                second_ob[i - 1][j] == 'I'):
            return True
    return False


def check_all_board(observations, dict_of_all, medics, police, options, kb):
    cnf = []
    medics_uses = []
    police_uses = []
    temp_p = []
    temp_m = []
    temp_can_be_i = []

    for turn in range(len(observations) - 1):
        medics_uses.append([])
        police_uses.append([])

        for i in range(len(observations[turn])):
            for j in range(len(observations[turn][0])):
                if turn == 0:
                    if police != 0:
                        cnf.append([-dict_of_all[((i,j), turn, 'Q')]])
                    if medics != 0:
                        cnf.append([-dict_of_all[((i,j), turn, 'I')]])

                #################################################### H
                if observations[turn][i][j] == 'H':
                    cnf.append([dict_of_all[((i, j), turn, 'H')]])

                    if observations[turn + 1][i][j] == 'I':
                        cnf.append([dict_of_all[((i, j), turn + 1, 'I')]])

                    elif observations[turn + 1][i][j] == '?':
                        cnf.append([-dict_of_all[((i, j), turn + 1, 'U')]])  # H-> ?
                        temp_cnf = []

                        count = 0
                        for l in range(len(observations[turn])):
                            for m in range(len(observations[turn][0])):
                                if observations[turn][l][m] == 'H' and observations[turn+1][l][m] == 'I':
                                    count += 1

                        if count < medics:
                            temp_m.append(dict_of_all[((i, j), turn + 1, 'I')])
                            temp_cnf.append(dict_of_all[((i, j), turn + 1, 'I')])

                        if has_sick_neighbor((i, j), observations[turn], observations[turn + 1]):
                            temp_cnf.append(dict_of_all[((i, j), turn + 1, 'S')])
                            cnf.append([-dict_of_all[((i, j), turn + 1, 'H')]])
                            if police > 0:
                                cnf.append([-dict_of_all[((i, j), turn + 1, 'Q')]])

                        elif (has_uk_neighbor((i, j), observations[turn]) == False) and \
                                (has_sick_neighbor((i, j), observations[turn], observations[turn + 1]) == False):

                            temp_cnf.append(dict_of_all[((i, j), turn + 1, 'H')])
                            cnf.append([-dict_of_all[((i, j), turn + 1, 'S')]])
                            cnf.append([-dict_of_all[((i, j), turn + 1, 'U')]])
                            if police > 0:
                                cnf.append([-dict_of_all[((i, j), turn + 1, 'Q')]])
                        if temp_cnf:
                            cnf.append(temp_cnf)

                    elif observations[turn + 1][i][j] == 'S':
                        cnf.append([dict_of_all[((i, j), turn + 1, 'S')]])

                        if (has_sick_neighbor((i, j), observations[turn], observations[turn + 1]) == False) and \
                                (has_uk_neighbor((i, j), observations[turn]) == True):
                            uk_neigh = find_uk_neighbors((i, j), observations[turn])
                            if len(uk_neigh) == 1:
                                cnf.append([dict_of_all[(uk_neigh[0], turn, 'S')]])
                                cnf.append([-dict_of_all[(uk_neigh[0], turn, 'U')]])
                                cnf.append([-dict_of_all[(uk_neigh[0], turn, 'H')]])
                                if medics > 0:
                                    cnf.append([-dict_of_all[(uk_neigh[0], turn, 'I')]])
                                if police > 0:
                                    cnf.append([-dict_of_all[(uk_neigh[0], turn, 'Q')]])

                            else:
                                s_cnf = []
                                if police == 0:
                                    for uk in uk_neigh:
                                        s_cnf.append(dict_of_all[(uk, turn, 'S')])
                                    cnf.append(s_cnf)
                                else:
                                    for uk in uk_neigh:
                                        s_cnf.append([dict_of_all[(uk, turn, 'S')], -dict_of_all[(uk, turn + 1, 'Q')]])
                                    cnf.append(list(product(*s_cnf)))

                        elif has_sick_neighbor((i, j), observations[turn], observations[turn + 1]):
                            cnf.append([dict_of_all[((i, j), turn + 1, 'S')]])

                    elif observations[turn + 1][i][j] == 'H':
                        cnf.append([dict_of_all[((i, j), turn + 1, 'H')]])

                        if has_sick_neighbor((i, j), observations[turn], observations[turn + 1]) and not \
                                has_uk_neighbor((i, j), observations[turn]):  # yes sick no uk
                            sick_neigh = find_sick_neighbors((i, j), observations[turn])
                            for sick in sick_neigh:
                                cnf.append([dict_of_all[(sick, turn + 1, 'Q')]])
                                police_uses[turn].append(sick)

                        elif not has_sick_neighbor((i, j), observations[turn], observations[turn + 1]) and \
                                has_uk_neighbor((i, j), observations[turn]):  # no sick yes uk
                            uk_neigh = find_uk_neighbors((i, j), observations[turn])
                            for ne in uk_neigh:
                                if police == 0:
                                    cnf.append([-dict_of_all[(ne, turn, 'S')]])
                                else:
                                    cnf.append([dict_of_all[(ne, turn + 1, 'Q')], -dict_of_all[(ne, turn, 'S')]])

                        elif has_sick_neighbor((i, j), observations[turn], observations[turn + 1]) and \
                                has_uk_neighbor((i, j), observations[turn]):  # yes sick yes uk
                            sick_neigh = find_sick_neighbors((i, j), observations[turn])
                            for sick in sick_neigh:
                                cnf.append([dict_of_all[(sick, turn + 1, 'Q')]])
                                cnf.append([-dict_of_all[(sick, turn + 1, 'H')]])
                                cnf.append([-dict_of_all[(sick, turn + 1, 'S')]])
                                cnf.append([-dict_of_all[(sick, turn + 1, 'U')]])
                                police_uses[turn].append(sick)
                                if medics > 0:
                                    cnf.append([-dict_of_all[(sick, turn + 1, 'I')]])

                            uk_neigh = find_uk_neighbors((i, j), observations[turn])
                            for ne in uk_neigh:
                                cnf.append([-dict_of_all[(ne, turn, 'S')]])
                                if police > 0:
                                    cnf.append([-dict_of_all[(ne, turn, 'S')], dict_of_all[(ne, turn + 1, 'Q')]])

                ####################################################################### S

                elif observations[turn][i][j] == 'S':  # check if need
                    cnf.append([dict_of_all[((i, j), turn, 'S')]])

                    if observations[turn + 1][i][j] == 'Q':
                        cnf.append([dict_of_all[((i, j), turn + 1, 'Q')]])
                        police_uses[turn].append((i, j))
                        if turn+2 < len(observations):
                            cnf.append([dict_of_all[((i, j), turn + 2, 'Q')]])

                    elif observations[turn + 1][i][j] == 'S':
                        cnf.append([dict_of_all[((i, j), turn + 1, 'S')]])

                    elif observations[turn + 1][i][j] == 'H':
                        cnf.append([dict_of_all[((i, j), turn + 1, 'H')]])
                        if turn >= 2:
                            cnf.append([dict_of_all[((i, j), turn - 1, 'S')]])
                            cnf.append([dict_of_all[((i, j), turn - 2, 'S')]])

                    elif observations[turn + 1][i][j] == '?':
                        cnf.append([-dict_of_all[((i, j), turn + 1, 'U')]])  # not i
                        # maybe I
                        cnf_s = []

                        count = 0
                        for l in range(len(observations[turn])):
                            for m in range(len(observations[turn][0])):
                                if observations[turn][l][m] == 'S' and observations[turn+1][l][m] == 'Q':
                                    count += 1

                        if count < police:
                            temp_p.append([dict_of_all[((i, j), turn + 1, 'Q')]])
                            cnf_s.append(dict_of_all[((i, j), turn + 1, 'Q')])

                        if turn >= 2:
                            if medics > 0:
                                cnf.append([-dict_of_all[((i, j), turn + 1, 'I')]])
                            if observations[turn - 1][i][j] == 'S' and observations[turn - 2][i][j] == 'S':
                                cnf_s.append(dict_of_all[((i, j), turn + 1, 'H')])
                                cnf.append([-dict_of_all[((i, j), turn + 1, 'S')]])
                            elif observations[turn - 1][i][j] == 'S' and observations[turn - 2][i][j] == 'H':
                                cnf_s.append(dict_of_all[((i, j), turn + 1, 'S')])
                                cnf.append([-dict_of_all[((i, j), turn + 1, 'H')]])

                        elif turn > 0:
                            if medics > 0:
                                cnf.append([-dict_of_all[((i, j), turn + 1, 'I')]])
                            cnf_s.append(dict_of_all[((i, j), turn + 1, 'S')])
                            cnf.append([-dict_of_all[((i, j), turn + 1, 'H')]])

                        elif turn == 0:
                            cnf_s.append(dict_of_all[((i, j), turn + 1, 'S')])
                            cnf.append([-dict_of_all[((i, j), turn + 1, 'H')]])
                            cnf.append([-dict_of_all[((i, j), turn + 1, 'U')]])
                            if medics > 0:
                                cnf.append([-dict_of_all[((i, j), turn + 1, 'I')]])

                        if cnf_s:
                            cnf.append(cnf_s)

                ####################################################### Q
                elif observations[turn][i][j] == 'Q':

                    cnf.append([dict_of_all[((i, j), turn, 'Q')]])

                    if turn >= 2:
                        if observations[turn-2] == 'S' and observations[turn-1] == 'Q':
                            cnf.append([dict_of_all[((i, j), turn, 'H')]])

                    if medics > 0:
                        cnf.append([-dict_of_all[((i, j), turn - 1, 'I')]])

                    if observations[turn + 1][i][j] == 'Q' or turn == 1:
                        cnf.append([dict_of_all[((i, j), turn + 1, 'Q')]])
                        cnf.append([dict_of_all[((i, j), turn - 1, 'S')]])
                        cnf.append([-dict_of_all[((i, j), turn - 1, 'H')]])
                        cnf.append([-dict_of_all[((i, j), turn - 1, 'U')]])

                    if observations[turn + 1][i][j] == 'Q' and turn+2 < len(observations):
                        cnf.append([dict_of_all[((i, j), turn + 2, 'H')]])
                        for op in options:
                            if op != 'H':
                                cnf.append([-dict_of_all[((i, j), turn + 2, op)]])
                        cnf.append([-dict_of_all[((i, j), turn - 1, 'H')]])
                        cnf.append([-dict_of_all[((i, j), turn - 1, 'U')]])

                    elif observations[turn + 1][i][j] == '?':
                        cnf.append([-dict_of_all[((i, j), turn + 1, 'U')]])
                        if turn >= 1:
                            if observations[turn - 1][i][j] == 'Q':
                                cnf.append([dict_of_all[((i, j), turn + 1, 'H')]])
                                for op in options:
                                    if op != 'H':
                                        cnf.append([-dict_of_all[((i, j), turn + 1, op)]])

                            elif observations[turn - 1][i][j] == 'S':
                                cnf.append([dict_of_all[((i, j), turn + 1, 'Q')]])
                                for op in options:
                                    if op != 'Q':
                                        cnf.append([-dict_of_all[((i, j), turn + 1, op)]])

                            elif observations[turn - 1][i][j] != '?':
                                cnf.append([dict_of_all[((i, j), turn + 1, 'Q')]])

                            else:  # prev turn was '?'
                                cnf.append([dict_of_all[((i, j), turn + 1, 'H')], dict_of_all[((i, j), turn - 1, 'S')]])
                                cnf.append([dict_of_all[((i, j), turn + 1, 'H')], dict_of_all[((i, j), turn + 1, 'Q')]])
                                cnf.append([dict_of_all[((i, j), turn - 1, 'Q')], dict_of_all[((i, j), turn - 1, 'S')]])
                                cnf.append([dict_of_all[((i, j), turn - 1, 'Q')], dict_of_all[((i, j), turn + 1, 'Q')]])
                                cnf.append([-dict_of_all[((i, j), turn - 1, 'H')]])
                                if medics > 0:
                                    cnf.append([-dict_of_all[((i, j), turn - 1, 'I')]])

                    elif observations[turn + 1][i][j] == 'H':
                        cnf.append([dict_of_all[((i, j), turn + 1, 'H')]])
                        cnf.append([dict_of_all[((i, j), turn - 1, 'Q')]])
                        cnf.append([-dict_of_all[((i, j), turn - 1, 'H')]])
                        cnf.append([-dict_of_all[((i, j), turn - 1, 'S')]])
                        cnf.append([dict_of_all[((i, j), turn - 2, 'S')]])
                        cnf.append([-dict_of_all[((i, j), turn - 2, 'H')]])
                        cnf.append([-dict_of_all[((i, j), turn - 2, 'Q')]])
                        if medics > 0:
                            cnf.append([-dict_of_all[((i, j), turn - 1, 'I')]])
                            cnf.append([-dict_of_all[((i, j), turn - 2, 'I')]])

                ############################# I
                elif observations[turn][i][j] == 'I':
                    cnf.append([dict_of_all[((i, j), turn, 'I')]])
                    for p in range(turn, len(observations)):
                        cnf.append([dict_of_all[((i, j), p, 'I')]])
                        cnf.append([-dict_of_all[((i, j), p, 'H')]])
                        cnf.append([-dict_of_all[((i, j), p, 'S')]])
                        if police > 0:
                            cnf.append([-dict_of_all[((i, j), p, 'Q')]])

                    if turn == 1:
                        cnf.append([dict_of_all[((i, j), turn - 1, 'H')]])
                        cnf.append([-dict_of_all[((i, j), turn - 1, 'I')]])
                        cnf.append([-dict_of_all[((i, j), turn - 1, 'S')]])
                        if police > 0:
                            cnf.append([-dict_of_all[((i, j), turn - 1, 'Q')]])

                    if observations[turn + 1][i][j] == '?':
                        cnf.append([dict_of_all[((i, j), turn + 1, 'I')]])
                        cnf.append([-dict_of_all[((i, j), turn + 1, 'H')]])
                        cnf.append([-dict_of_all[((i, j), turn + 1, 'S')]])
                        cnf.append([-dict_of_all[((i, j), turn + 1, 'U')]])
                        if police > 0:
                            cnf.append([-dict_of_all[((i, j), turn + 1, 'Q')]])

                ################################# ?
                elif observations[turn][i][j] == '?':
                    if check_if_H_neighbor_didnt_turn_to_S((i, j), observations[turn], observations[turn + 1], medics):
                        if police > 0:
                            cnf.append([-dict_of_all[((i, j), turn, 'S')], dict_of_all[((i, j), turn + 1, 'Q')]])
                        else:
                            cnf.append([-dict_of_all[((i, j), turn, 'S')]])

                    if observations[turn + 1][i][j] == '?':
                        check1 = has_sick_neighbor((i, j), observations[turn], observations[turn+1])
                        if check1:
                            if turn+2 < len(observations):
                                check2 = check_if_H_neighbor_didnt_turn_to_S((i, j), observations[turn+1],
                                                                             observations[turn+2], medics)
                                if check2: #has sick nei but h nei wont turn to s
                                    #cnf.append([-dict_of_all[((i, j), turn, 'H')]])

                                    count_S_to_Q = 0
                                    count_S = 0
                                    for l in range(len(observations[turn])):
                                        for m in range(len(observations[turn][0])):
                                            if observations[turn + 1][l][m] == 'S':
                                                count_S += 1
                                            if observations[turn][l][m] == 'S' and observations[turn + 1][l][m] == 'Q':
                                                count_S_to_Q += 1

                                    if count_S_to_Q < police and count_S != 0:
                                        cnf.append([dict_of_all[((i, j), turn, 'S')]])
                                        cnf.append([dict_of_all[((i, j), turn+1, 'Q')]])
                                        for op in options:
                                            if op != 'S':
                                                cnf.append([-dict_of_all[((i, j), turn, op)]])
                                        for op in options:
                                            if op != 'Q':
                                                cnf.append([-dict_of_all[((i, j), turn+1, op)]])
                                    elif count_S_to_Q == police:
                                        cnf.append([dict_of_all[((i, j), turn, 'U')]])
                                        for op in options:
                                            if op != 'U':
                                                cnf.append([-dict_of_all[((i, j), turn, op)]])
                                        for tu in range(len(observations)):
                                            cnf.append([dict_of_all[((i, j), tu, 'U')]])
                                            for op in options:
                                                if op != 'U':
                                                    cnf.append([-dict_of_all[((i, j), tu, op)]])


                                else: #has sick nei, h nei turn to s
                                    h_to_s_nei = find_h_to_s_nei((i,j), observations[turn+1], observations[turn+2])
                                    count_check = 0
                                    for h in h_to_s_nei:
                                        check3 = has_sick_neighbor(h, observations[turn+1], observations[turn+2])
                                        if check3:
                                            count_check += 1
                                    if count_check < len(h_to_s_nei):
                                        cnf.append([dict_of_all[((i, j), turn, 'H')]])
                                        cnf.append([dict_of_all[((i, j), turn+1, 'S')]])
                                        for op in options:
                                            if op != 'H':
                                                cnf.append([-dict_of_all[((i, j), turn, op)]])
                                        for op in options:
                                            if op != 'S':
                                                cnf.append([-dict_of_all[((i, j), turn + 1, op)]])

                                        count_S_to_Q = 0
                                        for l in range(len(observations[turn])):
                                            for m in range(len(observations[turn][0])):
                                                if observations[turn+1][l][m] == 'S' and\
                                                        observations[turn + 2][l][m] == 'Q':
                                                    count_S_to_Q += 1
                                        if count_S_to_Q < police:
                                            cnf.append([dict_of_all[((i, j), turn + 2, 'Q')]])
                                            for op in options:
                                                if op != 'Q':
                                                    cnf.append([-dict_of_all[((i, j), turn+2, op)]])
                                        elif count_S_to_Q == police:
                                            cnf.append([dict_of_all[((i, j), turn + 2, 'S')]])
                                            for op in options:
                                                if op != 'S':
                                                    cnf.append([-dict_of_all[((i, j), turn + 2, op)]])
                            elif turn+1 < len(observations):
                                if has_sick_neighbor((i,j), observations[turn], observations[turn+1]):
                                    cnf.append([-dict_of_all[((i, j), turn + 1, 'H')]])
                                if check_if_H_neighbor_didnt_turn_to_S((i,j), observations[turn], observations[turn+1], medics):
                                    cnf.append([-dict_of_all[((i, j), turn, 'S')]])

                        count_h_to_i = 0
                        count_h = 0
                        for l in range(len(observations[turn])):
                            for m in range(len(observations[turn][0])):
                                if observations[turn+1][l][m] == 'H':
                                    count_h += 1
                                if observations[turn][l][m] == 'H' and observations[turn + 1][l][m] == 'I':
                                    count_h_to_i += 1
                        count_S_to_Q = 0
                        count_S = 0
                        for l in range(len(observations[turn])):
                            for m in range(len(observations[turn][0])):
                                if observations[turn + 1][l][m] == 'S':
                                    count_S += 1
                                if observations[turn][l][m] == 'S' and observations[turn + 1][l][m] == 'Q':
                                    count_S_to_Q += 1

                        ## add check if other ? can turn to i
                        ##doesnt have sick nei
                        if not check1 and count_h_to_i < medics and count_h != 0 and turn+1<len(observations) and\
                                check_if_H_neighbor_didnt_turn_to_S((i,j),observations[turn],observations[turn+1],medics) and count_S_to_Q == police:

                            cnf.append([dict_of_all[((i, j), turn, 'H')],dict_of_all[((i, j), turn, 'U')]])
                            cnf.append([-dict_of_all[((i, j), turn + 1, 'U')], -dict_of_all[((i, j), turn + 1, 'H')]])

                            #temp_can_be_i.append(dict_of_all[((i, j), turn+1, 'I')])
                            #cnf.append([dict_of_all[((i, j), turn+1, 'I')]])
                            cnf.append([dict_of_all[((i, j), turn + 1, 'I')],dict_of_all[((i, j), turn + 1, 'H')],dict_of_all[((i, j), turn + 1, 'U')]])
                            cnf.append([-dict_of_all[((i, j), turn + 1, 'I')], -dict_of_all[((i, j), turn + 1, 'H')]])
                            cnf.append([-dict_of_all[((i, j), turn + 1, 'I')], -dict_of_all[((i, j), turn + 1, 'U')]])
                            cnf.append([-dict_of_all[((i, j), turn + 1, 'U')], -dict_of_all[((i, j), turn + 1, 'H')]])
                            for op in options:
                                if op != 'H' and op != 'U':
                                    cnf.append([-dict_of_all[((i, j), turn, op)]])

                            for op in options:
                                if op != 'I' and op != 'H' and op != 'U':
                                    cnf.append([-dict_of_all[((i, j), turn+1, op)]])

                            if turn > 0:
                                cnf.append([dict_of_all[((i, j), turn-1, 'H')]])
                                for op in options:
                                    if op != 'H':
                                        cnf.append([-dict_of_all[((i, j), turn - 1, op)]])


                    elif observations[turn + 1][i][j] == 'Q':
                        cnf.append([dict_of_all[((i, j), turn, 'S')], dict_of_all[((i, j), turn, 'Q')]])
                        cnf.append([-dict_of_all[((i, j), turn, 'H')]])
                        if medics > 0:
                            cnf.append([-dict_of_all[((i, j), turn, 'I')]])

                    elif observations[turn + 1][i][j] == 'I':
                        cnf.append([dict_of_all[((i, j), turn, 'H')], dict_of_all[((i, j), turn, 'I')]])
                        cnf.append([-dict_of_all[((i, j), turn, 'S')]])
                        if police > 0:
                            cnf.append([-dict_of_all[((i, j), turn, 'Q')]])

                    elif observations[turn + 1][i][j] == 'H':
                        if turn > 3:
                            cnf += list(product(*[
                                [dict_of_all[((i, j), turn - 2, 'S')], dict_of_all[((i, j), turn, 'Q')],
                                 dict_of_all[((i, j), turn - 1, 'Q')]],
                                [dict_of_all[((i, j), turn - 3, 'H')], dict_of_all[((i, j), turn - 2, 'S')],
                                 dict_of_all[((i, j), turn - 1, 'S')], dict_of_all[((i, j), turn, 'S')]]
                                [dict_of_all[((i, j), turn, 'H')]]
                            ]))

                        elif turn == 0:
                            cnf.append([dict_of_all[((i, j), turn, 'H')]])
                            cnf.append([-dict_of_all[((i, j), turn, 'S')]])
                            cnf.append([-dict_of_all[((i, j), turn, 'U')]])
                            if medics > 0:
                                cnf.append([-dict_of_all[((i, j), turn, 'I')]])
                            if police > 0:
                                cnf.append([-dict_of_all[((i, j), turn, 'Q')]])

                        elif turn <= 2:
                            cnf.append([dict_of_all[((i, j), turn, 'H')]])
                            cnf.append([-dict_of_all[((i, j), turn, 'S')]])
                            cnf.append([-dict_of_all[((i, j), turn, 'U')]])
                            if medics > 0:
                                cnf.append([-dict_of_all[((i, j), turn, 'I')]])
                            if police > 0:
                                cnf.append([-dict_of_all[((i, j), turn, 'Q')]])

                            if observations[turn - 1][i][j] == '?':
                                cnf.append([dict_of_all[((i, j), turn - 1, 'H')]])
                                cnf.append([-dict_of_all[((i, j), turn - 1, 'S')]])
                                cnf.append([-dict_of_all[((i, j), turn - 1, 'U')]])
                                if medics > 0:
                                    cnf.append([-dict_of_all[((i, j), turn - 1, 'I')]])
                                if police > 0:
                                    cnf.append([-dict_of_all[((i, j), turn - 1, 'Q')]])

                        if turn == 2:
                            if observations[turn - 2][i][j] == '?':
                                cnf.append([dict_of_all[((i, j), turn - 2, 'H')]])
                                cnf.append([-dict_of_all[((i, j), turn - 2, 'S')]])
                                cnf.append([-dict_of_all[((i, j), turn - 2, 'U')]])
                                if medics > 0:
                                    cnf.append([-dict_of_all[((i, j), turn - 2, 'I')]])
                                if police > 0:
                                    cnf.append([-dict_of_all[((i, j), turn - 2, 'Q')]])

                    elif observations[turn + 1][i][j] == 'S':

                        sick_and_no_q = []
                        if police == 0:

                            if i - 1 > 0:
                                sick_and_no_q.append(dict_of_all[((i - 1, j), turn, 'S')])
                            if i + 1 < len(observations[0]):
                                sick_and_no_q.append(dict_of_all[((i + 1, j), turn, 'S')])
                            if j - 1 > 0:
                                sick_and_no_q.append(dict_of_all[((i, j - 1), turn, 'S')])
                            if j + 1 < len(observations[0][0]):
                                sick_and_no_q.append(dict_of_all[((i, j + 1), turn, 'S')])
                            sick_and_no_q.append(dict_of_all[((i, j), turn, 'S')])
                            cnf.append(sick_and_no_q)
                        else:
                            if j - 1 > 0:
                                sick_and_no_q.append(
                                    [dict_of_all[((i, j - 1), turn, 'S')], -dict_of_all[((i, j - 1), turn, 'Q')]])
                            if j + 1 < len(observations[0][0]):
                                sick_and_no_q.append(
                                    [dict_of_all[((i, j + 1), turn, 'S')], -dict_of_all[((i, j + 1), turn, 'Q')]])
                            if i - 1 > 0:
                                sick_and_no_q.append(
                                    [dict_of_all[((i - 1, j), turn, 'S')], -dict_of_all[((i - 1, j), turn, 'Q')]])
                            if i + 1 < len(observations[0]):
                                sick_and_no_q.append(
                                    [dict_of_all[((i + 1, j), turn, 'S')], -dict_of_all[((i + 1, j), turn, 'Q')]])

                            sick_and_no_q.append([dict_of_all[((i, j), turn, 'S')]])

                            products = list(product(*sick_and_no_q))
                            if len(sick_and_no_q) != 1:
                                for pro in products:
                                    cnf.append(list(pro))

                    elif observations[turn + 1][i][j] == 'U':
                        cnf.append([dict_of_all[((i, j), turn, 'U')]])
                        for option in options:
                            if option != 'U':
                                cnf.append([-dict_of_all[((i, j), turn, option)]])
                    ############################# check uv

                    more_cnf = free_teams(police, medics, cnf, kb, observations, dict_of_all)
                    cnf += more_cnf
                    #cnf.append(temp_can_be_i)
        #U
        for i in range(len(observations[0])):
            for j in range(len(observations[0][0])):
                for turn in range(len(observations)):
                    if observations[turn][i][j] == 'U':
                        for turn2 in range(len(observations)):
                            cnf.append([dict_of_all[((i, j), turn2, 'U')]])
                            for option in options:
                                if option != 'U':
                                    cnf.append([-dict_of_all[((i, j), turn2, option)]])
                        continue
                    elif observations[turn][i][j] != '?':
                        for turn2 in range(len(observations)):
                            cnf.append([-dict_of_all[((i, j), turn2, 'U')]])
                        continue

    return cnf, police_uses, medics_uses


def to_solver(q, kb, options, ob, dict_of_all, medics, police):
    cnf_all, police_uses, medics_uses = check_all_board(ob, dict_of_all, medics, police, options, kb)
    s = Solver(name='g4')
    other_results = []
    if medics == 0 and police == 0:

        if q[2] == 'S':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([dict_of_all[q]])
            result = s.solve()

            others = ['H', 'U']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

        elif q[2] == 'H':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([dict_of_all[q]])
            result = s.solve()

            others = ['S', 'U']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

        if q[2] == 'U':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([q])
            result = s.solve()

            others = ['H', 'S']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

    elif medics == 0:
        if q[2] == 'S':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([dict_of_all[q]])
            result = s.solve()

            others = ['H', 'U', 'Q']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

        elif q[2] == 'H':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([dict_of_all[q]])
            result = s.solve()

            others = ['S', 'U', 'Q']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

        elif q[2] == 'U':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([dict_of_all[q]])
            result = s.solve()

            others = ['H', 'S', 'Q']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

        elif q[2] == 'Q':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([dict_of_all[q]])
            result = s.solve()

            others = ['H', 'S', 'U']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

    elif police == 0:
        if q[2] == 'S':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([dict_of_all[q]])
            result = s.solve()

            others = ['H', 'U', 'I']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

        elif q[2] == 'H':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([dict_of_all[q]])
            result = s.solve()

            others = ['S', 'U', 'I']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

        elif q[2] == 'U':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([dict_of_all[q]])
            result = s.solve()

            others = ['H', 'S', 'I']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

        elif q[2] == 'I':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([dict_of_all[q]])
            result = s.solve()

            others = ['H', 'S', 'U']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

    else:  # medics and police > 0
        if q[2] == 'S':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([dict_of_all[q]])
            result = s.solve()

            others = ['H', 'U', 'Q', 'I']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

        elif q[2] == 'H':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([dict_of_all[q]])
            result = s.solve()

            others = ['S', 'U', 'Q', 'I']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

        elif q[2] == 'U':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([dict_of_all[q]])
            result = s.solve()

            others = ['H', 'S', 'Q', 'I']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

        elif q[2] == 'Q':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([dict_of_all[q]])
            result = s.solve()

            others = ['H', 'S', 'U', 'I']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

        elif q[2] == 'I':
            for c in kb:
                s.add_clause(c)
            for c in cnf_all:
                s.add_clause(c)
            s.add_clause([dict_of_all[q]])
            result = s.solve()

            others = ['H', 'S', 'U', 'Q']
            for other in others:
                temp = Solver(name='g4')
                for c in kb:
                    temp.add_clause(c)
                for c in cnf_all:
                    temp.add_clause(c)
                temp.add_clause([dict_of_all[(q[0], q[1], other)]])
                other_results.append(temp.solve())

    if result == True:
        for o in other_results:
            if o == True:
                return '?'
        return 'T'
    else:
        return 'F'


def solve_problem(input):
    police = input["police"]
    medics = input["medics"]
    observations = input["observations"]
    queries = input["queries"]

    options = ['H', 'S', 'U']
    if police:
        options.append('Q')
    if medics:
        options.append('I')

    dict_of_all = initial_literals(medics, police, observations)
    kb, clauses, uk_index = Knowledge_Base(observations, dict_of_all, options)

    answers = {}
    for q in queries:
        answers[q] = to_solver(q, kb, options, observations, dict_of_all, medics, police)

    return answers
