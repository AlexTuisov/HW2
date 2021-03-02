ids = ['308036441', '316407873']
from utils import *
from pysat.formula import CNF
from pysat.solvers import Solver
from sympy.logic import simplify_logic
from sympy.logic.boolalg import to_cnf, is_cnf, Equivalent
from sympy import symbols
def solve_problem(input):
    pass
    """ 
    every cell in the observations matrix will be represented by:                  
                            _ ____ _
    
    first digit will be the state by the legend below
    middle digits will be the index in the flattered matrix 
    last digit will be the round
     
    legend:
        
        +- 1 = U
        +- 2 = H
        +- 3 = S
        +- 4 = I
        +- 5 = Q 
    """
    police = input["police"]
    medics = input["medics"]
    queries = input["queries"]
    cnf = CNF()
    obs_control = ()
    #
    # Initial state + goal:
    #
    control = []
    max_round = len(input["observations"])
    for round in range(len(input["observations"])):
        turn = input["observations"][round]
        # divide all observations to clauses for CNF
        idx = 1
        for line in range(len(turn)):
            for col in range(len(turn[line])):
                state1 = 0
                if turn[line][col] == 'U':
                    state1 = 1
                    temp = '1' + str(idx) + str(round)
                    cnf.append([int(temp)])
                    control.append([temp])
                    idx += 1
                if turn[line][col] == 'H':
                    state1 = 2
                    temp = '2' + str(idx) + str(round)
                    cnf.append([int(temp)])
                    control.append([temp])
                    idx += 1
                if turn[line][col] == 'S':
                    state1 = 3
                    temp = '3' + str(idx) + str(round)
                    cnf.append([int(temp)])
                    control.append([temp])
                    idx += 1
                if turn[line][col] == 'I':
                    state1 = 4
                    temp = '4' + str(idx) + str(round)
                    cnf.append([int(temp)])
                    control.append([temp])
                    idx += 1
                if turn[line][col] == 'Q':
                    state1 = 5
                    temp = '5' + str(idx) + str(round)
                    cnf.append([int(temp)])
                    control.append([temp])
                    idx += 1
                if turn[line][col] == '?':
                    state1 = 6
                    temp_arr = []
                    temp2 = []
                    for i in ['1', '2', '3', '4', '5']:
                        temp = i + str(idx) + str(round)
                        temp_arr.append(int(temp))
                        temp2.append(temp)
                    cnf.append(temp_arr)
                    control.append(temp2)
                    for i in ['1', '2', '3', '4', '5']:
                        for j in ['1', '2', '3', '4', '5']:
                            if i == j:
                                continue
                            else:
                                temp = [int('-' + i + str(idx) + str(round)), int('-' + j + str(idx) + str(round))]
                                temp2 = [int('-' + j + str(idx) + str(round)), int('-' + i + str(idx) + str(round))]
                                if temp not in cnf.clauses:
                                    cnf.append(temp)
                                if temp2 not in cnf.clauses:
                                    cnf.append(temp2)
                    idx += 1
                if state1 != 6:
                    for i in range(1, 6):
                        if i == state1:
                            continue
                        else:
                            temp = "-" + str(i) + str(idx - 1) + str(round)
                            cnf.append([int(temp)])
                # divide all observations to control variables:
                add = ((line, col), round, turn[line][col])
                obs_control = obs_control + (add,)
    # action pre conditions:
    max_idx = int(len(obs_control)/len(input["observations"]))
    col = int(max_idx ** 0.5)

    for j in range(len(control)):
        step = control[j]
        if len(step) > 1:
            continue
        else:
            for i in range(len(step)):
                iner = step[i]
                if iner[-1] == '0':
                    continue
                else:
                    t = len(step[0]) - 1
                    idx = int(step[0][1:t])
                    rou = int(iner[-1])
                    if iner[0] == '1':
                        precon = U_precondition(idx, rou, col, max_idx, max_round)
                        for pre in precon:
                            cnf.append(pre)
                    elif iner[0] == '2':
                        precon = H_precondition(idx, rou, col, max_idx, police)
                        for pre in precon:
                            cnf.append(pre)
                    elif iner[0] == '3':
                        precon = S_precondition(idx, rou, col,max_idx, police)
                        for pre in precon:
                            cnf.append(pre)
                    elif iner[0] == '4':
                        precon = I_precondition(idx, rou, col,max_idx, medics, max_round)
                        for pre in precon:
                            cnf.append(pre)
                    elif iner[0] == '5':
                        precon = Q_precondition(idx, rou, col, max_idx)
                        for pre in precon:
                            cnf.append(pre)

    ## infected people forced to heal after 3 rounds
    if max_round > 3:
        for i in range(1, len(obs_control) + 1):
            if obs_control[i - 1][2] == 'S':
                if i - 1 + max_idx < len(obs_control):
                    if obs_control[i - 1 + max_idx][2] == 'S':
                        if i - 1 + 2* max_idx < len(obs_control):
                            if obs_control[i - 1 + 2*max_idx][2] == 'S':
                                idx = obs_control[i-1][0][0] * col + obs_control[i-1][0][1] + 1
                                ro = str(obs_control[i-1][1] + 3)
                                temp = '2' + str(idx) + ro
                                cnf.append([int(temp)])
    ## if no police, infected people is sick for 3 rounds
    if police == 0:
        for i in range(1, len(obs_control) + 1):
            if obs_control[i - 1][2] == '?':
                count = 3
                if i - 1 - max_idx >= 0:
                    if obs_control[i - 1 - max_idx][2] == 'S':
                        count -= 1
                        if i - 1 - 2*max_idx >= 0:
                            if obs_control[i - 1 - 2*max_idx][2] == 'S':
                                count -= 1
                                if i - 1 - 3*max_idx >= 0:
                                    if obs_control[i - 1 - 3*max_idx][2] == 'S':
                                        count -= 1
                elif i - 1 + max_idx < len(obs_control):
                    if obs_control[i - 1 + max_idx][2] == 'S':
                        count -= 1
                        if i - 1 + 2*max_idx < len(obs_control):
                            if obs_control[i - 1 + 2*max_idx][2] == 'S':
                                count -= 1
                                if i - 1 + 3*max_idx < len(obs_control):
                                    if obs_control[i - 1 + 3*max_idx][2] == 'S':
                                        count -= 1
                if count > 0 and count < 3:
                    idx = obs_control[i - 1][0][0] * col + obs_control[i - 1][0][1] + 1
                    ro = str(obs_control[i - 1][1])
                    temp = '3' + str(idx) + ro
                    cnf.append([int(temp)])

    # if  police, infected people may get to quarantine
    elif police == 1:
        for r in range(len(input["observations"])):
            pol_act = []
            pol_list = []
            for i in range(1, len(obs_control) + 1):
                idx = obs_control[i - 1][0][0] * col + obs_control[i - 1][0][1] + 1
                ro = (obs_control[i - 1][1])
                if obs_control[i-1][2] == 'S' and ro == r:
                    temp = '5' + str(idx) + str(ro+1)
                    pol_act.append(int(temp))
            if len(pol_act) == 1:
                cnf.append(pol_act)
            else:
                pol_list = [(-pol_act[k], -pol_act[l]) for k in range(len(pol_act)) for l in range(k+1, len(pol_act))]
                for p in pol_list:
                    cnf.append([p[0], p[1]])

    # if  medics, health people may get vaccinated
    if medics == 1:
        for r in range(len(input["observations"])):
            pol_act = []
            pol_list = []
            for i in range(1, len(obs_control) + 1):
                idx = obs_control[i - 1][0][0] * col + obs_control[i - 1][0][1] + 1
                ro = (obs_control[i - 1][1])
                if obs_control[i-1][2] == 'H' and ro == r:
                    temp = '4' + str(idx) + str(ro+1)
                    pol_act.append(int(temp))
            if len(pol_act) == 1:
                cnf.append(pol_act)
            else:
                pol_list = [(-pol_act[k], -pol_act[l]) for k in range(len(pol_act)) for l in range(k+1, len(pol_act))]
                for p in pol_list:
                    cnf.append([p[0], p[1]])
    # solution
    result_dict = {}
    for query in queries:
        S = Solver()
        max_val = col
        idx = query[0][0]*col + query[0][1] + 1
        rou = query[1]
        precon_chosen = []
        if query[2] == 'U':
            sta = '1'
            if rou > 0:
                precon_chosen = U_precondition(idx, rou, col, max_idx, max_round)
        if query[2] == 'H':
            sta = '2'
            if rou > 0:
                precon_chosen = H_precondition(idx, rou, col, max_idx, police)
        if query[2] == 'S':
            sta = '3'
            if rou > 0:
                precon_chosen = S_precondition(idx, rou, col,max_idx, police)
        if query[2] == 'I':
            sta = '4'
            if rou > 0:
                precon_chosen = I_precondition(idx, rou, col,max_idx, medics, max_round)
        if query[2] == 'Q':
            sta = '5'
            if rou > 0:
                precon_chosen = Q_precondition(idx, rou, col, max_idx)
        for i in range(1, 6):
            if i == int(sta):
                continue
            else:
                temp = "-" + str(i) + str(idx) + str(rou)
                precon_chosen.append([int(temp)])
        query_clause = sta + str(idx) + str(rou)
        precon_chosen.append([int(query_clause)])
        for n in precon_chosen:
            cnf.append(n)

        if not S.append_formula(cnf.clauses, no_return=False):
            result_dict[query] = 'F'
            for n in precon_chosen:
                cnf.clauses.remove(n)
        else:
            for n in precon_chosen:
                cnf.clauses.remove(n)
            chosen = query_clause[0]
            flag = True
            for i in range(1, 6):
                S = Solver()
                precon_chosen = []
                if str(i) == str(chosen):
                    continue
                else:
                    if i == 1:
                        if rou > 0:
                            precon_chosen = U_precondition(idx, rou, col, max_idx, max_round)
                    elif i == 2:
                        if rou > 0:
                            precon_chosen = H_precondition(idx, rou, col, max_idx, police)
                    elif i == 3:
                        if rou > 0:
                            precon_chosen = S_precondition(idx, rou, col,max_idx, police)
                    elif i == 4:
                        if rou > 0:
                            precon_chosen = I_precondition(idx, rou, col,max_idx, medics, max_round)
                    elif i == 5:
                        if rou > 0:
                            precon_chosen = Q_precondition(idx, rou, col, max_idx)
                    temp = str(i) + query_clause[1:]
                    precon_chosen.append([int(temp)])
                    for j in range(1, 6):
                        if j == i:
                            continue
                        else:
                            temp = '-' + str(j) + query_clause[1:]
                            precon_chosen.append([int(temp)])
                    for x in precon_chosen:
                        cnf.append(x)
                    if S.append_formula(cnf.clauses, no_return=False):
                        result_dict[query] = '?'
                        flag = False
                    for x in precon_chosen:
                        cnf.clauses.remove(x)
                    if flag == False:
                        break
            if flag:
                result_dict[query] = 'T'
    return result_dict

