from pysat.solvers import Glucose3
import numpy as np

ids = ['313551707', '205946866']


def solve_problem(input_problem):
    """ init of variables """
    g = Glucose3()
    num_police = input_problem["police"]
    num_medics = input_problem["medics"]
    num_observations = len(input_problem["observations"])
    num_rows = len(input_problem["observations"][0])
    num_columns = len(input_problem["observations"][0][0])
    queries = input_problem["queries"]
    observations = input_problem["observations"]

    """ create 5 matrix of each status """
    h_matrix = np.zeros((num_observations, num_rows, num_columns), dtype=int)
    s_matrix = np.zeros((num_observations, num_rows, num_columns), dtype=int)
    q_matrix = np.zeros((num_observations, num_rows, num_columns), dtype=int)
    i_matrix = np.zeros((num_observations, num_rows, num_columns), dtype=int)
    u_matrix = np.zeros((num_observations, num_rows, num_columns), dtype=int)

    """ actions for solving """
    atom_num = create_atoms(g, observations, num_rows, num_columns, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix)
    actions_clauses(g, atom_num, observations, num_rows, num_columns, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix, num_police, num_medics)
    return_dict = query_solve(g, queries, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix)
    return return_dict


def create_atoms(g, observations, num_rows, num_columns, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix):
    atom_num = 0
    for time in range(len(observations)):
        for row in range(num_rows):
            for col in range(num_columns):
                atom_list = []
                atom_num = add_clause_by_status(g, 'H', time, row, col, atom_num, observations, h_matrix)
                atom_list.append(atom_num)
                atom_num = add_clause_by_status(g, 'S', time, row, col, atom_num, observations, s_matrix)
                atom_list.append(atom_num)
                atom_num = add_clause_by_status(g, 'Q', time, row, col, atom_num, observations, q_matrix)
                atom_list.append(atom_num)
                atom_num = add_clause_by_status(g, 'I', time, row, col, atom_num, observations, i_matrix)
                atom_list.append(atom_num)
                atom_num = add_clause_by_status(g, 'U', time, row, col, atom_num, observations, u_matrix)
                atom_list.append(atom_num)
                make_xor_clauses_for_states(atom_list, g)
    return atom_num


def add_clause_by_status(g, status, time, row, col, atom_num, observations, temp_matrix):
    atom_num += 1
    if observations[time][row][col] == status:
        g.add_clause([atom_num])
        temp_matrix[time][row][col] = atom_num
    elif observations[time][row][col] == '?':
        temp_matrix[time][row][col] = atom_num
    else:
        g.add_clause([(-1) * atom_num])
        temp_matrix[time][row][col] = atom_num
    return atom_num


def make_actions_clauses(g, atom_num, pre_conditions_list, add_effects_list, del_effects_list):
    """ creating clauses for each list """
    action_pred = atom_num + 1
    for condition in pre_conditions_list:
        if condition[0] == 'T':
            g.add_clause([(-1) * action_pred, int(condition[1])])
        elif condition[0] == 'F':
            g.add_clause([(-1) * action_pred, (-1) * int(condition[1])])

    for condition in add_effects_list:
        g.add_clause([(-1) * action_pred, int(condition)])

    for condition in del_effects_list:
        g.add_clause([(-1) * action_pred, (-1) * int(condition)])

    return action_pred


def actions_clauses(g, atom_num, observations, num_rows, num_columns, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix, num_police, num_medics):
    for time in range(len(observations)-1):
        obs_immune_action_list = []
        obs_quarantine_action_list = []
        for row in range(num_rows):
            for col in range(num_columns):
                atom_num, h_action_list, immune_action_list = h_clauses(g, atom_num, time, row, col, num_rows,
                                                                        num_columns, h_matrix, s_matrix, q_matrix,
                                                                        i_matrix, u_matrix, num_police, num_medics)
                atom_num, s_action_list, quarantine_action_list = s_clauses(g, atom_num, time, row, col, h_matrix,
                                                                            s_matrix, q_matrix, i_matrix, u_matrix,
                                                                            num_police, num_medics)
                atom_num, q_action_list = q_clauses(g, atom_num, time, row, col, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix, num_police, num_medics)
                atom_num, i_action_list = i_clauses(g, atom_num, time, row, col, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix, num_police, num_medics)
                atom_num, u_action_list = u_clauses(g, atom_num, time, row, col, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix, num_police, num_medics)
                xor(h_action_list+s_action_list+q_action_list+i_action_list+u_action_list, g)
                obs_immune_action_list = obs_immune_action_list + immune_action_list
                obs_quarantine_action_list = obs_quarantine_action_list + quarantine_action_list
        if num_medics == 1:
            make_immune_action(g, obs_immune_action_list)
        if num_police == 1:
            make_quarantine_action(g, obs_quarantine_action_list)


