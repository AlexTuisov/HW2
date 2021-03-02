import numpy as np
from pysat.solvers import Glucose3
from itertools import chain, combinations
from sympy import *


ids = ['208451997', '307871376']


def get_initial_observations(raw_observations, sat_model):
    clauses = {}
    n_obs = len(raw_observations)
    n_rows = len(raw_observations[0])
    n_cols = len(raw_observations[0][0])
    # initial all observations arrays by time, i and j
    h_observations = np.zeros((n_obs, n_rows, n_cols), dtype=int)
    s_observations = np.zeros((n_obs, n_rows, n_cols), dtype=int)
    i_observations = np.zeros((n_obs, n_rows, n_cols), dtype=int)
    q_observations = np.zeros((n_obs, n_rows, n_cols), dtype=int)
    u_observations = np.zeros((n_obs, n_rows, n_cols), dtype=int)
    # initial actions arrays by time, i and j
    h_infect_actions = np.zeros((n_obs, n_rows, n_cols), dtype=int)
    s_recover_actions = np.zeros((n_obs, n_rows, n_cols), dtype=int)
    h_medics_actions = np.zeros((n_obs, n_rows, n_cols), dtype=int)
    s_police_actions = np.zeros((n_obs, n_rows, n_cols), dtype=int)
    s_no_op = np.zeros((n_obs, n_rows, n_cols), dtype=int)
    h_no_op = np.zeros((n_obs, n_rows, n_cols), dtype=int)
    i_no_op = np.zeros((n_obs, n_rows, n_cols), dtype=int)
    q_no_op = np.zeros((n_obs, n_rows, n_cols), dtype=int)
    q_out_to_h = np.zeros((n_obs, n_rows, n_cols), dtype=int)
    u_no_op = np.zeros((n_obs, n_rows, n_cols), dtype=int)
    # initial clause numbers
    clause_num = 1
    for time in range(n_obs):
        for row in range(n_rows):
            for col in range(n_cols):
                # according to (time,i,j), give negative clause if false, positive otherwise.
                if raw_observations[time][row][col] == "H":
                    h_observations[time][row][col] = clause_num
                    sat_model.add_clause([clause_num])
                    clause_num += 1
                    h_infect_actions[time][row][col] = clause_num
                    clause_num += 1
                    h_medics_actions[time][row][col] = clause_num
                    clause_num += 1
                    h_no_op[time][row][col] = clause_num
                    clause_num += 1
                    s_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    # s_police_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    i_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    q_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    u_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    # s_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # s_recover_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # i_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # q_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # u_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # q_out_to_h[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                elif raw_observations[time][row][col] == "S":
                    h_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    # h_medics_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    s_recover_actions[time][row][col] = clause_num
                    clause_num += 1
                    s_police_actions[time][row][col] = clause_num
                    clause_num += 1
                    s_no_op[time][row][col] = clause_num
                    clause_num += 1
                    s_observations[time][row][col] = clause_num
                    sat_model.add_clause([clause_num])
                    clause_num += 1
                    i_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    q_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    u_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    # h_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # h_infect_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # i_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # q_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # u_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # q_out_to_h[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                elif raw_observations[time][row][col] == "I":
                    h_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    # h_medics_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # s_police_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    s_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    i_observations[time][row][col] = clause_num
                    sat_model.add_clause([clause_num])
                    clause_num += 1
                    q_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    u_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    # s_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # h_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # s_recover_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # h_infect_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    i_no_op[time][row][col] = clause_num
                    sat_model.add_clause([clause_num])
                    clause_num += 1
                    # q_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # u_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # q_out_to_h[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                elif raw_observations[time][row][col] == "Q":
                    h_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    # h_medics_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # s_police_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    s_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    i_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    q_observations[time][row][col] = clause_num
                    sat_model.add_clause([clause_num])
                    clause_num += 1
                    u_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    # s_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # h_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # s_recover_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # h_infect_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # i_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    q_no_op[time][row][col] = clause_num
                    clause_num += 1
                    # u_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    q_out_to_h[time][row][col] = clause_num
                    clause_num += 1
                elif raw_observations[time][row][col] == "U":
                    h_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    # s_police_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # h_medics_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    s_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    i_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    q_observations[time][row][col] = clause_num
                    sat_model.add_clause([-clause_num])
                    clause_num += 1
                    u_observations[time][row][col] = clause_num
                    sat_model.add_clause([clause_num])
                    clause_num += 1
                    # s_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # h_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # s_recover_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # h_infect_actions[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # i_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    # q_no_op[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                    u_no_op[time][row][col] = clause_num
                    sat_model.add_clause([clause_num])
                    clause_num += 1
                    # q_out_to_h[time][row][col] = clause_num
                    # sat_model.add_clause([-clause_num])
                    # clause_num += 1
                # not inserting '?' clauses into the solver yet.
                elif raw_observations[time][row][col] == "?":
                    h_observations[time][row][col] = clause_num
                    clause_num += 1
                    s_observations[time][row][col] = clause_num
                    clause_num += 1
                    u_observations[time][row][col] = clause_num
                    clause_num += 1
                    if time != 0:
                        i_observations[time][row][col] = clause_num
                        clause_num += 1
                        q_observations[time][row][col] = clause_num
            # One clause is positive out of 5
                        one_and_only([clause_num, clause_num - 1, clause_num - 2, clause_num - 3, clause_num - 4], sat_model)
                        clause_num += 1
                    else:
                        i_observations[time][row][col] = clause_num
                        sat_model.add_clause([-clause_num])
                        clause_num += 1
                        q_observations[time][row][col] = clause_num
                        sat_model.add_clause([-clause_num])
                        one_and_only([clause_num - 2, clause_num - 3, clause_num - 4], sat_model)
                        clause_num += 1
                    h_infect_actions[time][row][col] = clause_num
                    clause_num += 1
                    h_medics_actions[time][row][col] = clause_num
                    clause_num += 1
                    h_no_op[time][row][col] = clause_num
                    clause_num += 1
                    s_no_op[time][row][col] = clause_num
                    clause_num += 1
                    s_recover_actions[time][row][col] = clause_num
                    clause_num += 1
                    s_police_actions[time][row][col] = clause_num
                    clause_num += 1
                    i_no_op[time][row][col] = clause_num
                    clause_num += 1
                    q_no_op[time][row][col] = clause_num
                    clause_num += 1
                    u_no_op[time][row][col] = clause_num
                    clause_num += 1
                    q_out_to_h[time][row][col] = clause_num
                    one_and_only(
                        [clause_num, clause_num - 1, clause_num - 2, clause_num - 3, clause_num - 4, clause_num - 5,
                         clause_num - 6, clause_num - 7, clause_num - 8, clause_num - 9], sat_model)
                    clause_num += 1
    clauses["h_observations"] = h_observations
    clauses["s_observations"] = s_observations
    clauses["i_observations"] = i_observations
    clauses["q_observations"] = q_observations
    clauses["u_observations"] = u_observations
    clauses["h_infect_actions"] = h_infect_actions
    clauses["s_recover_actions"] = s_recover_actions
    clauses["h_medics_actions"] = h_medics_actions
    clauses["s_police_actions"] = s_police_actions
    clauses["raw_observations"] = raw_observations
    clauses["h_no_op"] = h_no_op
    clauses["s_no_op"] = s_no_op
    clauses["i_no_op"] = i_no_op
    clauses["q_no_op"] = q_no_op
    clauses["u_no_op"] = u_no_op
    clauses["q_out_to_h"] = q_out_to_h
    return clauses


