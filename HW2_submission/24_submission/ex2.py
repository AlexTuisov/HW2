
from pysat.solvers import Solver
from itertools import chain, combinations, product

ids = ['212197222', '315392639']


def initiate_dict(medics, police, obs_num, obs_rows, obs_cols):
    dict = {}
    index = 1

    if police == 0 and medics == 0:
        for i in range(obs_rows):
            for j in range(obs_cols):
                for t in range(obs_num):
                    dict[((i,j), t, 'H')] = index
                    dict[((i, j), t, 'S')] = index+1
                    dict[((i, j), t, 'U')] = index+2
                    index += 3
    elif medics == 0:
        for i in range(obs_rows):
            for j in range(obs_cols):
                for t in range(obs_num):
                    dict[((i,j), t, 'H')] = index
                    dict[((i, j), t, 'S')] = index+1
                    dict[((i, j), t, 'U')] = index+2
                    dict[((i, j), t, 'Q')] = index+3
                    index += 4
    elif police == 0:
        for i in range(obs_rows):
            for j in range(obs_cols):
                for t in range(obs_num):
                    dict[((i,j), t, 'H')] = index
                    dict[((i, j), t, 'S')] = index+1
                    dict[((i, j), t, 'U')] = index+2
                    dict[((i, j), t, 'I')] = index+3
                    index += 4
    else:
        for i in range(obs_rows):
            for j in range(obs_cols):
                for t in range(obs_num):
                    dict[((i,j), t, 'H')] = index
                    dict[((i, j), t, 'S')] = index+1
                    dict[((i, j), t, 'U')] = index+2
                    dict[((i, j), t, 'I')] = index+3
                    dict[((i, j), t, 'Q')] = index+4
                    index += 5
    return dict

#create KB from observations only:
def create_KB(observations, dict, police, medics):
    KB = []
    unknown_indexes = []

    if police == 0 and medics == 0:
        options = ['H', 'S', 'U']
    elif police == 0:
        options = ['H', 'S', 'U', 'I']
    elif medics == 0:
        options = ['H', 'S', 'U', 'Q']
    else:
        options = ['H', 'S', 'U', 'I', 'Q']

    for turn, obs_rows in enumerate(observations):
        for i, row in enumerate(obs_rows):
            for j, area in enumerate(row):
                if area != '?':
                    KB.append([dict[((i,j), turn, area)]])
                    for option in options:
                        if option != area:
                            KB.append([-dict[((i, j), turn, option)]])
                else:
                    unknown_indexes.append((i,j))
                    if turn == 0:
                        if police > 0:
                            KB.append([-dict[((i, j), turn, 'Q')]])
                        if medics > 0:
                            KB.append([-dict[((i, j), turn, 'I')]])
    return KB, unknown_indexes

def get_unknown_neighbors(observations, index, turn):
    i, j = index
    unknown_neighbors = []
    if i - 1 > 0 and observations[turn][i - 1][j] == '?':
        unknown_neighbors.append((i - 1, j))
    if i + 1 < len(observations[0]) and observations[turn][i + 1][j] == '?':
        unknown_neighbors.append((i + 1, j))
    if j - 1 > 0 and observations[turn][i][j - 1] == '?':
        unknown_neighbors.append((i, j - 1))
    if j + 1 < len(observations[0][0]) and observations[turn][i][j + 1] == '?':
        unknown_neighbors.append((i, j + 1))
    return unknown_neighbors

def get_sick_neighbors(observations, index, turn): #FIX???
    i, j = index
    sick_neighbors = []
    if i - 1 > 0 and observations[turn][i - 1][j] == 'S':
        sick_neighbors.append((i - 1, j))
    if i + 1 < len(observations[0]) and observations[turn][i + 1][j] == 'S':
        sick_neighbors.append((i + 1, j))
    if j - 1 > 0 and observations[turn][i][j - 1] == 'S':
        sick_neighbors.append((i, j - 1))
    if j + 1 < len(observations[0][0]) and observations[turn][i][j + 1] == 'S':
        sick_neighbors.append((i, j + 1))
    return sick_neighbors

def count_H_to_I(observations, turn):
    count = 0
    for i in range(len(observations[0])):
        for j in range(len(observations[0][0])):
            if observations[turn][i][j] == 'H' and observations[turn+1][i][j] == 'I':
                count += 1
    return count

def count_S_to_Q(observations, turn):
    count = 0
    for i in range(len(observations[0])):
        for j in range(len(observations[0][0])):
            if observations[turn][i][j] == 'S' and observations[turn + 1][i][j] == 'Q':
                count += 1
    return count