def H_precondition(idx, rou, col, max_idx, police):
    precon_list = []
    if rou > 2:
        if idx > col:
            if (idx-1) % col == 0:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1)),
                         int('3' + str(idx - col) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 2)),
                         int('3' + str(idx) + str(rou - 3))]
                if idx + col <= max_idx:
                    steps.append(int('3' + str(idx + col) + str(rou - 1)))
                    if police > 0:
                        steps.append(int('5' + str(idx) + str(rou - 1)))
                        steps.append(int('5' + str(idx) + str(rou - 2)))
                        for i in range(len(steps)):
                            steps[i] = symbols('{}'.format(steps[i]))
                        prec = (((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3])) | (steps[4] & steps[5] & steps[6]) | (steps[7] & steps[8]))
                        if len(steps) > 8:
                            boolian = False
                        else:
                            boolian = True
                    else:
                        for i in range(len(steps)):
                            steps[i] = symbols('{}'.format(steps[i]))
                        prec = (((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3])) | (steps[4] & steps[5] & steps[6]))
                        if len(steps) > 8:
                            boolian = False
                        else:
                            boolian = True
                else:
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = (((steps[0]) >> (~steps[1] & ~steps[2])) | (steps[3] & steps[4] & steps[5]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)

            elif idx % col == 0:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1)),
                         int('3' + str(idx - col) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 2)),
                         int('3' + str(idx) + str(rou - 3))]
                if idx + col <= max_idx:
                    steps.append(int('3' + str(idx + col) + str(rou - 1)))
                    if police > 0:
                        steps.append(int('5' + str(idx) + str(rou - 1)))
                        steps.append(int('5' + str(idx) + str(rou - 2)))
                        for i in range(len(steps)):
                            steps[i] = symbols('{}'.format(steps[i]))
                        prec = (((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3])) | (steps[4] & steps[5] & steps[6]) | (steps[7] & steps[8]))
                        if len(steps) > 8:
                            boolian = False
                        else:
                            boolian = True
                    else:
                        for i in range(len(steps)):
                            steps[i] = symbols('{}'.format(steps[i]))
                        prec = (((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3])) | (steps[4] & steps[5] & steps[6]))
                        if len(steps) > 8:
                            boolian = False
                        else:
                            boolian = True
                else:
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = (((steps[0]) >> (~steps[1] & ~steps[2])) | (steps[3] & steps[4] & steps[5]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)
            else:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1)),
                         int('3' + str(idx - col) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 2)),
                         int('3' + str(idx) + str(rou - 3))]
                if idx + col <= max_idx:
                    steps.append(int('3' + str(idx + col) + str(rou - 1)))
                    if police > 0:
                        steps.append(int('5' + str(idx) + str(rou - 1)))
                        steps.append(int('5' + str(idx) + str(rou - 2)))
                        for i in range(len(steps)):
                            steps[i] = symbols('{}'.format(steps[i]))
                        prec = (((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3] & ~steps[4])) | (steps[5] & steps[6] & steps[7]) | (steps[8] & steps[9]))
                        if len(steps) > 8:
                            boolian = False
                        else:
                            boolian = True
                    else:
                        for i in range(len(steps)):
                            steps[i] = symbols('{}'.format(steps[i]))
                        prec = (((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3] & ~steps[4])) | (steps[5] & steps[6] & steps[7]))
                        if len(steps) > 8:
                            boolian = False
                        else:
                            boolian = True
                else:
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = (((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3])) | (steps[5] & steps[6] & steps[7]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)
        else:
            if idx == 1:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 2)),
                         int('3' + str(idx) + str(rou - 3))]
                if police > 0:
                    steps.append(int('5' + str(idx) + str(rou - 1)))
                    steps.append(int('5' + str(idx) + str(rou - 2)))
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2]) | (steps[3] & steps[4] & steps[5]) | (steps[6] & steps[7]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                else:
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2]) | (steps[3] & steps[4] & steps[5]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)
            elif idx == col:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 2)),
                         int('3' + str(idx) + str(rou - 3))]
                if police > 0:
                    steps.append(int('5' + str(idx) + str(rou - 1)))
                    steps.append(int('5' + str(idx) + str(rou - 2)))
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2]) | (steps[3] & steps[4] & steps[5]) | (steps[6] & steps[7]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                else:
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2]) | (steps[3] & steps[4] & steps[5]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)
            else:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 2)),
                         int('3' + str(idx) + str(rou - 3))]
                if police > 0:
                    steps.append(int('5' + str(idx) + str(rou - 1)))
                    steps.append(int('5' + str(idx) + str(rou - 2)))
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3])  | (steps[4] & steps[5] & steps[6]) | (steps[7] & steps[8]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                else:
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3])  | (steps[4] & steps[5] & steps[6]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)

    elif rou > 1:
        if idx > col:
            if (idx-1) % col == 0:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1)),
                         int('3' + str(idx - col) + str(rou - 1))]
                if idx + col <= max_idx:
                    steps.append(int('3' + str(idx + col) + str(rou - 1)))
                    if police > 0:
                        steps.append(int('5' + str(idx) + str(rou - 1)))
                        steps.append(int('5' + str(idx) + str(rou - 2)))
                        for i in range(len(steps)):
                            steps[i] = symbols('{}'.format(steps[i]))
                        prec = (((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3])) | (steps[4] & steps[5]))
                        if len(steps) > 8:
                            boolian = False
                        else:
                            boolian = True
                    else:
                        for i in range(len(steps)):
                            steps[i] = symbols('{}'.format(steps[i]))
                        prec = (((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3])))
                        if len(steps) > 8:
                            boolian = False
                        else:
                            boolian = True
                else:
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = (((steps[0]) >> (~steps[1] & ~steps[2])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)

            elif idx % col == 0:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1)),
                         int('3' + str(idx - col) + str(rou - 1))]
                if idx + col <= max_idx:
                    steps.append(int('3' + str(idx + col) + str(rou - 1)))
                    if police > 0:
                        steps.append(int('5' + str(idx) + str(rou - 1)))
                        steps.append(int('5' + str(idx) + str(rou - 2)))
                        for i in range(len(steps)):
                            steps[i] = symbols('{}'.format(steps[i]))
                        prec = (((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3])) | (steps[4] & steps[5]))
                        if len(steps) > 8:
                            boolian = False
                        else:
                            boolian = True
                    else:
                        for i in range(len(steps)):
                            steps[i] = symbols('{}'.format(steps[i]))
                        prec = ((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3]))
                        if len(steps) > 8:
                            boolian = False
                        else:
                            boolian = True
                else:
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)
            else:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1)),
                         int('3' + str(idx - col) + str(rou - 1))]
                if idx + col <= max_idx:
                    steps.append(int('3' + str(idx + col) + str(rou - 1)))
                    if police > 0:
                        steps.append(int('5' + str(idx) + str(rou - 1)))
                        steps.append(int('5' + str(idx) + str(rou - 2)))
                        for i in range(len(steps)):
                            steps[i] = symbols('{}'.format(steps[i]))
                        prec = (((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3] & ~steps[4])) | (steps[5] & steps[6]))
                        if len(steps) > 8:
                            boolian = False
                        else:
                            boolian = True
                    else:
                        for i in range(len(steps)):
                            steps[i] = symbols('{}'.format(steps[i]))
                        prec = (((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3] & ~steps[4])))
                        if len(steps) > 8:
                            boolian = False
                        else:
                            boolian = True
                else:
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = (((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)
        else:
            if idx == 1:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1))]
                if police > 0:
                    steps.append(int('5' + str(idx) + str(rou - 1)))
                    steps.append(int('5' + str(idx) + str(rou - 2)))
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2]) | (steps[3] & steps[4]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                else:
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)
            elif idx == col:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1))]
                if police > 0:
                    steps.append(int('5' + str(idx) + str(rou - 1)))
                    steps.append(int('5' + str(idx) + str(rou - 2)))
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2]) | (steps[3] & steps[4]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                else:
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)
            else:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1))]
                if police > 0:
                    steps.append(int('5' + str(idx) + str(rou - 1)))
                    steps.append(int('5' + str(idx) + str(rou - 2)))
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3]) | (steps[7] & steps[8]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                else:
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)

            precon_list = sympy_to_pysat(prec, boolian)
        precon = [int('2' + str(idx) + str(rou - 1)), int('5' + str(idx) + str(rou - 1))]
        precon_list.append(precon)
        precon = [int('-2' + str(idx) + str(rou - 1)), int('-5' + str(idx) + str(rou - 1))]
        precon_list.append(precon)
        precon = [int('-1' + str(idx) + str(rou - 1))]
        precon_list.append(precon)
        precon = [int('-4' + str(idx) + str(rou - 1))]
        precon_list.append(precon)
        precon = [int('-3' + str(idx) + str(rou - 1))]
        precon_list.append(precon)
    else:
        if idx > col:
            if (idx-1) % col == 0:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1)),
                         int('3' + str(idx - col) + str(rou - 1))]
                if idx + col <= max_idx:
                    steps.append(int('3' + str(idx + col) + str(rou - 1)))
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                else:
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)
            elif idx % col == 0:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1)),
                         int('3' + str(idx - col) + str(rou - 1))]
                if idx + col <= max_idx:
                    steps.append(int('3' + str(idx + col) + str(rou - 1)))
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                else:
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)
            else:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1)),
                         int('3' + str(idx - col) + str(rou - 1))]
                if idx + col <= max_idx:
                    steps.append(int('3' + str(idx + col) + str(rou - 1)))
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3] & ~steps[4]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True

                else:
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3]))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)
        else:
            if idx == 1:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1))]
                for i in range(len(steps)):
                    steps[i] = symbols('{}'.format(steps[i]))
                prec = ((steps[0]) >> (~steps[1] & ~steps[2]))
                if len(steps) > 8:
                    boolian = False
                else:
                    boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)
            elif idx == col:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1))]
                for i in range(len(steps)):
                    steps[i] = symbols('{}'.format(steps[i]))
                prec = ((steps[0]) >> (~steps[1] & ~steps[2]))
                if len(steps) > 8:
                    boolian = False
                else:
                    boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)
            else:
                steps = [int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1))]
                for i in range(len(steps)):
                    steps[i] = symbols('{}'.format(steps[i]))
                prec = ((steps[0]) >> (~steps[1] & ~steps[2] & ~steps[3]))
                if len(steps) > 8:
                    boolian = False
                else:
                    boolian = True
                temp = sympy_to_pysat(prec, boolian)
                for i in temp:
                    precon_list.append(i)

            precon_list = sympy_to_pysat(prec, boolian)
        if police > 0:
            precon = [int('2' + str(idx) + str(rou - 1)), int('5' + str(idx) + str(rou - 1))]
            precon_list.append(precon)
            precon = [int('-2' + str(idx) + str(rou - 1)), int('-5' + str(idx) + str(rou - 1))]
            precon_list.append(precon)
            precon = [int('-1' + str(idx) + str(rou - 1))]
            precon_list.append(precon)
            precon = [int('-4' + str(idx) + str(rou - 1))]
            precon_list.append(precon)
            precon = [int('-3' + str(idx) + str(rou - 1))]
            precon_list.append(precon)
        else:
            precon = [int('2' + str(idx) + str(rou - 1))]
            precon_list.append(precon)
            precon = [int('-5' + str(idx) + str(rou - 1))]
            precon_list.append(precon)
            precon = [int('-1' + str(idx) + str(rou - 1))]
            precon_list.append(precon)
            precon = [int('-4' + str(idx) + str(rou - 1))]
            precon_list.append(precon)
            precon = [int('-3' + str(idx) + str(rou - 1))]
            precon_list.append(precon)
    return precon_list

