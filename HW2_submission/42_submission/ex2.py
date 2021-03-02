import itertools
from pysat.solvers import Glucose3


ids = ['318483906', '316051903']


def solve_problem(input):

    clauses = []
    row = len(input['observations'][0])
    column = len(input['observations'][0][0])
    number_of_observations = len(input['observations'])
    array_len = row * column * number_of_observations * 8
    med = input['medics']
    police = input['police']
    matrix_array = []
    i = 0
    while i < array_len:
        matrix_array.append(-(i+1))
        i = i+1
    arr = variable_arr(input)
    checkmatrix = check_mat(input, matrix_array)
    clauses_0 = one_state(arr)
    clauses_1 = S_condition(checkmatrix, number_of_observations, row, column)
    clauses_2 = Q_condition(checkmatrix, row, column)
    clauses_3 = H_condition(checkmatrix, row, column)
    clauses_4 = U_condition(checkmatrix, row, column)
    clauses_5 = I_condition(checkmatrix, row, column)
    clauses_6 = QMark_condition(checkmatrix, number_of_observations, row, column,med,police)
    clauses_7 = first_observation(checkmatrix,column ,row,number_of_observations)
    clauses_8 = NoMed(checkmatrix)
    clauses_9 = NoPli(checkmatrix)
    clauses_10 = medics(checkmatrix,column,row,number_of_observations)
    clauses_11 = poli(checkmatrix, column, row, number_of_observations)
    if clauses_0:
        for cl in clauses_0:
            clauses.append(cl)
    if clauses_1:
        for cl in clauses_1:
            clauses.append(cl)
    if clauses_2:
        for cl in clauses_2:
            clauses.append(cl)
    if clauses_3:
        for cl in clauses_3:
            clauses.append(cl)
    if clauses_4:
        for cl in clauses_4:
            clauses.append(cl)
    if clauses_5:
        for cl in clauses_5:
            clauses.append(cl)
    if clauses_6:
        for cl in clauses_6:
            clauses.append(cl)
    if clauses_7:
        for cl in clauses_7:
            clauses.append(cl)
    if med == 0 :
        for cl in clauses_8:
            clauses.append(cl)
    if police == 0:
        for cl in clauses_9:
            clauses.append(cl)
    if med == 1:
        for cl in clauses_10:
            clauses.append(cl)
    if police == 1:
        for cl in clauses_11:
            clauses.append(cl)
    Q_clause = queries_clause(input, column, row)
    j=0
    ret_dic = {}
    for C in Q_clause:
        i = 1
        count = 0
        flag = False
        for c in C:
            g = Glucose3()
            g.add_clause(c)
            for cl in clauses:
                g.add_clause(cl)
            if g.solve() == False and i == 1:
                ret_dic[input['queries'][j]] = "F"
                flag = True
                break
            if g.solve() == True:
                count = count + 1
            if count > 1:
                ret_dic[input['queries'][j]] = "?"
                flag = True
                break
            g.delete()
            i = i + 1
            continue
        if flag == False:
            ret_dic[input['queries'][j]] = 'T'
        j = j+1
    return ret_dic


def variable_arr(input):
    row = len(input['observations'][0])
    column = len(input['observations'][0][0])
    number_of_observations = len(input['observations'])
    array_len = row * column * number_of_observations * 8
    matrix_array = []
    i = 0
    while i < array_len:
        matrix_array.append(-(i + 1))
        i = i + 1
    return matrix_array