def H_neighbor_not_infected(observations, index, turn, medics):
    i, j = index
    if medics > 0:
        if i - 1 > 0:
            check_obs = observations[turn][i - 1][j]
            check_obs_next = observations[turn+1][i - 1][j]
            if check_obs == 'H' and not check_obs_next == 'S' and not check_obs_next == 'I':
                return True
        if i + 1 < len(observations[0]):
            check_obs = observations[turn][i + 1][j]
            check_obs_next = observations[turn + 1][i + 1][j]
            if check_obs == 'H' and not check_obs_next == 'S' and not check_obs_next == 'I':
                return True
        if j - 1 > 0:
            check_obs = observations[turn][i][j-1]
            check_obs_next = observations[turn+1][i][j-1]
            if check_obs == 'H' and not check_obs_next == 'S' and not check_obs_next == 'I':
                return True
        if j + 1 < len(observations[0][0]):
            check_obs = observations[turn][i][j+1]
            check_obs_next = observations[turn + 1][i][j+1]
            if check_obs == 'H' and not check_obs_next == 'S' and not check_obs_next == 'I':
                return True
    else:
        if i - 1 > 0:
            check_obs = observations[turn][i - 1][j]
            check_obs_next = observations[turn+1][i - 1][j]
            if check_obs == 'H' and not check_obs_next == 'S':
                return True
        if i + 1 < len(observations[0]):
            check_obs = observations[turn][i + 1][j]
            check_obs_next = observations[turn + 1][i + 1][j]
            if check_obs == 'H' and not check_obs_next == 'S':
                return True
        if j - 1 > 0:
            check_obs = observations[turn][i][j-1]
            check_obs_next = observations[turn+1][i][j-1]
            if check_obs == 'H' and not check_obs_next == 'S':
                return True
        if j + 1 < len(observations[0][0]):
            check_obs = observations[turn][i][j+1]
            check_obs_next = observations[turn + 1][i][j+1]
            if check_obs == 'H' and not check_obs_next == 'S':
                return True
    return False

def has_infecting_neighbors(observations, index, turn, medics):
    i, j = index
    if medics > 0:
        if i - 1 > 0:
            check_obs = observations[turn][i - 1][j]
            check_obs_next = observations[turn+1][i - 1][j]
            if check_obs == 'S' and not check_obs_next == 'Q':
                return True
        if i + 1 < len(observations[0]):
            check_obs = observations[turn][i + 1][j]
            check_obs_next = observations[turn + 1][i + 1][j]
            if check_obs == 'S' and not check_obs_next == 'Q':
                return True
        if j - 1 > 0:
            check_obs = observations[turn][i][j-1]
            check_obs_next = observations[turn+1][i][j-1]
            if check_obs == 'S' and not check_obs_next == 'Q':
                return True
        if j + 1 < len(observations[0][0]):
            check_obs = observations[turn][i][j+1]
            check_obs_next = observations[turn + 1][i][j+1]
            if check_obs == 'S' and not check_obs_next == 'Q':
                return True
    else:
        if i - 1 > 0 and observations[turn][i - 1][j] == 'S':
                return True
        if i + 1 < len(observations[0]) and observations[turn][i + 1][j] == 'S':
                return True
        if j - 1 > 0 and observations[turn][i][j-1] == 'S':
                return True
        if j + 1 < len(observations[0][0]) and observations[turn][i][j+1] == 'S':
                return True
    return False

def get_neighbors(observations, index):
    neighbors = []
    i,j = index
    if i - 1 > 0:
        neighbors.append((i - 1, j))
    if i + 1 < len(observations[0]):
        neighbors.append((i + 1, j))
    if j - 1 > 0:
        neighbors.append((i, j - 1))
    if j + 1 < len(observations[0][0]):
        neighbors.append((i, j + 1))
    return neighbors