def get_pre_h_infect(h, clauses, sat_model):
    pre = []
    row_lim = len(clauses["s_observations"][0])
    col_lim = len(clauses["s_observations"][0][0])
    time = h[0]
    i = h[1]
    j = h[2]
    cl = int(clauses["h_infect_actions"][time][i][j])
    h_neighbours = tuple(((i+1, j), (i, j+1), (i-1, j), (i, j-1)))
    for tile in h_neighbours:
        if 0 <= tile[0] < row_lim and 0 <= tile[1] < col_lim:
            pre.append(int(clauses["s_observations"][time][tile[0]][tile[1]]))
            # If there is a neighbour 'S', he will infect 'H' for sure
            sat_model.add_clause([int(-clauses["s_observations"][time][tile[0]][tile[1]]), int(-clauses["h_observations"][time][i][j]), cl])
    pre.append(-cl)
    sat_model.add_clause(pre)


def get_add_eff_h_infect(h, clauses, sat_model):
    time = h[0]
    i = h[1]
    j = h[2]
    cl = int(clauses["h_infect_actions"][time][i][j])
    sat_model.add_clause([-cl, int(clauses["s_observations"][time + 1][i][j])])


def get_del_eff_h_infect(h, clauses, sat_model):
    time = h[0]
    i = h[1]
    j = h[2]
    cl = int(clauses["h_infect_actions"][time][i][j])
    sat_model.add_clause([-cl, int(-clauses["h_observations"][time + 1][i][j])])


def infect_h_total_conditions(h, clauses, sat_model):
    get_pre_h_infect(h, clauses, sat_model)
    get_add_eff_h_infect(h, clauses, sat_model)
    get_del_eff_h_infect(h, clauses, sat_model)


def get_del_eff_s_recover(curr_s, clauses, sat_model):
    time = curr_s[0]
    i = curr_s[1]
    j = curr_s[2]
    cl = int(clauses["s_recover_actions"][time][i][j])
    sat_model.add_clause([-cl, int(-clauses["s_observations"][time + 1][i][j])])


def get_add_eff_s_recover(curr_s, clauses, sat_model):
    time = curr_s[0]
    i = curr_s[1]
    j = curr_s[2]
    cl = int(clauses["s_recover_actions"][time][i][j])
    sat_model.add_clause([-cl, int(clauses["h_observations"][time + 1][i][j])])


def get_pre_s_recover(curr_s, clauses, sat_model):
    time = curr_s[0]
    i = curr_s[1]
    j = curr_s[2]
    cl = int(clauses["s_recover_actions"][time][i][j])
    sat_model.add_clause([-cl, int(clauses["s_observations"][time][i][j])])
    sat_model.add_clause([-cl, int(clauses["s_observations"][time - 1][i][j])])
    sat_model.add_clause([-cl, int(clauses["s_observations"][time - 2][i][j])])
    sat_model.add_clause([int(-clauses["s_observations"][time][i][j]), int(-clauses["s_observations"][time - 1][i][j]),
                          int(-clauses["s_observations"][time - 2][i][j]),
                          int(clauses["s_recover_actions"][time][i][j])])


def recover_s_total_conditions(sat_model, curr_s, clauses):
    get_pre_s_recover(curr_s, clauses, sat_model)
    get_add_eff_s_recover(curr_s, clauses, sat_model)
    get_del_eff_s_recover(curr_s, clauses, sat_model)


def solve_problem(problem):
    g = Glucose3()
    police = problem["police"]
    medics = problem["medics"]
    queries = problem["queries"]
    raw_observations = problem["observations"]
    # get initial arrays with clauses numbers
    clauses = get_initial_observations(raw_observations, g)
    # check if the problem is "easy"
    if police == 0 and medics == 0:
        res_dict = solve_problem_no_teams(clauses, queries, g)
        return res_dict
    # otherwise solve with complexity
    else:
        res_dict = solve_problem_with_teams(clauses, police, medics, queries, g)
        return res_dict


def get_extra_conditions_h(curr_h, clauses, sat_model):
    time = curr_h[0]
    i = curr_h[1]
    j = curr_h[2]
    # If H becomes S, make h_infect live
    sat_model.add_clause([int(-clauses["h_observations"][time][i][j]), int(-clauses["s_observations"][time + 1][i][j]),
                          int(clauses["h_infect_actions"][time][i][j])])
    # If nothing happen, make no op live
    sat_model.add_clause([int(-clauses["h_observations"][time][i][j]), int(-clauses["h_observations"][time + 1][i][j]),
                          int(clauses["h_no_op"][time][i][j])])


def get_extra_conditions_s(curr_s, clauses, sat_model):
    time = curr_s[0]
    i = curr_s[1]
    j = curr_s[2]
    # If nothing happen, make no op live
    sat_model.add_clause([int(-clauses["s_observations"][time][i][j]),
                          int(-clauses["s_observations"][time + 1][i][j]),
                          int(clauses["s_no_op"][time][i][j])])
    # if H become S than REC must happen
    sat_model.add_clause(([int(-clauses["h_observations"][time + 1][i][j]),
                           int(-clauses["s_observations"][time][i][j]),
                           int(clauses["s_recover_actions"][time][i][j])]))


