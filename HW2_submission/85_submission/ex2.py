from pysat.solvers import Glucose3
from sympy import simplify
from sympy import symbols
from sympy.logic.boolalg import to_cnf
from itertools import chain, combinations

ids = ['2056333258', '205717176']


def only_one_from_five(solver, num_list):
    solver.add_clause(num_list)
    solver.add_clause([-num_list[0], -num_list[1]])
    solver.add_clause([-num_list[0], -num_list[2]])
    solver.add_clause([-num_list[0], -num_list[3]])
    solver.add_clause([-num_list[0], -num_list[4]])
    solver.add_clause([-num_list[1], -num_list[2]])
    solver.add_clause([-num_list[1], -num_list[3]])
    solver.add_clause([-num_list[1], -num_list[4]])
    solver.add_clause([-num_list[2], -num_list[3]])
    solver.add_clause([-num_list[2], -num_list[4]])
    solver.add_clause([-num_list[3], -num_list[4]])


def only_one_from_three(solver, num_list):
    solver.add_clause(num_list)
    solver.add_clause([-num_list[0], -num_list[1]])
    solver.add_clause([-num_list[0], -num_list[2]])
    solver.add_clause([-num_list[1], -num_list[2]])


def power_set_by_num(iterable, num):
    """ Given an object and a number
        Returns a list of all combinations by the number received."""
    s = list(iterable)
    return list(chain.from_iterable(combinations(s, r) for r in range(num + 1)))[1:]


def limited_teams(solver, action_list, num_teams):
    """stage 1: create all possible variations of actions"""
    possible_variations = power_set_by_num(action_list, num_teams)
    before_cnf = []
    final_permutation_list = []
    max_len_per = 1
    for per in possible_variations:
        if len(per) > max_len_per:
            max_len_per = len(per)
    for combi in possible_variations:
        if len(combi) == max_len_per:
            final_permutation_list.append(combi)
    """add all other actions which are not in the action permutations with NOT on them"""
    for permutation_tuple in final_permutation_list:
        permutation_list = []
        for act in action_list:
            if act in permutation_tuple:
                permutation_list.append(act)
            else:
                permutation_list.append(-act)
        """convert to symbols"""
        formula = symbols('{}'.format(permutation_list[0]))
        for x in permutation_list[1:]:
            symbol_x = symbols('{}'.format(x))
            formula = formula & symbol_x
        before_cnf.append(formula)

    formula_to_cnf = before_cnf[0]
    for cnf_formula in before_cnf[1:]:
        formula_to_cnf = formula_to_cnf | cnf_formula

    cnf_final = to_cnf(formula_to_cnf)
    cnf_final_simple = simplify(cnf_final)

    """if we only get one action possible"""
    if len(cnf_final_simple.args) == 0:
        adding = [int(str(cnf_final_simple))]
        solver.add_clause([int(str(cnf_final_simple))])

    """convert simple cnf symbols to list of int (each list is clause) and add to solver"""
    for clause in cnf_final_simple.args:
        clause_list = []
        if (len(clause.args)) == 0:
            if str(clause)[0] == '-':
                clause_list.append(int(str(clause)[1]) * (-1))
            else:
                clause_list.append(int(str(clause)))
        else:
            for atom in clause.args:
                if str(atom)[0] == "-":
                    clause_list.append(int(str(atom)[1:]) * (-1))
                else:
                    clause_list.append(int(str(atom)))
        solver.add_clause(clause_list)


def initial_states(solver, distributor, observation_map, num_rows, num_columns):
    num_observe = len(observation_map)
    dict_char = {'H': [[[0 for w in range(num_columns)] for i in range(num_rows)] for j in range(num_observe)],
                 'S': [[[0 for w in range(num_columns)] for i in range(num_rows)] for j in range(num_observe)],
                 'U': [[[0 for w in range(num_columns)] for i in range(num_rows)] for j in range(num_observe)],
                 'I': [[[0 for w in range(num_columns)] for i in range(num_rows)] for j in range(num_observe)],
                 'Q': [[[0 for w in range(num_columns)] for i in range(num_rows)] for j in range(num_observe)]}

    for time in range(num_observe):
        for i in range(num_rows):
            for j in range(num_columns):
                char = observation_map[time][i][j]
                if char != '?':
                    dict_char[char][time][i][j] = distributor
                    solver.add_clause([distributor])             #Add to knowledge base
                    distributor += 1
                    for other_char in ['H', 'Q', 'I', 'U', 'S']:
                        if char != other_char:
                            dict_char[other_char][time][i][j] = distributor
                            solver.add_clause([-distributor])     #Add to knowledge base
                            distributor += 1
                elif time > 0:
                    temp_list = []
                    for other_char in ['H', 'Q', 'I', 'U', 'S']:
                        dict_char[other_char][time][i][j] = distributor
                        temp_list.append(distributor)
                        distributor += 1
                    only_one_from_five(solver, temp_list)        #Add to knowledge base
                else:
                    temp_list = []
                    for other_char in ['H', 'U', 'S']:
                        dict_char[other_char][time][i][j] = distributor
                        temp_list.append(distributor)
                        distributor += 1
                    only_one_from_three(solver, temp_list)      #Add to knowledge base
                    for other_char in ['I', 'Q']:
                        dict_char[other_char][time][i][j] = distributor
                        solver.add_clause([-distributor])       #Add to knowledge base
                        distributor += 1

    return dict_char, distributor