def check_mat(input, arr):
    ob_pointer = 0
    k = 0
    while ob_pointer < len(input['observations']):
        for row in range(len(input['observations'][0])):
            for column in range(len(input['observations'][0][0])):
                if input['observations'][ob_pointer][row][column] == "?":
                    arr[k] = '?'
                    arr[k+1] = '?'
                    arr[k+2] = '?'
                    arr[k+3] = '?'
                    arr[k+4] = '?'
                    arr[k+5] = '?'
                    arr[k+6] = '?'
                    arr[k+7] = '?'
                if input['observations'][ob_pointer][row][column] == 'H':
                    arr[k] = k + 1
                if input['observations'][ob_pointer][row][column] == 'S':
                    if ob_pointer == 0:
                        arr[k + 1] = k + 2
                    if ob_pointer == 1:
                        if input['observations'][ob_pointer - 1][row][column] == "H":
                            arr[k + 1] = k + 2
                        elif input['observations'][ob_pointer - 1][row][column] == "?":
                            arr[k + 1] = 'S'
                            arr[k + 2] = 'S'
                            arr[k + 3] = 'S'
                        elif input['observations'][ob_pointer - 1][row][column] == "S":
                            arr[k + 2] = k + 3
                    if ob_pointer - 2 >= 0:
                        if input['observations'][ob_pointer - 1][row][column] == "S":
                            if input['observations'][ob_pointer - 2][row][column] == "H":
                                arr[k + 2] = k + 3
                            elif input['observations'][ob_pointer - 2][row][column] == "S":
                                arr[k + 3] = k + 4
                            elif input['observations'][ob_pointer - 2][row][column] == "?":
                                arr[k + 1] = 'S'
                                arr[k + 2] = 'S'
                                arr[k + 3] = 'S'
                        if input['observations'][ob_pointer - 1][row][column] == "H":
                            arr[k + 1] = k + 2
                        if input['observations'][ob_pointer - 1][row][column] == "?":
                            arr[k + 1] = 'S'
                            arr[k + 2] = 'S'
                            arr[k + 3] = 'S'
                if input['observations'][ob_pointer][row][column] == 'Q':
                    if ob_pointer == 0:
                        arr[k + 4] = k + 5
                    if ob_pointer - 1 >= 0:
                        if input['observations'][ob_pointer - 1][row][column] == "S":
                            arr[k + 4] = k + 5
                        elif input['observations'][ob_pointer - 1][row][column] == "Q":
                            arr[k + 5] = k + 6
                        elif input['observations'][ob_pointer - 1][row][column] == "?":
                            arr[k + 4] = 'Q'
                            arr[k + 5] = 'Q'
                if input['observations'][ob_pointer][row][column] == 'I':
                    arr[k + 6] = k + 7
                if input['observations'][ob_pointer][row][column] == 'U':
                    arr[k + 7] = k + 8
                k = k + 8
        ob_pointer = ob_pointer + 1
    return arr


def NoMed(arr):
    clauses=[]
    for i in range(6,len(arr),8):
        clauses.append([-(i+1)])
    return clauses


def NoPli(arr):
    clauses = []
    for i in range(1, len(arr), 8):
        clauses.append([-(i + 4)])
        clauses.append([-(i + 5)])
    return clauses


def poli(arr,column,row,obs):
    j=4
    newQ=[]
    QM=[]
    clauses=[]
    for i in range(row*column*obs):
        if i >= row * column:
            if type(arr[i * 8 + j]) == int:
                if arr[i * 8 + j] > 0:
                    newQ.append(i * 8 + j+1)
            if arr[i * 8 + j] == "?":
                if type(arr[i * 8 - row * column * 8]) == int:
                    if arr[i * 8 - row * column * 8+1] > 0:
                        QM.append(i * 8 + j + 1)
                    elif arr[i * 8 - row * column * 8+2] > 0:
                        QM.append(i * 8 + j + 1)
                    elif arr[i * 8 - row * column * 8 + 3] > 0:
                        QM.append(i * 8 + j + 1)
                if i * 8 - row * column * 8 > 0:
                    if arr[i * 8 - row * column * 8] == '?':
                        if i * 8 - 2 * row * column * 8 > 0:
                            if arr[i * 8 + 1 - row * column * 8] > 0:
                                QM.append(i * 8 + j+1)
                        if i * 8 - 2 * row * column * 8 < 0 :
                            QM.append(i * 8 + j + 1)
    if len(newQ) >= 1:
        clauses.append(newQ)
        for q in newQ:
            clauses.append([q])
        for q in QM:
            clauses.append([-(q)])
    if len(newQ) == 0:
        digits = QM
        clauses.append([l for l in digits])
        for pair in itertools.combinations(digits, 2):
            clauses.append([-l for l in pair])
    return clauses