def solve_problem_no_teams(clauses, queries, sat_model):
    # get clauses for all 'H' in map
    time_lim = len(clauses["h_observations"])
    n_rows = len(clauses["h_observations"][0])
    n_cols = len(clauses["h_observations"][0][0])
    dict_to_return = {}
    recover_flag = bool(time_lim >= 4)
    for time in range(time_lim - 1):
        for i in range(n_rows):
            for j in range(n_cols):
                if clauses["raw_observations"][time][i][j] == 'H':
                    curr_h = tuple((time, i, j))
                    infect_h_total_conditions(curr_h, clauses, sat_model)
                    insert_noop_h_clause(sat_model, curr_h, clauses)
                    get_extra_conditions_h(curr_h, clauses, sat_model)
                    one_and_only([int(clauses["h_infect_actions"][time][i][j]), int(clauses["h_no_op"][time][i][j])], sat_model)
                elif clauses["raw_observations"][time][i][j] == 'S':
                    curr_s = tuple((time, i, j))
                    insert_noop_s_clause(sat_model, curr_s, clauses)
                    get_extra_conditions_s(curr_s, clauses, sat_model)
                    one_and_only([int(clauses["s_no_op"][time][i][j]), int(clauses["s_recover_actions"][time][i][j])], sat_model)
                    if recover_flag:
                        if time >= 2:
                            recover_s_total_conditions(sat_model, curr_s, clauses)
                        else:
                            sat_model.add_clause([int(clauses["s_no_op"][time][i][j])])
                            sat_model.add_clause([int(-clauses["s_recover_actions"][time][i][j])])

                    else:
                        # 'S' stay 'S' if there is not time to recover
                        sat_model.add_clause([int(clauses["s_no_op"][time][i][j])])
                        sat_model.add_clause([int(-clauses["s_recover_actions"][time][i][j])])
                elif clauses["raw_observations"][time][i][j] == 'U':
                    curr_u = tuple((time, i, j))
                    insert_noop_u_clause(sat_model, curr_u, clauses)
                    sat_model.add_clause([int(-clauses["u_observations"][time][i][j]), int(-clauses["u_observations"][time + 1][i][j]), int(clauses["u_no_op"][time][i][j])])
                    sat_model.add_clause([int(clauses["u_no_op"][time][i][j])])
                elif clauses["raw_observations"][time][i][j] == '?':
                    curr_ques = tuple((time, i, j))
                    one_and_only([int(clauses["h_no_op"][time][i][j]), int(clauses["s_no_op"][time][i][j]),
                                  int(clauses["s_recover_actions"][time][i][j]),
                                  int(clauses["h_infect_actions"][time][i][j]),
                                  int(clauses["u_no_op"][time][i][j])], sat_model)
                    infect_h_total_conditions(curr_ques, clauses, sat_model)
                    insert_noop_h_clause(sat_model, curr_ques, clauses)
                    get_extra_conditions_h(curr_ques, clauses, sat_model)
                    insert_noop_s_clause(sat_model, curr_ques, clauses)
                    get_extra_conditions_s(curr_ques, clauses, sat_model)
                    if recover_flag:
                        if time >= 2:
                            recover_s_total_conditions(sat_model, curr_ques, clauses)
                        else:
                            sat_model.add_clause([int(-clauses["s_recover_actions"][time][i][j])])
                    else:
                        # 'S' stay 'S' if there is not time to recover
                        sat_model.add_clause([int(-clauses["s_recover_actions"][time][i][j])])
                    insert_noop_u_clause(sat_model, curr_ques, clauses)
                    sat_model.add_clause(
                        [int(-clauses["u_observations"][time][i][j]), int(-clauses["u_observations"][time + 1][i][j]),
                         int(clauses["u_no_op"][time][i][j])])
                    sat_model.add_clause([int(-clauses["u_observations"][time][i][j]), int(clauses["u_no_op"][time][i][j])])
                sat_model.add_clause(
                    [int(-clauses["u_observations"][time + 1][i][j]), int(clauses["u_observations"][time][i][j])])
                sat_model.add_clause(
                    [int(-clauses["q_observations"][time + 1][i][j]), int(clauses["q_observations"][time][i][j])])
                sat_model.add_clause(
                    [int(-clauses["i_observations"][time + 1][i][j]), int(clauses["i_observations"][time][i][j])])
    # after the model is complete, check for solutions with suggested queries
    for query in queries:
        i = query[0][0]
        j = query[0][1]
        time = query[1]
        type_obs = query[2]
        if type_obs in ['Q', 'I'] and time == 0:
            dict_to_return[query] = 'F'
        else:
            if type_obs == 'H':
                if not sat_model.solve(assumptions=[int(clauses["h_observations"][time][i][j])]):
                    dict_to_return[query] = 'F'
                else:
                    for observation in ['s_observations', 'i_observations', 'q_observations', 'u_observations']:
                        if sat_model.solve(assumptions=[int(clauses[observation][time][i][j])]):
                            dict_to_return[query] = '?'
                            break
                        dict_to_return[query] = 'T'
            elif type_obs == 'S':
                if not sat_model.solve(assumptions=[int(clauses["s_observations"][time][i][j])]):
                    dict_to_return[query] = 'F'
                else:
                    for observation in ['h_observations', 'i_observations', 'q_observations', 'u_observations']:
                        if sat_model.solve(assumptions=[int(clauses[observation][time][i][j])]):
                            dict_to_return[query] = '?'
                            break
                        dict_to_return[query] = 'T'
            elif type_obs == 'I':
                if not sat_model.solve(assumptions=[int(clauses["i_observations"][time][i][j])]):
                    dict_to_return[query] = 'F'
                else:
                    for observation in ['h_observations', 's_observations', 'q_observations', 'u_observations']:
                        if sat_model.solve(assumptions=[int(clauses[observation][time][i][j])]):
                            dict_to_return[query] = '?'
                            break
                        dict_to_return[query] = 'T'
            elif type_obs == 'Q':
                if not sat_model.solve(assumptions=[int(clauses["q_observations"][time][i][j])]):
                    dict_to_return[query] = 'F'
                else:
                    for observation in ['h_observations', 'i_observations', 's_observations', 'u_observations']:
                        if sat_model.solve(assumptions=[int(clauses[observation][time][i][j])]):
                            dict_to_return[query] = '?'
                            break
                        dict_to_return[query] = 'T'
            elif type_obs == 'U':
                if not sat_model.solve(assumptions=[int(clauses["u_observations"][time][i][j])]):
                    dict_to_return[query] = 'F'
                else:
                    for observation in ['h_observations', 'i_observations', 'q_observations', 's_observations']:
                        if sat_model.solve(assumptions=[int(clauses[observation][time][i][j])]):
                            dict_to_return[query] = '?'
                            break
                        dict_to_return[query] = 'T'
    return dict_to_return


def get_pre_h_med(curr_h, clauses, sat_model):
    time = curr_h[0]
    i = curr_h[1]
    j = curr_h[2]
    cl = int(clauses["h_medics_actions"][time][i][j])
    sat_model.add_clause([-cl, int(clauses["h_observations"][time][i][j])])


def get_add_eff_h_med(curr_h, clauses, sat_model):
    time = curr_h[0]
    i = curr_h[1]
    j = curr_h[2]
    cl = int(clauses["h_medics_actions"][time][i][j])
    sat_model.add_clause([-cl, int(clauses["i_observations"][time + 1][i][j])])


def get_del_eff_h_med(curr_h, clauses, sat_model):
    time = curr_h[0]
    i = curr_h[1]
    j = curr_h[2]
    cl = int(clauses["h_medics_actions"][time][i][j])
    sat_model.add_clause([-cl, int(-clauses["h_observations"][time + 1][i][j])])


def med_h_total_conditions(curr_h, clauses, sat_model):
    get_pre_h_med(curr_h, clauses, sat_model)
    get_add_eff_h_med(curr_h, clauses, sat_model)
    get_del_eff_h_med(curr_h, clauses, sat_model)


