# import search
import itertools
import random
import math
from itertools import product
import copy


ids = ["312884307", "317644730"]

def solve_problem(problem):
    police_num = problem["police"]
    medic_num = problem["medics"]
    my_state = problem["observations"]
    # print(my_state[0])
    queries = problem["queries"]
    # print((queries[0][0]))
    unpopulated = []
    healthy = []
    sick = []
    immune = []
    quarantine = []
    question = []
    time_dict = {}
    row_len = len(my_state[0])
    col_len = len(my_state)
    # print(len(my_state[0]))
    # print(len(my_state))

    for (i, row) in enumerate(my_state[0]):
        for (j, col) in enumerate(row):
            # if col == 'U':  # find all unpopulated places
            #             #     unpopulated.append((i, j))
            #             # if col == 'H':  # find all healthy people
            #             #     healthy.append((i, j))
            #             # if col == 'S':  # find all sick people
            #             #     sick.append((i, j))
            #             # if col == 'I':  # find all immune people
            #             #     immune.append((i, j))
            #             # if col == 'Q':  # find all quarantined people
            #             #     quarantine.append((i, j))
            # col = list(col)
            if col == '?':  # find all unknown places
                question.append((i, j))
            time_dict[(i, j)] = 0
    perm = list(product('HS', repeat=len(question)))
    temp_state = []
    for row in my_state:
        for col in row:
            # for a in col:
                temp_state.append(list(col))
    # print(temp_state)
    # print(my_state)
    # print(temp_state[0][1])
    # print(temp_state[2][1])

    pd = [[] for _ in range(len(perm))]
    # print(pd)
    for i in range(len(perm)):
        for j in range(len(question)):
            temp_state[question[j][0]][question[j][1]] = perm[i][j]
        temp = copy.deepcopy(temp_state)
        pd[i].append(temp[0:col_len])
    # print(len(pd[0]))
    # print(pd[0])
    # pd[0].append([['H', 'H'], ['b', 'b']])
    # print(len(pd[0]))
    # print(pd[0][1])
    # print(pd[0][0][0][0])
    # print(pd[0][0][0][1])
    # print(pd[0][0][1][0])
    # print(pd[0][0][1][1])
    # print(pd[1][0][0][0])
    # print(pd[1][0][0][1])
    # print(pd[1][0][1][0])
    # print(pd[1][0][1][1])


    for b in range(len(my_state)-1):
        for m in range(len(perm)):
            if len(pd[m]) >= 3:
                for m in range(len(perm)):
                    for row in range(int(col_len)):
                        for bow in range(int(col_len)):
                            if temp[0][row][bow] == 'S':
                                temp[0][row][bow] = 'H'
            if len(pd[m])>1:
                temp = copy.deepcopy(pd[m][len(pd[m])-1])
            else:
                temp = copy.deepcopy(pd[m])

            for row in range(int(col_len)):
                for bow in range(int(col_len)):
                            if temp[0][row][bow] == 'H' and have_sick_neighbor(temp,row,bow,col_len):
                                temp[0][row][bow] = 'S'
            pd[m].append(temp)
            # print(pd[m])
    true_state = []
    for row in my_state:
        for col in row:
            # for a in col:
                true_state.append(list(col))
    # print(true_state)
    # print(true_state[3][0])
    for m in range(len(perm)):
            for m in range(len(perm)):
                for row in range(int(col_len)):
                    for bow in range(int(col_len)):
                        # if pd[m][0][row][bow] == true_state
                            temp[0][row][bow] = 'H'



    # print("state after the second stage- virus spreading: ")
    # for i in temp_state:
        # print(i)

    # for (i, row) in enumerate(temp_state): # third stage- the sickness expires
    #     for (j, col) in enumerate(row):
    #         if col=="S" and self.time_dict[(i,j)]>3:
    #             temp_state[i][j] = "H"
    #             time_dict[(i,j)]=-1
    # # print("state after the third stage- sickness expires: ")
    # # for i in temp_state:
    #     # print(i)

def have_sick_neighbor(state,i,j,col_len):
    if i > 0:  # check for sick neighbors above me
        if state[0][i - 1][j] == "S":
            # print(state[0][i - 1][j])
            return True
    if i < col_len - 1:  # check for sick neighbors below me
        if state[0][i + 1][j] == "S":
            # print(state[0][i + 1][j])
            return True
    if j > 0:  # check for healthy neighbors to the left
        if state[0][i][j - 1] == "S":
            # print(state[0][i][j - 1])
            return True
    if j < col_len - 1:  # check for healthy neighbors to the right
        if state[0][i][j + 1] == "S":
            # print(state[0][i][j + 1])
            return True
    return False