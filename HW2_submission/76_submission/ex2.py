ids = ['315881656']
import numpy as np
from sympy.logic.algorithms.dpll import dpll
from sympy import *
from sympy.logic.inference import PropKB


def solve_problem(input):
    pass
    kb = PropKB()
    observations = input['observations']
    turns = len(observations)
    M = len(observations[0])
    N = len(observations[0][0])
    police_num = input['police']
    medics_num = input['medics']
    queries = input['queries']
    map_indexes = [(i, j) for i, j in np.ndindex(M, N)]
    neighbours = lambda i, j: [x for x in [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)] if
                               x in map_indexes and observations[0][x[0]][x[1]] != 'U']

    def symbolize(string, i, j, t):
        return symbols(string + str(i) + str(j) + str(t))

    for k in range(3):
        for index,observation in enumerate(observations):
            # --- Hijt == Healthy at location (i, j) at turn t
            for i, j in map_indexes:
                # ***
                proposition = lambda string: ~symbols(string[1] + str(i) + str(j) + str(index)) \
                    if string[0] == '~' else symbols(string + str(i) + str(j) + str(index))
                if observation[i][j] != 'U' and observation[i][j] != '?':
                    if observation[i][j] == 'H':
                        kb.tell(proposition('H'))
                    else:
                        kb.tell(proposition('~H'))
                    if observation[i][j] == 'S':
                        kb.tell(proposition('S'))
                    else:
                        kb.tell(proposition('~S'))
                    if observation[i][j] == 'Q':
                        kb.tell(proposition('Q'))
                    else:
                        kb.tell(proposition('~Q'))
                    if observation[i][j] == 'I':
                        kb.tell(proposition('I'))
                    else:
                        kb.tell(proposition('~I'))
                if observation[i][j] == '?':
                    kb.tell(proposition('?'))

        # print("kb after initial constraints:")
        # print(kb.clauses)

        for i, j in map_indexes:
            for t in range(turns-1):
                # Healthy infected by neighbour:
                # area must not take medics at t+1 => ~Iijt+1
                # neighbour sick area must not be quarantined at t+1 => ~Qsick_neighbour
                ijneighbours = neighbours(i, j)
                clauses2 = [symbolize("S", X[0], X[1], t) & symbolize("?", i, j, t + 1) & symbolize('H', i, j, t) for X in ijneighbours]
                clauses2 = [to_cnf(x) for x in clauses2]
                clauses_union2 = clauses2[0]
                for clause in clauses2:
                    clauses_union2 = clauses_union2 | clause
                clauses_union2 = clauses_union2 >> (symbolize('S', i, j, t + 1) | symbolize('I', i, j, t+1))
                kb.tell(clauses_union2)
        # print("kb after infection constraints:")
        # print(kb.clauses)
        # sick areas stay sick for three turns exactly
        for i, j in map_indexes:
            # for t in range(turns):
            # if area is sick at turn 0
            # turns H after three turns:
            clauses = [symbolize("S", i, j, t) for t in range(turns)]
            clauses_union2 = []
            if turns > 2:
                for t in range(turns - 2):
                    clauses_union2.append((clauses[t] & clauses[t + 1] & clauses[t + 2] & symbolize('?', i, j, t + 3)) >> (
                            symbolize('H', i, j, t + 3) & ~symbolize("S", i, j, t + 3)))
                for clause in clauses_union2:
                    kb.tell(clause)
        # print("kb after sick areas duration constraint:")
        # print(kb.clauses)

        # quarantined areas stay quarantined for two turns
        for i, j in map_indexes:
            clauses = [symbolize("Q", i, j, t) for t in range(turns)]
            clauses_union3 = []
            clauses_union31 = []
            clauses_union32= []
            for t in range(turns - 1):
                clauses_union3.append((clauses[t] & clauses[t + 1] & symbolize('?', i, j, t + 2)) >> (
                        symbolize('H', i, j, t + 2) & ~symbolize("Q", i, j, t + 2)))
                if t < turns - 2:
                    clauses_union31.append((symbolize("S", i, j, t) & clauses[t+1] & symbolize('?', i, j, t + 2)) >> clauses[t+2])
            for clause in clauses_union3:
                kb.tell(clause)
            for clause in clauses_union31:
                kb.tell(clause)

        for i, j in map_indexes:
            clauses = [symbolize("S", i, j, t) for t in range(turns)]
            clauses_union7 = []
            clauses_union8 = []
            if turns > 1:
                kb.tell((clauses[0] & symbolize('?', i, j, 1)) >> ((~symbolize('H', i, j, 1) & symbolize("S", i, j, 1)) | (~symbolize('H', i, j, 1) & symbolize("Q", i, j, 1))))
            if turns> 2:
                kb.tell((clauses[0] & clauses[1] & symbolize('?', i, j, 2)) >> ((~symbolize('H', i, j, 2) & symbolize("S", i, j, 2)) | (~symbolize('H', i, j, 2) & symbolize("Q", i, j, 2))))
            if turns > 3:
                kb.tell((clauses[0] & clauses[1] & clauses[2] & symbolize('?', i, j, 3)) >> (symbolize('H', i, j, 3) & ~symbolize("S", i, j, 3)))
            for t in range(turns - 2):
                clauses_union7.append((symbolize('H', i, j, t) & clauses[t + 1] & symbolize('?', i, j, t+2)) >>((~symbolize('H', i, j, t + 2) & symbolize("S", i, j, t + 2)) | (~symbolize('H', i, j, t + 2) & symbolize('Q', i, j, t + 2))))
            for clause in clauses_union7:
                kb.tell(clause)
            for t in range(turns - 3):
                clauses_union8.append((symbolize('H', i, j, t) & clauses[t + 1] & clauses[t + 2] & symbolize('?', i, j, t+3)) >> ((
                        ~symbolize('H', i, j, t + 3) & symbolize("S", i, j, t + 3)) | (~symbolize('H', i, j, t + 3) & symbolize("Q", i, j, t + 3))))
            for clause in clauses_union8:
                kb.tell(clause)
        # print("kb after quarantined areas duration constraint 1:")
        # print(kb.clauses)

        # unknown areas can be eather H or S or I or Q
        for i, j in map_indexes:
            for index, observation in enumerate(observations):
                obs_index = index
                if observation[i][j] == '?':
                    # turns >= turn > 0 :               *****infer from past*****
                    # ?001 & H000 & (no S neighbours at turn 0) => H001
                    if obs_index > 0 and not any(
                            [observations[obs_index - 1][X[0]][X[1]] == 'S' for X in neighbours(i, j)]):
                        kb.tell(symbolize('H', i, j, obs_index - 1) >> (symbolize('H', i, j, obs_index) | symbolize('I', i, j, obs_index)))

                    if obs_index > 0 and any([observations[obs_index - 1][X[0]][X[1]] == 'S' for X in neighbours(i, j)]):
                        # ?001 & H000 & (S neighbours at turn 0) & num_of_police > 0 & num_of_medics = 0 => S001
                        if police_num and medics_num == 0:
                            # must check duration of quarantine
                            num_of_quar_areas = sum([observation[X[0]][X[1]] == 'Q' for X in map_indexes])
                            if num_of_quar_areas < police_num:
                                kb.tell((symbolize('H', i, j, obs_index - 1)) >> (
                                        symbolize('Q', i, j, obs_index) | symbolize('S', i, j, obs_index)))
                            else:
                                kb.tell((symbolize('H', i, j, obs_index - 1)) >> symbolize(
                                    'S', i, j, obs_index))
                        # ?001 & H000 & (S neighbours at turn 0) & num_of_police = 0 & num_of_medics > 0 => S001
                        if police_num == 0 and medics_num:
                            # must check duration of quarantine
                            num_of_vac_areas = sum(
                                [observationtag[X[0]][X[1]] == 'I' for X in map_indexes for observationtag in observations])
                            if num_of_vac_areas < medics_num:
                                kb.tell((symbolize('H', i, j, obs_index - 1)) >> (
                                        symbolize('I', i, j, obs_index) | symbolize('S', i, j, obs_index)))
                            else:
                                kb.tell(
                                    (symbolize('H', i, j, obs_index - 1)) >> symbolize(
                                        'S', i, j, obs_index))
                            # print(i, j, index)
                            # print((symbolize('S', i, j, obs_index-1)) >> (symbolize('S', i, j, obs_index) | symbolize('H', i, j, obs_index)))
                            kb.tell((symbolize('S', i, j, obs_index) | symbolize('H', i, j, obs_index)))
                            # kb.tell((symbolize('S', i, j, obs_index-1)) >> (symbolize('S', i, j, obs_index) | symbolize('H', i, j, obs_index)))
                        if police_num == 0 and medics_num == 0:
                            kb.tell((symbolize('S', i, j, obs_index) | symbolize('H', i, j, obs_index)))
                            kb.tell(~symbolize('I', i, j, obs_index))
                            kb.tell(~symbolize('Q', i, j, obs_index))

                    # turns > turn >= 0:                  *****infer from future*****
                    # ?002 & H003 => H002
                    # *************************
                    if 0 <= obs_index < turns - 1:
                        # does not include all situations possible but the most one (must check if works)
                        kb.tell(symbolize('H', i, j, obs_index + 1) >> symbolize('H', i, j, obs_index))


        # ?001 & H000 & (S neighbours at turn 0) & num_of_police>0 = num_of_medics = 0 => S001
        # if area is H it stays H in the next turn if no interference
        # if area is S it stays S in the next turn if no interference

        # if area is ? at i and all neighbours at

        # if num of Q areas must be num _of_police*turn
        for index, observation in enumerate(observations):
            num_of_Q_areas = sum([observation[X[0]][X[1]] == 'Q' for X in map_indexes])
            indexes_of_unk_areas = [X for X in map_indexes if observation[X[0]][X[1]] == '?']
            if len(indexes_of_unk_areas)>0:
                if num_of_Q_areas < police_num * index:
                    clause4 = symbolize('Q', indexes_of_unk_areas[0][0], indexes_of_unk_areas[0][1], index)
                    for i1, j1 in indexes_of_unk_areas:
                        clause4 = clause4 | symbolize('Q', i1, j1, index)
                    # print('this is clause4:')
                    # print(clause4)
                    kb.tell(clause4)
                if num_of_Q_areas == police_num * index:
                    clause5 = ~symbolize('Q', indexes_of_unk_areas[0][0], indexes_of_unk_areas[0][1], index)
                    for i1, j1 in indexes_of_unk_areas:
                        clause5 = clause5 & ~symbolize('Q', i1, j1, index)
                    kb.tell(clause5)
        # print("kb after quarantined areas duration constraint 2:")
        # print(kb.clauses)
        # if num of I areas must be num _of_medics*turn
        for index, observation in enumerate(observations):
            num_of_I_areas = sum([observation[X[0]][X[1]] == 'I' for X in map_indexes])
            indexes_of_unk_areas = [X for X in map_indexes if observation[X[0]][X[1]] == '?']
            if len(indexes_of_unk_areas) > 0:
                if num_of_I_areas < medics_num * index:
                    clause5 = symbolize('I', indexes_of_unk_areas[0][0], indexes_of_unk_areas[0][1], index)
                    for i2, j2 in indexes_of_unk_areas:
                        clause5 = clause5 | symbolize('I', i2, j2, index)
                    kb.tell(clause5)
                if num_of_I_areas == medics_num * index:
                    clause5 = ~symbolize('I', indexes_of_unk_areas[0][0], indexes_of_unk_areas[0][1], index)
                    for i2, j2 in indexes_of_unk_areas:
                        clause5 = clause5 & ~symbolize('I', i2, j2, index)
                    kb.tell(clause5)
        # if U at turn i then U at all turns ---- if I at turn i then I at turn i+1

        for index, observation in enumerate(observations):
            indexes_of_I_areas = [X for X in map_indexes if observation[X[0]][X[1]] == 'I']
            indexes_of_U_areas = [X for X in map_indexes if observation[X[0]][X[1]] == 'U']
            for i, j in indexes_of_I_areas:
                for t in range(index + 1, turns):
                    kb.tell(symbolize('I', i, j, t))
            for i, j in indexes_of_U_areas:
                for t in range(turns):
                    kb.tell(symbolize('U', i, j, t))

        for t in range(turns):
            for i, j in map_indexes:
                kb.tell(~symbolize('H', i, j, t) | ~symbolize('S', i, j, t)) # S or H not both true

        for t in range(turns-1):
            for i,j in map_indexes:
                if observations[t][i][j] =='H':
                    ijneighbours = neighbours(i, j)
                    if not any(observations[t][X[0]][X[1]]=='S' for X in ijneighbours):
                        if any(observations[t][X[0]][X[1]]=='?' for X in ijneighbours):
                            if observations[t+1][i][j] == 'S':
                                clauses = [symbolize('S', X[0], X[1],t) for X in ijneighbours if observations[t][X[0]][X[1]] == '?']
                                union_clauses10 = clauses[0]
                                for clause in clauses:
                                    union_clauses10 = union_clauses10|clause
                                kb.tell(union_clauses10)
    # agent must quarintine or medic

    result_in_dic = dict()
    for query in queries:
        if kb.ask(symbolize(query[2], query[0][0], query[0][1], query[1])):
            result_in_dic[query] = 'T'
        else:
            if not kb.ask(symbolize('H', query[0][0], query[0][1], query[1])) and not kb.ask(symbolize('S', query[0][0], query[0][1], query[1])) and not kb.ask(symbolize('Q', query[0][0], query[0][1], query[1]))and not kb.ask(symbolize('I', query[0][0], query[0][1], query[1]))and not kb.ask(symbolize('U', query[0][0], query[0][1], query[1])):
                result_in_dic[query] = '?'
            else:
                result_in_dic[query] = 'F'
    return result_in_dic
    # put your solution here, remember the format needed
