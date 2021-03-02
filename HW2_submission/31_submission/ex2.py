import pysat
import sympy
from pysat.solvers import Glucose3
from sympy.logic.boolalg import to_cnf
from itertools import product, combinations

ids = ['206354672', '318885001']

def init_num_turns(turn):
    if turn == "S":
        return ("S", 3)
    elif turn == "Q":
        return ("Q", 2)
    elif turn == "H":
        return ("H", 0)
    elif turn == "U":
        return ("U", 0)
    elif turn == "I":
        return ("I", 0)
    else:
        return (turn, "?")


def tuple_row(row):
    return tuple(map(init_num_turns, row))

def get_medics(problem):
    num_medics = problem["medics"]
    return num_medics

def get_police(problem):
    num_police = problem["police"]
    return num_police

def get_observations(problem):
    observations = problem['observations']
    obs_list = []
    for obs in observations:
        obs = tuple(map(tuple_row, obs))
        obs_list.append(obs)
    return obs_list


def get_queries(problem):
    query = problem['queries']
    return query


def update_to_healthy(initial, index_row, index_col):
    len_row = len(initial) - 1
    len_col = len(initial[0]) - 1
    curr_row = initial[index_row]
    if index_col == len_col:
        updated_val = curr_row[:index_col] + (("H", 0),)
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    elif index_row == len_row:
        updated_val = curr_row[:index_col] + (("H", 0),) + curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,)
    elif (index_col == len_col) and (index_row == len_row):
        updated_val = curr_row[:index_col] + (("H", 0),)
        updated_map = initial[:index_row] + (updated_val,)
    else:
        updated_val = curr_row[:index_col] + (("H", 0),) + curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    return updated_map

def update_to_sick(initial, index_row, index_col, counter=0):
    #print(index_row, index_col)
    len_row = len(initial) - 1
    len_col = len(initial[0]) - 1
    curr_row = initial[index_row]
    if (index_col == len_col) and (index_row == len_row):
        updated_val = curr_row[:index_col] + (("S", counter),)
        updated_map = initial[:index_row] + (updated_val,)
    elif index_col == len_col:
        updated_val = curr_row[:index_col] + (("S", counter),)
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    elif index_row == len_row:
        updated_val = curr_row[:index_col] + (("S", counter),) + curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,)
    else:
        updated_val = curr_row[:index_col] + (("S", counter),) + curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    return updated_map

def update_healthy_to_sick(initial, index_row, index_col, counter=0):
    len_row = len(initial) - 1
    len_col = len(initial[0]) - 1
    curr_row = initial[index_row]
    if (index_col == len_col) and (index_row == len_row):
        updated_val = curr_row[:index_col] + (("S", 3 - counter),)
        updated_map = initial[:index_row] + (updated_val,)
    elif index_col == len_col:
        updated_val = curr_row[:index_col] + (("S", 3 - counter),)
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    elif index_row == len_row:
        updated_val = curr_row[:index_col] + (("S", 3 - counter),) + curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,)
    else:
        updated_val = curr_row[:index_col] + (("S", 3 - counter),) + curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    return updated_map

def update_to_unpopulated(initial, index_row, index_col):
    len_row = len(initial) - 1
    len_col = len(initial[0]) - 1
    curr_row = initial[index_row]
    if index_col == len_col:
        updated_val = curr_row[:index_col] + (("U", 0),)
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    elif index_row == len_row:
        updated_val = curr_row[:index_col] + (("U", 0),) + curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,)
    elif (index_col == len_col) and (index_row == len_row):
        updated_val = curr_row[:index_col] + (("U", 0),)
        updated_map = initial[:index_row] + (updated_val,)
    else:
        updated_val = curr_row[:index_col] + (("U", 0),) + curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    return updated_map

def update_healthy_to_immune(initial, index_row, index_col):
    len_row = len(initial) - 1
    len_col = len(initial[0]) - 1
    curr_row = initial[index_row]
    if (index_col == len_col) and (index_row == len_row):
        updated_val = curr_row[:index_col] + (("I", 0),)
        updated_map = initial[:index_row] + (updated_val,)
    elif index_col == len_col:
        updated_val = curr_row[:index_col] + (("I", 0),)
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    elif index_row == len_row:
        updated_val = curr_row[:index_col] + (("I", 0),) + curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,)
    else:
        updated_val = curr_row[:index_col] + (("I", 0),) + curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    return updated_map

def update_to_quarantine(initial, index_row, index_col, counter):
    len_row = len(initial) - 1
    len_col = len(initial[0]) - 1
    curr_row = initial[index_row]
    if index_col == len_col:
        updated_val = curr_row[:index_col] + (("Q", counter),)
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    elif index_row == len_row:
        updated_val = curr_row[:index_col] + (("Q", counter),) + curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,)
    elif (index_col == len_col) and (index_row == len_row):
        updated_val = curr_row[:index_col] + (("Q", counter),)
        updated_map = initial[:index_row] + (updated_val,)
    else:
        updated_val = curr_row[:index_col] + (("Q", counter),) + curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    return updated_map

def update_sick_to_quarantine(initial, index_row, index_col, counter=0):
    len_row = len(initial) - 1
    len_col = len(initial[0]) - 1
    curr_row = initial[index_row]
    if index_col == len_col:
        updated_val = curr_row[:index_col] + (("Q", 2 - counter),)
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    elif index_row == len_row:
        updated_val = curr_row[:index_col] + (("Q", 2 - counter),) + curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,)
    elif (index_col == len_col) and (index_row == len_row):
        updated_val = curr_row[:index_col] + (("Q", 2 - counter),)
        updated_map = initial[:index_row] + (updated_val,)
    else:
        updated_val = curr_row[:index_col] + (("Q", 2 - counter),) + curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    return updated_map


def valid_counters(option):
    #print(option)
    updated_option = [option[0]]
    #print(updated_option)
    for day, obs in enumerate(option):
        #print("obs",obs)
        if day > 0:
            obs1 = option[day]
            for idx1, row in enumerate(obs1):
                for idx2, val in enumerate(row):
                    #print(updated_option[-1])
                    if option[day][idx1][idx2][0] == "S" and updated_option[-1][idx1][idx2][0] == "S":
                        obs1 = update_to_sick(obs1, idx1, idx2, updated_option[-1][idx1][idx2][1]-1)
                    elif option[day][idx1][idx2][0] == "Q" and updated_option[-1][idx1][idx2][0] == "Q":
                        #print("in")
                        obs1 = update_to_quarantine(obs1, idx1, idx2, updated_option[-1][idx1][idx2][1]-1)
            updated_option.append(obs1)
    return updated_option

def update_option_with_iter(initial, index_row, index_col, value):
    len_row = len(initial) - 1
    len_col = len(initial[0]) - 1
   # print("**", len_col, len_row)
    curr_row = initial[index_row]
    if (index_col == len_col) and (index_row == len_row):
        updated_val = curr_row[:index_col] + ((value),)
        updated_map = initial[:index_row] + (updated_val,)
    elif index_col == len_col:
        updated_val = curr_row[:index_col] + ((value),)
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    elif index_row == len_row:
        updated_val = curr_row[:index_col] + ((value),)+ curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,)
    else:
        updated_val = curr_row[:index_col] + ((value),) + curr_row[index_col + 1:]
        updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
    #print("map", updated_map)
    return updated_map

def update_map_with_turns(option2, num_of_options):
    n = len(option2[0])  # cols
    m = len(option2[0][0])  # rows
    option2 = valid_counters(option2)
    indexes = []
    #print("op2", option2)
    option2 = tuple(option2)
    option2_new = []
    for t in option2:
        option2_new.append(t)
    all_option2_new = []
    #print("new_option", option2_new)
    updated_option = option2
    num_of_iterations = 0
    for num in range(len(option2)):
        for j, prob in enumerate(option2[num]):
            #print("prob", option2[num])
            for k in range(len(prob)):
                # print("k",prob[k])
                if (num_of_iterations <= m * n * len(option2)):
                    #print("n*m*len",m * n * len(option2))
                    prob_new = (num_of_iterations, prob[k])
                    #print(num_of_iterations)
                    updated_option = (update_option_with_iter(option2_new[num], j, k, prob_new))
                    #print(updated_option)
                    option2_list = []
                    if num > 0:
                        for idx in indexes:
                            option2_list.append(idx)
                    option2_list.append(updated_option)
                    #print(option2_list)
                    num_of_iterations += 1
                    option2_new = option2_list
                    all_option2_new.append(option2_new[num])
                    #print(option2_result)
                    #print(option2_new)
        #updated_option[-1]
        indexes.append(all_option2_new[-1])
        option2_new = option2
    #print("xxxxxx", option2_result)
    return indexes


