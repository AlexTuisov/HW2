ids = ['336481148', '314625039']

from pysat.solvers import Solver, Glucose3
import math
import itertools


def neighbors(row, col, rows, colls):
    def vert_neighbors(row, col):
        res = [(row + 1, col)] if (row == 0) else (
            [(row - 1, col)] if (row == rows - 1) else [(row + 1, col), (row - 1, col)])
        return res

    def horiz_neighbors(row, col):
        res = [(row, col + 1)] if (col == 0) else (
            [(row, col - 1)] if (col == colls - 1) else [(row, col + 1), (row, col - 1)])
        return res

    neighbor_coords = vert_neighbors(row, col) + horiz_neighbors(row, col)
    return neighbor_coords


def flip_the_table(cell_number, turns):
    for i in cell_number:
        for j in range(turns):
            a = cell_number[i][j]
            a[:] = [-1 * x for x in a]


def flatten(list_of_lists):
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flatten(list_of_lists[0]) + flatten(list_of_lists[1:])
    return list_of_lists[:1] + flatten(list_of_lists[1:])


def solve_problem(input):
    '''
    Since we need to transform the input into atoms and stuff, we map states of cells and address of
    each cell in orderly fashion. See cell_states dict.
    Once we receive the input we infer the dimensions of the map.
    :param input:
    :return:
    '''
    cell_states = {('H', None): 0, ('S', 3): 1, ('S', 2): 2, ('S', 1): 3, ('Q', 2): 4, ('Q', 1): 5,
                   ('I', None): 6, ('U', None): 7}

    first_day = [0, 1, 7]
    second_day_no_medics_no_police = [0, 1, 2, 7]
    third_day_no_medics_no_police = [0, 1, 2, 3, 7]

    second_day_no_medics = [0, 1, 2, 4, 7]
    third_day_no_medics = [0, 1, 2, 3, 4, 5, 7]

    second_day_no_police = [0, 1, 2, 6, 7]
    third_day_no_police = [0, 1, 2, 3, 6, 7]

    second_day = [0, 1, 2, 4, 6, 7]
    third_day_and_so_on = [0, 1, 2, 3, 4, 5, 6, 7]

    police_num = input["police"]
    med_num = input["medics"]
    maps_list = input["observations"]
    query_list = input["queries"]
    # print(query_list[1])
    rows, colls = len(maps_list[0]), len(maps_list[0][0])
    second_day_prob = []
    third_day_prob = []
    turns = len(maps_list)
    if police_num != 0 and med_num != 0:
        second_day_prob = second_day
        third_day_prob = third_day_and_so_on
    elif police_num == 0 and med_num != 0:
        second_day_prob = second_day_no_police
        third_day_prob = third_day_no_police
    elif police_num != 0 and med_num == 0:
        second_day_prob = second_day_no_medics
        third_day_prob = third_day_no_medics
    else:
        second_day_prob = second_day_no_medics_no_police
        third_day_prob = third_day_no_medics_no_police

    # We define mapping of the states:
    # Dictionary cell_numbers has Keys of coordinates that contain values of list of lists.
    # {(0,0):[[1,2,3],[20,21,23,29]],

    cell_number = {}
    count = 1

    # map the indexes for the first turn
    for i in range(rows):
        for j in range(colls):
            coord = (i, j)
            cell_number[coord] = [[count, count + 1, count + 2]]
            count += 3

    # map all the rest of the turns
    for day in range(turns - 1):
        for i in range(rows):
            for j in range(colls):
                list_of_states = []
                if day == 0:
                    day_prob = second_day_prob
                else:
                    day_prob = third_day_prob
                for k in range(len(day_prob)):
                    list_of_states.append(count + day_prob[k])
                count += 8
                cell_number[(i, j)] = cell_number[(i, j)] + [list_of_states]

    KB = []

    for day in range(turns):  # DATA inputs
        for i in range(rows):
            for j in range(colls):
                if maps_list[day][i][j] == 'S':
                    if day == 0:
                        KB.append([cell_number[(i, j)][day][1]])
                    elif day == 1:
                        if maps_list[day - 1][i][j] == 'H':
                            KB.append([cell_number[(i, j)][day][1]])
                        elif maps_list[day - 1][i][j] == 'S':
                            KB.append([cell_number[(i, j)][day][2]])
                        else:
                            KB.append([cell_number[(i, j)][day][1], cell_number[(i, j)][day][2]])
                    else:
                        if maps_list[day - 1][i][j] == 'H':
                            KB.append([cell_number[(i, j)][day][1]])
                        elif maps_list[day - 1][i][j] == 'S':
                            if maps_list[day - 2][i][j] == 'S':
                                KB.append([cell_number[(i, j)][day][3]])
                            elif maps_list[day - 2][i][j] == 'H':
                                KB.append([cell_number[(i, j)][day][2]])
                            else:
                                KB.append([cell_number[(i, j)][day][2], cell_number[(i, j)][day][3]])
                        else:
                            if maps_list[day - 2][i][j] == 'H':
                                KB.append([cell_number[(i, j)][day][1], cell_number[(i, j)][day][2]])
                            elif maps_list[day - 2][i][j] == 'S':
                                KB.append([cell_number[(i, j)][day][1], cell_number[(i, j)][day][3]])
                            elif maps_list[day - 2][i][j] == 'Q':
                                KB.append([cell_number[(i, j)][day][1]])
                            else:
                                KB.append([cell_number[(i, j)][day][1], cell_number[(i, j)][day][2],
                                           cell_number[(i, j)][day][3]])

                elif maps_list[day][i][j] == 'H':
                    KB.append([cell_number[(i, j)][day][0]])

                elif maps_list[day][i][j] == 'U':
                    for k in range(turns):
                        KB.append([cell_number[(i, j)][k][-1]])
                elif maps_list[day][i][j] == 'Q':
                    if day == 1  :
                        KB.append([cell_number[(i, j)][day][3]])
                    elif day >= 2 :
                        if maps_list[day - 1][i][j] == 'S':
                            KB.append([cell_number[(i, j)][day][4]])
                        elif maps_list[day - 1][i][j] == 'Q':
                            KB.append([cell_number[(i, j)][day][5]])
                        else:
                            if maps_list[day - 2][i][j] == 'H':
                                KB.append([cell_number[(i, j)][day][4]])
                            else:
                                KB.append([cell_number[(i, j)][day][4], cell_number[(i, j)][day][5]])
                elif maps_list[day][i][j] == 'I':
                    for k in range(day, turns):  # TODO check the range of the loop
                        KB.append([cell_number[(i, j)][k][-2]])
                elif maps_list[day][i][j] == '?':
                    daylist = []
                    for foo in range(len(cell_number[(i, j)][day])):
                        daylist.append(cell_number[(i, j)][day][foo])
                    KB.append(daylist)



    # print(KB)
    # I can't be in more than one state each turn
    flip_the_table(cell_number, turns)
    for i in cell_number:
        for j in range(turns):
            for x in itertools.combinations(cell_number[i][j], 2):
                KB.append(list(x))
    flip_the_table(cell_number, turns)
    
    for j in range(colls):  # if I'm s3 then one of my neighbors was s
        for i in range(rows):
            for day in range(turns):
                neib_list = neighbors(i, j, rows, colls)
                if day == 0:
                    continue
                if police_num == 0:

                    neib_list_sick = []
                    for k in neib_list:
                        if day == 1:
                            neib_list_sick.append(cell_number[k][day - 1][1])
                        elif day == 2:
                            neib_list_sick.append(cell_number[k][day - 1][1])
                            neib_list_sick.append(cell_number[k][day - 1][2])
                        else:
                            neib_list_sick.append(cell_number[k][day - 1][1])
                            neib_list_sick.append(cell_number[k][day - 1][2])
                            neib_list_sick.append(cell_number[k][day - 1][3])
                        x = [(-1) * cell_number[(i, j)][day][1]]
                    for foo in neib_list_sick:
                        x.append(foo)
                    KB.append(x)
                # if I'm S and was not set to Q2 all my healthy neigbors will be S3/
                # if i'm s3 then at least one of my neigbors was S and was not set to Q
                elif police_num > 0:
                    neib_dict = {}  # example of neib_dict{} when there is two neibs and it's day 2 ,neibs of (0,0), neib_dict{1:[5,~25],2:[8,~33]}
                    curr_S3 = [[(-1) * cell_number[(i, j)][day][1]]]
                    for r in range(len(neib_list)):
                        if day == 1:
                            neib_dict[r + 1] = [[cell_number[neib_list[r]][day - 1][1]],
                                                [(-1) * cell_number[neib_list[r]][day][3]]]
                        elif day == 2:
                            neib_dict[r + 1] = [[cell_number[neib_list[r]][day - 1][1:3]],
                                                [(-1) * cell_number[neib_list[r]][day][4]]]
                        else:
                            neib_dict[r + 1] = [[cell_number[neib_list[r]][day - 1][1:4]],
                                                [(-1) * cell_number[neib_list[r]][day][4]]]
                    if len(neib_list) == 2:
                        neib1 = neib_dict[1]
                        neib2 = neib_dict[2]
                        comb_unflat_y = [[a, b, c] for a in curr_S3 for b in neib1 for c in neib2]
                    elif len(neib_list) == 3:
                        neib1 = neib_dict[1]
                        neib2 = neib_dict[2]
                        neib3 = neib_dict[3]
                        comb_unflat_y = [[a, b, c, d] for a in curr_S3 for b in neib1 for c in neib2 for d in neib3]
                    else:
                        neib1 = neib_dict[1]
                        neib2 = neib_dict[2]
                        neib3 = neib_dict[3]
                        neib4 = neib_dict[4]
                        comb_unflat_y = [[a, b, c, d, e] for a in curr_S3 for b in neib1 for c in neib2 for d in neib3
                                         for e in neib4]
                    for x in comb_unflat_y:
                        z = [val for sublist in x for val in sublist]
                        z1 = flatten(z)
                        KB.append(z1)
    
    # if I'm H and all my neihbors are notS3 and notS2 and notS1 then I will be H or I(if I have medics)
    for day in range(turns):
        for i in range(rows):
            for j in range(colls):
                neib_list = neighbors(i, j, rows, colls)

                neibh_list = []
                if med_num == 0:
                    if day == turns - 1:
                        continue
                    x = [(-1) * cell_number[(i, j)][day][0], cell_number[(i, j)][day + 1][0]]
                elif med_num > 0:
                    if day == turns - 1:
                        continue
                    x = [(-1) * cell_number[(i, j)][day][0], cell_number[(i, j)][day + 1][0],
                         cell_number[(i, j)][day + 1][-2]]
                if day == 0:
                    for k in neib_list:
                        neibh_list.append(cell_number[k][day][1])
                elif day >= turns - 1:
                    continue
                elif day == 1 and day != turns - 1:
                    for k in neib_list:
                        neibh_list.append(cell_number[k][day][1])
                        neibh_list.append(cell_number[k][day][2])
                elif day >= 2 and day != turns - 1:
                    for k in neib_list:
                        neibh_list.append(cell_number[k][day][1])
                        neibh_list.append(cell_number[k][day][2])
                        neibh_list.append(cell_number[k][day][3])
                for foo in neibh_list:
                    x.append(foo)
                KB.append(x)
    
    #problematic
    for day in range(turns):
        for i in range(rows):
            for j in range(colls):
                # If I am S2, then I was S3
                # If I am s3 then I was H
                # If I am s1 then I was S2
                if day == 0:  # change:added
                    continue
                elif day == 1:
                    y = [cell_number[(i, j)][day - 1][0], (-1) * cell_number[(i, j)][day][1]]
                    y1 = [cell_number[(i, j)][day - 1][1], (-1) * cell_number[(i, j)][day][2]]  # change:added
                    KB.append(y)
                    KB.append(y1)  # change:added
                else:
                    y = [cell_number[(i, j)][day - 1][0], (-1) * cell_number[(i, j)][day][1]]
                    y1 = [cell_number[(i, j)][day - 1][1], (-1) * cell_number[(i, j)][day][2]]
                    y2 = [cell_number[(i, j)][day - 1][2], (-1) * cell_number[(i, j)][day][3]]
                    KB.append(y)
                    KB.append(y1)
                    KB.append(y2)

                if police_num > 0:
                    # If I am Q2 then I will be Q1
                    # If I am Q1 then I will be H
                    if day == 0 or day == turns - 1:
                        continue

                    elif day == 1:
                        y = [cell_number[(i, j)][day + 1][5], (-1) * cell_number[(i, j)][day][3]]
                        KB.append(y)

                    elif day >= 2:
                        x = [cell_number[(i, j)][day + 1][5], (-1) * cell_number[(i, j)][day][4]]
                        y = [cell_number[(i, j)][day + 1][0], (-1) * cell_number[(i, j)][day][5]]
                        KB.append(x)
                        KB.append(y)
    
    # If I am Q1 then I was Q2
    for day in range(turns):
        for i in range(rows):
            for j in range(colls):
                if police_num > 0:
                    if day < 2:
                        continue
                    elif day == 2:
                        x = [cell_number[(i, j)][day - 1][3], (-1) * cell_number[(i, j)][day][5]]
                    elif day > 2:
                        x = [cell_number[(i, j)][day - 1][4], (-1) * cell_number[(i, j)][day][5]]
                    KB.append(x)
    # actions
    # If I am S3 the I will be S2 or Q2
    # If I am S2 then I will be S1 or Q2
    # If I am S1 the I will be H or Q2
    for day in range(turns):
        for i in range(rows):
            for j in range(colls):
                if police_num > 0:
                    if day == 0:
                        x = [(-1) * cell_number[(i, j)][day][1], cell_number[(i, j)][day + 1][2],
                             cell_number[(i, j)][day + 1][3]]
                        KB.append(x)
                    elif day == turns - 1:
                        continue
                    elif day == 1:
                        x = [(-1) * cell_number[(i, j)][day][1], cell_number[(i, j)][day + 1][2],
                             cell_number[(i, j)][day + 1][4]]
                        y = [(-1) * cell_number[(i, j)][day][2], cell_number[(i, j)][day + 1][3],
                             cell_number[(i, j)][day + 1][4]]
                        KB.append(x)
                        KB.append(y)
                    elif day >= 2:
                        x = [(-1) * cell_number[(i, j)][day][1], cell_number[(i, j)][day + 1][2],
                             cell_number[(i, j)][day + 1][4]]
                        y = [(-1) * cell_number[(i, j)][day][2], cell_number[(i, j)][day + 1][3],
                             cell_number[(i, j)][day + 1][4]]
                        z = [(-1) * cell_number[(i, j)][day][3], cell_number[(i, j)][day + 1][0],
                             cell_number[(i, j)][day + 1][4]]
                        KB.append(x)
                        KB.append(y)
                        KB.append(z)
                ##nour:if there is no police
                # if I'm s3 then i will be s2
                # if I'm s2 then i will be s1
                # if I'm s1 then i will be H
                elif police_num == 0:
                    if day == 0:
                        x = [cell_number[(i, j)][day + 1][2], (-1) * cell_number[(i, j)][day][1]]
                        KB.append(x)
                    elif day == turns - 1:
                        continue
                    elif day == 1:
                        x = [cell_number[(i, j)][day + 1][2], (-1) * cell_number[(i, j)][day][1]]
                        y = [cell_number[(i, j)][day + 1][3], (-1) * cell_number[(i, j)][day][2]]
                        KB.append(x)
                        KB.append(y)
                    elif day >= 2:
                        x = [cell_number[(i, j)][day + 1][2], (-1) * cell_number[(i, j)][day][1]]
                        y = [cell_number[(i, j)][day + 1][3], (-1) * cell_number[(i, j)][day][2]]
                        z = [cell_number[(i, j)][day + 1][0], (-1) * cell_number[(i, j)][day][3]]
                        KB.append(x)
                        KB.append(y)
                        KB.append(z)
    
    # nour-ADD:if I'm H then I was H or S1 or Q1
    for day in range(turns):
        for i in range(rows):
            for j in range(colls):
                if police_num == 0:
                    if day == 0:
                        continue
                    elif day == 1 or day == 2:
                        KB.append([cell_number[(i, j)][day - 1][0], (-1) * cell_number[(i, j)][day][0]])
                    else:
                        KB.append([cell_number[(i, j)][day - 1][3],
                                   cell_number[(i, j)][day - 1][0], (-1) * cell_number[(i, j)][day][0]])
                elif police_num > 0:
                    if day == 0:
                        continue
                    elif day == 1 or day == 2:
                        KB.append([cell_number[(i, j)][day - 1][0], (-1) * cell_number[(i, j)][day][0]])

                    else:
                        KB.append([cell_number[(i, j)][day - 1][3], cell_number[(i, j)][day - 1][5],
                                   cell_number[(i, j)][day - 1][0], (-1) * cell_number[(i, j)][day][0]])
    
    # If I was H(and in case of medics did not became I) and one of neigbourghs was S
    # (which in case of police did not became Q) then I will be S3
    # ((x1IM H & x2 IM WILL NOT BE I) & ((x3 NEIB1 IS S3)OrS2 or S1 & x4 WILL NOT BE Q2) | (x5 NEIB2 IS S & x6 WILL NOT BE Q2)
    # | (x7 NEIB3 IS S & x8 WILL NOT BE Q2))) >>9 I WILL BECOME S3)
    # (9 | ~1 | ~3 | ~4) & (9 | ~1 | ~5 | ~6) & (9 | ~1 | ~7 | ~8)

    # (9 | ~1 | ~10 | ~4) & (9 | ~1 | ~11 | ~4) & (9 | ~1 | ~3 | ~4) & (9 | ~1 | ~5 | ~6) & (9 | ~1 | ~7 | ~8)
    for day in range(turns):
        for j in range(colls):
            for i in range(rows):
                neib_list = neighbors(i, j, rows, colls)
                neib_list_sick = []
                if police_num == 0:
                    for k in neib_list:
                        if day == 0:
                            neib_list_sick.append((-1) * cell_number[k][day][1])
                        elif day == turns - 1:
                            continue
                        elif day == 1:
                            neib_list_sick.append((-1) * cell_number[k][day][1])
                            neib_list_sick.append((-1) * cell_number[k][day][2])
                        elif day >= 2:
                            neib_list_sick.append((-1) * cell_number[k][day][1])
                            neib_list_sick.append((-1) * cell_number[k][day][2])
                            neib_list_sick.append((-1) * cell_number[k][day][3])
                    if med_num == 0:
                        for foo in neib_list_sick:
                            x = [(-1) * cell_number[(i, j)][day][0], cell_number[(i, j)][day + 1][1]]
                            x.append(foo)
                            KB.append(x)
                            x = [(-1) * cell_number[(i, j)][day][0], cell_number[(i, j)][day + 1][1]]
                    elif med_num > 0:
                        for foo in neib_list_sick:
                            x = [(-1) * cell_number[(i, j)][day][0], cell_number[(i, j)][day + 1][1],
                                 cell_number[(i, j)][day + 1][-2]]
                            x.append(foo)
                            KB.append(x)
                            x = [(-1) * cell_number[(i, j)][day][0], cell_number[(i, j)][day + 1][1],
                                 cell_number[(i, j)][day + 1][-2]]
                elif police_num > 0:
                    for k in neib_list:
                        if day == 0:
                            neib_list_sick.append([(-1) * cell_number[k][day][1], cell_number[k][day + 1][3]])
                        elif day == turns - 1:
                            continue
                        elif day == 1:
                            neib_list_sick.append([(-1) * cell_number[k][day][1], cell_number[k][day + 1][4]])
                            neib_list_sick.append([(-1) * cell_number[k][day][2], cell_number[k][day + 1][4]])
                        elif day >= 2:
                            neib_list_sick.append([(-1) * cell_number[k][day][1], cell_number[k][day + 1][4]])
                            neib_list_sick.append([(-1) * cell_number[k][day][2], cell_number[k][day + 1][4]])
                            neib_list_sick.append([(-1) * cell_number[k][day][3], cell_number[k][day + 1][4]])
                    if med_num == 0:
                        for foo in neib_list_sick:
                            x = [(-1) * cell_number[(i, j)][day][0], cell_number[(i, j)][day + 1][1]]
                            x.append(foo[0])
                            x.append(foo[1])
                            KB.append(x)
                    elif med_num > 0:
                        for foo in neib_list_sick:
                            x = [(-1) * cell_number[(i, j)][day][0], cell_number[(i, j)][day + 1][1],
                                        cell_number[(i, j)][day + 1][-2]]
                            x.append(foo[0])
                            x.append(foo[1])
                            KB.append(x)
    

    # If I am H, then I will be H or S3 or I
    for day in range(turns):
        for i in range(rows):
            for j in range(colls):
                if med_num > 0:
                    if day < turns - 1:
                        KB.append([(-1) * cell_number[(i, j)][day][0], cell_number[(i, j)][day + 1][0],
                                   cell_number[(i, j)][day + 1][1], cell_number[(i, j)][day + 1][-2]])
                    elif day == turns - 1:
                        continue
                elif med_num == 0:
                    if day < turns - 1:
                        KB.append([(-1) * cell_number[(i, j)][day][0], cell_number[(i, j)][day + 1][0],
                                   cell_number[(i, j)][day + 1][1]])
                    elif day == turns - 1:
                        continue
    
    def Q2_list_day(day):
        qlist = []

        for i in range(rows):
            for j in range(colls):
                if day == 1:
                    qlist.append((-1) * cell_number[(i, j)][day][3])
                else:
                    qlist.append((-1) * cell_number[(i, j)][day][4])
        return qlist

    for day in range(turns):
        if police_num > 0:
            if day == 0:
                continue
            else:
                q2_list = Q2_list_day(day)
                for x in itertools.combinations(q2_list, police_num + 1):  # maybe police + police*day
                    KB.append(list(x))
    
    def I_list_day(day):
        Ilist = []
        for i in range(rows):
            for j in range(colls):
                if police_num > 0:
                    if day == 0:
                        continue
                    elif day == 1:
                        Ilist.append((-1) * cell_number[(i, j)][day][4])
                    else:
                        Ilist.append((-1) * cell_number[(i, j)][day][6])
                else:
                    if day == 1:
                        Ilist.append((-1) * cell_number[(i, j)][day][3])
                    else:
                        Ilist.append((-1) * cell_number[(i, j)][day][4])
        return Ilist

    for day in range(1, turns):
        if med_num > 0 and med_num * day <= rows * colls:
            I_list = I_list_day(day)
            for x in itertools.combinations(I_list, med_num * day + 1):
                KB.append(list(x))
    # print(cell_number)
    # print(KB)
    '''"queries": [
        [((0, 1), 1, "H"), ((1, 0), 1, "S")]
    ]'''
    ans_dict = {}
    print('IStartTocheck')
    for query in query_list:
        if query[2] == 'H':
            KB.append([cell_number[query[0]][query[1]][0]])
            with Glucose3(bootstrap_with=KB) as m:
                truth = m.solve()
            KB.pop(-1)
            if truth == True:
                KB.append([(-1) * cell_number[query[0]][query[1]][0]])
                with Glucose3(bootstrap_with=KB) as m:
                    truth = m.solve()
                KB.pop(-1)
                if truth == True:
                    ans_dict[query] = '?'
                else:
                    ans_dict[query] = 'T'
            else:
                ans_dict[query] = 'F'
        elif query[2] == 'S':
            if query[1] == 0:
                KB.append([cell_number[query[0]][query[1]][1]])
                with Glucose3(bootstrap_with=KB) as m:
                    truth = m.solve()
                KB.pop(-1)
                if truth == True:
                    KB.append([(-1) * cell_number[query[0]][query[1]][1]])
                    with Glucose3(bootstrap_with=KB) as m:
                        truth = m.solve()
                    KB.pop(-1)
                    if (truth == True):
                        ans_dict[query] = '?'
                    else:
                        ans_dict[query] = 'T'
                else:
                    ans_dict[query] = 'F'
            elif query[1] == 1:
                KB.append([cell_number[query[0]][query[1]][1], cell_number[query[0]][query[1]][2]])
                with Glucose3(bootstrap_with=KB) as m:
                    truth = m.solve()

                KB.pop(-1)
                if truth == True:
                    truth = False  # flag
                    KB.append([(-1) * cell_number[query[0]][query[1]][1]])
                    KB.append([(-1) * cell_number[query[0]][query[1]][2]])
                    with Glucose3(bootstrap_with=KB) as m:
                        truth = m.solve()
                    KB.pop(-1)
                    KB.pop(-1)
                    if truth == True:
                        ans_dict[query] = '?'
                    else:
                        ans_dict[query] = 'T'
                else:
                    ans_dict[query] = 'F'
            else:
                KB.append([cell_number[query[0]][query[1]][1], cell_number[query[0]][query[1]][2],
                           cell_number[query[0]][query[1]][3]])
                with Glucose3(bootstrap_with=KB) as m:
                    truth = m.solve()
                KB.pop(-1)
                if truth == True:
                    KB.append([(-1) * cell_number[query[0]][query[1]][1]])
                    KB.append([(-1) * cell_number[query[0]][query[1]][2]])
                    KB.append([(-1) * cell_number[query[0]][query[1]][3]])
                    with Glucose3(bootstrap_with=KB) as m:
                        truth = m.solve()
                    KB.pop(-1)
                    KB.pop(-1)
                    KB.pop(-1)
                    if truth == True:
                        ans_dict[query] = '?'
                    else:
                        ans_dict[query] = 'T'
                else:
                    ans_dict[query] = 'F'
        elif query[2] == 'Q':
            if query[1] == 0:
                ans_dict[query] = 'F'
            elif query[1] == 1:
                KB.append([cell_number[query[0]][query[1]][3]])
                with Glucose3(bootstrap_with=KB) as m:
                    truth = m.solve()
                KB.pop(-1)
                if truth == True:
                    truth = False  # flag
                    KB.append([(-1) * cell_number[query[0]][query[1]][3]])
                    with Glucose3(bootstrap_with=KB) as m:
                        truth = m.solve()
                    KB.pop(-1)
                    if truth == True:
                        ans_dict[query] = '?'
                    else:
                        ans_dict[query] = 'T'
                else:
                    ans_dict[query] = 'F'
            else:
                KB.append([cell_number[query[0]][query[1]][4], cell_number[query[0]][query[1]][5]])
                with Glucose3(bootstrap_with=KB) as m:
                    truth = m.solve()
                KB.pop(-1)
                if truth == True:
                    KB.append([(-1) * cell_number[query[0]][query[1]][4]])
                    KB.append([(-1) * cell_number[query[0]][query[1]][5]])
                    with Glucose3(bootstrap_with=KB) as m:
                        truth = m.solve()
                    KB.pop(-1)
                    KB.pop(-1)
                    if truth == True:
                        ans_dict[query] = '?'
                    else:
                        ans_dict[query] = 'T'
                else:
                    ans_dict[query] = 'F'
        elif query[2] == 'I':

            if police_num > 0:
                a, b = 4, 6
            else:
                a, b = 3, 4
            if query[1] == 0:
                ans_dict[query] = 'F'
            elif query[1] == 1:
                KB.append([cell_number[query[0]][query[1]][a]])
                with Glucose3(bootstrap_with=KB) as m:
                    truth = m.solve()
                KB.pop(-1)
                if truth == True:
                    KB.append([(-1) * cell_number[query[0]][query[1]][a]])
                    with Glucose3(bootstrap_with=KB) as m:
                        truth = m.solve()
                    KB.pop(-1)
                    if truth == True:
                        ans_dict[query] = '?'
                    else:
                        ans_dict[query] = 'T'
                else:
                    ans_dict[query] = 'F'
            else:
                KB.append([cell_number[query[0]][query[1]][b]])
                with Glucose3(bootstrap_with=KB) as m:
                    truth = m.solve()
                KB.pop(-1)
                if truth == True:
                    KB.append([(-1) * cell_number[query[0]][query[1]][a]])
                    with Glucose3(bootstrap_with=KB) as m:
                        truth = m.solve()
                    KB.pop(-1)
                    if truth == True:
                        ans_dict[query] = '?'
                    else:
                        ans_dict[query] = 'T'
                else:
                    ans_dict[query] = 'F'
        else:
            KB.append([cell_number[query[0]][query[1]][-1]])
            with Glucose3(bootstrap_with=KB) as m:
                truth = m.solve()
            KB.pop(-1)
            if truth == True:
                KB.append([(-1) * cell_number[query[0]][query[1]][-1]])
                with Glucose3(bootstrap_with=KB) as m:
                    truth = m.solve()
                KB.pop(-1)
                if truth == True:
                    ans_dict[query] = '?'
                else:
                    ans_dict[query] = 'T'
            else:
                ans_dict[query] = 'F'
    # print("Imdone")
    return ans_dict