def actions_effects(solver, distributor, observation_map, num_rows, num_columns, char_dict, num_police, num_medics):
    num_observe = len(observation_map)
    action_dict = {'Infection':  [[[0 for w in range(num_columns)] for i in range(num_rows)] for j in range(num_observe-1)],
                   'Healing_S':    [[[0 for w in range(num_columns)] for i in range(num_rows)] for j in range(num_observe-1)],
                   'Quarantine': [[[0 for w in range(num_columns)] for i in range(num_rows)] for j in range(num_observe-1)],
                   'Healing_Q': [[[0 for w in range(num_columns)] for i in range(num_rows)] for j in range(num_observe - 1)],
                   'Immune':     [[[0 for w in range(num_columns)] for i in range(num_rows)] for j in range(num_observe-1)]}

    """Assume we have 0 police and 0 medics -> only take Infection and Healing"""
    for time in range(num_observe):
        q_list = []
        i_list = []
        available_police = num_police
        available_medics = num_medics
        for i in range(num_rows):
            for j in range(num_columns):
                curr_char = observation_map[time][i][j]

                """Quarantine Dealing, in case of num_police > 0 """
                if available_police > 0 and time > 0 and (curr_char == 'Q' or curr_char == '?'):
                    if curr_char == 'Q' and observation_map[time - 1][i][j] == 'S':
                        available_police -= 1
                    else:
                        if observation_map[time - 1][i][j] == '?' or observation_map[time - 1][i][j] == 'S':
                            action_dict['Quarantine'][time - 1][i][j] = distributor
                            """add effects and delete effects"""
                            solver.add_clause([-distributor, char_dict['Q'][time][i][j]])
                            for other_char in ['S', 'H', 'I', 'U']:
                                solver.add_clause([-distributor, -char_dict[other_char][time][i][j]])
                            if curr_char == 'Q':
                                solver.add_clause([distributor, char_dict['Q'][time - 1][i][j]])
                            solver.add_clause([-distributor, char_dict['S'][time - 1][i][j]])
                            for other_char in ['Q', 'H', 'I', 'U']:
                                solver.add_clause([-distributor, -char_dict[other_char][time-1][i][j]])
                            q_list.append(distributor)
                            distributor += 1

                """Immune Dealing, in case of num_medics > 0 """
                if available_medics > 0 and time > 0 and (curr_char == 'I' or curr_char == '?'):
                    if curr_char == 'I' and observation_map[time - 1][i][j] == 'H':
                        available_medics -= 1
                    else:
                        if observation_map[time - 1][i][j] == '?' or observation_map[time - 1][i][j] == 'H':
                            action_dict['Immune'][time - 1][i][j] = distributor
                            """add effects and delete effects"""
                            solver.add_clause([-distributor, char_dict['I'][time][i][j]])
                            for other_char in ['S', 'H', 'Q', 'U']:
                                solver.add_clause([-distributor, -char_dict[other_char][time][i][j]])
                            if curr_char == 'I':
                                solver.add_clause([distributor, char_dict['I'][time - 1][i][j]])
                            solver.add_clause([-distributor, char_dict['H'][time - 1][i][j]])
                            for other_char in ['S', 'I', 'Q', 'U']:
                                solver.add_clause([-distributor, -char_dict[other_char][time-1][i][j]])
                            i_list.append(distributor)
                            distributor += 1

                """Infection Dealing"""
                if time > 0 and (curr_char == 'S' or curr_char == '?'):
                    if observation_map[time-1][i][j] not in ['I', 'U', 'Q', 'S']:
                        """precondition"""
                        infect_pre = infection_preconditions(i, j, num_rows, num_columns, time - 1, observation_map, char_dict)
                        if len(infect_pre) != 0:
                            action_dict['Infection'][time - 1][i][j] = distributor
                            if len(infect_pre) == 1:
                                solver.add_clause([-distributor, infect_pre[0][0]])
                                for other_char in ['I', 'U', 'Q', 'H']:
                                    solver.add_clause([-distributor, -char_dict[other_char][time-1][infect_pre[0][1]][infect_pre[0][2]]])
                            for pre in infect_pre:
                                if action_dict['Immune'][time-1][i][j] != 0 and action_dict['Quarantine'][time-1][pre[1]][pre[2]] != 0:
                                    solver.add_clause([-pre[0], -char_dict['H'][time - 1][i][j], action_dict['Quarantine'][time-1][pre[1]][pre[2]], action_dict['Immune'][time-1][i][j], distributor])
                                elif action_dict['Immune'][time-1][i][j] != 0 and action_dict['Quarantine'][time-1][pre[1]][pre[2]] == 0:
                                    solver.add_clause([-pre[0], -char_dict['H'][time - 1][i][j], distributor])
                                elif action_dict['Immune'][time-1][i][j] == 0 and action_dict['Quarantine'][time-1][pre[1]][pre[2]] != 0:
                                    solver.add_clause([-pre[0], -char_dict['H'][time - 1][i][j], action_dict['Quarantine'][time-1][pre[1]][pre[2]], distributor])
                                else:
                                    solver.add_clause([-pre[0], -char_dict['H'][time - 1][i][j], distributor])
                            """add effects and delete effects"""
                            solver.add_clause([-distributor, char_dict['S'][time][i][j]])
                            for other_char in ['H', 'Q', 'I', 'U']:
                                solver.add_clause([-distributor, -char_dict[other_char][time][i][j]])
                            if curr_char == 'S':
                                solver.add_clause([distributor, char_dict['S'][time-1][i][j]])
                            solver.add_clause([-distributor, char_dict['H'][time - 1][i][j]])
                            for other_char in ['S', 'Q', 'I', 'U']:
                                solver.add_clause([-distributor, -char_dict[other_char][time-1][i][j]])

                            distributor += 1

                """Healing from Sickness Dealing"""
                if time - 2 > 0 and (curr_char == 'H' or curr_char == '?'):
                    """precondition"""
                    action_dict['Healing_S'][time-1][i][j] = distributor
                    solver.add_clause([-char_dict['S'][time-1][i][j], -char_dict['S'][time-2][i][j], -char_dict['S'][time-3][i][j], distributor])
                    for k in range(3):
                        solver.add_clause([char_dict['S'][time-1-k][i][j], -distributor])
                        for other_char in ['H', 'Q', 'I', 'U']:
                            solver.add_clause([-char_dict[other_char][time - 1 - k][i][j], -distributor])
                    """add effects and delete effects"""
                    solver.add_clause([-distributor, char_dict['H'][time][i][j]])
                    for other_char in ['S', 'Q', 'I', 'U']:
                        solver.add_clause([-distributor, -char_dict[other_char][time][i][j]])
                    distributor += 1

                """Healing from Quarantine Dealing"""
                if time - 1 > 0 and (curr_char == 'H' or curr_char == '?'):
                    """precondition"""
                    action_dict['Healing_Q'][time-1][i][j] = distributor
                    solver.add_clause([-char_dict['Q'][time-1][i][j], -char_dict['Q'][time-2][i][j], distributor])
                    for k in range(2):
                        solver.add_clause([char_dict['Q'][time-1-k][i][j], -distributor])
                        for other_char in ['H', 'S', 'I', 'U']:
                            solver.add_clause([-char_dict[other_char][time - 1 - k][i][j], -distributor])
                    """add effects and delete effects"""
                    solver.add_clause([-distributor, char_dict['H'][time][i][j]])
                    for other_char in ['S', 'Q', 'I', 'U']:
                        solver.add_clause([-distributor, -char_dict[other_char][time][i][j]])
                    if curr_char == 'H':
                        solver.add_clause([distributor, (distributor-1), char_dict['H'][time - 1][i][j]])
                    distributor += 1

                if time > 0 and curr_char == '?':
                    if check_h_neighbors(i, j, num_rows, num_columns, time-1, observation_map, char_dict):
                        solver.add_clause([-char_dict['S'][time-1][i][j]])

        if time > 0 and (available_medics == 0 or available_police == 0):
            for x in range(num_rows):
                for y in range(num_columns):
                    curr_char = observation_map[time][x][y]
                    if curr_char == '?' and available_police == 0:
                        solver.add_clause([-char_dict['Q'][time][x][y], char_dict['Q'][time - 1][x][y]])
                    if curr_char == '?' and available_medics == 0:
                        solver.add_clause([-char_dict['I'][time][x][y], char_dict['I'][time - 1][x][y]])

        for x in range(num_rows):
            for y in range(num_columns):
                solver.add_clause([-char_dict['U'][time][x][y], char_dict['U'][time-1][x][y]])
                solver.add_clause([char_dict['U'][time][x][y], -char_dict['U'][time - 1][x][y]])

        if available_police > 0 and time > 0 and len(q_list) != 0:
            limited_teams(solver, q_list, available_police)

        if available_medics > 0 and time > 0 and len(i_list) != 0:
            limited_teams(solver, i_list, available_medics)

    return action_dict, distributor