def get_lim_clauses_s_police(sat_model, police, clauses, police_options, police_opt_val):
    len_police_options = len(police_options)
    if police == 1:
        # make only one action of medic possible
        if len_police_options > 1:
            one_at_most(police_options, police_opt_val, sat_model, 1)
        else:
            # if only one medic and only one option for H, we will send it for sure
            sat_model.add_clause([-police_opt_val[0], police_options[0]])
    # if more than one medics team
    else:
        # if there enough teams to send everywhere
        if len_police_options <= police:
            one_at_most(police_options, police_opt_val, sat_model, police)
        # if not enough teams to send:
        else:
            one_at_most(police_options, police_opt_val, sat_model, police)


def get_lim_clauses_h_med(sat_model, medics, clauses, med_options, med_opt_val):
    len_med_options = len(med_options)
    if medics == 1:
        # make only one action of medic possible
        if len_med_options > 1:
            one_at_most(med_options, med_opt_val, sat_model, 1)
        else:
            # if only one medic and only one option for H, we will send it for sure
            sat_model.add_clause([-med_opt_val[0], med_options[0]])
    # if more than one medics team
    else:
        # if there enough teams to send everywhere
        if len_med_options <= medics:
            one_at_most(med_options, med_opt_val, sat_model, medics)
        # if not enough teams to send:
        else:
            one_at_most(med_options, med_opt_val, sat_model, medics)


def one_at_most(med_options, med_opt_val, sat_model, num_send_options):
    i = 0
    power_police = list(chain.from_iterable(combinations(med_options, r) for r in range(num_send_options + 1)))[1:]
    power_police_smaller = tuple()
    if power_police:
        big_action = len(power_police[-1])
        power_police_smaller = tuple((x for x in power_police if len(x) == big_action))
    cl = np.zeros(len(med_options), dtype=object)
    for item in med_options:
        cl[i] = tuple((symbols('{}'.format(item)), symbols('{}'.format(med_opt_val[i]))))
        i += 1
    formulas = np.zeros(len(power_police_smaller), dtype=object)
    for j in range(len(formulas)):
        i = 0
        if j == 0:
            no_h_in_map_cl = ~cl[0][0] & ~cl[0][1]
        for cli in cl:
            if i != 0 and j == 0:
                no_h_in_map_cl = no_h_in_map_cl & ~cli[0] & ~cli[1]
            if i == 0 and med_options[i] in power_police_smaller[j]:
                formulas[j] = cli[0] & cli[1]
            elif i == 0 and med_options[i] not in power_police_smaller[j]:
                formulas[j] = ~cli[0]
            elif i != 0 and med_options[i] in power_police_smaller[j]:
                formulas[j] = formulas[j] & cli[0] & cli[1]
            else:
                formulas[j] = formulas[j] & ~cli[0]
            i += 1
    formula = formulas[0]
    for i in range(1, len(formulas)):
        formula = formula | (formulas[i])
    formula = formula & no_h_in_map_cl
    cnf_formula = to_cnf(formula, simplify=True, force=True)
    for item in cnf_formula.args:
        cl_to_upload = []
        for cl in item.args:
            if type(cl) == Not:
                cl_to_upload.append(-int(str(cl.args[0])))
            else:
                cl_to_upload.append(int(str(cl)))
        sat_model.add_clause(cl_to_upload)


def get_del_eff_s_police(curr_s, clauses, sat_model):
    time = curr_s[0]
    i = curr_s[1]
    j = curr_s[2]
    cl = int(clauses["s_police_actions"][time][i][j])
    time_lim = len(clauses["h_observations"])
    sat_model.add_clause([-cl, int(-clauses["h_observations"][time + 1][i][j])])
    time += 2
    if time < time_lim:
        sat_model.add_clause([-cl, int(-clauses["h_observations"][time][i][j])])
    time += 1
    if time < time_lim:
        sat_model.add_clause([-cl, int(-clauses["q_observations"][time][i][j])])


def get_add_eff_s_police(curr_s, clauses, sat_model):
    time = curr_s[0]
    i = curr_s[1]
    j = curr_s[2]
    cl = int(clauses["s_police_actions"][time][i][j])
    time_lim = len(clauses["h_observations"])
    sat_model.add_clause([-cl, int(clauses["q_observations"][time + 1][i][j])])
    if clauses["raw_observations"][time + 1][i][j] in ['?', 'Q']:
        sat_model.add_clause([-cl, int(-clauses["q_observations"][time + 1][i][j]), int(clauses["q_no_op"][time + 1][i][j])])
    time += 2
    if time < time_lim:
        sat_model.add_clause([-cl, int(clauses["q_observations"][time][i][j])])
        if clauses["raw_observations"][time][i][j] in ['?', 'Q']:
            sat_model.add_clause([-cl, int(-clauses["q_observations"][time][i][j]), int(clauses["q_out_to_h"][time][i][j])])
    time += 1
    if time < time_lim:
        sat_model.add_clause([-cl, int(clauses["h_observations"][time][i][j])])


def get_pre_s_police(curr_s, clauses, sat_model):
    time = curr_s[0]
    i = curr_s[1]
    j = curr_s[2]
    cl = int(clauses["s_police_actions"][time][i][j])
    sat_model.add_clause([-cl, int(clauses["s_observations"][time][i][j])])


def police_s_total_conditions(curr_s, clauses, sat_model):
    get_pre_s_police(curr_s, clauses, sat_model)
    get_add_eff_s_police(curr_s, clauses, sat_model)
    get_del_eff_s_police(curr_s, clauses, sat_model)


def insert_noop_h_clause(sat_model, curr_h, clauses):
    time = curr_h[0]
    i = curr_h[1]
    j = curr_h[2]
    cl = int(clauses["h_no_op"][time][i][j])
    sat_model.add_clause([-cl, int(-clauses["h_observations"][time][i][j]), int(clauses["h_observations"][time + 1][i][j])])
    sat_model.add_clause([-cl, int(clauses["h_observations"][time][i][j])])
    sat_model.add_clause([-cl, int(clauses["h_observations"][time + 1][i][j])])


def insert_noop_s_clause(sat_model, curr_s, clauses):
    time = curr_s[0]
    i = curr_s[1]
    j = curr_s[2]
    cl = int(clauses["s_no_op"][time][i][j])
    # pre opp
    sat_model.add_clause([-cl, int(-clauses["s_observations"][time][i][j]), int(clauses["s_observations"][time + 1][i][j])])
    sat_model.add_clause([-cl, int(clauses["s_observations"][time][i][j])])
    sat_model.add_clause([-cl, int(clauses["s_observations"][time + 1][i][j])])


def insert_noop_i_clause(sat_model, curr_h, clauses):
    time = curr_h[0]
    i = curr_h[1]
    j = curr_h[2]
    cl = int(clauses["i_no_op"][time][i][j])
    sat_model.add_clause([-cl, int(clauses["i_observations"][time][i][j])])
    sat_model.add_clause([-cl, int(-clauses["i_observations"][time][i][j]), int(clauses["i_observations"][time + 1][i][j])])