def medics(arr,column,row,obs):
    j = 6
    newI=[]
    newQM =[]
    clauses = []
    for i in range(row * column * obs):
        if i >= row * column:
            if type(arr[i * 8 + j]) == int:
                if arr[i * 8 + j] > 0:
                    if type(arr[i * 8 + j - row * column * 8]) == int:
                        if arr[i * 8 + j - row * column * 8] < 0:
                            newI.append(i * 8 + j + 1)
            if arr[i * 8 + j] == "?":
                if type(arr[i * 8 - row * column * 8]) == int:
                    if arr[i * 8 - row * column * 8] > 0:
                        newQM.append(i * 8 + j + 1)
                if i * 8 - row * column * 8 >0:
                    if arr[i * 8 - row * column * 8] == '?':
                        if i * 8 - 2*row * column * 8 >0:
                            if arr[i * 8 + 1 - row * column * 8]<0 and \
                                    arr[i * 8 + 6 - row * column * 8]<0 and \
                                    arr[i * 8 + 7 - row * column * 8]<0:
                                newQM.append(i * 8 + j+1)
    if len(newI) >= 1:
        clauses.append(newI)
        for q in newI:
            clauses.append([q])
        for q in newQM:
            clauses.append([-(q)])
    if len(newI) == 0:
        digits = newQM
        clauses.append([l for l in digits])
        for pair in itertools.combinations(digits, 2):
            clauses.append([-l for l in pair])
    return clauses


def first_observation(arr,column,row,obs):
    list = []
    i = 0
    while i < row * column * 8 * obs:
        if type(arr[i]) == int:
            if arr[i] > 0:
                list.append([i +1])
        i = i + 1
    return list


def queries_clause(input,column,row):
    list = []
    queries = input['queries']
    for i in range(len(queries)):
        in_row = input['queries'][i][0][0] * 8 * column
        in_column = input['queries'][i][0][1] * 8
        num = input['queries'][i][1] * row * column * 8 + in_row + in_column
        if input['queries'][i][2] == 'H':
            list.append([[num+1],[num+7],[num+8],[num+2, num+3, num+4],[num+5, num+6]])
        if input['queries'][i][2] == 'I':
            list.append([[num+7],[num+1],[num+8],[num+2, num+3, num+4],[num+5, num+6]])
        if input['queries'][i][2] == 'U':
            list.append([[num+8],[num+1],[num+7],[num+2, num+3, num+4],[num+5, num+6]])
        if input['queries'][i][2] == 'S':
            list.append([[num+2, num+3, num+4],[num+1],[num+7],[num+8],[num+5, num+6]])
        if input['queries'][i][2] == 'Q':
            list.append([[num+5, num+6],[num+1],[num+7],[num+8],[num+2, num+3, num+4]])
            list.append([num+1])
            list.append([num+7])
            list.append([num+8])
            list.append([num+2, num+3, num+4])
    return list


def one_state(arr):
    clauses = []
    i = 1
    while i < len(arr):
        digits = range(i, i + 8)
        clauses.append([l for l in digits])
        for pair in itertools.combinations(digits, 2):
            clauses.append([-l for l in pair])
        i = i+8
    return clauses