def no_act_stay(solver, observation_map, num_rows, num_columns, char_dict, action_dict):
    num_observe = len(observation_map)
    for time in range(1, num_observe):
        for i in range(num_rows):
            for j in range(num_columns):
                curr_char = observation_map[time][i][j]
                before_char = observation_map[time-1][i][j]
                if before_char != '?' or curr_char != '?':
                    act_list = []
                    for act in ['Infection', 'Healing_S', 'Quarantine', 'Healing_Q', 'Immune']:
                        if action_dict[act][time-1][i][j] != 0:
                            act_list.append(action_dict[act][time-1][i][j])
                    if curr_char == '?' and before_char != '?':
                        act_list.append(char_dict[before_char][time][i][j])
                        solver.add_clause(act_list)
                    if curr_char != '?' and before_char == '?':
                        act_list.append(char_dict[curr_char][time-1][i][j])
                        solver.add_clause(act_list)
                else:
                    act_list = []
                    for act in ['Infection', 'Healing_S', 'Quarantine', 'Healing_Q', 'Immune']:
                        if action_dict[act][time-1][i][j] != 0:
                            act_list.append(action_dict[act][time-1][i][j])
                    if len(act_list) == 0:
                        for other_char in ['H', 'Q', 'I', 'U', 'S']:
                            solver.add_clause([-char_dict[other_char][time][i][j], char_dict[other_char][time-1][i][j]])