def S_precondition(idx, rou, col,max_idx, police):
    precon_list = []
    if idx > col:
        if rou > 2:
            if (idx-1) % col == 0:
                if idx+col <= max_idx:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('3' + str(idx) + str(rou - 2)),
                             int('3' + str(idx) + str(rou - 3)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx + 1) + str(rou - 1)),
                             int('3' + str(idx + col) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0] & steps[1] & ~steps[2]) | (steps[0] & ~steps[1]) | (steps[3] & (steps[4] | steps[5] | steps[6])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
                else:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('3' + str(idx) + str(rou - 2)),
                             int('3' + str(idx) + str(rou - 3)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx + 1) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0] & steps[1] & ~steps[2]) | (steps[0] & ~steps[1]) | (steps[3] & (steps[4] | steps[5])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
            elif idx % col == 0:
                if idx + col <= max_idx:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('3' + str(idx) + str(rou - 2)),
                             int('3' + str(idx) + str(rou - 3)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx - 1) + str(rou - 1)),
                             int('3' + str(idx + col) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0] & steps[1] & ~steps[2]) | (
                                steps[0] & ~steps[1]) | (steps[3] & (steps[4] | steps[5] | steps[6])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
                else:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('3' + str(idx) + str(rou - 2)),
                             int('3' + str(idx) + str(rou - 3)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx - 1) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0] & steps[1] & ~steps[2]) | (steps[0] & ~steps[1]) | (steps[3] & (steps[4] | steps[5])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
            else:
                if idx + col <= max_idx:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('3' + str(idx) + str(rou - 2)),
                             int('3' + str(idx) + str(rou - 3)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx - 1) + str(rou - 1)),
                             int('3' + str(idx + 1) + str(rou - 1)),
                             int('3' + str(idx + col) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0] & steps[1] & ~steps[2]) | (
                                steps[0] & ~steps[1]) | (steps[3] & (steps[4] | steps[5] | steps[6] | steps[7])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
                else:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('3' + str(idx) + str(rou - 2)),
                             int('3' + str(idx) + str(rou - 3)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx - 1) + str(rou - 1)),
                             int('3' + str(idx + 1) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0] & steps[1] & ~steps[2]) | (
                                steps[0] & ~steps[1]) | (steps[3] & (steps[4] | steps[5] | steps[6])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
        elif rou > 1:
            if (idx-1) % col == 0:
                if idx+col <= max_idx:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('3' + str(idx) + str(rou - 2)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx + 1) + str(rou - 1)),
                             int('3' + str(idx + col) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0] & steps[1]) | (steps[0] & ~steps[1]) | (steps[2] & (steps[3] | steps[4] | steps[5])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
                else:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('3' + str(idx) + str(rou - 2)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx + 1) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0] & steps[1]) | (steps[0] & ~steps[1]) | (steps[2] & (steps[3] | steps[4])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
            elif idx % col == 0:
                if idx + col <= max_idx:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('3' + str(idx) + str(rou - 2)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx - 1) + str(rou - 1)),
                             int('3' + str(idx + col) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0] & steps[1]) | (steps[0] & ~steps[1]) | (steps[2] & (steps[3] | steps[4] | steps[5])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
                else:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('3' + str(idx) + str(rou - 2)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx - 1) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0] & steps[1]) | (steps[0] & ~steps[1]) | (steps[2] & (steps[3] | steps[4])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
            else:
                if idx + col <= max_idx:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('3' + str(idx) + str(rou - 2)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx - 1) + str(rou - 1)),
                             int('3' + str(idx + 1) + str(rou - 1)),
                             int('3' + str(idx + col) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0] & steps[1]) | (steps[0] & ~steps[1]) | (steps[2] & (steps[3] | steps[4] | steps[5] | steps[6])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
                else:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('3' + str(idx) + str(rou - 2)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx - 1) + str(rou - 1)),
                             int('3' + str(idx + 1) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0] & steps[1]) | (steps[0] & ~steps[1]) | (steps[2] & (steps[3] | steps[4] | steps[5])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
        else:
            if (idx-1) % col == 0:
                if idx+col <= max_idx:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx + 1) + str(rou - 1)),
                             int('3' + str(idx + col) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) | (steps[1] & (steps[2] | steps[3] | steps[4])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
                else:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx + 1) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) | (steps[1] & (steps[2] | steps[3])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
            elif idx % col == 0:
                if idx + col <= max_idx:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx - 1) + str(rou - 1)),
                             int('3' + str(idx + col) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) | ((steps[1]) & (steps[2] | steps[3] | steps[4])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
                else:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx - 1) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) | (steps[1] & (steps[2] | steps[3])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
            else:
                if idx + col <= max_idx:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx - 1) + str(rou - 1)),
                             int('3' + str(idx + 1) + str(rou - 1)),
                             int('3' + str(idx + col) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) | (steps[1] & (steps[2] | steps[3] | steps[4] | steps[5])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)
                else:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx - 1) + str(rou - 1)),
                             int('3' + str(idx + 1) + str(rou - 1)),
                             int('3' + str(idx - col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0]) | (steps[1] & (steps[2] | steps[3] | steps[4])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)

    else:
        ######################################################################3
        if rou > 2:
            if idx == 1:
                steps = [int('3' + str(idx) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 2)),
                         int('3' + str(idx) + str(rou - 3)),
                         int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1))]
                for i in range(len(steps)):
                    steps[i] = symbols('{}'.format(steps[i]))
                prec = ((steps[0] & steps[1] & ~steps[2]) | (steps[0] & ~steps[1]) | (steps[3] & (steps[4] | steps[5])))
                if len(steps) > 8:
                    boolian = False
                else:
                    boolian = True
                precon_list = sympy_to_pysat(prec, boolian)

            elif idx == col:
                    steps = [int('3' + str(idx) + str(rou - 1)),
                             int('3' + str(idx) + str(rou - 2)),
                             int('3' + str(idx) + str(rou - 3)),
                             int('2' + str(idx) + str(rou - 1)),
                             int('3' + str(idx - 1) + str(rou - 1)),
                             int('3' + str(idx + col) + str(rou - 1))]
                    for i in range(len(steps)):
                        steps[i] = symbols('{}'.format(steps[i]))
                    prec = ((steps[0] & steps[1] & ~steps[2]) | (
                                steps[0] & ~steps[1]) | (steps[3] & (steps[4] | steps[5])))
                    if len(steps) > 8:
                        boolian = False
                    else:
                        boolian = True
                    precon_list = sympy_to_pysat(prec, boolian)

            else:
                steps = [int('3' + str(idx) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 2)),
                         int('3' + str(idx) + str(rou - 3)),
                         int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1))]
                for i in range(len(steps)):
                    steps[i] = symbols('{}'.format(steps[i]))
                prec = ((steps[0] & steps[1] & ~steps[2]) | (
                            steps[0] & ~steps[1]) | (steps[3] & (steps[4] | steps[5] | steps[6])))
                if len(steps) > 8:
                    boolian = False
                else:
                    boolian = True
                precon_list = sympy_to_pysat(prec, boolian)

        elif rou > 1:
            if idx == 1:
                steps = [int('3' + str(idx) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 2)),
                         int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1))]
                for i in range(len(steps)):
                    steps[i] = symbols('{}'.format(steps[i]))
                prec = ((steps[0] & steps[1]) | (steps[0] & ~steps[1]) | (steps[2] & (steps[3] | steps[4])))
                if len(steps) > 8:
                    boolian = False
                else:
                    boolian = True
                precon_list = sympy_to_pysat(prec, boolian)

            elif idx == col:
                steps = [int('3' + str(idx) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 2)),
                         int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1))]
                for i in range(len(steps)):
                    steps[i] = symbols('{}'.format(steps[i]))
                prec = ((steps[0] & steps[1]) | (steps[0] & ~steps[1]) | (steps[2] & (steps[3] | steps[4])))
                if len(steps) > 8:
                    boolian = False
                else:
                    boolian = True
                precon_list = sympy_to_pysat(prec, boolian)
            else:
                steps = [int('3' + str(idx) + str(rou - 1)),
                         int('3' + str(idx) + str(rou - 2)),
                         int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1))]
                for i in range(len(steps)):
                    steps[i] = symbols('{}'.format(steps[i]))
                prec = ((steps[0] & steps[1]) | (steps[0] & ~steps[1]) | (steps[2] & (steps[3] | steps[4] | steps[5])))
                if len(steps) > 8:
                    boolian = False
                else:
                    boolian = True
                precon_list = sympy_to_pysat(prec, boolian)
        else:
            if idx == 1:
                steps = [int('3' + str(idx) + str(rou - 1)),
                         int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1))]
                for i in range(len(steps)):
                    steps[i] = symbols('{}'.format(steps[i]))
                prec = ((steps[0]) | (steps[1] & (steps[2] | steps[3])))
                if len(steps) > 8:
                    boolian = False
                else:
                    boolian = True
                precon_list = sympy_to_pysat(prec, boolian)
            elif idx == col:
                steps = [int('3' + str(idx) + str(rou - 1)),
                         int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1))]
                for i in range(len(steps)):
                    steps[i] = symbols('{}'.format(steps[i]))
                prec = ((steps[0]) | ((steps[1]) & (steps[2] | steps[3])))
                if len(steps) > 8:
                    boolian = False
                else:
                    boolian = True
                precon_list = sympy_to_pysat(prec, boolian)
            else:
                steps = [int('3' + str(idx) + str(rou - 1)),
                         int('2' + str(idx) + str(rou - 1)),
                         int('3' + str(idx - 1) + str(rou - 1)),
                         int('3' + str(idx + 1) + str(rou - 1)),
                         int('3' + str(idx + col) + str(rou - 1))]
                for i in range(len(steps)):
                    steps[i] = symbols('{}'.format(steps[i]))
                prec = ((steps[0]) | (steps[1] & (steps[2] | steps[3] | steps[4])))
                if len(steps) > 8:
                    boolian = False
                else:
                    boolian = True
                precon_list = sympy_to_pysat(prec, boolian)

    temp = [int('-1' + str(idx) + str(rou - 1))]
    precon_list.append(temp)
    temp = [int('-4' + str(idx) + str(rou - 1))]
    precon_list.append(temp)
    temp = [int('-5' + str(idx) + str(rou - 1))]
    precon_list.append(temp)
    return precon_list