def inference_for_H(observations, index_dict, medics, police, turn, index):
    cnf = []
    i, j = index

    sick_neighbors = get_sick_neighbors(observations, (i, j), turn)
    unknown_neighbors = get_unknown_neighbors(observations, (i, j), turn)

    if observations[turn + 1][i][j] == '?':  # H-> ?
        temp_cnf = [] #what are the options?

        if medics > 0: # consider I
            if count_H_to_I(observations, turn) < medics:  # has medics, so ? could turn to I
                temp_cnf.append(index_dict[((i, j), turn + 1, 'I')])

        if sick_neighbors: #consider S - if we can be sure
            # has a sick neighbor, that didn't turn to Q, so ? = S
            # we don't check S that turned to ?
            temp_cnf.append(index_dict[((i, j), turn + 1, 'S')])
            cnf.append([-index_dict[((i, j), turn + 1, 'H')]])
            if police > 0:
                cnf.append([-index_dict[((i, j), turn + 1, 'Q')]])

        elif not sick_neighbors and not unknown_neighbors:
            # doesn't have ? neighbors or S neighbors, so stay will stay H or I if possible
            temp_cnf.append(index_dict[((i, j), turn + 1, 'H')])
            cnf.append([-index_dict[((i, j), turn + 1, 'S')]])
            if police > 0:
                cnf.append([-index_dict[((i, j), turn + 1, 'Q')]])

        if temp_cnf:
            cnf.append(temp_cnf)


    elif observations[turn + 1][i][j] == 'S':

        # is doesn't have a sick neighbor, and has an unknown neighbor:
        if not sick_neighbors and unknown_neighbors:
            if len(unknown_neighbors) == 1:
                cnf.append([index_dict[(unknown_neighbors[0], turn, 'S')]])
                cnf.append([-index_dict[(unknown_neighbors[0], turn, 'H')]])
                cnf.append([-index_dict[(unknown_neighbors[0], turn, 'U')]])
                if medics > 0:
                    cnf.append([-index_dict[(unknown_neighbors[0], turn, 'I')]])
                if police > 0:
                    cnf.append([-index_dict[(unknown_neighbors[0], turn, 'Q')]])

            else: #one of the neighbors has to be sick and inecting (not to turn to Q)
                temp = []
                if police > 0:
                    for unknown_index in unknown_neighbors:
                        temp.append([index_dict[(unknown_index, turn, 'S')], -index_dict[(unknown_index, turn+1, 'Q')]])
                    cnf.append(list(product(*temp)))
                else:
                    for unknown_index in unknown_neighbors:
                        temp.append(index_dict[(unknown_index, turn, 'S')])
                    cnf.append(temp)


    elif observations[turn + 1][i][j] == 'H':  #all unknown neighbors are not S, or S and then Q

        # sick neighbors and no unknowns - all sick must get Q:
        if sick_neighbors and not unknown_neighbors:
            for sick in sick_neighbors:
                cnf.append([index_dict[(sick, turn + 1, 'Q')]])

        # no sick neighbors but has unknowns - unknowns must be S then Q or not S
        elif not sick_neighbors and unknown_neighbors:
            for unknown_index in unknown_neighbors:
                if police > 0:
                    cnf.append([-index_dict[(unknown_index, turn, 'S')], index_dict[(unknown_index, turn + 1, 'Q')]])
                else:
                    cnf.append([-index_dict[(unknown_index, turn, 'S')]])

        #has sick neighbors and unknowns - sick must get Q, and unknowns are either S then Q or not S
        elif sick_neighbors and unknown_neighbors:
            for sick in sick_neighbors:
                cnf.append([index_dict[(sick, turn + 1, 'Q')]])
                cnf.append([-index_dict[(sick, turn + 1, 'H')]])
                cnf.append([-index_dict[(sick, turn + 1, 'S')]])
                if medics > 0:
                    cnf.append([-index_dict[(sick, turn + 1, 'I')]])

            for unknown_index in unknown_neighbors:
                if police > 0:
                    cnf.append([-index_dict[(unknown_index, turn, 'S')], index_dict[(unknown_index, turn + 1, 'Q')]])
                else:
                    cnf.append([-index_dict[(unknown_index, turn, 'S')]])

    return cnf

def inference_for_I(observations, dict_of_all, medics, police, turn, index):
    cnf = []
    i, j = index

    if observations[turn + 1][i][j] == '?':
        cnf.append([dict_of_all[((i, j), turn + 1, 'I')]])
        cnf.append([-dict_of_all[((i, j), turn + 1, 'H')]])
        cnf.append([-dict_of_all[((i, j), turn + 1, 'S')]])
        if police > 0:
            cnf.append([-dict_of_all[((i, j), turn + 1, 'Q')]])

    return cnf

