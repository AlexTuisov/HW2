ids = ['342390135', '318171824']
import numpy as np
from utils import expr, Expr, first
# from sympy import *
from pysat.formula import IDPool
# from pysat.solvers import Glucose3
# from sympy.core.compatibility import exec_
from custom_SAT_lib import eliminate_implications
from custom_SAT_lib import to_cnf
from pysat.solvers import Minisat22
import itertools


def solve_problem(input):
    # pass
    solution_dict = {}
    # put your solution here, remember the format needed
    observations = input["observations"]

    vpool = create_init_atoms(observations)
    true_assumptions, area_list_dict = get_true_assumptions(input, vpool)
    # print(true_assumptions, area_list_dict)
    l = 0
    ###print("Init vpool: ", vpool)
    get_all_S_assumptions(true_assumptions, input, area_list_dict, vpool)
    #get_all_H_assumptions(true_assumptions, input, area_list_dict, vpool)
    get_all_U_assumptions(true_assumptions, input, area_list_dict, vpool)
    get_general_assumptions(true_assumptions, input, area_list_dict, vpool)
    # get_all_H_assumptions(true_assumptions, input, area_list_dict, vpool)
    # get_all_H_assumptions(input, area_list_dict["H"], vpool)
    #print("after vpool: ", vpool)
    #print("true assumptions: ", true_assumptions)
    # convert_list_to_pysat(true_assumptions, vpool)
    pysat_list = convert_list_to_pysat(true_assumptions, vpool)
    #print(pysat_list)
    ###############################################
    assumptions = input["queries"]
    solution_dict = get_solution(pysat_list, assumptions, vpool)
    ###############################################
    # print("MINISAT: ")
    # with Minisat22(bootstrap_with=[[1], [17], [25], [6], [30], [-10, -25, 30], [-10, -25, -29], [-10, -1, 6], [-10, -1, -5], [-1, 5], [-17, 21], [-25, 29], [-9, 13], [-9, -10], [-9, -11], [-10, -11], [-10, -9], [-11, -9], [-11, -10], [-13, -14], [-13, -15], [-14, -15], [-14, -13], [-15, -13], [-15, -14], [-21, -22], [-21, -23], [-22, -23], [-22, -21], [-23, -21], [-23, -22]]) as m:
    #     print(m.solve(assumptions=[9]))
    #     print(m.get_model())
    #     print(m.nof_clauses())
    # ~A or B and ~C or
    #print(solution_dict)
    return solution_dict


def get_true_assumptions(input, vpool):
    true_assumptions_list = []
    true_assumptions_list_pysat = []
    H_list, S_list, U_list, D_list = [], [], [], []
    area_list_dict = {"H": H_list, "S": S_list, "U": U_list, "?": D_list}
    # sympify(locals="?")
    # ns = {}
    # exec_('from sympy.core.evalf import bitcount', ns)
    # ns["?"] = Symbol("?")
    for time, matrix in enumerate(input["observations"]):
        # print(time, matrix) #for debug
        for ix, row in enumerate(matrix):
            for ij, area in enumerate(row):
                if area == "?":
                    s = '{}_{}_{}_{}'.format(area, ix, ij, time)
                    area_list_dict[area].append((ix, ij, time))
                else:
                    # s = matrix[ix][ij] + "_" + str(ix) + "_" + str(ij) + "_" + str(time)
                    s = '{}_{}_{}_{}'.format(area, ix, ij, time)
                    true_assumptions_list.append(s)
                    area_list_dict[area].append((ix, ij, time))
    return [true_assumptions_list, area_list_dict]
    # S_t1 and S_t2 S_t3
    # 3 cycles H => Q
    # H and ~S and ~Q... or ...
    # ~U_ix_ij_0, ~U_ix_ij_0