def QMark_condition(arr, obs, row, column,med,police):
    clauses = []
    list = []
    for i in range(row * column * obs):
        if i < row * column:
            if arr[i * 8] == '?':
                # H
                list.append(i * 8 + 1)
                # S3
                list.append(i * 8 + 2)
                # U
                list.append(i * 8 + 8)
                copy = list.copy()
                clauses.append(copy)
                list.clear()
        flag = False
        if i >= row * column:
            if arr[i * 8] == '?':
                if arr[i * 8 - row * column * 8] == '?':
                    if i - 2 * row * column * 8 >= 0:
                        if arr[1 + i * 8 - row * column * 8] > 0:
                            list.append(i * 8 + 3 + 1)
                        elif arr[6 + i * 8 - row * column * 8] > 0:
                            list.append(i * 8 + 6 + 1)
                        elif arr[7 + i * 8 - row * column * 8] > 0:
                            list.append(i * 8 + 7 + 1)
                        else:
                            list.append(i * 8 + 6 + 1)
                            list.append(i * 8 + 5 + 1)
                            list.append(i * 8 + 4 + 1)
                            list.append(i * 8 + 3 + 1)
                            list.append(i * 8 + 2 + 1)
                            list.append(i * 8 + 1 + 1)
                            list.append(i * 8 + 1)
                    else:
                        list.append(i * 8 + 6 + 1)
                        list.append(i * 8 + 5 + 1)
                        list.append(i * 8 + 4 + 1)
                        list.append(i * 8 + 3 + 1)
                        list.append(i * 8 + 2 + 1)
                        list.append(i * 8 + 1 + 1)
                        list.append(i * 8 + 1)
                    copy1 = list.copy()
                    clauses.append(copy1)
                    list.clear()
                for j in range(8):
                    if j == 0:
                        if type(arr[i * 8 + j - row * column * 8]) == int:
                            if arr[i * 8 + j - row * column * 8] > 0:
                                if med != 0:
                                    list.append(i * 8 + j + 6 + 1)
                                if i % column != 0 and i > 0:
                                    if type(arr[1 + 8 * (i - 1) - row * column * 8]) == int:
                                        if arr[1 + 8 * (i - 1) - row * column * 8] > 0:
                                            list.append(i * 8 + j + 1 + 1)
                                            flag = True
                                        elif arr[2 + 8 * (i - 1) - row * column * 8] > 0:
                                            list.append(i * 8 + j + 1 + 1)
                                            flag = True
                                        elif arr[3 + 8 * (i - 1) - row * column * 8] > 0:
                                            list.append(i * 8 + j + 1 + 1)
                                            flag = True
                                    elif arr[2 + 8 * (i - 1) - row * column * 8] == '?':
                                        clauses.append([i * 8 + j + 1 + 1,-(1 + 8 * (i - 1) - row * column * 8)])
                                        clauses.append([i * 8 + j + 1 + 1, -(2 + 8 * (i - 1) - row * column * 8)])
                                        clauses.append([i * 8 + j + 1 + 1, -(3 + 8 * (i - 1) - row * column * 8)])
                                if (i + 1) % column != 0:
                                    if type(arr[2 + 8 * (i + 1) - row * column * 8]) == int:
                                        if arr[1 + 8 * (i + 1) - row * column * 8] > 0:
                                            list.append(i * 8 + j + 1 + 1)
                                            flag = True
                                        elif arr[2 + 8 * (i + 1) - row * column * 8] > 0:
                                            list.append(i * 8 + j + 1 + 1)
                                            flag = True
                                        elif arr[3 + 8 * (i + 1) - row * column * 8] > 0:
                                            list.append(i * 8 + j + 1 + 1)
                                            flag = True
                                    elif arr[2 + 8 * (i + 1) - row * column * 8] == '?':
                                        clauses.append([i * 8 + j + 1 + 1,-(1 + 8 * (i + 1) - row * column * 8)])
                                        clauses.append([i * 8 + j + 1 + 1, -(2 + 8 * (i + 1) - row * column * 8)])
                                        clauses.append([i * 8 + j + 1 + 1, -(3 + 8 * (i + 1) - row * column * 8)])
                                if (i) % (column * row) > column:
                                    if type(arr[2 + 8 * (i - column) - row * column * 8]) == int:
                                        if arr[1 + 8 * (i - column) - row * column * 8] > 0:
                                            list.append(i * 8 + j + 1 + 1)
                                            flag = True
                                        elif arr[2 + 8 * (i - column) - row * column * 8] > 0:
                                            list.append(i * 8 + j + 1 + 1)
                                            flag = True
                                        elif arr[3 + 8 * (i - column) - row * column * 8] > 0:
                                            list.append(i * 8 + j + 1 + 1)
                                            flag = True
                                    elif arr[2 + 8 * (i - column) - row * column * 8] == '?':
                                        clauses.append([i * 8 + j + 1 + 1, -(1 + 8 * (i - column) - row * column * 8)])
                                        clauses.append([i * 8 + j + 1 + 1, -(2 + 8 * (i - column) - row * column * 8)])
                                        clauses.append([i * 8 + j + 1 + 1, -(3 + 8 * (i - column) - row * column * 8)])
                                if (i + 1) % (row * column) != 0 and (i + 1) % (row * column) < (row - 1) * column:
                                    if type(arr[2 + 8 * (i + column) - row * column * 8]) == int:
                                        if arr[1 + 8 * (i + column) - row * column * 8] > 0:
                                            list.append(i * 8 + j + 1 + 1)
                                            flag = True
                                        elif arr[2 + 8 * (i + column) - row * column * 8] > 0:
                                            list.append(i * 8 + j + 1 + 1)
                                            flag = True
                                        elif arr[3 + 8 * (i + column) - row * column * 8] > 0:
                                            list.append(i * 8 + j + 1 + 1)
                                            flag = True
                                    elif arr[2 + 8 * (i + column) - row * column * 8] == '?':
                                        clauses.append([i * 8 + j + 1 + 1, -(1 + 8 * (i + column) - row * column * 8)])
                                        clauses.append([i * 8 + j + 1 + 1, -(2 + 8 * (i + column) - row * column * 8)])
                                        clauses.append([i * 8 + j + 1 + 1, -(3 + 8 * (i + column) - row * column * 8)])
                                if flag == False:
                                    list.append(i * 8 + j + 1)
                                copy = list.copy()
                                clauses.append(copy)
                                list.clear()
                    if j == 1:
                        if type(arr[i * 8 + j - row * column * 8]) == int:
                            if arr[i * 8 + j - row * column * 8] > 0:
                                if police >0 :
                                    clauses.append([i * 8 + j + 1 + 1,i * 8 + j + 3 + 1])
                                else:
                                    clauses.append([i * 8 + j + 1 + 1])
                    if j == 2:
                        if type(arr[i * 8 + j - row * column * 8]) == int:
                            if arr[i * 8 + j - row * column * 8] > 0:
                                if police >0 :
                                    clauses.append([i * 8 + j + 1 + 1,i * 8 + j + 2 + 1])
                                else:
                                    clauses.append([i * 8 + j + 1 + 1])
                    if j == 3:
                        if type(arr[i * 8 + j - row * column * 8]) == int:
                            if arr[i * 8 + j - row * column * 8] > 0:
                                if police >0 :
                                    clauses.append([i * 8 + j - 2, i * 8 + j + 2])
                                else:
                                    clauses.append([i * 8 + j - 2])
                    if j == 4:
                        if type(arr[i * 8 + j - row * column * 8]) == int:
                            if arr[i * 8 + j - row * column * 8] > 0:
                                clauses.append([i * 8 + j + 2])
                    if j == 5:
                        if type(arr[i * 8 + j - row * column * 8]) == int:
                            if arr[i * 8 + j - row * column * 8] > 0:
                                clauses.append([i * 8 + j - 4])
                    if j == 6:
                        if type(arr[i * 8 + j - row * column * 8]) == int:
                            if arr[i * 8 + j - row * column * 8] > 0:
                                clauses.append([i * 8 + j + 1])
                    if j == 7:
                        if type(arr[i * 8 + j - row * column * 8]) == int:
                            if arr[i * 8 + j - row * column * 8] > 0:
                                clauses.append([i * 8 + j + 1])
    return clauses