def inference_for_S(observations, index_dict, medics, police, turn, index, options):
    cnf = []
    i, j = index

    '''
    if turn == 0:
        #case1 - SSSH, case2 - SQQH, case3 - SSQQH, case4 -  SSSQQH

        if police > 0:
            if len(observations) == 2:
                cnf.append([index_dict[(i,j), turn+1, 'S'], index_dict[(i,j), turn+1, 'Q']])
                cnf.append([-index_dict[(i, j), turn + 1, 'H']])
                if medics > 0:
                    cnf.append([-index_dict[(i, j), turn + 1, 'I']])
            if len(observations) == 3:
                case1 = [index_dict[(i,j), turn+1, 'S'], index_dict[(i,j), turn+2, 'S']]
                case2 = [index_dict[(i,j), turn+1, 'Q'], index_dict[(i,j), turn+2, 'Q']]
                case3 = [index_dict[(i, j), turn + 1, 'S'], index_dict[(i, j), turn + 2, 'Q']]
                products = list(product(*[case1, case2, case3]))
                for p in products:
                    cnf.append(list(p))

                cnf.append([-index_dict[(i, j), turn + 1, 'H']])
                cnf.append([-index_dict[(i, j), turn + 2, 'H']])
                if medics > 0:
                    cnf.append([-index_dict[(i, j), turn + 1, 'I']])
                    cnf.append([-index_dict[(i, j), turn +2,  'I']])

            if len(observations) >= 4 :
                case2 = [index_dict[(i, j), turn + 1, 'Q'], index_dict[(i, j), turn + 2, 'Q'], index_dict[(i, j), turn + 3, 'H']]
                if len(observations) == 4:
                    case1 = [index_dict[(i, j), turn + 1, 'S'], index_dict[(i, j), turn + 2, 'S'],
                             index_dict[(i, j), turn + 3, 'S']]
                    case3 = [index_dict[(i, j), turn + 1, 'S'], index_dict[(i, j), turn + 2, 'Q'], index_dict[(i, j), turn + 3, 'Q']]
                    case4 = [index_dict[(i, j), turn + 1, 'S'], index_dict[(i, j), turn + 2, 'S'], index_dict[(i, j), turn + 3, 'Q']]
                else:
                    case1 = [index_dict[((i, j), turn + 1, 'S')], index_dict[((i, j), turn + 2, 'S')], index_dict[((i, j), turn + 3, 'S')],
                             index_dict[((i, j), turn + 4, 'H')]]
                    case3 = [index_dict[((i, j), turn + 1, 'S')], index_dict[((i, j), turn + 2, 'Q')], index_dict[((i, j), turn + 3, 'Q')],
                             index_dict[((i, j), turn + 4, 'H')]]
                    if len(observations) == 5:
                        case4 = [index_dict[((i, j), turn + 1, 'S')], index_dict[((i, j), turn + 2, 'S')],index_dict[((i, j), turn + 3, 'Q')],
                                 index_dict[((i, j), turn + 4, 'Q')]]
                    else:
                        case4 = [index_dict[((i, j), turn + 1, 'S')], index_dict[((i, j), turn + 2, 'S')],
                                 index_dict[((i, j), turn + 3, 'Q')], index_dict[((i, j), turn + 4, 'Q')],
                                 index_dict[((i, j), turn + 5, 'H')]]

                products = list(product(*[case1, case2, case3, case4]))
                for p in products:
                    cnf.append(list(p))

                cnf.append([-index_dict[(i, j), turn + 1, 'H']])
                cnf.append([-index_dict[(i, j), turn + 2, 'H']])
                if medics > 0:
                    cnf.append([-index_dict[(i, j), turn + 1, 'I']])
                    cnf.append([-index_dict[(i, j), turn + 2, 'I']])
                    cnf.append([-index_dict[(i, j), turn + 3, 'I']])

        else: #if there is no police, and S on turn 0
            if len(observations) == 2:
                cnf.append([index_dict[(i,j), turn+1, 'S']])
                cnf.append([-index_dict[(i, j), turn + 1, 'H']])
                if medics > 0:
                    cnf.append([-index_dict[(i, j), turn + 1, 'I']])
            if len(observations) == 3:
                cnf.append([index_dict[(i,j), turn+1, 'S']])
                cnf.append([index_dict[(i, j), turn + 2, 'S']])
                cnf.append([-index_dict[(i, j), turn + 1, 'H']])
                cnf.append([-index_dict[(i, j), turn + 2, 'H']])
                if medics > 0:
                    cnf.append([-index_dict[(i, j), turn + 1, 'I']])
                    cnf.append([-index_dict[(i, j), turn + 2, 'I']])
            if len(observations) == 4:
                cnf.append([index_dict[(i, j), turn + 1, 'S']])
                cnf.append([index_dict[(i, j), turn + 2, 'S']])
                cnf.append([index_dict[(i, j), turn + 3, 'H']])
                cnf.append([-index_dict[(i, j), turn + 1, 'H']])
                cnf.append([-index_dict[(i, j), turn + 2, 'H']])
                cnf.append([-index_dict[(i, j), turn + 3, 'S']])
                if medics > 0:
                    cnf.append([-index_dict[(i, j), turn + 1, 'I']])
                    cnf.append([-index_dict[(i, j), turn + 2, 'I']])
                    cnf.append([-index_dict[(i, j), turn + 3, 'I']])
        '''

    if observations[turn + 1][i][j] == 'Q':
        if turn+2 < len(observations) and observations[turn+2][i][j] == '?':
            cnf.append([index_dict[((i, j), turn+2, 'Q')]])
            for op in options:
                if op != 'Q':
                    cnf.append([-index_dict[((i, j), turn + 2, op)]])


    elif observations[turn + 1][i][j] == 'S':
        pass

    elif observations[turn + 1][i][j] == 'H':
        if turn >= 2:
            cnf.append([index_dict[((i, j), turn - 1, 'S')]])
            cnf.append([index_dict[((i, j), turn - 2, 'S')]])

    elif observations[turn + 1][i][j] == '?':
        temp_cnf = []

        if medics > 0:  #can't be I next turn:
            cnf.append([-index_dict[((i,j), turn+1, 'I')]])

        if count_S_to_Q(observations, turn) < police: #there could be available teams
            temp_cnf.append(index_dict[((i, j), turn + 1, 'Q')])

        if turn < 2:  # 0<turn<2
            temp_cnf.append(index_dict[((i, j), turn + 1, 'S')])
            cnf.append([-index_dict[((i, j), turn + 1, 'H')]])

        elif turn >= 2:
            if observations[turn - 1][i][j] == 'S' and observations[turn - 2][i][j] == 'S': # was SSS
                temp_cnf.append(index_dict[((i, j), turn + 1, 'H')])
                cnf.append([-index_dict[((i, j), turn + 1, 'S')]])

            else: #couldn't be SSS and heal:
                if observations[turn - 1][i][j] == 'S' and observations[turn - 2][i][j] == 'H':
                    temp_cnf.append(index_dict[((i, j), turn + 1, 'S')])
                    cnf.append([-index_dict[((i, j), turn + 1, 'H')]])

        if temp_cnf:
            cnf.append(temp_cnf)

    return cnf