def get_general_assumptions(true_assumptions, input, areas, vpool):
    matrix = input["observations"]
    shape = np.shape(matrix)  # t, i , j
    # print(shape)
    dimentions = [shape[1], shape[2]]
    epoch = shape[0]
    type1 = ['H', 'S', 'U']
    type2 = ['S', 'U', 'H']
    type3 = ['U', 'H', 'S']
    for area_type in ['H', 'S', 'U', '?']:
        for area in areas[area_type]:
            for i in range(len(type1)):
                cl_str = "~{3}_{0}_{1}_{2} | ~{4}_{0}_{1}_{2}".format(area[0], area[1], area[2], type1[i], type2[i])
                true_assumptions.append(str(cl_str))
                cl_str = "~{3}_{0}_{1}_{2} | ~{4}_{0}_{1}_{2}".format(area[0], area[1], area[2], type1[i], type3[i])
                true_assumptions.append(str(cl_str))
    for area_type in ['S', '?']:
        for area in areas[area_type]:
            if area[2] > 0:
                neighbours_list = find_neighbours(dimentions, area[0], area[1], area[2] - 1)
                #neighbours_list = []  # find_neighbours(dimentions, area[0], area[1], area[2] - 1)
                cl_str = "~H_{0}_{1}_{2} | ~S_{0}_{1}_{3}".format(area[0], area[1], area[2] - 1, area[2])
                for n in neighbours_list:
                    cl_str += " | " + "S_{0}_{1}_{2} & ~H_{0}_{1}_{2}".format(n[0], n[1], n[2])
                #print(cl_str)
                #print(to_cnf("A & B ==> ((C & ~D) | (E & ~F))"))
                cl_str = str(to_cnf(cl_str))
                #print("from gen_list: ", cl_str)
                x = cl_str.split('&')
                for clause in x:
                    #print("clause: ", clause)
                    true_assumptions.append(clause)
                #true_assumptions.append(str(cl_str))

                # print("n_list of area: ", area, neighbours_list)
            # for n in neighbours_list:

            # if area[2] < epoch - 1:
            #     if matrix[n[2]][n[0]][n[1]] == 'H' or matrix[n[2]][n[0]][n[1]] == '?':
            # a=> a or a=> b
    # s = '{}_{}_{}_{} & {}_{}_{}_{} & {}_{}_{}_{}'
    return


# H  ?    S
# S  H    S  S
# ~ A | ~B & ~A | ~C
# ~ B | ~C & ~B | ~A
# ~ C | ~A & ~C | ~B

def get_all_H_assumptions(true_assumptions, input, areas, vpool):
    from pysat.solvers import Glucose3
    # S_t and H_n_t => S_n_t+1   AND H_n_t => H_n_t+1
    # ~S_t or ~H_n_t or (S_n_t+1 and ~H_n_t+1) and ~H_n_t or H_n_t+1
    # print("H_list", H_list)
    matrix = input["observations"]
    shape = np.shape(matrix)  # t, i , j
    # print(shape)
    dimenstions = [shape[1], shape[2]]
    epoch = shape[0]
    for area_type in ['H', '?']:
        for area in areas[area_type]:
            if area[2] < epoch - 1:
                cl_str = "~H_{0}_{1}_{2} | H_{0}_{1}_{3}".format(area[0], area[1], area[2], area[2] + 1)
                true_assumptions.append(str(cl_str))
    return

def get_all_U_assumptions(true_assumptions, input, areas, vpool):
    from pysat.solvers import Glucose3
    # S_t and H_n_t => S_n_t+1   AND H_n_t => H_n_t+1
    # ~S_t or ~H_n_t or (S_n_t+1 and ~H_n_t+1) and ~H_n_t or H_n_t+1
    # print("H_list", H_list)
    matrix = input["observations"]
    shape = np.shape(matrix)  # t, i , j
    # print(shape)
    dimenstions = [shape[1], shape[2]]
    epoch = shape[0]
    #print(to_cnf("A <=> B"))
    for area_type in ['H', 'S', 'U', '?']:
        for area in areas[area_type]:
            if area[2] < epoch - 1:
                cl_str = "~U_{0}_{1}_{2} | U_{0}_{1}_{3}".format(area[0], area[1], area[2], area[2] + 1)
                true_assumptions.append(str(cl_str))
                cl_str = "U_{0}_{1}_{2} | ~U_{0}_{1}_{3}".format(area[0], area[1], area[2], area[2] + 1)
                true_assumptions.append(str(cl_str))
    return