def insert_noop_q_clause(sat_model, curr_h, clauses):
    time = curr_h[0]
    i = curr_h[1]
    j = curr_h[2]
    cl = int(clauses["q_no_op"][time][i][j])
    sat_model.add_clause([-cl, int(clauses["q_observations"][time][i][j])])
    sat_model.add_clause([-cl, int(-clauses["q_observations"][time][i][j]), int(clauses["q_observations"][time + 1][i][j])])


def insert_noop_u_clause(sat_model, curr_h, clauses):
    time = curr_h[0]
    i = curr_h[1]
    j = curr_h[2]
    cl = int(clauses["u_no_op"][time][i][j])
    sat_model.add_clause([-cl, int(clauses["u_observations"][time][i][j])])
    sat_model.add_clause([-cl, int(-clauses["u_observations"][time][i][j]), int(clauses["u_observations"][time + 1][i][j])])


def insert_q_out_to_h_clause(sat_model, curr_h, clauses):
    time = curr_h[0]
    i = curr_h[1]
    j = curr_h[2]
    cl = int(clauses["q_out_to_h"][time][i][j])
    if time >= 2:
        # pre conditions
        sat_model.add_clause(
            [-cl, int(clauses["q_observations"][time][i][j])])
        sat_model.add_clause(
            [-cl, int(clauses["q_observations"][time - 1][i][j])])
        # add effect
        sat_model.add_clause([-cl, int(-clauses["q_observations"][time][i][j]), int(clauses["h_observations"][time + 1][i][j])])
    else:
        sat_model.add_clause([int(-clauses["q_out_to_h"][time][i][j])])


def one_and_only(clauses, sat_model):
    or_cl = []
    lim = len(clauses)
    for i in range(lim):
        or_cl.append(clauses[i])
        for j in range(i + 1, lim):
            sat_model.add_clause([-clauses[i], -clauses[j]])
    sat_model.add_clause(or_cl)


def get_pre_h_infect_with_teams(h, clauses, sat_model):
    pre = []
    row_lim = len(clauses["s_observations"][0])
    col_lim = len(clauses["s_observations"][0][0])
    time = h[0]
    i = h[1]
    j = h[2]
    cl = int(clauses["h_infect_actions"][time][i][j])
    sat_model.add_clause([-cl, int(-clauses["h_medics_actions"][time][i][j])])
    sat_model.add_clause([-cl, int(clauses["h_observations"][time][i][j])])
    h_neighbours = tuple(((i+1, j), (i, j+1), (i-1, j), (i, j-1)))
    for tile in h_neighbours:
        if 0 <= tile[0] < row_lim and 0 <= tile[1] < col_lim:
            if clauses["raw_observations"][time][tile[0]][tile[1]] in ['S', '?']:
                pre.append([int(clauses["s_observations"][time][tile[0]][tile[1]]), int(clauses["s_police_actions"][time][tile[0]][tile[1]])])
                # If there is a neighbour 'S', he will infect 'H' for sure
                sat_model.add_clause([int(-clauses["s_observations"][time][tile[0]][tile[1]]),
                                      int(clauses["s_police_actions"][time][tile[0]][tile[1]]),
                                      int(clauses["h_medics_actions"][time][i][j]), int(-clauses["h_observations"][time][i][j]), cl])
    idx = len(pre)
    if idx == 2:
        sat_model.add_clause([pre[0][0], pre[1][0], -cl])
        sat_model.add_clause([pre[0][0], -pre[1][1], -cl])
        sat_model.add_clause([pre[1][0], -pre[0][1], -cl])
        sat_model.add_clause([-pre[0][1], -pre[1][1], -cl])
    elif idx == 3:
        sat_model.add_clause([pre[0][0], pre[1][0], pre[2][0], -cl])
        sat_model.add_clause([pre[0][0], pre[1][0], -pre[2][1], -cl])
        sat_model.add_clause([pre[0][0], pre[2][0], -pre[1][1], -cl])
        sat_model.add_clause([pre[1][0], pre[2][0], -pre[0][1], -cl])
        sat_model.add_clause([pre[0][0], -pre[1][1], -pre[2][1], -cl])
        sat_model.add_clause([pre[1][0], -pre[0][1], -pre[2][1], -cl])
        sat_model.add_clause([pre[2][0], -pre[0][1], -pre[1][1], -cl])
        sat_model.add_clause([-pre[0][1], -pre[1][1], -pre[2][1], -cl])
    elif idx == 4:
        sat_model.add_clause([pre[0][0], pre[1][0], pre[2][0], pre[3][0], -cl])
        sat_model.add_clause([pre[0][0], pre[1][0], pre[2][0], -pre[3][1], -cl])
        sat_model.add_clause([pre[0][0], pre[1][0], pre[3][0], -pre[2][1], -cl])
        sat_model.add_clause([pre[0][0], pre[2][0], pre[3][0], -pre[1][1], -cl])
        sat_model.add_clause([pre[1][0], pre[2][0], pre[3][0], -pre[0][1], -cl])
        sat_model.add_clause([pre[0][0], pre[1][0], -pre[2][1], -pre[3][1], -cl])
        sat_model.add_clause([pre[0][0], pre[2][0], -pre[1][1], -pre[3][1], -cl])
        sat_model.add_clause([pre[0][0], pre[3][0], -pre[1][1], -pre[2][1], -cl])
        sat_model.add_clause([pre[1][0], pre[2][0], -pre[0][1], -pre[3][1], -cl])
        sat_model.add_clause([pre[1][0], pre[3][0], -pre[0][1], -pre[2][1], -cl])
        sat_model.add_clause([pre[2][0], pre[3][0], -pre[0][1], -pre[1][1], -cl])
        sat_model.add_clause([pre[0][0], -pre[1][1], -pre[2][1], -pre[3][1], -cl])
        sat_model.add_clause([pre[1][0], -pre[0][1], -pre[2][1], -pre[3][1], -cl])
        sat_model.add_clause([pre[2][0], -pre[0][1], -pre[1][1], -pre[3][1], -cl])
        sat_model.add_clause([pre[3][0], -pre[0][1], -pre[1][1], -pre[2][1], -cl])
        sat_model.add_clause([-pre[0][1], -pre[1][1], -pre[2][1], -pre[3][1], -cl])


def get_add_eff_h_infect_with_teams(curr_h, clauses, sat_model):
    time = curr_h[0]
    i = curr_h[1]
    j = curr_h[2]
    cl = int(clauses["h_infect_actions"][time][i][j])
    sat_model.add_clause([-cl, int(clauses["s_observations"][time + 1][i][j])])


def get_del_eff_h_infect_with_teams(curr_h, clauses, sat_model):
    time = curr_h[0]
    i = curr_h[1]
    j = curr_h[2]
    cl = int(clauses["h_infect_actions"][time][i][j])
    sat_model.add_clause([-cl, int(-clauses["h_observations"][time + 1][i][j])])