def inference_for_Q(observations, dict_of_all, medics, police, turn, index, options):
    cnf = []
    i, j = index

    #information about the past:
    if turn == 1 and observations[turn - 1][i][j] == '?':
            cnf.append([dict_of_all[((i, j), turn-1, 'S')]])
            for op in options:
                if op != 'S':
                    cnf.append([-dict_of_all[((i, j), turn - 1, op)]])


    elif turn >= 2 and observations[turn - 1][i][j] == '?':
            #was either Q on previous turn and S before, or S on previous turn:,
            cnf.append([dict_of_all[((i, j), turn - 1, 'S')], dict_of_all[((i,j), turn-1, 'Q')]])
            cnf.append([dict_of_all[((i, j), turn - 1, 'S')], dict_of_all[((i, j), turn - 2, 'S')]])
            cnf.append([-dict_of_all[((i, j), turn - 1, 'H')]])
            cnf.append([-dict_of_all[((i, j), turn - 2, 'H')]])

    #information about the future:
    if observations[turn + 1][i][j] == 'Q':
        if observations[turn - 1][i][j] == '?':
            cnf.append([dict_of_all[((i, j), turn - 1, 'S')]])
            for op in options:
                if op != 'S':
                    cnf.append([-dict_of_all[((i, j), turn - 1, op)]])

    elif observations[turn + 1][i][j] == 'H':
        if turn >= 2:
            cnf.append([dict_of_all[((i, j), turn - 1, 'Q')]])
            cnf.append([dict_of_all[((i, j), turn - 2, 'S')]])
            for op in options:
                if op != 'Q':
                    cnf.append([-dict_of_all[((i, j), turn - 1, op)]])
                if op != 'S':
                    cnf.append([-dict_of_all[((i, j), turn - 2, op)]])

    elif observations[turn + 1][i][j] == '?':
        #will not be S or I next turn:
        cnf.append([-dict_of_all[((i, j), turn + 1, 'S')]])
        if medics > 0:
            cnf.append([-dict_of_all[((i, j), turn + 1, 'I')]])

        if turn == 1:
            cnf.append([dict_of_all[((i, j), turn + 1, 'Q')]])
            for op in options:
                if op != 'Q':
                    cnf.append([-dict_of_all[((i, j), turn + 1, op)]])

        if turn > 1:
            if observations[turn - 1][i][j] == 'Q':
                cnf.append([dict_of_all[((i, j), turn + 1, 'H')]])
                cnf.append([-dict_of_all[((i, j), turn + 1, 'Q')]])

            elif observations[turn - 1][i][j] != '?': #was something that is not Q
                cnf.append([dict_of_all[((i, j), turn + 1, 'Q')]])

            else:  # prev turn was '?'
                #either Q before and H next, or S before and Q next:
                QQH = [dict_of_all[((i, j), turn - 1, 'Q')], dict_of_all[((i, j), turn + 1, 'H')]]
                SQQ = [dict_of_all[((i, j), turn - 1, 'S')], dict_of_all[((i, j), turn + 1, 'Q')]]
                cnf.append(list(product(*[QQH, SQQ])))

                #couldn't be H or I on previous turn:
                cnf.append([-dict_of_all[((i, j), turn - 1, 'H')]])
                if medics > 0:
                    cnf.append([-dict_of_all[((i, j), turn - 1, 'I')]])

    return cnf