def get_all_S_assumptions(true_assumptions, input, areas, vpool):
    matrix = input["observations"]
    shape = np.shape(matrix)  # t, i , j
    # print(shape)
    dimentions = [shape[1], shape[2]]
    epoch = shape[0]
    # dimentions = [dimentions[0], dimentions[1]]
    t = 0
    if epoch > 3:
        while t + 3 < epoch:
            for ix in range(shape[1]):
                for ij in range(shape[2]):
                    cl_str = "~S_{0}_{1}_{2} | ~S_{0}_{1}_{3} | ~S_{0}_{1}_{4} | H_{0}_{1}_{5}".format(ix, ij, t,
                                                                                                       t + 1, t + 2,
                                                                                                       t + 3)
                    # print(cl_str)
                    # cl_str = to_cnf(cl_str)
                    true_assumptions.append(str(cl_str))
                    cl_str = "~S_{0}_{1}_{2} | ~S_{0}_{1}_{3} | ~S_{0}_{1}_{4} | ~S_{0}_{1}_{5}".format(ix, ij, t,
                                                                                                        t + 1, t + 2,
                                                                                                        t + 3)
                    true_assumptions.append(str(cl_str))

            t += 1
    for area_type in ['S', '?']:
        for area in areas[area_type]:
            # print("area:", area, find_neighbours(dimentions, area[0], area[1], area[2]))
            neighbours_list = find_neighbours(dimentions, area[0], area[1], area[2])
            for n in neighbours_list:
                if area[2] < epoch - 1:
                    if matrix[n[2]][n[0]][n[1]] == 'H' or matrix[n[2]][n[0]][n[1]] == '?':
                        # print("n: ",area,  n[0],n[1], n[2])
                        # cl_str = "S_{0}_{1}_{2} & H_{3}_{4}_{2} ==> S_{3}_{4}_{5} & ~H_{3}_{4}_{5}".format(area[0], area[1], area[2],   #~H_0_1_0 OR H_0_1_1
                        #                                                                   n[0], n[1], area[2] + 1)
                        cl_str = "~S_{0}_{1}_{2} | ~H_{3}_{4}_{2} | S_{3}_{4}_{5}".format(area[0], area[1], area[2],
                                                                                          n[0], n[1], area[2] + 1)
                        true_assumptions.append(str(cl_str))
                        cl_str = "~S_{0}_{1}_{2} | ~H_{3}_{4}_{2} | ~H_{3}_{4}_{5}".format(area[0], area[1], area[2],
                                                                                           n[0], n[1], area[2] + 1)
                        true_assumptions.append(str(cl_str))
    return


def generate_clause(str_sentence, vpool):
    # print(str_sentence)
    x = str_sentence.split('&')
    clauses = []
    for clause in x:
        clause = clause.replace(")", "")
        clause = clause.replace("(", "")
        clause = clause.replace(' ', '')
        clause = clause.split('|')
        clauses.append(clause)
    # print(clauses)
    # print(clauses)
    for clause in clauses:
        for i in range(0, len(clause)):
            if '~' in clause[i]:
                key = clause[i].replace("~", "")
                clause[i] = -vpool[key]
            else:
                clause[i] = vpool[clause[i]]
    # print(clauses)
    return clauses


def create_init_atoms(observations):
    # print("from atomfunc: ", len(observations[0]), len(observations[0][0]))
    atoms = {}
    for i in range(len(observations[0])):
        for j in range(len(observations[0][0])):
            for t in range(len(observations)):
                atoms[('H_{}_{}_{}'.format(i, j, t))] = None
                atoms[('S_{}_{}_{}'.format(i, j, t))] = None
                atoms[('U_{}_{}_{}'.format(i, j, t))] = None
                atoms[('?_{}_{}_{}'.format(i, j, t))] = None

    i = 1
    for key in atoms.keys():
        atoms[key] = i
        i += 1
    # print(atoms)
    return atoms


def convert_list_to_pysat(assumptions_list, vpool):
    pysat_converted = []
    # list = []
    for clause in assumptions_list:
        # print(generate_clause(clause, vpool))
        pysat_converted.append(generate_clause(clause, vpool)[0])
        # list.append(generate_clause(clause, vpool))
    # print("len[0]: ", len(pysat_converted))
    # print("len: ", len(list))
    return pysat_converted


def find_neighbours(dimenstions, i, j, t):
    neighbors_list = []
    if i > 0:
        neighbors_list.append([i - 1, j, t])
    if i < dimenstions[0] - 1:
        neighbors_list.append([i + 1, j, t])
    if j > 0:
        neighbors_list.append([i, j - 1, t])
    if j < dimenstions[1] - 1:
        neighbors_list.append([i, j + 1, t])
    return neighbors_list