def h_clauses(g, atom_num, time, row, col, num_rows, num_columns, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix, num_police, num_medics):
    h_action_list = []
    immune_action_list = []

    """ healthy becoming immune """
    if num_medics > 0:
        pre_condition_list = [('T', h_matrix[time][row][col])]
        add_effects_list = [i_matrix[time+1][row][col]]
        del_effects_list = [h_matrix[time+1][row][col]]
        atom_num = make_actions_clauses(g, atom_num, pre_condition_list, add_effects_list, del_effects_list)
        h_action_list.append(atom_num)
        immune_action_list.append(atom_num)

    """ healthy staying healthy """
    pre_condition_list = [('T', h_matrix[time][row][col])]
    if num_medics > 0:
        pre_condition_list.append(('F', i_matrix[time + 1][row][col]))
    true_list = []
    sick_list = []
    q_list = []
    if row - 1 >= 0:
        """ A neighbor from above """
        sick_list.append((-1)*int(s_matrix[time][row - 1][col]))
        q_list.append(int(q_matrix[time + 1][row - 1][col]))
        true_list.append(True)
    if row + 1 <= num_rows - 1:
        """ A neighbor from below """
        sick_list.append((-1)*int(s_matrix[time][row + 1][col]))
        q_list.append(int(q_matrix[time + 1][row + 1][col]))
        true_list.append(True)
    if col + 1 <= num_columns - 1:
        """ A neighbor to the right """
        sick_list.append((-1)*int(s_matrix[time][row][col + 1]))
        q_list.append(int(q_matrix[time + 1][row][col + 1]))
        true_list.append(True)
    if col - 1 >= 0:
        """ A neighbor to the left """
        sick_list.append((-1)*int(s_matrix[time][row][col - 1]))
        q_list.append(int(q_matrix[time + 1][row][col - 1]))
        true_list.append(True)

    temp_atom_num1 = atom_num + 1
    if len(true_list) == 1:
        add_for_1_clauses_for_H(sick_list, q_list, g, temp_atom_num1)
    elif len(true_list) == 2:
        add_for_2_clauses_for_H(sick_list, q_list, g, temp_atom_num1)
    elif len(true_list) == 3:
        add_for_3_clauses_for_H(sick_list, q_list, g, temp_atom_num1)
    elif len(true_list) == 4:
        add_for_4_clauses_for_H(sick_list, q_list, g, temp_atom_num1)

    add_effects_list = [h_matrix[time + 1][row][col]]
    del_effects_list = []
    atom_num = make_actions_clauses(g, atom_num, pre_condition_list, add_effects_list, del_effects_list)
    h_action_list.append(atom_num)

    """ healthy becoming sick """
    pre_condition_list = [('T', h_matrix[time][row][col])]
    if num_medics > 0:
        pre_condition_list.append(('F', i_matrix[time+1][row][col]))
    true_list = []
    sick_list = []
    q_list = []
    if row - 1 >= 0:
        """ A neighbor from above """
        sick_list.append(int(s_matrix[time][row - 1][col]))
        q_list.append((-1)*int(q_matrix[time + 1][row - 1][col]))
        true_list.append(True)
    if row + 1 <= num_rows - 1:
        """ A neighbor from below """
        sick_list.append(int(s_matrix[time][row + 1][col]))
        q_list.append((-1)*int(q_matrix[time + 1][row + 1][col]))
        true_list.append(True)
    if col + 1 <= num_columns - 1:
        """ A neighbor to the right """
        sick_list.append(int(s_matrix[time][row][col + 1]))
        q_list.append((-1)*int(q_matrix[time + 1][row][col + 1]))
        true_list.append(True)
    if col - 1 >= 0:
        """ A neighbor to the left """
        sick_list.append(int(s_matrix[time][row][col - 1]))
        q_list.append((-1)*int(q_matrix[time + 1][row][col - 1]))
        true_list.append(True)

    temp_atom_num = atom_num + 1
    if len(true_list) == 1:
        add_for_1_clauses(sick_list, q_list, g, temp_atom_num)
    elif len(true_list) == 2:
        add_for_2_clauses(sick_list, q_list, g, temp_atom_num)
    elif len(true_list) == 3:
        add_for_3_clauses(sick_list, q_list, g, temp_atom_num)
    elif len(true_list) == 4:
        add_for_4_clauses(sick_list, q_list, g, temp_atom_num)

    add_effects_list = [s_matrix[time + 1][row][col]]
    del_effects_list = [h_matrix[time + 1][row][col]]
    atom_num = make_actions_clauses(g, atom_num, pre_condition_list, add_effects_list, del_effects_list)
    h_action_list.append(atom_num)

    return atom_num, h_action_list, immune_action_list