def inference_for_unknown(observations, index_dict, medics, police, turn, index, options):
    cnf = []
    i, j = index

    # neighbor not infected - ? is either not S, or S that turned to Q
    if H_neighbor_not_infected(observations, index, turn, medics):
        if police > 0:
            cnf.append([-index_dict[((i,j), turn, 'S')], index_dict[((i,j), turn+1, 'Q')]])
        else:
            cnf.append([-index_dict[((i, j), turn, 'S')]])

    # if ? turned to Q, was either Q or S on previous turn
    if observations[turn + 1][i][j] == 'Q': #must have police
        cnf.append([index_dict[((i, j), turn, 'Q')], index_dict[((i, j), turn, 'S')]])
        cnf.append([-index_dict[((i, j), turn, 'H')]])
        if medics > 0:
            cnf.append([-index_dict[((i, j), turn, 'I')]])

    elif observations[turn + 1][i][j] == '?':

        if turn+2 < len(observations):
            if has_infecting_neighbors(observations, index, turn, medics) and \
                H_neighbor_not_infected(observations, index, turn+1, medics):
                if medics>0:
                    cnf.append([-index_dict[((i,j), turn, 'H')], index_dict[((i,j), turn+1, 'I')]])
                else:
                    cnf.append([-index_dict[((i, j), turn, 'H')]])

        #check if has neighbors that could only be infected by this area - then it was S
        neighbors = get_neighbors(observations, index)
        for neighbor in neighbors:
            if not has_infecting_neighbors(observations, neighbor, turn, medics):
                n_i, n_j = neighbor
                if observations[turn][n_i][n_j] == 'H' and observations[turn+1][n_i][n_j] == 'S':
                    cnf.append([index_dict[((i, j), turn, 'S')]])
                    cnf.append([-index_dict[((i, j), turn, 'H')]])
                    for t in range(len(observations)):
                        cnf.append([-index_dict[((i, j), t, 'U')]])
                    if police > 0:
                        cnf.append([-index_dict[((i, j), turn, 'Q')]])
                    if medics > 0:
                        for t in range(turn+1):
                            cnf.append([-index_dict[((i, j), t, 'I')]])

                    #for previous turn:
                    if turn != 0:
                        cnf.append([index_dict[((i,j), turn-1, 'S')], index_dict[((i,j), turn-1, 'H')]])
                        if police>0:
                            cnf.append([-index_dict[((i, j), turn - 1, 'Q')]])

                    #for next turn:
                    if police > 0:
                        if turn < 3:
                            cnf.append([index_dict[((i, j), turn+1, 'S')], index_dict[((i, j), turn+1, 'Q')]])
                            cnf.append([-index_dict[((i, j), turn + 1, 'H')]])
                    else:
                        if turn < 3:
                            cnf.append([index_dict[((i, j), turn + 1, 'S')]])
                            cnf.append([-index_dict[((i, j), turn + 1, 'H')]])

                    if medics > 0:
                        cnf.append([-index_dict[((i, j), turn+1, 'I')]])
                    continue

        #check if has an uninfected neighbore - then it is not S, or S then Q:
        if H_neighbor_not_infected(observations, index, turn, medics):
            if police > 0:
                cnf.append([-index_dict[((i, j), turn, 'S')], index_dict[(i,j), turn+1, 'Q']])
            else:
                cnf.append([-index_dict[((i, j), turn, 'S')]])


    #if ? turned to H, was either H previously, or Q or S
    elif observations[turn + 1][i][j] == 'H':
        if turn == 0:
            cnf.append([index_dict[((i, j), turn, 'H')]])
            for op in options:
                if op != 'H':
                    cnf.append([-index_dict[((i, j), turn, op)]])
        elif turn < 3:
            cnf.append([index_dict[((i, j), turn, 'H')]])
            for op in options:
                if op != 'H':
                    cnf.append([-index_dict[((i, j), turn, op)]])
            if observations[turn-1][i][j] == '?':
                cnf.append([index_dict[((i, j), turn-1, 'H')]])
                for op in options:
                    if op != 'H':
                        cnf.append([-index_dict[((i, j), turn-1, op)]])
            if turn == 2:
                if observations[turn - 2][i][j] == '?':
                    cnf.append([index_dict[((i, j), turn - 2, 'H')]])
                    for op in options:
                        if op != 'H':
                            cnf.append([-index_dict[((i, j), turn - 2, op)]])

        else: #was either S then healed, or S then QQ, or H previously
            temp_Q = [index_dict[((i, j), turn - 2, 'S' )], index_dict[((i, j), turn - 1, 'Q')], index_dict[((i, j), turn, 'Q')]]
            temp_S = [index_dict[((i, j), turn - 3, 'H')], index_dict[((i, j), turn - 2, 'S')],
                      index_dict[((i, j), turn-1, 'S')], index_dict[((i,j), turn, 'S')]]
            temp_H = [index_dict[((i,j), turn, 'H')]]

            #DON'T KNOW IF WORKS
            products = list(product(*[temp_H, temp_Q, temp_S]))
            cnf += products


    elif observations[turn+1][i][j] == 'I':
        cnf.append([index_dict[((i,j), turn, 'H')], index_dict[((i,j), turn, 'I')]])
        cnf.append([-index_dict[((i, j), turn, 'S')]])
        if police > 0:
            cnf.append([-index_dict[((i, j), turn, 'Q')]])

    elif observations[turn + 1][i][j] == 'S':
        how_sick = []
        if police > 0:
            if i - 1 > 0:
                how_sick.append([index_dict[((i - 1, j), turn, 'S')], -index_dict[((i - 1, j), turn, 'Q')]])
            if i + 1 < len(observations[0]):
                how_sick.append([index_dict[((i + 1, j), turn, 'S')], -index_dict[((i + 1, j), turn, 'Q')]])
            if j - 1 > 0:
                how_sick.append([index_dict[((i, j - 1), turn, 'S')], -index_dict[((i, j-1), turn, 'Q')]])
            if j + 1 < len(observations[0][0]):
                how_sick.append([index_dict[((i, j + 1), turn, 'S')], -index_dict[((i, j+1), turn, 'Q')]])
            how_sick.append([index_dict[((i, j), turn, 'S')]])

            products = list(product(*how_sick))
            if len(how_sick) != 1:
                for p in products:
                    cnf.append(list(p))

        else:
            if i - 1 > 0:
                how_sick.append(index_dict[((i - 1, j), turn, 'S')])
            if i + 1 < len(observations[0]):
                how_sick.append(index_dict[((i + 1, j), turn, 'S')])
            if j - 1 > 0:
                how_sick.append(index_dict[((i, j - 1), turn, 'S')])
            if j + 1 < len(observations[0][0]):
                how_sick.append(index_dict[((i, j + 1), turn, 'S')])
            how_sick.append(index_dict[((i, j), turn, 'S')])
            cnf.append(how_sick)

    return cnf