def S_condition(arr, obs, row, column):
    list = []
    new_list1 = []
    new_list2 = []
    clauses = []
    for i in range(row * column * obs):
        if i >= row * column:
            if type(arr[2 + 8 * i]) == int:
                if arr[2 + 8 * i] > 0:
                    clauses.append([3 + 8 * i])
                    clauses.append([2 + 8 * i - row * column * 8])
            if type(arr[3 + 8 * i]) == int:
                if arr[3 + 8 * i] > 0:
                    clauses.append([4 + 8 * i])
                    clauses.append([3 + 8 * i - row * column * 8])
            if type(arr[1 + 8 * i]) == int:
                if arr[1 + 8 * i] > 0:
                    clauses.append([2 + 8 * i])
                    if i % column != 0 and i > 0:
                        list.append(2 + 8 * (i - 1) - row * column * 8)
                        list.append(3 + 8 * (i - 1) - row * column * 8)
                        list.append(4 + 8 * (i - 1) - row * column * 8)
                    if (i + 1) % column != 0:
                        list.append(2 + 8 * (i + 1) - row * column * 8)
                        list.append(3 + 8 * (i + 1) - row * column * 8)
                        list.append(4 + 8 * (i + 1) - row * column * 8)
                    if (i) % (column * row) > column:
                        list.append(2 + 8 * (i - column) - row * column * 8)
                        list.append(3 + 8 * (i - column) - row * column * 8)
                        list.append(4 + 8 * (i - column) - row * column * 8)
                    if (i+1) % (row*column) != 0:
                        list.append(2 + 8 * (i + column) - row * column * 8)
                        list.append(3 + 8 * (i + column) - row * column * 8)
                        list.append(4 + 8 * (i + column) - row * column * 8)
                    list2 = list.copy()
                    clauses.append(list2)
                    list.clear()
            if arr[1 + 8 * i] == "S":
                if i % column != 0 and i > 0:
                    list.append(2 + 8 * (i - 1) - row * column * 8)
                    list.append(3 + 8 * (i - 1) - row * column * 8)
                    list.append(4 + 8 * (i - 1) - row * column * 8)
                if (i + 1) % column != 0:
                    list.append(2 + 8 * (i + 1) - row * column * 8)
                    list.append(3 + 8 * (i + 1) - row * column * 8)
                    list.append(4 + 8 * (i + 1) - row * column * 8)
                if (i) % (column * row) > column:
                    list.append(2 + 8 * (i - column) - row * column * 8)
                    list.append(3 + 8 * (i - column) - row * column * 8)
                    list.append(4 + 8 * (i - column) - row * column * 8)
                if (i+1) % (row*column) != 0 and (i+1) % (row*column) < (row-1)*column:
                    list.append(2 + 8 * (i + column) - row * column * 8)
                    list.append(3 + 8 * (i + column) - row * column * 8)
                    list.append(4 + 8 * (i + column) - row * column * 8)
                list.append(-(2 + 8 * i))
                clauses.append([-(2 + 8 * i),1 + 8 * i - row * column * 8])
                list2 = list.copy()
                clauses.append(list2)
                list.clear()
        if arr[2 + 8 * i] == "S":
            new_list1.append(2 + 8 * i - row * column * 8)
            new_list1.append(-(3 + 8 * i))
            copy1 = new_list1.copy()
            clauses.append(copy1)
            new_list1.clear()
        if arr[3 + 8 * i] == "S":
            new_list2.append(3 + 8 * i - row * column * 8)
            new_list2.append(-(4 + 8 * i))
            copy2 = new_list2.copy()
            clauses.append(copy2)
            new_list2.clear()
    return clauses