def s_clauses(g, atom_num, time, row, col, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix, num_police, num_medics):
    s_action_list = []
    quarantine_action_list = []

    """ sick becoming quarantine """
    if num_police > 0:
        pre_condition_list = [('T', s_matrix[time][row][col])]
        add_effects_list = [q_matrix[time + 1][row][col]]
        del_effects_list = [s_matrix[time + 1][row][col]]
        atom_num = make_actions_clauses(g, atom_num, pre_condition_list, add_effects_list, del_effects_list)
        s_action_list.append(atom_num)
        quarantine_action_list.append(atom_num)

    """ sick staying sick """
    pre_condition_list = [('T', s_matrix[time][row][col])]
    if num_police > 0:
        pre_condition_list.append(('F', q_matrix[time+1][row][col]))
    if time >= 2:
        pre_condition_list.append(('F', s_matrix[time-2][row][col]))
    add_effects_list = [s_matrix[time + 1][row][col]]
    del_effects_list = []
    atom_num = make_actions_clauses(g, atom_num, pre_condition_list, add_effects_list, del_effects_list)
    s_action_list.append(atom_num)

    """ sick becoming healthy """
    pre_condition_list = [('T', s_matrix[time][row][col])]
    if num_police > 0:
        pre_condition_list.append(('F', q_matrix[time+1][row][col]))
    if time >= 2:
        pre_condition_list.append(('T', s_matrix[time-2][row][col]))
        add_effects_list = [h_matrix[time + 1][row][col]]
        del_effects_list = [s_matrix[time + 1][row][col]]
        atom_num = make_actions_clauses(g, atom_num, pre_condition_list, add_effects_list, del_effects_list)
        s_action_list.append(atom_num)
    return atom_num, s_action_list, quarantine_action_list


def q_clauses(g, atom_num, time, row, col, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix, num_police, num_medics):
    q_action_list = []

    """ quarantined staying quarantined """
    pre_condition_list = [('T', q_matrix[time][row][col])]
    if time >= 1:
        pre_condition_list.append(('F', q_matrix[time - 1][row][col]))
    add_effects_list = [q_matrix[time + 1][row][col]]
    del_effects_list = []
    atom_num = make_actions_clauses(g, atom_num, pre_condition_list, add_effects_list, del_effects_list)
    q_action_list.append(atom_num)

    """ quarantined becoming healthy """
    if time >= 1:
        pre_condition_list = [('T', q_matrix[time][row][col]), ('T', q_matrix[time-1][row][col])]
        add_effects_list = [h_matrix[time + 1][row][col]]
        del_effects_list = [q_matrix[time + 1][row][col]]
        atom_num = make_actions_clauses(g, atom_num, pre_condition_list, add_effects_list, del_effects_list)
        q_action_list.append(atom_num)
    return atom_num, q_action_list


def i_clauses(g, atom_num, time, row, col, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix, num_police, num_medics):
    i_action_list = []

    """ immune staying immune """
    pre_condition_list = [('T', i_matrix[time][row][col])]
    add_effects_list = [i_matrix[time + 1][row][col]]
    del_effects_list = []
    atom_num = make_actions_clauses(g, atom_num, pre_condition_list, add_effects_list, del_effects_list)
    i_action_list.append(atom_num)

    return atom_num, i_action_list