def check_available_teams(index_dict, KB, add_to_KB, observations, police, medics):
    teams_cnf = []
    all_cnf = KB + add_to_KB

    #check how many teams were used or not used for sure on each turn:
    police_used, medics_used = [], []
    police_not_used, medics_not_used = [], []

    obs_num = len(observations)

    for turn in range(obs_num-1):
        unknown_indexes = []
        police_used.append([])
        medics_used.append([])
        police_not_used.append([])
        medics_not_used.append([])
        for i in range(len(observations[0])):
            for j in range(len(observations[0][0])):
                if observations[turn][i][j] == '?':
                    unknown_indexes.append((i,j))
                if medics > 0:
                    if [index_dict[((i,j), turn, 'H')]] in all_cnf and [index_dict[((i,j), turn+1, 'I')]] in all_cnf:
                        medics_used[turn].append((i,j))
                    if [index_dict[((i,j), turn, 'H')]] in all_cnf and [-index_dict[((i,j), turn+1, 'I')]] in all_cnf:
                        medics_not_used[turn].append((i,j))
                if police > 0:
                    if [index_dict[((i,j), turn, 'S')]] in all_cnf and [index_dict[((i,j), turn+1, 'Q')]] in all_cnf:
                        police_used[turn].append((i,j))
                    if [index_dict[((i,j), turn, 'S')]] in all_cnf and [-index_dict[((i,j), turn+1, 'Q')]] in all_cnf:
                        police_not_used[turn].append((i,j))

        if len(medics_used[turn]) == medics and medics != 0:
            #insert that anyone else couldn't be I next turn, unless was I prev turn:
            for i in range(len(observations[0])):
                for j in range(len(observations[0][0])):
                    if (i,j) not in medics_used[turn]:
                        teams_cnf.append([-index_dict[((i,j), turn+1, 'I')], index_dict[((i,j), turn, 'I')]])
        elif medics != 0:
            if len(medics_not_used[turn]) > 0: #meaning medics were used on '?'
                possible_uses = []
                for index in unknown_indexes:
                    if police > 0:
                        possible_uses.append([index_dict[(index, turn, 'H')], index_dict[(index, turn + 1, 'I')],
                                              -index_dict[(index, turn, 'S')], -index_dict[(index, turn, 'Q')],
                                              -index_dict[(index, turn, 'I')], -index_dict[(index, turn, 'U')],
                                              -index_dict[(index, turn+1, 'S')], -index_dict[(index, turn+1, 'H')],
                                              -index_dict[(index, turn+1, 'Q')], -index_dict[(index, turn+1, 'U')]])
                    else:
                        possible_uses.append([index_dict[(index, turn, 'H')], index_dict[(index, turn + 1, 'I')],
                                                -index_dict[(index, turn, 'S')], -index_dict[(index, turn, 'U')],
                                                -index_dict[(index, turn, 'I')], -index_dict[(index, turn + 1, 'S')],
                                                -index_dict[(index, turn + 1, 'H')], -index_dict[(index, turn + 1, 'U')]])
                # create combinations:
                combos = list(combinations(possible_uses, min(len(unknown_indexes), medics - len(medics_used[turn]))))
                prepare_for_product = []
                for com in combos:
                    temp = list(com)
                    temp = [item for sublist in temp for item in sublist]
                    prepare_for_product.append(temp)
                products = list(product(*prepare_for_product))
                for p in products:
                    teams_cnf.append(list(p))

        if len(police_used[turn]) == police and police != 0:
            # insert that anyone else couldn't be Q next turn, unless was Q prev turn:
            for i in range(len(observations[0])):
                for j in range(len(observations[0][0])):
                    if (i,j) not in police_used[turn]:
                        teams_cnf.append([-index_dict[((i,j), turn+1, 'Q')], index_dict[((i,j), turn, 'Q')]])

        elif police != 0: #used must be smaller than what we have
            if len(police_not_used[turn]) > 0:  # meaning police were used on '?'
                possible_uses = []
                for index in unknown_indexes:
                    if medics > 0:
                        possible_uses.append([index_dict[(index, turn, 'S')], index_dict[(index, turn + 1, 'Q')],
                                              -index_dict[(index, turn, 'H')], -index_dict[(index, turn, 'Q')],
                                              -index_dict[(index, turn, 'I')], -index_dict[(index, turn, 'U')],
                                              -index_dict[(index, turn+1, 'S')], -index_dict[(index, turn+1, 'H')],
                                              -index_dict[(index, turn+1, 'I')], -index_dict[(index, turn+1, 'U')]])
                    else:
                        possible_uses.append([index_dict[(index, turn, 'S')], index_dict[(index, turn + 1, 'Q')],
                                                -index_dict[(index, turn, 'H')], -index_dict[(index, turn, 'Q')],
                                                -index_dict[(index, turn, 'U')], -index_dict[(index, turn + 1, 'S')],
                                                -index_dict[(index, turn + 1, 'H')], -index_dict[(index, turn + 1, 'U')]])
                # create combinations:
                combos = list(combinations(possible_uses, min(len(unknown_indexes), police - len(police_used[turn]))))
                prepare_for_product = []
                for com in combos:
                    temp = list(com)
                    temp = [item for sublist in temp for item in sublist]
                    prepare_for_product.append(temp)
                products = list(product(*prepare_for_product))
                for p in products:
                    teams_cnf.append(list(p))
            else:
                pass

    return teams_cnf