def Q_condition(arr,row,column):
    clauses = []
    i = 4 + row * column * 8
    list1 = []
    list2 = []
    list3 = []
    while i < len(arr):
        if arr[i] == 'Q':
            list1.append(-(i+1))
            list1.append(i+1+1)
            list1.append(i + 1 - row * column * 8 - 1)
            list1.append(i + 1 - row * column * 8 - 2)
            list1.append(i + 1 - row * column * 8 - 3)
            copy1 = list1.copy()
            clauses.append(copy1)
            list1.clear()
            list2.append(-(i+1+1))
            list1.append(i+1)
            list1.append(i+1 - row * column * 8)
            copy2 = list1.copy()
            clauses.append(copy2)
            list2.clear()
        if type(arr[i]) == int:
            if arr[i] > 0:
                list3.append(i + 1 - row * column * 8 - 1)
                list3.append(i + 1 - row * column * 8 - 2)
                list3.append(i + 1 - row * column * 8 - 3)
                list3.append((i+1))
                copy3 = list3.copy()
                clauses.append(copy3)
                list3.clear()
                clauses.append(-(i+1))
        if type(arr[i+1]) == int:
            if arr[i+1] > 0:
                clauses.append(-(i+1+1))
                clauses.append(i+1 - row * column * 8)
        i = i + 8
    return clauses


def U_condition(arr,row,column):
    clauses = []
    list = []
    i = 7 + row * column * 8
    while i < len(arr):
        if type(arr[i]) == int:
            if arr[i] > 0:
                list.append(i+1)
                copy = list.copy()
                clauses.append(copy)
                list.clear()
                list.append(i+1 - row * column * 8)
                copy = list.copy()
                clauses.append(copy)
                list.clear()
        i = i + 8
    return clauses


def I_condition(arr,row,column):
    clauses = []
    list = []
    i = 6 + row * column * 8
    while i < len(arr):
        if type(arr[i]) == int:
            if arr[i] > 0:
                list.append(i+1 - row * column * 8-6)
                list.append(i+1 - row * column * 8)
                list.append(-(i+1))
                copy = list.copy()
                clauses.append(copy)
                list.clear()
        i = i + 8
    return clauses


def H_condition(arr, row,column):
    clauses = []
    list = []
    i = row * column * 8
    while i < len(arr):
        if type(arr[i]) == int:
            if arr[i] > 0:
                list.append(i+1 - row * column * 8)
                clauses.append([-(i + 1 - row * column * 8 + 7)])
                if i > row * column * 8 * 3:
                    list.append(i+1 - row * column * 8 + 3)
                else:
                   clauses.append([-(i + 1 - row * column * 8 + 3)])
                if i > row * column * 8 * 2:
                    list.append(i+1 - row * column * 8 + 5)
                else:
                   clauses.append([-(i + 1 - row * column * 8 + 5)])
                list.append(-(i+1))
                copy = list.copy()
                clauses.append(copy)
                list.clear()

        i = i + 8
    return clauses