def u_clauses(g, atom_num, time, row, col, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix, num_police, num_medics):
    u_action_list = []

    """ unpopulated staying unpopulated """
    pre_condition_list = [('T', u_matrix[time][row][col])]
    add_effects_list = [u_matrix[time + 1][row][col]]
    del_effects_list = []
    atom_num = make_actions_clauses(g, atom_num, pre_condition_list, add_effects_list, del_effects_list)
    u_action_list.append(atom_num)

    return atom_num, u_action_list


def query_solve(g, queries, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix):
    return_dict = {}
    for i in queries:
        flag = True
        row = i[0][0]
        col = i[0][1]
        obs = i[1]
        status = i[2]
        assumption_matrix, all_matrix = search_matrix(status, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix)
        result1 = g.solve(assumptions=[(-1) * int(assumption_matrix[obs][row][col])])
        result2 = g.solve(assumptions=[int(assumption_matrix[obs][row][col])])
        if result1 and (not result2):
            return_dict[i] = 'F'
            continue
        if not result1:
            return_dict[i] = 'T'
        else:
            for matrix in all_matrix:
                result3 = g.solve(assumptions=[(-1) * int(matrix[obs][row][col])])
                if not result3:
                    return_dict[i] = 'F'
                    flag = False
                    break
            if flag:
                return_dict[i] = '?'

    return return_dict


def search_matrix(status, h_matrix, s_matrix, q_matrix, i_matrix, u_matrix):
    assumption_matrix, all_matrix = [], []
    if status == 'H':
        assumption_matrix = h_matrix
        all_matrix = [s_matrix, q_matrix, i_matrix, u_matrix]
    elif status == 'S':
        assumption_matrix = s_matrix
        all_matrix = [h_matrix, q_matrix, i_matrix, u_matrix]
    elif status == 'Q':
        assumption_matrix = q_matrix
        all_matrix = [h_matrix, s_matrix, i_matrix, u_matrix]
    elif status == 'I':
        assumption_matrix = i_matrix
        all_matrix = [h_matrix, s_matrix, q_matrix, u_matrix]
    elif status == 'U':
        assumption_matrix = u_matrix
        all_matrix = [h_matrix, s_matrix, q_matrix, i_matrix]
    return assumption_matrix, all_matrix


def make_xor_clauses_for_states(predicate_list, g):
    predicate_list = list(map(int, predicate_list))
    g.add_clause(predicate_list)

    for i in range(len(predicate_list)):
        for j in range(i+1, len(predicate_list)):
            if i != j:
                g.add_clause([(-1)*predicate_list[i], (-1)*predicate_list[j]])


def xor(predicate_list, g):
    if len(predicate_list) == 2:
        g.add_clause([(-1)*int(predicate_list[0]), (-1)*int(predicate_list[1])])
    else:
        predicate_list = list(map(int, predicate_list))
        g.add_clause(predicate_list)

        for i in range(len(predicate_list)):
            for j in range(i+1, len(predicate_list)):
                g.add_clause([(-1)*predicate_list[i], (-1)*predicate_list[j]])


def make_immune_action(g, obs_immune_action_list):
    obs_immune_action_list = list(map(int, obs_immune_action_list))
    g.add_clause(obs_immune_action_list)

    for i in range(len(obs_immune_action_list)):
        for j in range(i + 1, len(obs_immune_action_list)):
            g.add_clause(([(-1) * obs_immune_action_list[i], (-1) * obs_immune_action_list[j]]))


def make_quarantine_action(g, obs_quarantine_action_list):
    obs_quarantine_action_list = list(map(int, obs_quarantine_action_list))
    g.add_clause(obs_quarantine_action_list)

    for i in range(len(obs_quarantine_action_list)):
        for j in range(i + 1, len(obs_quarantine_action_list)):
            g.add_clause(([(-1) * obs_quarantine_action_list[i], (-1) * obs_quarantine_action_list[j]]))