def infect_h_total_conditions_with_teams(curr_h, clauses, sat_model):
    get_pre_h_infect_with_teams(curr_h, clauses, sat_model)
    get_add_eff_h_infect_with_teams(curr_h, clauses, sat_model)
    get_del_eff_h_infect_with_teams(curr_h, clauses, sat_model)


def get_pre_s_recover_with_teams(curr_s, clauses, sat_model):
    time = curr_s[0]
    i = curr_s[1]
    j = curr_s[2]
    cl = int(clauses["s_recover_actions"][time][i][j])
    sat_model.add_clause([-cl, -int(clauses["s_police_actions"][time][i][j])])
    sat_model.add_clause([-cl, int(clauses["s_observations"][time][i][j])])
    if clauses["raw_observations"][time - 1][i][j] in ['?', 'S']:
        sat_model.add_clause([-cl, -int(clauses["s_police_actions"][time - 1][i][j])])
    sat_model.add_clause([-cl, int(clauses["s_observations"][time - 1][i][j])])
    if clauses["raw_observations"][time - 2][i][j] in ['?', 'S']:
        sat_model.add_clause([-cl, -int(clauses["s_police_actions"][time - 2][i][j])])
    sat_model.add_clause([-cl, int(clauses["s_observations"][time - 2][i][j])])


def recover_s_total_conditions_with_teams(sat_model, curr_s, clauses):
    get_pre_s_recover_with_teams(curr_s, clauses, sat_model)
    get_add_eff_s_recover(curr_s, clauses, sat_model)
    get_del_eff_s_recover(curr_s, clauses, sat_model)


def no_op_terms(curr, clauses, sat_model, o_type):
    time = curr[0]
    i = curr[1]
    j = curr[2]
    if o_type == 'H':
        # If nothing happen, make no op live for H
        sat_model.add_clause(
            [int(-clauses["h_observations"][time][i][j]), int(-clauses["h_observations"][time + 1][i][j]),
             int(clauses["h_no_op"][time][i][j])])
    elif o_type == 'S':
        # If nothing happen, make no op live for S
        sat_model.add_clause(
            [int(-clauses["s_observations"][time][i][j]), int(-clauses["s_observations"][time + 1][i][j]),
             int(clauses["s_no_op"][time][i][j])])
    elif o_type == 'U':
        # If nothing happen, make no op live for U
        sat_model.add_clause(
            [int(-clauses["u_observations"][time][i][j]), int(-clauses["u_observations"][time + 1][i][j]),
             int(clauses["u_no_op"][time][i][j])])
        # If 'U', make no op live for U
        sat_model.add_clause(
            [int(-clauses["u_observations"][time][i][j]), int(clauses["u_no_op"][time][i][j])])
    elif o_type == 'Q':
        # If nothing happen, make no op live for Q
        sat_model.add_clause(
            [int(-clauses["q_observations"][time][i][j]), int(-clauses["q_observations"][time + 1][i][j]),
             int(clauses["q_no_op"][time][i][j])])
        # If 'Q' and happened time - 1 then NO-OP must happen
        if time > 0:
            if clauses["raw_observations"][time - 1][i][j] in ['?', 'S']:
                sat_model.add_clause(
                    [int(-clauses["q_observations"][time][i][j]), int(-clauses["s_police_actions"][time - 1][i][j]),
                     int(clauses["q_no_op"][time][i][j])])
    elif o_type == 'I':
        # If 'I' then NO-OP must happen
        sat_model.add_clause(
            [int(-clauses["i_observations"][time][i][j]), int(clauses["i_no_op"][time][i][j])])
        # If nothing happen, make no op live for I
        sat_model.add_clause(
            [int(-clauses["i_observations"][time][i][j]), int(-clauses["i_observations"][time + 1][i][j]),
             int(clauses["i_no_op"][time][i][j])])


def actions_terms(curr_tile, clauses, sat_model, o_type):
    time = curr_tile[0]
    i = curr_tile[1]
    j = curr_tile[2]
    if o_type == 'H':
        # If H becomes S, make h_infect live
        sat_model.add_clause(
            [int(-clauses["h_observations"][time][i][j]), int(-clauses["s_observations"][time + 1][i][j]),
             int(clauses["h_infect_actions"][time][i][j])])
        # If 'H' became 'I', make h_medic live
        sat_model.add_clause(
            [int(-clauses["h_observations"][time][i][j]), int(-clauses["i_observations"][time + 1][i][j]),
             int(clauses["h_medics_actions"][time][i][j])])
    elif o_type == 'S':
        # If 'S' became 'Q', make s_police live
        sat_model.add_clause(([int(-clauses["q_observations"][time + 1][i][j]),
                               int(-clauses["s_observations"][time][i][j]),
                               int(clauses["s_police_actions"][time][i][j])]))
        # if S become H , make s_recover live
        sat_model.add_clause(([int(-clauses["h_observations"][time + 1][i][j]),
                               int(-clauses["s_observations"][time][i][j]),
                               int(clauses["s_recover_actions"][time][i][j])]))
    elif o_type == 'I':
        if time > 0:
            if clauses["raw_observations"][time - 1][i][j] in ['?', 'I']:
                # If 'I', make i_no_op / h_observations live
                sat_model.add_clause([int(-clauses["i_observations"][time][i][j]), int(clauses["i_no_op"][time - 1][i][j]),
                                      int(clauses["h_observations"][time - 1][i][j])])
            if clauses["raw_observations"][time - 1][i][j] in ['?', 'H']:
                sat_model.add_clause(
                            [int(-clauses["i_observations"][time][i][j]), int(-clauses["h_observations"][time - 1][i][j]),
                             int(clauses["h_medics_actions"][time - 1][i][j])])
            # If 'H' became 'I', make i_no_op live in next turn
            if time + 2 < len(clauses["i_observations"]):
                if clauses["raw_observations"][time + 2][i][j] in ['?', 'I']:
                    sat_model.add_clause(
                        [int(-clauses["h_observations"][time][i][j]), int(-clauses["i_observations"][time + 1][i][j]),
                         int(clauses["i_no_op"][time + 2][i][j])])
            if clauses["raw_observations"][time - 1][i][j] in ['?', 'I']:
                sat_model.add_clause(
                    [int(-clauses["i_no_op"][time][i][j]), int(clauses["i_no_op"][time + 1][i][j])])
    elif o_type == 'U':
        if clauses["raw_observations"][time - 1][i][j] in ['?', 'U']:
            sat_model.add_clause(
                [int(-clauses["u_no_op"][time][i][j]), int(clauses["u_no_op"][time + 1][i][j])])
    elif o_type == 'Q':
        # If 'Q' became 'H', make q_out_to_h live
        sat_model.add_clause(([int(-clauses["q_observations"][time][i][j]),
                               int(-clauses["h_observations"][time + 1][i][j]),
                               int(clauses["q_out_to_h"][time][i][j])]))
        # If S became Q, make q_out_to_h live in 2 turns
        if len(clauses["q_observations"]) - (time + 1) >= 3:
            if clauses["raw_observations"][time + 2][i][j] in ['?', 'Q']:
                sat_model.add_clause(
                    ([int(-clauses["s_police_actions"][time][i][j]), int(clauses["q_out_to_h"][time + 2][i][j])]))
        # if 2 'Q' in a row, make q_out_to_h live
        if time + 1 < len(clauses["i_observations"]):
            if clauses["raw_observations"][time + 1][i][j] in ['?', 'Q']:
                sat_model.add_clause(([int(-clauses["q_observations"][time][i][j]),
                                       int(-clauses["q_observations"][time + 1][i][j]),
                                       int(clauses["q_out_to_h"][time + 1][i][j])]))