def infection_preconditions(i, j, num_rows, num_columns, time, observation_map, char_dict):
    infection_clause_list = []
    if (i - 1) >= 0:
        if observation_map[time][i - 1][j] == 'S' or observation_map[time][i - 1][j] == '?':
            infection_clause_list.append([char_dict['S'][time][i-1][j], i - 1, j])
    """check valid down place"""
    if (i + 1) < num_rows:
        if observation_map[time][i + 1][j] == 'S' or observation_map[time][i + 1][j] == '?':
            infection_clause_list.append([char_dict['S'][time][i+1][j], i + 1, j])
    """check valid left place"""
    if (j - 1) >= 0:
        if observation_map[time][i][j - 1] == 'S' or observation_map[time][i][j - 1] == '?':
            infection_clause_list.append([char_dict['S'][time][i][j-1], i, j - 1])
    """check valid right place"""
    if (j + 1) < num_columns:
        if observation_map[time][i][j + 1] == 'S' or observation_map[time][i][j + 1] == '?':
            infection_clause_list.append([char_dict['S'][time][i][j+1], i, j + 1])

    return infection_clause_list


def check_h_neighbors(i, j, num_rows, num_columns, time, observation_map, char_dict):
    flag = False
    if (i - 1) >= 0:
        if observation_map[time][i - 1][j] == 'H' and observation_map[time+1][i - 1][j] == 'H':
            flag = True
    """check valid down place"""
    if (i + 1) < num_rows:
        if observation_map[time][i + 1][j] == 'H' and observation_map[time+1][i + 1][j] == 'H':
            flag = True
    """check valid left place"""
    if (j - 1) >= 0:
        if observation_map[time][i][j - 1] == 'H' and observation_map[time+1][i][j - 1] == 'H':
            flag = True
    """check valid right place"""
    if (j + 1) < num_columns:
        if observation_map[time][i][j + 1] == 'H' and observation_map[time+1][i][j + 1] == 'H':
            flag = True
    return flag


# def result():
def solve_problem(input):
    solver = Glucose3()
    num_police = input['police']
    num_medics = input['medics']
    observation_map = input['observations']
    num_rows = len(observation_map[0])
    num_columns = len(observation_map[0][0])
    queries = input['queries']
    distributor = 1
    char_dict, distributor = initial_states(solver, distributor, observation_map, num_rows, num_columns)
    action_dict, distributor = actions_effects(solver, distributor, observation_map, num_rows, num_columns, char_dict, num_police, num_medics)
    no_act_stay(solver, observation_map, num_rows, num_columns, char_dict, action_dict)

    result_dict = {}
    for query in queries:
        """Isolate properties of the current query"""
        query_time = query[1]
        query_i = query[0][0]
        query_j = query[0][1]
        query_char = query[2]
        """Solve with assumption """
        bool_answer = solver.solve(assumptions=[char_dict[query_char][query_time][query_i][query_j]])
        # print(solver.get_model())
        if not bool_answer:
            result_dict[query] = 'F'
        else:
            result_dict[query] = 'T'
            for other_char in ['H', 'Q', 'I', 'U', 'S']:
                if query_char != other_char:
                    temp_bool = solver.solve(assumptions=[char_dict[other_char][query_time][query_i][query_j]])
                    if temp_bool:
                        result_dict[query] = '?'
                        break
    return result_dict
    pass