def axiom_spread_infection(option2, num_of_options, axiom_per_option):
    n = len(option2[0])  # cols
    m = len(option2[0][0])  # rows
    option2_result = update_map_with_turns(option2, num_of_options)
    #print("option", option2_result)
    final_axioms = []
    #axiom_per_option = []
    for idx_state, state in enumerate(option2_result):
        all_axioms_per_option = []
        for ni in range(n):
            for nj in range(m):
            #for idx_state, state in enumerate(option2_result):
                clause = []
                clause1 = []
                clause2 = []
                clause3 = []
                clause4 = []
                #if option2_result[idx_state][ni][nj][1][0] == "H":
                if idx_state+1 < len(option2_result):
                    #if option2_result[idx_state+1][ni][nj][1][0] == "S":
                    if nj + 1 < m:
                        clause1.append(2 + (num_of_options * option2_result[idx_state][ni][nj+1][0]))
                        clause1.append(3 + (num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        clause1.append(4 + (num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                    # left
                    if nj - 1 >= 0:
                        clause1.append(2 + (num_of_options * option2_result[idx_state][ni][nj-1][0]))
                        clause1.append(3 + (num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        clause1.append(4 + (num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        # down
                    if ni + 1 < n:
                        clause1.append(2 + (num_of_options * option2_result[idx_state][ni+1][nj][0]))
                        clause1.append(3 + (num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        clause1.append(4 + (num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        # up
                    if ni - 1 >= 0:
                        clause1.append(2 + (num_of_options * option2_result[idx_state][ni-1][nj][0]))
                        clause1.append(3 + (num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        clause1.append(4 + (num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                    clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                    clause1.append(-(2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                    all_axioms_per_option.append(clause1)
                   # print(all_axioms_per_option)
            #axiom_per_option.append(all_axioms_per_option)
                #print("axiom_per_option", axiom_per_option)
                    clause1 = []
            for axiom in (all_axioms_per_option):
                #print(all_axioms_per_option)
                #if axiom != [] and axiom not in all_axioms_per_option:
                axiom_per_option.append(axiom)
    #print(all_axioms_per_option)
    #print(axiom_per_option)
    return axiom_per_option

def axiom_spread_infection_from_sick(option2, num_of_options, axiom_per_option):
    n = len(option2[0])  # cols
    m = len(option2[0][0])  # rows
    option2_result = update_map_with_turns(option2, num_of_options)
    #print("option", option2_result)
    final_axioms = []
    #axiom_per_option = []
    for idx_state, state in enumerate(option2_result):
        all_axioms_per_option = []
        for ni in range(n):
            for nj in range(m):
            #for idx_state, state in enumerate(option2_result):
                clause = []
                clause1 = []
                clause2 = []
                clause3 = []
                clause4 = []
                if idx_state == 0:
                    if nj + 1 < m:
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append((3 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append(-(1 + (num_of_options * option2_result[idx_state][ni][nj+1][0])))
                        clause1.append(-(2 + (num_of_options * option2_result[idx_state + 1][ni][nj + 1][0])))
                        all_axioms_per_option.append(clause1)
                    # left
                    if nj - 1 >= 0:
                        clause2.append(-(2 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append((3 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + (num_of_options * option2_result[idx_state][ni][nj - 1][0])))
                        clause2.append(-(2 + (num_of_options * option2_result[idx_state + 1][ni][nj - 1][0])))
                        all_axioms_per_option.append(clause2)
                        # down
                    if ni + 1 < n:
                        clause3.append(-(2 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append((3 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + (num_of_options * option2_result[idx_state][ni+1][nj][0])))
                        clause3.append(-(2 + (num_of_options * option2_result[idx_state + 1][ni+1][nj][0])))
                        all_axioms_per_option.append(clause3)
                        # up
                    if ni - 1 >= 0:
                        clause4.append(-(2 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause4.append((3 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause4.append(-(1 + (num_of_options * option2_result[idx_state][ni - 1][nj][0])))
                        clause4.append(-(2 + (num_of_options * option2_result[idx_state + 1][ni - 1][nj][0])))
                        all_axioms_per_option.append(clause4)

            for axiom in (all_axioms_per_option):
                #print(all_axioms_per_option)
                #if axiom != [] and axiom not in all_axioms_per_option:
                axiom_per_option.append(axiom)
    return axiom_per_option

def axiom_healthy_validity(given_problem, num_of_options, axiom_per_option): #medics = 0 and police = 0
    n = len(given_problem[0])  # cols
    m = len(given_problem[0][0])  # rows
    option2_result = update_map_with_turns(given_problem, num_of_options)
    # print("option", option2_result)
    final_axioms = []
  #  axiom_per_option = []
    for idx_state, state in enumerate(option2_result):
        all_axioms_per_option = []
        for ni in range(n):
            for nj in range(m):
                clause = []
                clause1 = []
                clause2 = []
                clause3 = []
                clause4 = []
                if idx_state + 1 < len(option2_result):
                    # if option2_result[idx_state+1][ni][nj][1][0] == "S":
                    if nj + 1 < m:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
                    # left
                    if nj - 1 >= 0:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
                        # down
                    if ni + 1 < n:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
                        # up
                    if ni - 1 >= 0:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
    return axiom_per_option


def axiom_healthy_validity_vaccinate(given_problem, num_of_options, axiom_per_option): #medics > 0 and police > 0
    n = len(given_problem[0])  # cols
    m = len(given_problem[0][0])  # rows
    option2_result = update_map_with_turns(given_problem, num_of_options)
    # print("option", option2_result)
    final_axioms = []
  #  axiom_per_option = []
    for idx_state, state in enumerate(option2_result):
        all_axioms_per_option = []
        for ni in range(n):
            for nj in range(m):
                clause = []
                clause1 = []
                clause2 = []
                clause3 = []
                clause4 = []
                if idx_state + 1 < len(option2_result):
                    # if option2_result[idx_state+1][ni][nj][1][0] == "S":
                    if nj + 1 < m:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        clause1.append((7 + num_of_options * option2_result[idx_state+1][ni][nj + 1][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        clause2.append((7 + num_of_options * option2_result[idx_state + 1][ni][nj + 1][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        clause3.append((7 + num_of_options * option2_result[idx_state + 1][ni][nj + 1][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
                    # left
                    if nj - 1 >= 0:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        clause1.append((7 + num_of_options * option2_result[idx_state + 1][ni][nj - 1][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        clause2.append((7 + num_of_options * option2_result[idx_state + 1][ni][nj - 1][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        clause3.append((7 + num_of_options * option2_result[idx_state + 1][ni][nj - 1][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
                        # down
                    if ni + 1 < n:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        clause1.append((7 + num_of_options * option2_result[idx_state + 1][ni + 1][nj][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        clause2.append((7 + num_of_options * option2_result[idx_state + 1][ni + 1][nj][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        clause3.append((7 + num_of_options * option2_result[idx_state + 1][ni + 1][nj][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
                        # up
                    if ni - 1 >= 0:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        clause1.append((7 + num_of_options * option2_result[idx_state + 1][ni - 1][nj][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        clause2.append((7 + num_of_options * option2_result[idx_state + 1][ni - 1][nj][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        clause3.append((7 + num_of_options * option2_result[idx_state + 1][ni - 1][nj][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
    return axiom_per_option

def axiom_healthy_validity_immune(given_problem, num_of_options, axiom_per_option): # spread infection medics > 0 police = 0
    n = len(given_problem[0])  # cols
    m = len(given_problem[0][0])  # rows
    option2_result = update_map_with_turns(given_problem, num_of_options)
    # print("option", option2_result)
    final_axioms = []
    #axiom_per_option = []
    for idx_state, state in enumerate(option2_result):
        all_axioms_per_option = []
        for ni in range(n):
            for nj in range(m):
                clause = []
                clause1 = []
                clause2 = []
                clause3 = []
                clause4 = []
                if idx_state + 1 < len(option2_result):
                    # if option2_result[idx_state+1][ni][nj][1][0] == "S":
                    if nj + 1 < m:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
                    # left
                    if nj - 1 >= 0:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
                        # down
                    if ni + 1 < n:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
                        # up
                    if ni - 1 >= 0:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
    return axiom_per_option

def axiom_healthy_validity_quarantine_vaccinate(given_problem, num_of_options, axiom_per_option): # spread infection medics > 0 police > 0
    n = len(given_problem[0])  # cols
    m = len(given_problem[0][0])  # rows
    option2_result = update_map_with_turns(given_problem, num_of_options)
    # print("option", option2_result)
    final_axioms = []
    #axiom_per_option = []
    for idx_state, state in enumerate(option2_result):
        all_axioms_per_option = []
        for ni in range(n):
            for nj in range(m):
                clause = []
                clause1 = []
                clause2 = []
                clause3 = []
                clause4 = []
                if idx_state + 1 < len(option2_result):# H, my neighbor S >> H, S, I
                    if nj + 1 < m:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
                    # left
                    if nj - 1 >= 0:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
                        # down
                    if ni + 1 < n:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
                        # up
                    if ni - 1 >= 0:
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause1.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause2.append(-(3 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        clause2.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause2.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append(-(1 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause3.append(-(4 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        clause3.append((2 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((6 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        clause3.append((1 + num_of_options * option2_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        axiom_per_option.append(clause2)
                        axiom_per_option.append(clause3)
                        clause1 = []
                        clause2 = []
                        clause3 = []
    return axiom_per_option

def check_sick_neighbors_counter(curr_map, ni, nj):
    n = len(curr_map) #cols
    m = len(curr_map[0]) #rows
    neighbor_list = []
    if nj + 1 < m:
        #if curr_map[ni][nj + 1][1][0] == "S":
        neighbor_list.append((ni, nj+1))
#left
    if nj - 1 >= 0:
        #if curr_map[ni][nj - 1][1][0] == "S":
        neighbor_list.append((ni, nj - 1))
#down
    if ni + 1 < n:
        #if curr_map[ni + 1][nj][1][0] == "S":
        neighbor_list.append((ni + 1, nj))

#up
    if ni - 1 >= 0:
        #if curr_map[ni - 1][nj][1][0] == "S":
        neighbor_list.append((ni - 1, nj))
  #  print(counter)
    return neighbor_list

def axiom_healthy_validity_quarantine(option2, num_of_options, final_axioms): #spread infection police > 0
    n = len(option2[0])  # cols
    m = len(option2[0][0])  # rows
    option2_result = update_map_with_turns(option2, num_of_options)
    #final_axioms = []
    axiom_per_option = []
    for idx_state, state in enumerate(option2_result):
        for ni in range(n):
            for nj in range(m):
                curr_val = [[-(2 + num_of_options * option2_result[idx_state][ni][nj][0])]]
                neighbor_list1_sick = []
                neighbor_list2_sick = []
                neighbor_list3_sick = []
                neighbor_list4_sick = []
                neighbor_list1_q = []
                neighbor_list2_q = []
                neighbor_list3_q = []
                neighbor_list4_q = []
                neighbor_list1 = []
                neighbor_list2 = []
                neighbor_list3 = []
                neighbor_list4 = []
                if idx_state > 0:
                    if num_of_options == 7:
                        neighbors_list = check_sick_neighbors_counter(option2_result[idx_state-1], ni, nj)
                       # print(neighbors_list)
                        if len(neighbors_list) == 2:
                            x = neighbors_list[0][0]
                            y = neighbors_list[0][1]
                            neighbor_list1_sick.append((2 + num_of_options * option2_result[idx_state-1][x][y][0]))
                            neighbor_list1_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list1_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list1_q.append(-(6 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list1.append(neighbor_list1_sick)
                            neighbor_list1.append(neighbor_list1_q)
                            x = neighbors_list[1][0]
                            y = neighbors_list[1][1]
                            neighbor_list2_sick.append((2 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_q.append(-(6 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list2.append(neighbor_list2_sick)
                            neighbor_list2.append(neighbor_list2_q)
                            axiom_per_option = [[a, b, c] for a in curr_val for b in neighbor_list1 for c in neighbor_list2]
                        elif len(neighbors_list) == 3:
                            x = neighbors_list[0][0]
                            y = neighbors_list[0][1]
                            neighbor_list1_sick.append((2 + num_of_options * option2_result[idx_state-1][x][y][0]))
                            neighbor_list1_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list1_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list1_q.append(-(6 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list1.append(neighbor_list1_sick)
                            neighbor_list1.append(neighbor_list1_q)
                            x = neighbors_list[1][0]
                            y = neighbors_list[1][1]
                            neighbor_list2_sick.append((2 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_q.append(-(6 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list2.append(neighbor_list2_sick)
                            neighbor_list2.append(neighbor_list2_q)
                            x = neighbors_list[2][0]
                            y = neighbors_list[2][1]
                            neighbor_list3_sick.append((2 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list3_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list3_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list3_q.append(-(6 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list3.append(neighbor_list3_sick)
                            neighbor_list3.append(neighbor_list3_q)
                            axiom_per_option = [[a, b, c, d] for a in curr_val for b in neighbor_list1 for c in neighbor_list2 for d in neighbor_list3]
                        elif len(neighbors_list) == 4:
                            x = neighbors_list[0][0]
                            y = neighbors_list[0][1]
                            neighbor_list1_sick.append((2 + num_of_options * option2_result[idx_state-1][x][y][0]))
                            neighbor_list1_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list1_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list1_q.append(-(6 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list1.append(neighbor_list1_sick)
                            neighbor_list1.append(neighbor_list1_q)
                            x = neighbors_list[1][0]
                            y = neighbors_list[1][1]
                            neighbor_list2_sick.append((2 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_q.append(-(6 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list2.append(neighbor_list2_sick)
                            neighbor_list2.append(neighbor_list2_q)
                            x = neighbors_list[2][0]
                            y = neighbors_list[2][1]
                            neighbor_list3_sick.append((2 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list3_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list3_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list3_q.append(-(6 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list3.append(neighbor_list3_sick)
                            neighbor_list3.append(neighbor_list3_q)
                            x = neighbors_list[3][0]
                            y = neighbors_list[3][1]
                            neighbor_list4_sick.append((2 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list4_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list4_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list4_q.append(-(6 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list4.append(neighbor_list4_sick)
                            neighbor_list4.append(neighbor_list4_q)
                            axiom_per_option = [[a, b, c, d, e] for a in curr_val for b in neighbor_list1 for c in neighbor_list2 for d in neighbor_list3 for e in neighbor_list4]
                        for x in axiom_per_option:
                            final_axioms.append([val for sublist in x for val in sublist])
                    elif num_of_options == 8:
                        neighbors_list = check_sick_neighbors_counter(option2_result[idx_state-1], ni, nj)
                       # print(neighbors_list)
                        if len(neighbors_list) == 2:
                            x = neighbors_list[0][0]
                            y = neighbors_list[0][1]
                            neighbor_list1_sick.append((2 + num_of_options * option2_result[idx_state-1][x][y][0]))
                            neighbor_list1_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list1_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list1_q.append(-(7 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list1.append(neighbor_list1_sick)
                            neighbor_list1.append(neighbor_list1_q)
                            x = neighbors_list[1][0]
                            y = neighbors_list[1][1]
                            neighbor_list2_sick.append((2 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_q.append(-(7 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list2.append(neighbor_list2_sick)
                            neighbor_list2.append(neighbor_list2_q)
                            axiom_per_option = [[a, b, c] for a in curr_val for b in neighbor_list1 for c in neighbor_list2]
                        elif len(neighbors_list) == 3:
                            x = neighbors_list[0][0]
                            y = neighbors_list[0][1]
                            neighbor_list1_sick.append((2 + num_of_options * option2_result[idx_state-1][x][y][0]))
                            neighbor_list1_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list1_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list1_q.append(-(7 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list1.append(neighbor_list1_sick)
                            neighbor_list1.append(neighbor_list1_q)
                            x = neighbors_list[1][0]
                            y = neighbors_list[1][1]
                            neighbor_list2_sick.append((2 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_q.append(-(7 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list2.append(neighbor_list2_sick)
                            neighbor_list2.append(neighbor_list2_q)
                            x = neighbors_list[2][0]
                            y = neighbors_list[2][1]
                            neighbor_list3_sick.append((2 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list3_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list3_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list3_q.append(-(7 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list3.append(neighbor_list3_sick)
                            neighbor_list3.append(neighbor_list3_q)
                            axiom_per_option = [[a, b, c, d] for a in curr_val for b in neighbor_list1 for c in neighbor_list2 for d in neighbor_list3]
                        elif len(neighbors_list) == 4:
                            x = neighbors_list[0][0]
                            y = neighbors_list[0][1]
                            neighbor_list1_sick.append((2 + num_of_options * option2_result[idx_state-1][x][y][0]))
                            neighbor_list1_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list1_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list1_q.append(-(7 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list1.append(neighbor_list1_sick)
                            neighbor_list1.append(neighbor_list1_q)
                            x = neighbors_list[1][0]
                            y = neighbors_list[1][1]
                            neighbor_list2_sick.append((2 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list2_q.append(-(7 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list2.append(neighbor_list2_sick)
                            neighbor_list2.append(neighbor_list2_q)
                            x = neighbors_list[2][0]
                            y = neighbors_list[2][1]
                            neighbor_list3_sick.append((2 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list3_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list3_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list3_q.append(-(7 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list3.append(neighbor_list3_sick)
                            neighbor_list3.append(neighbor_list3_q)
                            x = neighbors_list[3][0]
                            y = neighbors_list[3][1]
                            neighbor_list4_sick.append((2 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list4_sick.append(
                                (3 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list4_sick.append(
                                (4 + num_of_options * option2_result[idx_state - 1][x][y][0]))
                            neighbor_list4_q.append(-(7 + num_of_options * option2_result[idx_state][x][y][0]))
                            neighbor_list4.append(neighbor_list4_sick)
                            neighbor_list4.append(neighbor_list4_q)
                            axiom_per_option = [[a, b, c, d, e] for a in curr_val for b in neighbor_list1 for c in neighbor_list2 for d in neighbor_list3 for e in neighbor_list4]
                        for x in axiom_per_option:
                            final_axioms.append([val for sublist in x for val in sublist])
    return final_axioms



def check_sick_neighbors(curr_map, ni, nj):
    n = len(curr_map) #cols
    m = len(curr_map[0]) #rows
    if nj + 1 < m:
        if curr_map[ni][nj + 1][0] == "S":
            return True
#left
    if nj - 1 >= 0:
        if curr_map[ni][nj - 1][0] == "S":
            return True
#down
    if ni + 1 < n:
        if curr_map[ni + 1][nj][0] == "S":
            return True

#up
    if ni - 1 >= 0:
        if curr_map[ni - 1][nj][0] == "S":
            return True
    return False



def axiom_validity_police(given_problem, num_of_options, axiom_per_option):
    n = len(given_problem[0])  # cols
    m = len(given_problem[0][0])  # rows
    prob_result = update_map_with_turns(given_problem, num_of_options)
    all_axioms = []
    #axiom_per_option = []
    for idx_state, state in enumerate(prob_result):
        for ni in range(n):
            for nj in range(m):
                clause1 = []
                clause2 = []
                if idx_state + 1 < len(prob_result):# Q2 -> Q1
                    if num_of_options == 7:
                        clause1.append(-(6 + num_of_options * prob_result[idx_state][ni][nj][0]))
                        clause1.append((7 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        clause1 = []
                    elif num_of_options == 8:
                        clause1.append(-(7 + num_of_options * prob_result[idx_state][ni][nj][0]))
                        clause1.append((8 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        clause1 = []
                if idx_state + 1 < len(prob_result): # Q1 -> H
                    if num_of_options == 7:
                        clause1.append(-(7 + num_of_options * prob_result[idx_state][ni][nj][0]))
                        clause1.append((1 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        clause1 = []
                    elif num_of_options == 8:
                        clause1.append(-(8 + num_of_options * prob_result[idx_state][ni][nj][0]))
                        clause1.append((1 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        clause1 = []
                # for idx_state, state in enumerate(prob_result): #S3->S2, Q2
                if idx_state + 1 < len(prob_result):
                    if num_of_options == 7:
                        clause1.append(-(2 + num_of_options * prob_result[idx_state][ni][nj][0]))
                        clause1.append((3 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                        clause1.append((6 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        clause1 = []
                    elif num_of_options == 8:
                        clause1.append(-(2 + num_of_options * prob_result[idx_state][ni][nj][0]))
                        clause1.append((3 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                        clause1.append((7 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        clause1 = []
                # for idx_state, state in enumerate(prob_result): #S2 -> S1, Q2
                if idx_state + 1 < len(prob_result):
                    if idx_state != 0:
                        if num_of_options == 7:
                            clause1.append(-(3 + num_of_options * prob_result[idx_state][ni][nj][0]))
                            clause1.append((4 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                            clause1.append((6 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                            axiom_per_option.append(clause1)
                            clause1 = []
                        elif num_of_options == 8:
                            clause1.append(-(3 + num_of_options * prob_result[idx_state][ni][nj][0]))
                            clause1.append((4 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                            clause1.append((7 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                            axiom_per_option.append(clause1)
                            clause1 = []
                if idx_state + 1 < len(prob_result): #S1 - > Q2/H
                    if idx_state != 0:
                        if num_of_options == 7:
                            clause1.append(-(4 + num_of_options * prob_result[idx_state][ni][nj][0]))
                            clause1.append((6 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                            clause1.append((1 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                            axiom_per_option.append(clause1)
                            clause1 = []
                        elif num_of_options == 8:
                            clause1.append(-(4 + num_of_options * prob_result[idx_state][ni][nj][0]))
                            clause1.append((7 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                            clause1.append((1 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                            axiom_per_option.append(clause1)
                            clause1 = []
                # if idx_state-1 > 0:# H in the next step-> H in the prev
                if idx_state == 1 or idx_state == 2:  # H was H
                    clause1.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    # clause2.append((1 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    # clause2.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    # axiom_per_option.append(clause2)
                    clause1 = []
                   # clause2 = []
                if idx_state > 0:  # S3 was H
                    clause1.append(-(2 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause1 = []
                if idx_state > 2:  # H was H or S1 or Q1
                    if num_of_options == 7:
                        clause1.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                        clause1.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                        clause1.append((4 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                        clause1.append((7 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        clause1 = []
                    elif num_of_options == 8:
                        clause1.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                        clause1.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                        clause1.append((4 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                        clause1.append((8 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        clause1 = []
                if idx_state > 0:  # Q2 was S3 or S2 or S1
                    if num_of_options == 7:
                        clause1.append(-(6 + num_of_options * prob_result[idx_state][ni][nj][0]))
                        clause1.append((2 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                        clause1.append((3 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                        clause1.append((4 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        clause1 = []
                    elif num_of_options == 8:
                        clause1.append(-(7 + num_of_options * prob_result[idx_state][ni][nj][0]))
                        clause1.append((2 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                        clause1.append((3 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                        clause1.append((4 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        clause1 = []
                if idx_state + 1 < len(prob_result):  # U->U
                    clause1.append(-(5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((5 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause2.append((5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause2.append(-(5 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    # #print("u axioms", clause1, clause2)
                    axiom_per_option.append(clause2)
                    clause1 = []
                    clause2 = []
                # for idx_state, state in enumerate(prob_result):#H->H, S3
                if idx_state + 1 < len(prob_result):
                    # print("state",idx_state)
                    clause1.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    clause1.append((2 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    # print("clause", clause1)
                    axiom_per_option.append(clause1)
                    clause1 = []
    return axiom_per_option

def axiom_medics_validity(given_problem, num_of_options, axiom_per_option):
    n = len(given_problem[0])  # cols
    m = len(given_problem[0][0])  # rows
    prob_result = update_map_with_turns(given_problem, num_of_options)
    all_axioms = []
   # axiom_per_option = []
    for idx_state, state in enumerate(prob_result):
        for ni in range(n):
            for nj in range(m):
                clause1 = []
                clause2 = []
                if idx_state + 1 < len(prob_result):#S3->S2
                    clause1.append(-(2 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((3 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause2.append((2 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause2.append(-(3 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    axiom_per_option.append(clause2)
                    clause1 = []
                    clause2 = []
                # for idx_state, state in enumerate(prob_result): #S2 -> S1
                if idx_state + 1 < len(prob_result):
                    if idx_state != 0:
                        clause1.append(-(3 + num_of_options * prob_result[idx_state][ni][nj][0]))
                        clause1.append((4 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        clause1 = []
                # if idx_state-1 > 0:# H in the next step-> H in the prev
                if idx_state > 0: #S2 was S3
                    clause1.append(-(3 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((2 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause1 = []
                if idx_state == 1 or idx_state == 2:  # H was H
                    clause1.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    # clause2.append((1 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    # clause2.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    # axiom_per_option.append(clause2)
                    clause1 = []
                    # clause2 = []
                if idx_state > 0:  # S3 was H
                    clause1.append(-(2 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause1 = []
                if idx_state > 2:  # H was H or S1
                    clause1.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    clause1.append((4 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause1 = []
                if idx_state > 0: #I was I or H
                    clause1.append(-(6 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((6 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause1 = []
                if idx_state + 1 < len(prob_result):  # U->U
                    clause1.append(-(5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((5 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause2.append((5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause2.append(-(5 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    # #print("u axioms", clause1, clause2)
                    axiom_per_option.append(clause2)
                    clause1 = []
                    clause2 = []
                # for idx_state, state in enumerate(prob_result):#H->H, S3, I
                if idx_state + 1 < len(prob_result):
                    # print("state",idx_state)
                    clause1.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    clause1.append((2 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    clause1.append((6 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    # print("clause", clause1)
                    axiom_per_option.append(clause1)
                    clause1 = []
                if idx_state + 1 < len(prob_result): # I -> I
                    clause1.append(-(6 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((6 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause1 = []
    return axiom_per_option

def check_if_med(given_problem, num_of_options, num_of_meds, axiom_per_option):
    n = len(given_problem[0])  # cols
    m = len(given_problem[0][0])  # rows
    prob_result = update_map_with_turns(given_problem, num_of_options)
    for idx_state in range(1, len(prob_result), 1):
        question_mark_list = [] #as I
        counter_I = 0
        for ni in range(n):
            for nj in range(m):
                if prob_result[idx_state][ni][nj][1][0] == "?":
                    question_mark_list.append((6 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    #print(question_mark_list)
                if prob_result[idx_state][ni][nj][1][0] == "I":
                    counter_I += 1
        if (counter_I < num_of_meds*(idx_state) and idx_state > 1):
            axiom_per_option.append(question_mark_list)
        elif (counter_I < num_of_meds and idx_state == 1):
            axiom_per_option.append(question_mark_list)
    return axiom_per_option

def check_if_police(given_problem, num_of_options, num_of_police, axiom_per_option):
    n = len(given_problem[0])  # cols
    m = len(given_problem[0][0])  # rows
    prob_result = update_map_with_turns(given_problem, num_of_options)
    for idx_state in range(1, len(prob_result), 1):
        question_mark_list = [] #as Q
        counter_Q = 0
        for ni in range(n):
            for nj in range(m):
                if prob_result[idx_state][ni][nj][1][0] == "?":
                    if num_of_options == 7:
                        question_mark_list.append((6 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    elif num_of_options == 8:
                        question_mark_list.append((7 + num_of_options * prob_result[idx_state][ni][nj][0]))
                if prob_result[idx_state][ni][nj][1][0] == "Q":
                    counter_Q += 1
        if counter_Q < num_of_police and idx_state == 1:
            axiom_per_option.append(question_mark_list)
        elif counter_Q < 2*num_of_police and idx_state > 1:
            axiom_per_option.append(question_mark_list)
    return axiom_per_option

def axiom_validity_police_and_medics(given_problem, num_of_options, axiom_per_option):
    n = len(given_problem[0])  # cols
    m = len(given_problem[0][0])  # rows
    prob_result = update_map_with_turns(given_problem, num_of_options)
   # axiom_per_option = []
    for idx_state, state in enumerate(prob_result):
        for ni in range(n):
            for nj in range(m):
                clause1 = []
                clause2 = []
                clause3 = []
                clause4 = []
                clause5 = []
                clause6 = []
                clause7 = []
                clause8 = []
                if idx_state + 1 < len(prob_result):  # Q2 -> Q1
                    clause1.append(-(7 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((8 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause1 = []
                if idx_state + 1 < len(prob_result):  # Q1 -> H
                    clause1.append(-(8 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause1 = []
                # for idx_state, state in enumerate(prob_result): #S3->S2, Q2
                if idx_state + 1 < len(prob_result):
                    clause1.append(-(2 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((3 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    clause1.append((7 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause1 = []
                # for idx_state, state in enumerate(prob_result): #S2 -> S1, Q2
                if idx_state + 1 < len(prob_result):
                    if idx_state != 0:
                        clause1.append(-(3 + num_of_options * prob_result[idx_state][ni][nj][0]))
                        clause1.append((4 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                        clause1.append((7 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        clause1 = []
                if idx_state + 1 < len(prob_result): #S1 -> H/Q2
                    if idx_state != 0:
                        clause1.append(-(4 + num_of_options * prob_result[idx_state][ni][nj][0]))
                        clause1.append((1 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                        clause1.append((7 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        clause1 = []
                # if idx_state-1 > 0:# H in the next step-> H in the prev
                if idx_state == 1 or idx_state == 2:  # H was H
                    clause1.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause2.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    clause2.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    axiom_per_option.append(clause2)
                    clause1 = []
                    clause2 = []
                if idx_state > 0:  # S3 was H
                    clause1.append(-(2 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause1 = []
                if idx_state > 0:  # Q1 was Q2
                    clause1.append(-(8 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((7 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause1 = []
                if idx_state > 2:  # H was H or S1 or Q1
                    clause1.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    clause1.append((4 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    clause1.append((8 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause1 = []
                if idx_state + 1 < len(prob_result):  # U->U
                    clause1.append(-(5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((5 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause2.append((5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause2.append(-(5 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    #print("u axioms", clause1, clause2)
                    axiom_per_option.append(clause2)
                    clause1 = []
                    clause2 = []
                if idx_state > 0: #U in the next round -> in the prev round not S1, S2, S3, Q1, Q2, H, I
                    clause1.append(-(5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append(-(1 + num_of_options * prob_result[idx_state-1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause2.append(-(5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause2.append(-(2 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause2)
                    clause3.append(-(5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause3.append(-(3 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause3)
                    clause4.append(-(5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause4.append(-(4 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause4)
                    clause5.append(-(5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause5.append(-(6 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause5)
                    clause6.append(-(5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause6.append(-(7 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause6)
                    clause7.append(-(5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause7.append(-(8 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause7)
                    clause8.append(-(5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause8.append((5 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause8)
                    clause1 = []
                    clause2 = []
                    clause3 = []
                    clause4 = []
                    clause5 = []
                    clause6 = []
                    clause7 = []
                    clause8 = []
                # for idx_state, state in enumerate(prob_result):#H->H, S3, I
                if idx_state + 1 < len(prob_result):
                    # print("state",idx_state)
                    clause1.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    clause1.append((2 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    clause1.append((6 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    # print("clause", clause1)
                    axiom_per_option.append(clause1)
                    clause1 = []
                if idx_state == 1:#I was H
                    clause1.append(-(6 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause1 = []
                if idx_state > 0:  # I was I or H
                    clause1.append(-(6 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((6 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause1 = []
                if idx_state + 1 < len(prob_result): # I -> I
                    clause1.append(-(6 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((6 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause1 = []
    return axiom_per_option


def axiom_validity(given_problem, num_of_options, axiom_per_option):
    #given_problem = valid_counters(given_problem)
    n = len(given_problem[0])  # cols
    m = len(given_problem[0][0])  # rows
    prob_result = update_map_with_turns(given_problem, num_of_options)
    all_axioms = []
    #axiom_per_option = []
    for idx_state, state in enumerate(prob_result):
        for ni in range(n):
            for nj in range(m):
                clause1 = []
                clause2 = []
                #for idx_state, state in enumerate(prob_result): #S3->S2
                if idx_state+1 < len(prob_result):
                    clause1.append(-(2 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((3 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    #clause1.append((2 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause2.append((2 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause2.append(-(3 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    axiom_per_option.append(clause2)
                    clause1 = []
                    clause2 = []
               # for idx_state, state in enumerate(prob_result): #S2 -> S1
                if idx_state+1 < len(prob_result):
                    if idx_state != 0:
                        clause1.append(-(3 + num_of_options * prob_result[idx_state][ni][nj][0]))
                        clause1.append((4 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause1)
                        #print(clause1)
                        clause2.append((3 + num_of_options * prob_result[idx_state][ni][nj][0]))
                        clause2.append(-(4 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                        axiom_per_option.append(clause2)
                        clause1 = []
                        clause2 = []
                #if idx_state-1 > 0:# H in the next step-> H in the prev
                if idx_state == 1 or idx_state == 2: #H was H
                    clause1.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state-1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    # clause2.append((1 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    # clause2.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    #axiom_per_option.append(clause2)
                    clause1 = []
                    #clause2 = []
                if idx_state > 0: #S3 was H
                    clause1.append(-(2 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    axiom_per_option.append(clause1)
                    clause1 = []
                if idx_state > 2:  # H was H or S1
                    clause1.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    clause1.append((4 + num_of_options * prob_result[idx_state - 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    axiom_per_option.append(clause1)
                    clause1 = []
                #for idx_state, state in enumerate(prob_result):
                if idx_state+1 < len(prob_result): #U->U
                    clause1.append(-(5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((5 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    axiom_per_option.append(clause1)
                    clause2.append((5 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause2.append(-(5 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    # #print("u axioms", clause1, clause2)
                    axiom_per_option.append(clause2)
                    clause1 = []
                    clause2 = []
                #for idx_state, state in enumerate(prob_result):#H->H, S3
                if idx_state+1 < len(prob_result):
                    #print("state",idx_state)
                    clause1.append(-(1 + num_of_options * prob_result[idx_state][ni][nj][0]))
                    clause1.append((1 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    clause1.append((2 + num_of_options * prob_result[idx_state + 1][ni][nj][0]))
                    #print("clause", clause1)
                    axiom_per_option.append(clause1)
                    clause1 = []
    return axiom_per_option


def create_police_or_meds_axiom(duplicate_a_minus, val_list):
    list_for_comb = []
    for val in duplicate_a_minus:
        new_list = []
        for t in val_list:
            new_list.append(t)
        new_list.append(val)
        list_for_comb.append(new_list)
    return list_for_comb

def create_base_axiom_police_or_meds(a, num_of_groups):
    final_list = []
    list_a = list(combinations(a, num_of_groups))
    for val in list_a:
        val_list = []
        #print(val)
        duplicate_a = []
        for t in a:
            duplicate_a.append(t)
        not_in_val = []
        for num in val:
            val_list.append(-num)
            #print(val_list)
            #print(num)
            for i in duplicate_a:
                if i == num:
                    #not_in_val.append(i)
                    duplicate_a.remove(num)
        duplicate_a_minus = [-x for x in duplicate_a]
        for axiom_list in create_police_or_meds_axiom(duplicate_a_minus, val_list):
            final_list.append(axiom_list)
    return final_list

def get_police_axioms(problem, num_of_options, num_police, all_quarantine_list):
    problem_ = update_map_with_turns(problem, num_of_options)
    n = len(problem_[0])  # cols
    m = len(problem_[0][0])  # rows
    num_combs = 0
    #all_quarantine_list = []
    for idx_state, state in enumerate(problem_):
        quarantine_list_1 = []
        quarantine_list_2 = []
        quarantine_list_not = []
        actual_quarantine = []
        counter_Q = 0
        for ni in range(n):
            for nj in range(m):
               # if idx_state > 0:
                #if problem_[idx_state - 1][ni][nj][1][0] != "Q":
                if num_of_options == 7:
                    quarantine_list_1.append((6 + num_of_options * problem_[idx_state][ni][nj][0]))
                    if problem_[idx_state][ni][nj][1][0] == "Q":
                        counter_Q += 1
                        actual_quarantine.append((6 + num_of_options * problem_[idx_state][ni][nj][0]))
                        actual_quarantine.append((7 + num_of_options * problem_[idx_state][ni][nj][0]))

                elif num_of_options == 8:
                    quarantine_list_1.append((7 + num_of_options * problem_[idx_state][ni][nj][0]))
                    if problem_[idx_state][ni][nj][1][0] == "Q":
                        counter_Q += 1
                        actual_quarantine.append((7 + num_of_options * problem_[idx_state][ni][nj][0]))
                        actual_quarantine.append((8 + num_of_options * problem_[idx_state][ni][nj][0]))
        if idx_state >= 1 and num_police != counter_Q:
            for base in create_base_axiom_police_or_meds(quarantine_list_1, num_police):
                all_quarantine_list.append(base)
        else:
            quarantine_list_not = [-x for x in quarantine_list_1]
            for val in quarantine_list_not:
             #   print(abs(val), actual_quarantine)
                if abs(val) not in actual_quarantine:
                    all_quarantine_list.append([val])
                    all_quarantine_list.append([val-1])
    #print(all_quarantine_list)
    return all_quarantine_list

def get_medic_axioms(problem, num_of_options, num_meds, all_vaccinate_list):
    problem_ = update_map_with_turns(problem, num_of_options)
    num_combs = 0
    n = len(problem_[0])  # cols
    m = len(problem_[0][0])  # rows
    #all_vaccinate_list = []
    for idx_state, state in enumerate(problem_):
        vaccinate_list = []
        vaccinate_list_not = []
        for ni in range(n):
            for nj in range(m):
                vaccinate_list.append((6 + num_of_options * problem_[idx_state][ni][nj][0]))
           # print(all_vaccinate_list)
        if idx_state > 0:
            for base in create_base_axiom_police_or_meds(vaccinate_list, num_combs):
                all_vaccinate_list.append(base)
        num_combs += num_meds
    return all_vaccinate_list

def infection_for_police(option2, num_of_options, axiom_per_option):
    n = len(option2[0])  # cols
    m = len(option2[0][0])  # rows
    option2_result = update_map_with_turns(option2, num_of_options)
    # print("option", option2_result)
    final_axioms = []
    # axiom_per_option = []
    for idx_state, state in enumerate(option2_result):
        all_axioms_per_option = []
        for ni in range(n):
            for nj in range(m):
                # for idx_state, state in enumerate(option2_result):
                clause = []
                clause1 = []
                if idx_state > 0:
                    if nj + 1 < m:
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state - 1][ni][nj][0]))
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []
                    # left
                    if nj - 1 >= 0:
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state - 1][ni][nj][0]))
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []

                        # down
                    if ni + 1 < n:
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state - 1][ni][nj][0]))
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni+1][nj][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []
                        # up
                    if ni - 1 >= 0:
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(2 + num_of_options * option2_result[idx_state - 1][ni][nj][0]))
                        clause1.append(-(1 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []
                for axiom in all_axioms_per_option:
                    axiom_per_option.append(axiom)
    return axiom_per_option

def infection_for_police_2(option2, num_of_options, axiom_per_option):
    n = len(option2[0])  # cols
    m = len(option2[0][0])  # rows
    option2_result = update_map_with_turns(option2, num_of_options)
    # print("option", option2_result)
    final_axioms = []
    # axiom_per_option = []
    for idx_state, state in enumerate(option2_result):
        all_axioms_per_option = []
        for ni in range(n):
            for nj in range(m):
                # for idx_state, state in enumerate(option2_result):
                clause = []
                clause1 = []
                if idx_state > 0:
                    if nj + 1 < m:
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append((1 + num_of_options * option2_result[idx_state - 1][ni][nj][0]))
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []
                    # left
                    if nj - 1 >= 0:
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append((1 + num_of_options * option2_result[idx_state - 1][ni][nj][0]))
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []

                        # down
                    if ni + 1 < n:
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append((1 + num_of_options * option2_result[idx_state - 1][ni][nj][0]))
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni+1][nj][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []
                        # up
                    if ni - 1 >= 0:
                        clause1.append(-(2 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append((1 + num_of_options * option2_result[idx_state - 1][ni][nj][0]))
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []
                for axiom in all_axioms_per_option:
                    axiom_per_option.append(axiom)
    return axiom_per_option

def infection_for_police_3(option2, num_of_options, axiom_per_option):
    n = len(option2[0])  # cols
    m = len(option2[0][0])  # rows
    option2_result = update_map_with_turns(option2, num_of_options)
    # print("option", option2_result)
    final_axioms = []
    # axiom_per_option = []
    for idx_state, state in enumerate(option2_result):
        all_axioms_per_option = []
        for ni in range(n):
            for nj in range(m):
                # for idx_state, state in enumerate(option2_result):
                clause1 = []
                if idx_state > 0:
                    if nj + 1 < m:
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(1 + num_of_options * option2_result[idx_state - 1][ni][nj + 1][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []
                    # left
                    if nj - 1 >= 0:
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(1 + num_of_options * option2_result[idx_state - 1][ni][nj - 1][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []

                        # down
                    if ni + 1 < n:
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(1 + num_of_options * option2_result[idx_state - 1][ni + 1][nj][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []
                        # up
                    if ni - 1 >= 0:
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(1 + num_of_options * option2_result[idx_state - 1][ni - 1][nj][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []
                for axiom in all_axioms_per_option:
                    axiom_per_option.append(axiom)
    return axiom_per_option

def infection_for_police_3_medics(option2, num_of_options, axiom_per_option):
    n = len(option2[0])  # cols
    m = len(option2[0][0])  # rows
    option2_result = update_map_with_turns(option2, num_of_options)
    # print("option", option2_result)
    final_axioms = []
    # axiom_per_option = []
    for idx_state, state in enumerate(option2_result):
        all_axioms_per_option = []
        for ni in range(n):
            for nj in range(m):
                # for idx_state, state in enumerate(option2_result):
                clause1 = []
                if idx_state > 0:
                    if nj + 1 < m:
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(1 + num_of_options * option2_result[idx_state - 1][ni][nj + 1][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state][ni][nj + 1][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []
                    # left
                    if nj - 1 >= 0:
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(1 + num_of_options * option2_result[idx_state - 1][ni][nj - 1][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state][ni][nj - 1][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []

                        # down
                    if ni + 1 < n:
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(1 + num_of_options * option2_result[idx_state - 1][ni + 1][nj][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state][ni + 1][nj][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []
                        # up
                    if ni - 1 >= 0:
                        clause1.append(-(3 + num_of_options * option2_result[idx_state][ni][nj][0]))
                        clause1.append(-(1 + num_of_options * option2_result[idx_state - 1][ni - 1][nj][0]))
                        clause1.append((2 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        clause1.append((6 + num_of_options * option2_result[idx_state][ni - 1][nj][0]))
                        all_axioms_per_option.append(clause1)
                        clause1 = []
                for axiom in all_axioms_per_option:
                    axiom_per_option.append(axiom)
    return axiom_per_option
#if num_options = 5 - > day > 0  & medics = 0, police = 0
#if num_option = 7 - > day > 0 & police >= 1 and medics = 0
#if num_option = 6 - > day > 0 & police = 0 & medics >= 1
#if num_oprions = 8 - > day > 0 & police >= 1 & medics >= 1
def build_world(option, num_of_option): #check day before calling this function
    the_world = []
    #print(option)
    init_problem = valid_counters(option)
    days = len(init_problem)
    list_problem = []
    len_row = len(init_problem[0])
    len_col = len(init_problem[0][0])
    for i in range(len_col * len_row * num_of_option * days):  # 3 option in the first turn
        list_problem.append(i + 1)  # so we can modulo %num_of_options=3 -> if 1 = H, 2 = S, 0=U
    # print(list_problem)
    # if num_of_option == 3:
    #     init_map = [('H', 0), ('S', 3), ('U', 0)]
    if num_of_option == 5:
        init_map = [('H', 0), ('S', 3), ('S', 2), ('S', 1), ('U', 0)]
    elif num_of_option == 6:
        init_map = [('H', 0), ('S', 3), ('S', 2), ('S', 1), ('U', 0), ('I', 0)]
    elif num_of_option == 7:
        init_map = [('H', 0), ('S', 3), ('S', 2), ('S', 1), ('U', 0), ('Q', 2), ('Q', 1)]
    elif num_of_option == 8:
        init_map = [('H', 0), ('S', 3), ('S', 2), ('S', 1), ('U', 0), ('I', 0), ('Q', 2), ('Q', 1)]
    for num in range(len(init_problem)):
        # print("num", num)
        num_of_iterations = 0
        # print(init_problem[num])
        for j, prob in enumerate(init_problem[num]):
         #   print("prob", prob)
            for k in range(len(prob)):
                # print("k",prob[k])
                mylist = []
                if (num_of_iterations <= len_col * len_row*len(init_problem)*num_of_option):
                    for q, val in enumerate(init_map):
                        if prob[k] == init_map[q] and prob[k] != ('S', 3):
                            #print(prob[k], init_map[q])
                            mylist.append(list_problem[(num * (
                                        len_row * len_col * num_of_option)) + q + num_of_option * num_of_iterations])
                            the_world.append([list_problem[(num * (
                                        len_row * len_col * num_of_option)) + q + num_of_option * num_of_iterations]])
                        if num == 0 and prob[k] == init_map[q] and prob[k] == ('S', 3):
                            mylist.append(list_problem[(num * (
                                        len_row * len_col * num_of_option)) + q + num_of_option * num_of_iterations])
                            the_world.append([list_problem[(num * (
                                        len_row * len_col * num_of_option)) + q + num_of_option * num_of_iterations]])
                        if check_sick_neighbors(init_problem[num - 1], j, k) == True and num > 0:
                            if init_problem[num - 1][j][k][0] == "H":
                                #print(init_problem[num - 1], init_problem[num])
                                if prob[k] == ('S', 3) and prob[k] == init_map[q]:
                                    mylist.append(list_problem[(num * (
                                            len_row * len_col * num_of_option)) + q + num_of_option * num_of_iterations])
                                    the_world.append([list_problem[(num * (
                                            len_row * len_col * num_of_option)) + q + num_of_option * num_of_iterations]])
                        elif num == 1 and prob[k] == init_map[q] and prob[k] == ('S', 3):
                            mylist.append(list_problem[(num * (
                                        len_row * len_col * num_of_option)) + q + num_of_option * num_of_iterations])
                            the_world.append([list_problem[(num * (
                                        len_row * len_col * num_of_option)) + q + num_of_option * num_of_iterations], list_problem[(num * (
                                        len_row * len_col * num_of_option)) + q + 1 + num_of_option * num_of_iterations]])
                        elif num > 1 and prob[k] == init_map[q] and prob[k] == ('S', 3):
                            mylist.append(list_problem[(num * (
                                    len_row * len_col * num_of_option)) + q + num_of_option * num_of_iterations])
                            the_world.append([list_problem[(num * (
                                    len_row * len_col * num_of_option)) + q + num_of_option * num_of_iterations],list_problem[(num * (
                                    len_row * len_col * num_of_option)) + 1 + q + num_of_option * num_of_iterations], list_problem[(num * (
                                    len_row * len_col * num_of_option)) + 2 + q + num_of_option * num_of_iterations]])
                        if prob[k] != init_map[q] or prob[k] == ('?', '?'):
                            mylist.append(list_problem[(num * (
                                        len_row * len_col * num_of_option)) + q + num_of_option * num_of_iterations])
                    num_of_iterations += 1
                new_list = [-x for x in mylist]
                mylist_combo_tuple = list(combinations(new_list, 2))
                mylist_combo = [list(elem) for elem in mylist_combo_tuple]
                for list_comb in mylist_combo:
                    the_world.append(list_comb)
   # print(the_world)
    return the_world

def translate_query(query, problem_query, num_of_options):
    #n = len(option2[0])  # cols
    #m = len(option2[0][0])  # rows
    x = query[0][0]
    y = query[0][1]
    value = query[2]
    turn = query[1]
    query_numbers = []
    problem = update_map_with_turns(problem_query, num_of_options)
    if num_of_options == 5:
        if value == "H":
            query_num = 1 + num_of_options * problem[turn][x][y][0]
            query_numbers.append(query_num)
        elif value == "S":
            if turn == 0:
                query_num = 2 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num)
            elif turn == 1:
                query_num = 2 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num)
                query_num_2 = 3 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num_2)
            elif turn > 1:
                query_num = 2 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num)
                query_num_2 = 3 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num_2)
                query_num_3 = 4 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num_3)
        elif value == "U":
            query_num =  5 + num_of_options * problem[turn][x][y][0]
            query_numbers.append(query_num)
    elif num_of_options == 6:
        if value == "H":
            query_num = 1 + num_of_options * problem[turn][x][y][0]
            query_numbers.append(query_num)
        elif value == "S":
            if turn == 0:
                query_num = 2 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num)
            elif turn == 1:
                query_num = 2 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num)
                query_num_2 = 3 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num_2)
            elif turn > 1:
                query_num = 2 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num)
                query_num_2 = 3 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num_2)
                query_num_3 = 4 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num_3)
        elif value == "U":
            query_num = 5 + num_of_options * problem[turn][x][y][0]
            query_numbers.append(query_num)
        elif value == "I":
            query_num = 6 + num_of_options * problem[turn][x][y][0]
            query_numbers.append(query_num)
    elif num_of_options == 7 or num_of_options == 8:
        if value == "H":
            query_num = 1 + num_of_options * problem[turn][x][y][0]
            query_numbers.append(query_num)
        elif value == "S":
            if turn == 0:
                query_num = 2 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num)
            elif turn == 1:
                query_num = 2 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num)
                query_num_2 = 3 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num_2)
            elif turn > 1:
                query_num = 2 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num)
                query_num_2 = 3 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num_2)
                query_num_3 = 4 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num_3)
        elif value == "U":
            query_num = 5 + num_of_options * problem[turn][x][y][0]
            query_numbers.append(query_num)
        elif value == "Q":
            if num_of_options == 7:
                query_num = 6 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num)
                query_num_2 = 7 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num_2)
            elif num_of_options == 8:
                query_num = 7 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num)
                query_num_2 = 8 + num_of_options * problem[turn][x][y][0]
                query_numbers.append(query_num_2)
        elif value == "I":
            query_num = 8 + num_of_options * problem[turn][x][y][0]
            query_numbers.append(query_num)
    return query_numbers

def translate_query_not(query, problem_query, num_of_options):
    n = len(problem_query[0])  # cols
    m = len(problem_query[0][0])  # rows
    query_not_list = []
    x = query[0][0]
    y = query[0][1]
    #print(query, x, y)
    value = query[2]
    turn = query[1]
    query_numbers = []
    problem = update_map_with_turns(problem_query, num_of_options)
    if num_of_options == 5:
        if value == "H":
            query_num = 1 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num])
        elif value == "S":
            query_num = 2 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num])
            query_num_2 = 3 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num_2])
            query_num_3 = 4 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num_3])
        elif value == "U":
            query_num = 5 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num])
    elif num_of_options == 6:
        if value == "H":
            query_num = 1 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num])
        elif value == "S":
            query_num = 2 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num])
            query_num_2 = 3 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num_2])
            query_num_3 = 4 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num_3])
        elif value == "U":
            query_num = 5 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num])
        elif value == "I":
            query_num = 6 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num])
    elif num_of_options == 7 or num_of_options == 8:
        if value == "H":
            query_num = 1 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num])
        elif value == "S":
            query_num = 2 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num])
            query_num_2 = 3 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num_2])
            query_num_3 = 4 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num_3])
        elif value == "U":
            query_num = 5 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num])
        elif value == "Q":
            if num_of_options == 7:
                query_num = 6 + num_of_options * problem[turn][x][y][0]
                query_numbers.append([query_num])
                query_num_2 = 7 + num_of_options * problem[turn][x][y][0]
                query_numbers.append([query_num_2])
            elif num_of_options == 8:
                query_num = 7 + num_of_options * problem[turn][x][y][0]
                query_numbers.append([query_num])
                query_num_2 = 8 + num_of_options * problem[turn][x][y][0]
                query_numbers.append([query_num_2])
    if num_of_options == 8:
        if value == "I":
            query_num = 8 + num_of_options * problem[turn][x][y][0]
            query_numbers.append([query_num])
    not_in_list = [x[0] for x in query_numbers]
    for i in range(num_of_options * problem[turn][x][y][0]+1, num_of_options * problem[turn][x][y][0]+num_of_options+1, 1):
        if i not in not_in_list:
            query_not_list.append(i)
    return query_not_list

def check_validity_start(given_problem):
    n = len(given_problem[0])  # cols
    m = len(given_problem[0][0])  # rows
    for idx_state, state in enumerate(given_problem):
        for ni in range(n):
            for nj in range(m):
                if idx_state == 0:
                    if given_problem[idx_state][ni][nj][0]=="I" or given_problem[idx_state][ni][nj][0]=="Q":
                        return False
    return True

def check_validity_query(query, num_of_police, num_of_meds):
    if query[1] == 0:
        if query[2] == "I" or query[2] == "Q":
            return False
    if num_of_police > 0 and num_of_meds == 0 and query[2] == "I":
        return False
    elif num_of_meds > 0 and num_of_police == 0 and query[2] == "Q":
        return False
    elif num_of_meds == 0 and num_of_police == 0 and (query[2] == "I" or query[2] == "Q"):
        return False
    return True


#check for every query in queries when calling function
def create_axiom(problem, num_of_options, query):
    num_police = get_police(problem)
    num_meds = get_medics(problem)
    in_problem = get_observations(problem)
    KB_meds_police_zero = [] #police = 0 and meds = 0
    KB_meds_zero_police = [] #police>0 and meds = 0
    KB_police_zero_meds = [] #police = 0 and meds>0
    KB_police_meds = [] #police>0 and meds>0
    world_clauses = []
    check_dict = {}
    world = build_world(in_problem, num_of_options)
    answer_list = []
    for value in world:
        KB_police_meds.append(value)
        KB_police_zero_meds.append(value)
        KB_meds_police_zero.append(value)
        KB_meds_zero_police.append(value)
    if num_police == 0 and num_meds == 0:
        axiom_spread_infection_from_sick(in_problem, num_of_options, KB_meds_police_zero)
        axiom_spread_infection(in_problem, num_of_options, KB_meds_police_zero)
        # for axiom in world_axioms:
        #     world_clauses.append(axiom)
        axiom_healthy_validity(in_problem, num_of_options, KB_meds_police_zero)
        # for healthy in world_axioms_healthy:
        #     world_clauses.append(healthy)
        axiom_validity(in_problem, num_of_options, KB_meds_police_zero)
        # for axiom2 in world_axioms_2:
        #     world_clauses.append(axiom2)
       # infection_for_police(in_problem, num_of_options, KB_meds_police_zero)
       # infection_for_police_2(in_problem, num_of_options, KB_meds_police_zero)
        infection_for_police_3(in_problem, num_of_options, KB_meds_police_zero)
        query_to_check = translate_query(query, in_problem, num_of_options)
        KB_meds_police_zero.append(query_to_check)
        with Glucose3(bootstrap_with=KB_meds_police_zero) as g:
            answer_list.append(g.solve())
        if answer_list[0] == False or check_validity_start(in_problem) == False or check_validity_query(query, num_police, num_meds) == False:
            check_dict[query] = 'F'
        else:
            KB_meds_police_zero.pop(-1)
            not_query = translate_query_not(query, in_problem, num_of_options)
            KB_meds_police_zero.append(not_query)
            with Glucose3(bootstrap_with=KB_meds_police_zero) as f:
                answer_list.append(f.solve())
            if answer_list[1] == True:
                check_dict[query] = '?'
            else:
                check_dict[query] = 'T'
    elif num_police > 0 and num_meds == 0:
        axiom_spread_infection(in_problem, num_of_options, KB_meds_zero_police)
        check_if_police(in_problem, num_of_options, num_police, KB_meds_zero_police)
    #    axiom_spread_infection_from_sick(in_problem, num_of_options, KB_meds_zero_police)
        axiom_healthy_validity_quarantine(in_problem, num_of_options, KB_meds_zero_police)
        # for healthy in world_axioms_healthy_vacc:
        #     world_clauses.append(healthy)
        axiom_validity_police(in_problem, num_of_options, KB_meds_zero_police)
        # for axiom_v_q in world_clauses_quar_validity:
        #     world_clauses.append(axiom_v_q)
        get_police_axioms(in_problem, num_of_options, num_police, KB_meds_zero_police)
        # for axiom_q in world_axioms_quarantine:
        #     world_clauses.append(axiom_q)
        #infection_for_police(in_problem, num_of_options, KB_meds_zero_police)
        #infection_for_police_2(in_problem, num_of_options, KB_meds_zero_police)
        infection_for_police_3(in_problem, num_of_options, KB_meds_zero_police)
        query_to_check = translate_query(query, in_problem, num_of_options)
        KB_meds_zero_police.append(query_to_check)
        with Glucose3(bootstrap_with=KB_meds_zero_police) as g:
            answer_list.append(g.solve())
        if (answer_list[0] == False) or (check_validity_start(in_problem) == False) or check_validity_query(query, num_police, num_meds) == False:
            check_dict[query] = 'F'
        else:
            KB_meds_zero_police.pop(-1)
            not_query = translate_query_not(query, in_problem, num_of_options)
            KB_meds_zero_police.append(not_query)
            with Glucose3(bootstrap_with=KB_meds_zero_police) as f:
                answer_list.append(f.solve())
            if answer_list[1] == True:
                check_dict[query] = '?'
            else:
                check_dict[query] = 'T'
    elif num_meds > 0 and num_police == 0:
        axiom_spread_infection(in_problem, num_of_options, KB_police_zero_meds)
        check_if_med(in_problem, num_of_options, num_meds, KB_police_zero_meds)
      #  axiom_spread_infection_from_sick(in_problem, num_of_options, KB_police_zero_meds)
        # for axiom in world_axioms:
        #     world_clauses.append(axiom)
        axiom_healthy_validity_immune(in_problem, num_of_options, KB_police_zero_meds)
        # for healthy in world_axioms_healthy_immune:
        #     world_clauses.append(healthy)
        axiom_medics_validity(in_problem, num_of_options, KB_police_zero_meds)
        # for axiom_v_v in world_clauses_vacc_validity:
        #     world_clauses.append(axiom_v_v)
        get_medic_axioms(in_problem, num_of_options, num_meds, KB_police_zero_meds)
        # for axiom_v in world_axioms_vaccinate:
        #     world_clauses.append(axiom_v)
        #infection_for_police(in_problem, num_of_options, KB_police_zero_meds)
        #infection_for_police_2(in_problem, num_of_options, KB_police_zero_meds)
        infection_for_police_3_medics(in_problem, num_of_options, KB_police_zero_meds)
        query_to_check = translate_query(query, in_problem, num_of_options)
        KB_police_zero_meds.append(query_to_check)
        with Glucose3(bootstrap_with=KB_police_zero_meds) as g:
            answer_list.append(g.solve())
        if answer_list[0] == False or check_validity_start(in_problem) == False or check_validity_query(query, num_police, num_meds) == False:
            check_dict[query] = 'F'
        else:
            KB_police_zero_meds.pop(-1)
            not_query = translate_query_not(query, in_problem, num_of_options)
            KB_police_zero_meds.append(not_query)
            with Glucose3(bootstrap_with=KB_police_zero_meds) as f:
                answer_list.append(f.solve())
            if answer_list[1] == True:
                check_dict[query] = '?'
            else:
                check_dict[query] = 'T'
    elif num_meds > 0 and num_police > 0:
        axiom_spread_infection(in_problem, num_of_options, KB_police_meds)
        check_if_med(in_problem, num_of_options, num_meds, KB_police_meds)
        check_if_police(in_problem, num_of_options, num_police, KB_police_meds)
       # axiom_spread_infection_from_sick(in_problem, num_of_options, KB_police_meds)
        axiom_healthy_validity_quarantine(in_problem, num_of_options, KB_police_meds)
        # for axiom in world_axioms:
        #     world_clauses.append(axiom)
       # axiom_healthy_validity_quarantine_vaccinate(in_problem, num_of_options, KB_police_meds)
        axiom_healthy_validity_vaccinate(in_problem, num_of_options, KB_police_meds)
        # for healthy in world_axioms_healthy_immune_q:
        #     world_clauses.append(healthy)
        axiom_validity_police_and_medics(in_problem, num_of_options, KB_police_meds)
        # for axiom_v_v_q in world_clauses_vacc_quar_validity:
        #     world_clauses.append(axiom_v_v_q)
        get_medic_axioms(in_problem, num_of_options, num_meds, KB_police_meds)
        # for axiom_v in world_axioms_vaccinate:
        #     world_clauses.append(axiom_v)
        get_police_axioms(in_problem, num_of_options, num_police, KB_police_meds)
        #infection_for_police(in_problem, num_of_options, KB_police_meds)
        #infection_for_police_2(in_problem, num_of_options, KB_police_meds)
        infection_for_police_3_medics(in_problem, num_of_options, KB_police_meds)
        # for axiom_q in world_axioms_quarantine:
        #     world_clauses.append(axiom_q)
        query_to_check = translate_query(query, in_problem, num_of_options)
        KB_police_meds.append(query_to_check)
        with Glucose3(bootstrap_with=KB_police_meds) as g:
            answer_list.append(g.solve())
        if answer_list[0] == False or check_validity_start(in_problem) == False or check_validity_query(query, num_police, num_meds) == False:
            check_dict[query] = 'F'
        else:
            KB_police_meds.pop(-1)
            not_query = translate_query_not(query, in_problem, num_of_options)
            KB_police_meds.append(not_query)
            with Glucose3(bootstrap_with=KB_police_meds) as f:
                answer_list.append(f.solve())
            if answer_list[1] == True:
                check_dict[query] = '?'
            else:
                check_dict[query] = 'T'
    #print("query", query_to_check)

   # print(not_query)
   #  g = Glucose3()
   #  for value in world_clauses:
   #      g.add_clause(value)
   #  g.add_clause(query_to_check)
   #  answer_list.append(g.solve())
   #
   #  if answer_list[0] == False:
   #      check_dict[query] = 'F'
   #  else:
   #      f = Glucose3()
   #      for value in world_clauses:
   #          f.add_clause(value)
   #      f.add_clause(not_query)
   #      answer_list.append(f.solve())
   #      if answer_list[1] == True:
   #          check_dict[query] = '?'
   #      else:
   #          check_dict[query] = 'T'
    return check_dict


def solve_problem(input):
    num_police = get_police(input)
    num_medics = get_medics(input)
    if num_police == 0 and num_medics == 0:
        num_of_options = 5
    elif num_police > 0 and num_medics == 0:
        num_of_options = 7
    elif num_medics > 0 and num_police == 0:
        num_of_options = 6
    else:
        num_of_options = 8
    check_dict = {}
    for query in get_queries(input):
        #print(query)
        answer = create_axiom(input, num_of_options, query).get(query)
        check_dict[query] = answer
    return check_dict
    pass
    # put your solution here, remember the format needed