def solve_problem_with_teams(clauses, police, medics, queries, sat_model):
    time_lim = len(clauses["h_observations"])
    n_rows = len(clauses["h_observations"][0])
    n_cols = len(clauses["h_observations"][0][0])
    dict_to_return = {}
    recover_flag = bool(time_lim >= 4)
    for time in range(time_lim - 1):
        med_options = []
        med_opt_val = []
        police_options = []
        police_opt_val = []
        curr_police = police
        curr_medics = medics
        for i in range(n_rows):
            for j in range(n_cols):
                curr_tile = tuple((time, i, j))
                # 'H' conditions
                if clauses["raw_observations"][time][i][j] == 'H':
                    one_and_only([int(clauses["h_no_op"][time][i][j]),
                                  int(clauses["h_medics_actions"][time][i][j]),
                                  int(clauses["h_infect_actions"][time][i][j])], sat_model)
                    infect_h_total_conditions_with_teams(curr_tile, clauses, sat_model)
                    insert_noop_h_clause(sat_model, curr_tile, clauses)
                    no_op_terms(curr_tile, clauses, sat_model, 'H')
                    actions_terms(curr_tile, clauses, sat_model, 'H')
                    if medics != 0:
                        med_h_total_conditions(curr_tile, clauses, sat_model)
                        # # how many possible medics options
                        if clauses["raw_observations"][time][i][j] in ['?', 'H']:
                            if clauses["raw_observations"][time + 1][i][j] == 'I' and clauses["raw_observations"][time][i][j] == 'H':
                                curr_medics -= 1
                                sat_model.add_clause([int(clauses["h_medics_actions"][time][i][j])])
                            else:
                                med_options.append(int(clauses["h_medics_actions"][time][i][j]))
                                med_opt_val.append(int(clauses["h_observations"][time][i][j]))
                    else:
                        # no medics, no healing
                        sat_model.add_clause([int(-clauses["h_medics_actions"][time][i][j])])
                        sat_model.add_clause([int(-clauses["i_observations"][time + 1][i][j])])
                # 'S' conditions
                elif clauses["raw_observations"][time][i][j] == 'S':
                    one_and_only([int(clauses["s_no_op"][time][i][j]),
                                  int(clauses["s_police_actions"][time][i][j]),
                                  int(clauses["s_recover_actions"][time][i][j])], sat_model)
                    insert_noop_s_clause(sat_model, curr_tile, clauses)
                    no_op_terms(curr_tile, clauses, sat_model, 'S')
                    actions_terms(curr_tile, clauses, sat_model, 'S')
                    if police != 0:
                        police_s_total_conditions(curr_tile, clauses, sat_model)
                        # # how many possible police options
                        if clauses["raw_observations"][time][i][j] in ['?', 'S']:
                            if clauses["raw_observations"][time + 1][i][j] == 'Q' and clauses["raw_observations"][time][i][j] == 'S':
                                curr_police -= 1
                                sat_model.add_clause([int(clauses["s_police_actions"][time][i][j])])
                            else:
                                police_options.append(int(clauses["s_police_actions"][time][i][j]))
                                police_opt_val.append(int(clauses["s_observations"][time][i][j]))
                    else:
                        sat_model.add_clause([int(-clauses["s_police_actions"][time][i][j])])
                        sat_model.add_clause([int(-clauses["q_observations"][time + 1][i][j])])
                    if recover_flag:
                        if time >= 2:
                            recover_s_total_conditions_with_teams(sat_model, curr_tile, clauses)
                            # if S for 3 turns and no police , make s_recover live
                            sat_model.add_clause([int(-clauses["s_observations"][time][i][j]),
                                                  int(-clauses["s_observations"][time - 1][i][j]),
                                                  int(-clauses["s_observations"][time - 2][i][j]),
                                                  int(clauses["s_police_actions"][time][i][j]),
                                                  int(clauses["s_recover_actions"][time][i][j])])
                        else:
                            sat_model.add_clause([int(-clauses["s_recover_actions"][time][i][j])])
                    else:
                        # 'S' stay 'S' if there is not time to recover
                        sat_model.add_clause([int(-clauses["s_recover_actions"][time][i][j])])
                # 'Q' conditions
                elif clauses["raw_observations"][time][i][j] == 'Q':
                    one_and_only([int(clauses["q_no_op"][time][i][j]), int(clauses["q_out_to_h"][time][i][j])], sat_model)
                    insert_q_out_to_h_clause(sat_model, curr_tile, clauses)
                    no_op_terms(curr_tile, clauses, sat_model, 'Q')
                    actions_terms(curr_tile, clauses, sat_model, 'Q')
                    # if time > 0:
                    insert_noop_q_clause(sat_model, curr_tile, clauses)
                # 'I' conditions
                elif clauses["raw_observations"][time][i][j] == 'I':
                    sat_model.add_clause([int(clauses["i_no_op"][time][i][j])])
                    no_op_terms(curr_tile, clauses, sat_model, 'I')
                    actions_terms(curr_tile, clauses, sat_model, 'I')
                    # if time > 0:
                    insert_noop_i_clause(sat_model, curr_tile, clauses)
                # 'U' conditions
                elif clauses["raw_observations"][time][i][j] == 'U':
                    sat_model.add_clause([int(clauses["u_no_op"][time][i][j])])
                    insert_noop_u_clause(sat_model, curr_tile, clauses)
                    no_op_terms(curr_tile, clauses, sat_model, 'U')
                    actions_terms(curr_tile, clauses, sat_model, 'U')
                # '?' conditions
                elif clauses["raw_observations"][time][i][j] == '?':
                    one_and_only([int(clauses["h_no_op"][time][i][j]), int(clauses["s_no_op"][time][i][j]),
                                  int(clauses["s_police_actions"][time][i][j]),
                                  int(clauses["h_medics_actions"][time][i][j]),
                                  int(clauses["s_recover_actions"][time][i][j]),
                                  int(clauses["h_infect_actions"][time][i][j]),
                                  int(clauses["u_no_op"][time][i][j]),
                                  int(clauses["q_no_op"][time][i][j]),
                                  int(clauses["i_no_op"][time][i][j]), int(clauses["q_out_to_h"][time][i][j])], sat_model)
                    infect_h_total_conditions_with_teams(curr_tile, clauses, sat_model)
                    insert_noop_h_clause(sat_model, curr_tile, clauses)
                    no_op_terms(curr_tile, clauses, sat_model, 'H')
                    actions_terms(curr_tile, clauses, sat_model, 'H')
                    if medics != 0:
                        med_h_total_conditions(curr_tile, clauses, sat_model)
                        # # how many possible medics options
                        if clauses["raw_observations"][time][i][j] in ['?', 'H']:
                            if clauses["raw_observations"][time + 1][i][j] == 'I' and clauses["raw_observations"][time][i][j] == 'H':
                                curr_medics -= 1
                                sat_model.add_clause([int(clauses["h_medics_actions"][time][i][j])])
                            else:
                                med_options.append(int(clauses["h_medics_actions"][time][i][j]))
                                med_opt_val.append(int(clauses["h_observations"][time][i][j]))
                    else:
                        # no medics, no healing
                        sat_model.add_clause([int(-clauses["h_medics_actions"][time][i][j])])
                        sat_model.add_clause([int(-clauses["i_observations"][time + 1][i][j])])
                    insert_noop_s_clause(sat_model, curr_tile, clauses)
                    no_op_terms(curr_tile, clauses, sat_model, 'S')
                    actions_terms(curr_tile, clauses, sat_model, 'S')
                    if police != 0:
                        police_s_total_conditions(curr_tile, clauses, sat_model)
                        # # how many possible police options
                        if clauses["raw_observations"][time][i][j] in ['?', 'S']:
                            if clauses["raw_observations"][time + 1][i][j] == 'Q' and \
                                    clauses["raw_observations"][time][i][j] == 'S':
                                curr_police -= 1
                                sat_model.add_clause([int(clauses["s_police_actions"][time][i][j])])
                            else:
                                police_options.append(int(clauses["s_police_actions"][time][i][j]))
                                police_opt_val.append(int(clauses["s_observations"][time][i][j]))
                    else:
                        sat_model.add_clause([int(-clauses["s_police_actions"][time][i][j])])
                        sat_model.add_clause([int(-clauses["q_observations"][time + 1][i][j])])
                    if recover_flag:
                        if time >= 2:
                            recover_s_total_conditions_with_teams(sat_model, curr_tile, clauses)
                            # if S for 3 turns and no police , make s_recover live
                            sat_model.add_clause([int(-clauses["s_observations"][time][i][j]),
                                                  int(-clauses["s_observations"][time - 1][i][j]),
                                                  int(-clauses["s_observations"][time - 2][i][j]),
                                                  int(clauses["s_police_actions"][time][i][j]),
                                                  int(clauses["s_recover_actions"][time][i][j])])
                        else:
                            sat_model.add_clause([int(-clauses["s_recover_actions"][time][i][j])])
                    else:
                        # 'S' stay 'S' if there is not time to recover
                        sat_model.add_clause([int(-clauses["s_recover_actions"][time][i][j])])
                    insert_q_out_to_h_clause(sat_model, curr_tile, clauses)
                    no_op_terms(curr_tile, clauses, sat_model, 'Q')
                    actions_terms(curr_tile, clauses, sat_model, 'Q')
                    # if time > 0:
                    insert_noop_q_clause(sat_model, curr_tile, clauses)
                    no_op_terms(curr_tile, clauses, sat_model, 'I')
                    actions_terms(curr_tile, clauses, sat_model, 'I')
                    # if time > 0:
                    insert_noop_i_clause(sat_model, curr_tile, clauses)
                    insert_noop_u_clause(sat_model, curr_tile, clauses)
                    no_op_terms(curr_tile, clauses, sat_model, 'U')
                    actions_terms(curr_tile, clauses, sat_model, 'U')
        if med_options is not None and curr_medics != 0:
            get_lim_clauses_h_med(sat_model, curr_medics, clauses, med_options, med_opt_val)
        elif med_options is not None and curr_medics == 0:
            for cl in med_options:
                sat_model.add_clause([-cl])
        if police_options is not None and curr_police != 0:
            get_lim_clauses_s_police(sat_model, curr_police, clauses, police_options, police_opt_val)
        elif police_options is not None and curr_police == 0:
            for cl in police_options:
                sat_model.add_clause([-cl])
    # after the model is complete, check for solutions with suggested queries
    for query in queries:
        i = query[0][0]
        j = query[0][1]
        time = query[1]
        type_obs = query[2]
        if type_obs in ['Q', 'I'] and time == 0:
            dict_to_return[query] = 'F'
        else:
            if type_obs == 'H':
                if not sat_model.solve(assumptions=[int(clauses["h_observations"][time][i][j])]):
                    dict_to_return[query] = 'F'
                else:
                    for observation in ['s_observations', 'i_observations', 'q_observations', 'u_observations']:
                        if sat_model.solve(assumptions=[int(clauses[observation][time][i][j])]):
                            dict_to_return[query] = '?'
                            break
                        dict_to_return[query] = 'T'
            elif type_obs == 'S':
                if not sat_model.solve(assumptions=[int(clauses["s_observations"][time][i][j])]):
                    dict_to_return[query] = 'F'
                else:
                    for observation in ['h_observations', 'i_observations', 'q_observations', 'u_observations']:
                        if sat_model.solve(assumptions=[int(clauses[observation][time][i][j])]):
                            dict_to_return[query] = '?'
                            break
                        dict_to_return[query] = 'T'
            elif type_obs == 'I':
                if not sat_model.solve(assumptions=[int(clauses["i_observations"][time][i][j])]):
                    dict_to_return[query] = 'F'
                else:
                    for observation in ['h_observations', 's_observations', 'q_observations', 'u_observations']:
                        if sat_model.solve(assumptions=[int(clauses[observation][time][i][j])]):
                            dict_to_return[query] = '?'
                            break
                        dict_to_return[query] = 'T'
            elif type_obs == 'Q':
                if not sat_model.solve(assumptions=[int(clauses["q_observations"][time][i][j])]):
                    dict_to_return[query] = 'F'
                else:
                    for observation in ['h_observations', 'i_observations', 's_observations', 'u_observations']:
                        if sat_model.solve(assumptions=[int(clauses[observation][time][i][j])]):
                            dict_to_return[query] = '?'
                            break
                        dict_to_return[query] = 'T'
            elif type_obs == 'U':
                if not sat_model.solve(assumptions=[int(clauses["u_observations"][time][i][j])]):
                    dict_to_return[query] = 'F'
                else:
                    for observation in ['h_observations', 'i_observations', 'q_observations', 's_observations']:
                        if sat_model.solve(assumptions=[int(clauses[observation][time][i][j])]):
                            dict_to_return[query] = '?'
                            break
                        dict_to_return[query] = 'T'
    return dict_to_return