def inference_main(observations, index_dict, medics, police, options, KB):
    cnf = []

    # inference for all I ahead:
    for i in range(len(observations[0])):
        for j in range(len(observations[0][0])):
            for turn in range(len(observations)):
                if observations[turn][i][j] == 'I':
                    for sub_turn in range(turn, len(observations)):
                        if observations[sub_turn][i][j] == '?':
                            cnf.append([index_dict[((i, j), sub_turn, 'I')]])
                            for op in options:
                                if op != 'I':
                                    cnf.append([-index_dict[((i, j), sub_turn, op)]])
                    continue

    #inference for all U/non-U:
    for i in range(len(observations[0])):
        for j in range(len(observations[0][0])):
            for turn in range(len(observations)):
                if observations[turn][i][j] == 'U':
                    for sub_turn in range(len(observations)):
                        if observations[sub_turn][i][j] == '?':
                            cnf.append([index_dict[((i, j), sub_turn, 'U')]])
                            for op in options:
                                if op != 'U':
                                    cnf.append([-index_dict[((i, j), sub_turn, op)]])
                    continue
                elif observations[turn][i][j] != '?':
                    for sub_turn in range(len(observations)):
                        if observations[sub_turn][i][j] == '?':
                            cnf.append([-index_dict[((i, j), sub_turn, 'U')]])
                    continue

    #print("U:", cnf)

    for turn in range(len(observations) - 1):
        for i in range(len(observations[turn])):
            for j in range(len(observations[turn][0])):

                if observations[turn][i][j] == 'H':
                    sub_cnf = inference_for_H(observations, index_dict, medics, police, turn, (i, j))
                    cnf += sub_cnf
                    #print("H:", sub_cnf)

                elif observations[turn][i][j] == 'S':
                    sub_cnf = inference_for_S(observations, index_dict, medics, police, turn, (i, j), options)
                    cnf += sub_cnf
                    #print("S:", sub_cnf)

                elif observations[turn][i][j] == 'Q':
                    sub_cnf = inference_for_Q(observations, index_dict, medics, police, turn, (i, j), options)
                    cnf += sub_cnf
                    #print("Q:", sub_cnf)

                elif observations[turn][i][j] == 'I':
                    sub_cnf = inference_for_I(observations, index_dict, medics, police, turn, (i, j))
                    cnf += sub_cnf
                    #print("I:", sub_cnf )

                elif observations[turn][i][j] == '?':
                    sub_cnf = inference_for_unknown(observations, index_dict, medics, police, turn, (i,j), options)
                    cnf += sub_cnf
                    #print("?:", sub_cnf)

    cnf += check_available_teams(index_dict, KB, cnf, observations, police, medics)

    return cnf

def send_to_solver(query, KB, obs_num, index_dict, police, medics, obs_rows, obs_cols, observations):
    #print(query, "medics:", medics, "police:", police)
    index, turn, area = query

    if police == 0 and medics == 0:
        options = ['H', 'S', 'U']
    elif police == 0:
        options = ['H', 'S', 'U', 'I']
    elif medics == 0:
        options = ['H', 'S', 'U', 'Q']
    else:
        options = ['H', 'S', 'U', 'I', 'Q']

    add_to_KB = inference_main(observations, index_dict, medics, police, options, KB)
    s = Solver(name='g4')


    if medics == 0 and police == 0:
        if area == 'U':
            order = ['S', 'H']
        elif area == 'S':
            order = ['U', 'H']
        elif area == 'H':
            order = ['U', 'S']

    elif police == 0: #only medics
        if area == 'U':
            order = ['S', 'H', 'I']
        elif area == 'S':
            order = ['U', 'H', 'I']
        elif area == 'H':
            order = ['S', 'S', 'I']
        elif area == 'I':
            order = ['U', 'S', 'H']

    elif medics == 0: #only police
        if area == 'U':
            order = ['S', 'H', 'Q']
        elif area == 'S':
            order = ['U', 'H', 'Q']
        elif area == 'H':
            order = ['U', 'S', 'Q']
        elif area == 'Q':
            order = ['U', 'S', 'H']

    else: #has both teams
        if area == 'U':
            order = ['S', 'H','Q', 'I']
        elif area == 'S':
            order = ['U', 'H', 'Q', 'I']
        elif area == 'H':
            order = ['U', 'S', 'Q', 'I']
        elif area == 'Q':
            order = ['U', 'S', 'H', 'I']
        elif area == 'I':
            order = ['U', 'S', 'H', 'Q']

    # add KB:
    for info in KB:
        s.add_clause(info)
    for c in add_to_KB:
        s.add_clause(c)
    s.add_clause([index_dict[query]])
    wanted_result = s.solve()
    #print(query[2], wanted_result)

    #check other options:
    o_results = []
    for o in order:
        temp_s = Solver(name='g4')
        for info in KB:
            temp_s.add_clause(info)
        for c in add_to_KB:
            temp_s.add_clause(c)
        temp_s.add_clause([index_dict[(index, turn, o)]])

        temp_result = temp_s.solve()
        #print(o, temp_result)
        o_results.append(temp_result)

    #check final result:
    if wanted_result == False:
        return 'F'
    else:
        for result in o_results:
            if result == True:
                return '?'
        return 'T'

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

    obs_rows = len(observations[0])
    obs_cols = len(observations[0][0])
    obs_num = len(observations)

    index_dict = initiate_dict(medics, police, obs_num, obs_rows, obs_cols)
    KB, unknown_indexes = create_KB(observations, index_dict, police, medics)

    answers = {}
    for q in queries:
        answers[q] = send_to_solver(q, KB, obs_num, index_dict, police, medics, obs_rows, obs_cols, observations)

    return answers