def add_for_4_clauses(sick_list, q_list, g, temp_atom):
    g.add_clause([(-1) * temp_atom] + sick_list)
    g.add_clause([(-1) * temp_atom, q_list[1], sick_list[0], sick_list[2], sick_list[3]])
    g.add_clause([(-1) * temp_atom, q_list[0], sick_list[1], sick_list[2], sick_list[3]])
    g.add_clause([(-1) * temp_atom, q_list[1], q_list[0], sick_list[2], sick_list[3]])
    g.add_clause([(-1) * temp_atom, q_list[2], sick_list[0], sick_list[1], sick_list[3]])
    g.add_clause([(-1) * temp_atom, q_list[1], q_list[2], sick_list[0], sick_list[3]])
    g.add_clause([(-1) * temp_atom, q_list[0], q_list[2], sick_list[1], sick_list[3]])
    g.add_clause([(-1) * temp_atom, q_list[1], q_list[0], q_list[2], sick_list[3]])
    g.add_clause([(-1) * temp_atom, q_list[3], sick_list[0], sick_list[1], sick_list[2]])
    g.add_clause([(-1) * temp_atom, q_list[1], q_list[3], sick_list[0], sick_list[2]])
    g.add_clause([(-1) * temp_atom, q_list[0], q_list[3], sick_list[1], sick_list[2]])
    g.add_clause([(-1) * temp_atom, q_list[1], q_list[0], q_list[3], sick_list[2]])
    g.add_clause([(-1) * temp_atom, q_list[3], q_list[2], sick_list[0], sick_list[1]])
    g.add_clause([(-1) * temp_atom, q_list[3], q_list[2], q_list[1], sick_list[0]])
    g.add_clause([(-1) * temp_atom, q_list[3], q_list[2], q_list[0], sick_list[1]])
    g.add_clause([(-1) * temp_atom, q_list[1], q_list[0], q_list[2], q_list[3]])


def add_for_4_clauses_for_H(sick_list, q_list, g, temp_atom):
    g.add_clause([(-1) * temp_atom, sick_list[0], q_list[0]])
    g.add_clause([(-1) * temp_atom, sick_list[1], q_list[1]])
    g.add_clause([(-1) * temp_atom, sick_list[2], q_list[2]])
    g.add_clause([(-1) * temp_atom, sick_list[3], q_list[3]])


def add_for_1_clauses(sick_list, q_list, g, temp_atom):
    g.add_clause([(-1) * temp_atom, sick_list[0]])
    g.add_clause([(-1) * temp_atom, q_list[0]])


def add_for_1_clauses_for_H(sick_list, q_list, g, temp_atom):
    g.add_clause([(-1) * temp_atom, sick_list[0], q_list[0]])


def add_for_2_clauses(sick_list, q_list, g, temp_atom):
    g.add_clause([(-1) * temp_atom, sick_list[0], sick_list[1]])
    g.add_clause([(-1) * temp_atom, q_list[1], sick_list[0]])
    g.add_clause([(-1) * temp_atom, q_list[0], sick_list[1]])
    g.add_clause([(-1) * temp_atom, q_list[1], q_list[0]])


def add_for_2_clauses_for_H(sick_list, q_list, g, temp_atom):
    g.add_clause([(-1) * temp_atom, sick_list[0], q_list[0]])
    g.add_clause([(-1) * temp_atom, sick_list[1], q_list[1]])


def add_for_3_clauses(sick_list, q_list, g, temp_atom):
    g.add_clause([(-1) * temp_atom, sick_list[1], sick_list[0], sick_list[2]])
    g.add_clause([(-1) * temp_atom, q_list[1], sick_list[0], sick_list[2]])
    g.add_clause([(-1) * temp_atom, sick_list[1], q_list[0], sick_list[2]])
    g.add_clause([(-1) * temp_atom, q_list[1], q_list[0], sick_list[2]])
    g.add_clause([(-1) * temp_atom, sick_list[1], sick_list[0], q_list[2]])
    g.add_clause([(-1) * temp_atom, q_list[1], sick_list[0], q_list[2]])
    g.add_clause([(-1) * temp_atom, sick_list[1], q_list[0], q_list[2]])
    g.add_clause([(-1) * temp_atom, q_list[1], q_list[0], q_list[2]])


def add_for_3_clauses_for_H(sick_list, q_list, g, temp_atom):
    g.add_clause([(-1) * temp_atom, sick_list[0], q_list[0]])
    g.add_clause([(-1) * temp_atom, sick_list[1], q_list[1]])
    g.add_clause([(-1) * temp_atom, sick_list[2], q_list[2]])