def get_solution(pysat_list, assumptions, vpool):
    solution_dict = {}
    g = Minisat22
    # print(pysat_list)
    area_type = ['H', 'S', 'U']
    for assumption in assumptions:
        s_b = '{}_{}_{}_{}'.format(assumption[2], assumption[0][0], assumption[0][1], assumption[1])
        # n_s = '~{}_{}_{}_{}'.format(assumption[2], assumption[0][0], assumption[0][1], assumption[1])
        s = generate_clause(s_b, vpool)
        # n_s = generate_clause(n_s, vpool)
        #sub_s = []
        #sub_s.append(s)
        sub_s = ['{}_{}_{}_{}'.format(area, assumption[0][0], assumption[0][1], assumption[1]) for area in area_type if area is not assumption[2]]
        sub_s.append(s_b)
        #print(sub_s)
        #print(s, n_s)
        ###print("clause:", s[0])
        solution_list = []
        for sub_assumption in sub_s:

            sub_assumption = generate_clause(sub_assumption, vpool)
            with Minisat22(bootstrap_with=pysat_list) as m:
                #print(m.solve(assumptions=s[0]))
                #result = m.solve(assumptions=s[0])
                solution_list.append(m.solve(assumptions=sub_assumption[0]))
            m.delete()
        if solution_list.count(1) > 1:
            solution_dict[assumption] = '?'
        elif solution_list[2]:
             solution_dict[assumption] = "T"
        else:
            solution_dict[assumption] = "F"
            # if result:
            #    solution_dict[assumption] = "T"
            # else:
            #    solution_dict[assumption] = "F"

    #solution_dict = {}
    return solution_dict

# def get_general_assumptions(true_assumptions, input, areas, vpool):
#     matrix = input["observations"]
#     shape = np.shape(matrix)  # t, i , j
#     # print(shape)
#     dimentions = [shape[1], shape[2]]
#     epoch = shape[0]
#     type1 = ['H', 'S', 'U']
#     type2 = ['S', 'U', 'H']
#     type3 = ['U', 'H', 'S']
#     for area in areas["?"]:
#         for i in range(len(type1)):
#             cl_str = "~{3}_{0}_{1}_{2} | ~{4}_{0}_{1}_{2}".format(area[0], area[1], area[2], type1[i], type2[i])
#             true_assumptions.append(str(cl_str))
#             cl_str = "~{3}_{0}_{1}_{2} | ~{4}_{0}_{1}_{2}".format(area[0], area[1], area[2], type1[i], type3[i])
#             true_assumptions.append(str(cl_str))
#     for area_type in ['S', '?']:
#         for area in areas[area_type]:
#             if area[2] > 0:
#                 neighbours_list = find_neighbours(dimentions, area[0], area[1], area[2] - 1)
#                 #neighbours_list = []  # find_neighbours(dimentions, area[0], area[1], area[2] - 1)
#                 cl_str = "~H_{0}_{1}_{2} | ~S_{0}_{1}_{3}".format(area[0], area[1], area[2] - 1, area[2])
#                 for n in neighbours_list:
#                     cl_str += " | " + "S_{0}_{1}_{2} & ~H_{0}_{1}_{2}".format(n[0], n[1], n[2])
#                 #print(cl_str)
#                 #print(to_cnf("A & B ==> ((C & ~D) | (E & ~F))"))
#                 cl_str = str(to_cnf(cl_str))
#                 #print("from gen_list: ", cl_str)
#                 x = cl_str.split('&')
#                 for clause in x:
#                     #print("clause: ", clause)
#                     true_assumptions.append(clause)
#                 #true_assumptions.append(str(cl_str))
#
#                 # print("n_list of area: ", area, neighbours_list)
#             # for n in neighbours_list:
#
#             # if area[2] < epoch - 1:
#             #     if matrix[n[2]][n[0]][n[1]] == 'H' or matrix[n[2]][n[0]][n[1]] == '?':
#             # a=> a or a=> b
#     # s = '{}_{}_{}_{} & {}_{}_{}_{} & {}_{}_{}_{}'
#     return