def U_precondition(idx, rou, col, max_idx, max_round):
    precon_list = []
    for i in range(max_round):
        if i == rou:
            continue
        else:
            precon = [int('1' + str(idx) + str(i)),
                      int('-2' + str(idx) + str(i)),
                      int('-3' + str(idx) + str(i)),
                      int('-4' + str(idx) + str(i)),
                      int('-5' + str(idx) + str(i))]
            for j in precon:
                precon_list.append([j])
    return precon_list

def I_precondition(idx, rou, col,max_idx, medics, max_round):
    precon_list = []
    if medics == 0:
        precon = [int('-4' + str(idx) + str(rou))]
        precon_list.append(precon)
    else:
        for i in range(rou + 1, max_round - rou):
            precon = [int('4' + str(idx) + str(rou + i)),
                      int('-1' + str(idx) + str(rou + i)),
                      int('-2' + str(idx) + str(rou + i)),
                      int('-3' + str(idx) + str(rou + i)),
                      int('-5' + str(idx) + str(rou + i))]
            for j in precon:
                precon_list.append([j])
        precon = [int('4' + str(idx) + str(rou - 1)),
                      int('2' + str(idx) + str(rou - 1))]
        precon_list.append(precon)
        precon = [int('-4' + str(idx) + str(rou - 1)),
                      int('-2' + str(idx) + str(rou - 1))]
        precon_list.append(precon)
    return precon_list

def Q_precondition(idx, rou, col, max_idx):
    precon_list = []
    precon = [int('5' + str(idx) + str(rou - 1)),
              int('3' + str(idx) + str(rou - 1))]
    precon_list.append(precon)
    precon = [int('-5' + str(idx) + str(rou - 1)),
              int('-3' + str(idx) + str(rou - 1))]
    precon_list.append(precon)
    return precon_list

def sympy_to_pysat(statement, bool_val):
    cnf_s = to_cnf(statement, simplify=bool_val)
    cnf_args = cnf_s.args
    and_clause = []
    for arg in cnf_args:
        str_arg = str(arg)
        str_arg_splited = str_arg.split(" | ")
        or_clause = []
        for symbol in str_arg_splited:
            if "~" in symbol:
                or_clause.append(-int(symbol[1:]))
            else:
                or_clause.append(int(symbol))
        and_clause.append(or_clause)
    return and_clause