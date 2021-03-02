from pysat.solvers import Solver
from sympy import symbols
from sympy.logic.boolalg import to_cnf, is_cnf, Equivalent, Implies
from itertools import chain, combinations


def powerset(iterable, limit):
    """powerset([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return list(chain.from_iterable(combinations(s, r) for r in range(limit+1)))[1:]


def constructor_of_db(map):  # Approach to an element by: db['status']['time']['row']['column']
    T = len(map)
    num_of_rows = len(map[0])
    num_of_columns = len(map[0][0])
    db = ()  # The status order is S, H, Q, U, I
    id = 1
    for _ in range(5):
        db_status = ()
        for t in range(T):
            matrix_tuple = ()
            for i in range(num_of_rows):
                row_tuple = ()
                for j in range(num_of_columns):
                    row_tuple += (id,)
                    id += 1
                matrix_tuple += ((row_tuple),)
            db_status += ((matrix_tuple),)
        db += ((db_status),)
    return db


def constructor_of_ops(map):  # Approach to an element by: db['operation']['time']['row']['column']
    T = len(map)
    num_of_rows = len(map[0])
    num_of_columns = len(map[0][0])
    db_ops = ()  # The operations order is recover, infect, H_noop, U_noop, S_noop, vac, quar, Q_noop, I_noop, end_of_Q
    id = 5*T*(num_of_rows)*(num_of_columns)+1  # Continues counting from the last id of db constructor
    for _ in range(10):
        db_status = ()
        for t in range(T):
            matrix_tuple = ()
            for i in range(num_of_rows):
                row_tuple = ()
                for j in range(num_of_columns):
                    row_tuple += (id,)
                    id += 1
                matrix_tuple += ((row_tuple),)
            db_status += ((matrix_tuple),)
        db_ops += ((db_status),)
    return db_ops


def initial_clause(db, db_ops, dic, sat_solver):  
    # The status order is S, H, Q, U, I
    # The operations order is recover, infect, H_noop, U_noop, S_noop, vac, quar, Q_noop, I_noop, end_of_Q
    maps = dic["observations"]
    maps_num = len(maps)
    row_num = len(maps[0])
    col_num = len(maps[0][0])
    police = dic["police"]
    medics = dic["medics"]

    for t in range(maps_num):
        for row in range(row_num):
            for col in range(col_num):
                if maps[t][row][col] == 'S':
                    sat_solver.add_clause([db[0][t][row][col]])
                    sat_solver.add_clause([-db[1][t][row][col]])
                    sat_solver.add_clause([-db[2][t][row][col]])
                    sat_solver.add_clause([-db[3][t][row][col]])
                    sat_solver.add_clause([-db[4][t][row][col]])
                    # Operations:
                    if police == 0:
                        sat_solver.add_clause([-db_ops[1][t][row][col]])
                        sat_solver.add_clause([-db_ops[2][t][row][col]])
                        sat_solver.add_clause([-db_ops[3][t][row][col]])
                        if maps_num >= 4:
                            temp_list = [db_ops[0][t][row][col],db_ops[4][t][row][col]]
                            for index in range(len(temp_list)):
                                temp_list[index] = symbols('{}'.format(temp_list[index]))

                            st = (temp_list[0] ^ temp_list[1])
                            st_output = sympy_to_pysat(st, True) 
                            for i in st_output:
                                sat_solver.add_clause(i)
                        else:
                            sat_solver.add_clause([-db_ops[0][t][row][col]])
                            sat_solver.add_clause([db_ops[4][t][row][col]])
                            sat_solver.add_clause([-db_ops[5][t][row][col]])
                            sat_solver.add_clause([-db_ops[6][t][row][col]])
                            sat_solver.add_clause([-db_ops[7][t][row][col]])
                            sat_solver.add_clause([-db_ops[8][t][row][col]])
                            sat_solver.add_clause([-db_ops[9][t][row][col]])
       
                    elif police > 0:
                        sat_solver.add_clause([-db_ops[1][t][row][col]])
                        sat_solver.add_clause([-db_ops[2][t][row][col]])
                        sat_solver.add_clause([-db_ops[3][t][row][col]])
                        sat_solver.add_clause([-db_ops[5][t][row][col]])
                        sat_solver.add_clause([-db_ops[7][t][row][col]])
                        sat_solver.add_clause([-db_ops[8][t][row][col]])
                        sat_solver.add_clause([-db_ops[9][t][row][col]])
                        if maps_num >= 4:
                            temp_list = [db_ops[0][t][row][col], db_ops[4][t][row][col], db_ops[6][t][row][col]]

                            sat_solver.add_clause(temp_list)
                            sat_solver.add_clause([-temp_list[0], -temp_list[1]])
                            sat_solver.add_clause([-temp_list[0], -temp_list[2]])
                            sat_solver.add_clause([-temp_list[1], -temp_list[2]])
                        else:
                            sat_solver.add_clause([-db_ops[0][t][row][col]])
                            temp_list = [db_ops[4][t][row][col], db_ops[6][t][row][col]]
                            for index in range(len(temp_list)):
                                temp_list[index] = symbols('{}'.format(temp_list[index]))

                            st = (temp_list[0] ^ temp_list[1])
                            st_output = sympy_to_pysat(st, True) 
                            for i in st_output:
                                sat_solver.add_clause(i)

                elif maps[t][row][col] == 'H':
                    sat_solver.add_clause([-db[0][t][row][col]])
                    sat_solver.add_clause([db[1][t][row][col]])
                    sat_solver.add_clause([-db[2][t][row][col]])
                    sat_solver.add_clause([-db[3][t][row][col]])
                    sat_solver.add_clause([-db[4][t][row][col]])
                    # Operations:
                    if medics == 0:
                        sat_solver.add_clause([-db_ops[0][t][row][col]])
                        sat_solver.add_clause([-db_ops[3][t][row][col]])
                        sat_solver.add_clause([-db_ops[4][t][row][col]])
                        sat_solver.add_clause([-db_ops[5][t][row][col]])
                        sat_solver.add_clause([-db_ops[6][t][row][col]])
                        sat_solver.add_clause([-db_ops[7][t][row][col]])
                        sat_solver.add_clause([-db_ops[8][t][row][col]])
                        sat_solver.add_clause([-db_ops[9][t][row][col]])
                        temp_list = [db_ops[1][t][row][col],db_ops[2][t][row][col]]
                        for index in range(len(temp_list)):
                            temp_list[index] = symbols('{}'.format(temp_list[index]))

                        st = (temp_list[0] ^ temp_list[1])
                        st_output = sympy_to_pysat(st, True) 
                        for i in st_output:
                            sat_solver.add_clause(i)
                    elif medics > 0:
                        sat_solver.add_clause([-db_ops[0][t][row][col]])
                        sat_solver.add_clause([-db_ops[3][t][row][col]])
                        sat_solver.add_clause([-db_ops[4][t][row][col]])
                        sat_solver.add_clause([-db_ops[6][t][row][col]])
                        sat_solver.add_clause([-db_ops[7][t][row][col]])
                        sat_solver.add_clause([-db_ops[8][t][row][col]])
                        sat_solver.add_clause([-db_ops[9][t][row][col]])
                        temp_list = [db_ops[1][t][row][col], db_ops[2][t][row][col], db_ops[5][t][row][col]]

                        sat_solver.add_clause(temp_list)
                        sat_solver.add_clause([-temp_list[0], -temp_list[1]])
                        sat_solver.add_clause([-temp_list[0], -temp_list[2]])
                        sat_solver.add_clause([-temp_list[1], -temp_list[2]])

                elif maps[t][row][col] == 'Q':
                    sat_solver.add_clause([-db[0][t][row][col]])
                    sat_solver.add_clause([-db[1][t][row][col]])
                    sat_solver.add_clause([db[2][t][row][col]])
                    sat_solver.add_clause([-db[3][t][row][col]])
                    sat_solver.add_clause([-db[4][t][row][col]])
                    # Operations:
                    sat_solver.add_clause([-db_ops[0][t][row][col]])
                    sat_solver.add_clause([-db_ops[1][t][row][col]])
                    sat_solver.add_clause([-db_ops[2][t][row][col]])
                    sat_solver.add_clause([-db_ops[3][t][row][col]])
                    sat_solver.add_clause([-db_ops[4][t][row][col]])
                    sat_solver.add_clause([-db_ops[5][t][row][col]])
                    sat_solver.add_clause([-db_ops[6][t][row][col]])
                    sat_solver.add_clause([-db_ops[8][t][row][col]])
                    temp_list = [db_ops[7][t][row][col],db_ops[9][t][row][col]]
                    for index in range(len(temp_list)):
                        temp_list[index] = symbols('{}'.format(temp_list[index]))

                    st = (temp_list[0] ^ temp_list[1])
                    st_output = sympy_to_pysat(st, True) 
                    for i in st_output:
                        sat_solver.add_clause(i)

                elif maps[t][row][col] == 'U':
                    sat_solver.add_clause([-db[0][t][row][col]])
                    sat_solver.add_clause([-db[1][t][row][col]])
                    sat_solver.add_clause([-db[2][t][row][col]])
                    sat_solver.add_clause([db[3][t][row][col]])
                    sat_solver.add_clause([-db[4][t][row][col]])
                    # Operations: only U_noOp and NOT all the rest
                    sat_solver.add_clause([-db_ops[0][t][row][col]])
                    sat_solver.add_clause([-db_ops[1][t][row][col]])
                    sat_solver.add_clause([-db_ops[2][t][row][col]])
                    sat_solver.add_clause([db_ops[3][t][row][col]])
                    sat_solver.add_clause([-db_ops[4][t][row][col]])
                    sat_solver.add_clause([-db_ops[5][t][row][col]])
                    sat_solver.add_clause([-db_ops[6][t][row][col]])
                    sat_solver.add_clause([-db_ops[7][t][row][col]])
                    sat_solver.add_clause([-db_ops[8][t][row][col]])
                    sat_solver.add_clause([-db_ops[9][t][row][col]])
                    
                elif maps[t][row][col] == 'I':
                    sat_solver.add_clause([-db[0][t][row][col]])
                    sat_solver.add_clause([-db[1][t][row][col]])
                    sat_solver.add_clause([-db[2][t][row][col]])
                    sat_solver.add_clause([-db[3][t][row][col]])
                    sat_solver.add_clause([db[4][t][row][col]])
                    # Operations: only I_noOp and NOT all the rest
                    sat_solver.add_clause([-db_ops[0][t][row][col]])
                    sat_solver.add_clause([-db_ops[1][t][row][col]])
                    sat_solver.add_clause([-db_ops[2][t][row][col]])
                    sat_solver.add_clause([-db_ops[3][t][row][col]])
                    sat_solver.add_clause([-db_ops[4][t][row][col]])
                    sat_solver.add_clause([-db_ops[5][t][row][col]])
                    sat_solver.add_clause([-db_ops[6][t][row][col]])
                    sat_solver.add_clause([-db_ops[7][t][row][col]])
                    sat_solver.add_clause([db_ops[8][t][row][col]])
                    sat_solver.add_clause([-db_ops[9][t][row][col]])

                elif maps[t][row][col] == '?':  # For each time and location insert "?" as (some state) and ~(other states) for each state
                    temp_list = [db[0][t][row][col],db[1][t][row][col],db[2][t][row][col],db[3][t][row][col],db[4][t][row][col]]
                    temp_op_list = [db_ops[0][t][row][col],db_ops[1][t][row][col],db_ops[2][t][row][col],db_ops[3][t][row][col],db_ops[4][t][row][col]] 
                    # Operations:
                    if medics + police == 0:
                        sat_solver.add_clause(temp_op_list)
                        sat_solver.add_clause([-db_ops[0][t][row][col],-db_ops[1][t][row][col]])
                        sat_solver.add_clause([-db_ops[0][t][row][col],-db_ops[2][t][row][col]])
                        sat_solver.add_clause([-db_ops[0][t][row][col],-db_ops[3][t][row][col]])
                        sat_solver.add_clause([-db_ops[0][t][row][col],-db_ops[4][t][row][col]])
                        sat_solver.add_clause([-db_ops[1][t][row][col],-db_ops[2][t][row][col]])
                        sat_solver.add_clause([-db_ops[1][t][row][col],-db_ops[3][t][row][col]])
                        sat_solver.add_clause([-db_ops[1][t][row][col],-db_ops[4][t][row][col]])
                        sat_solver.add_clause([-db_ops[2][t][row][col],-db_ops[3][t][row][col]])
                        sat_solver.add_clause([-db_ops[2][t][row][col],-db_ops[4][t][row][col]])
                        sat_solver.add_clause([-db_ops[3][t][row][col],-db_ops[4][t][row][col]])
                    if medics + police > 0:
                        teams_temp_op_list = [db_ops[0][t][row][col],db_ops[1][t][row][col],db_ops[2][t][row][col],db_ops[3][t][row][col],db_ops[4][t][row][col],db_ops[5][t][row][col],db_ops[6][t][row][col],db_ops[7][t][row][col],db_ops[8][t][row][col],db_ops[9][t][row][col]]
                        sat_solver.add_clause(teams_temp_op_list)
                        c = 0
                        for one in teams_temp_op_list:
                            c += 1
                            for two in teams_temp_op_list[c:]:
                                sat_solver.add_clause([-one,-two])
                    
                    if t == maps_num-1:  # if U_t >> U forever (U_t-1 <> U_t)
                        U_temp_list = [db[3][t-1][row][col],db[3][t][row][col]]
                        for U_index in range(len(U_temp_list)):
                            U_temp_list[U_index] = symbols('{}'.format(U_temp_list[U_index]))

                        U_st = Equivalent(U_temp_list[0], U_temp_list[1])

                        U_st_output = sympy_to_pysat(U_st, True) 
                        for U_i in U_st_output:
                            sat_solver.add_clause(U_i) 
                    if t < maps_num-1:  # if U_t >> U forever (U_t <> U_t+1)
                        U_temp_list = [db[3][t][row][col],db[3][t+1][row][col]]
                        for U_index in range(len(U_temp_list)):
                            U_temp_list[U_index] = symbols('{}'.format(U_temp_list[U_index]))

                        U_st = Equivalent(U_temp_list[0], U_temp_list[1])

                        U_st_output = sympy_to_pysat(U_st, True) 
                        for U_i in U_st_output:
                            sat_solver.add_clause(U_i) 
                    
                     #status:
                    if t != 0:
                        sat_solver.add_clause(temp_list)
                        sat_solver.add_clause([-db[0][t][row][col],-db[1][t][row][col]])
                        sat_solver.add_clause([-db[0][t][row][col],-db[2][t][row][col]])
                        sat_solver.add_clause([-db[0][t][row][col],-db[3][t][row][col]])
                        sat_solver.add_clause([-db[0][t][row][col],-db[4][t][row][col]])
                        sat_solver.add_clause([-db[1][t][row][col],-db[2][t][row][col]])
                        sat_solver.add_clause([-db[1][t][row][col],-db[3][t][row][col]])
                        sat_solver.add_clause([-db[1][t][row][col],-db[4][t][row][col]])
                        sat_solver.add_clause([-db[2][t][row][col],-db[3][t][row][col]])
                        sat_solver.add_clause([-db[2][t][row][col],-db[4][t][row][col]])
                        sat_solver.add_clause([-db[3][t][row][col],-db[4][t][row][col]])
                    if t == 0:
                        sat_solver.add_clause([-db[4][t][row][col]])
                        sat_solver.add_clause([-db[2][t][row][col]])
                        sat_solver.add_clause([db[1][t][row][col],db[3][t][row][col],db[0][t][row][col]])
                        sat_solver.add_clause([-db[0][t][row][col],-db[1][t][row][col]])
                        sat_solver.add_clause([-db[0][t][row][col],-db[3][t][row][col]])
                        sat_solver.add_clause([-db[1][t][row][col],-db[3][t][row][col]])


def operations(db, db_ops, dic, sat_solver):
    # The status order is S, H, Q, U, I
    # The operations order is recover, infect, H_noop, U_noop, S_noop
    maps = dic["observations"]
    maps_num = len(maps)
    row_num = len(maps[0])
    col_num = len(maps[0][0])
    false_literal = 15*(maps_num)*(row_num)*(col_num) + 1
    
    for t in range(maps_num-1):
        for row in range(row_num):
            for col in range(col_num):
                    # S_noop & recover:
                    if maps_num <= 3:  # Just S_noop
                        S_temp_list = []  # [S_t, S_t+1, S_noop]
                        S_temp_list.append(db[0][t][row][col])
                        S_temp_list.append(db[0][t+1][row][col])
                        S_temp_list.append(db_ops[4][t][row][col])
                        for S_index in range(len(S_temp_list)):
                            S_temp_list[S_index] = symbols('{}'.format(S_temp_list[S_index]))
                        
                        S_st = Equivalent((S_temp_list[0] & S_temp_list[1]), S_temp_list[2])
                        S_st_output = sympy_to_pysat(S_st, True) 
                        for S_i in S_st_output:
                            sat_solver.add_clause(S_i)
                    else:
                        if t+3 < maps_num:
                            S_temp_list = []  # [S_t, S_t+1, S_t+2, S_t+3, H_t+3, recover_t+2, S_noop_t+2]
                            S_temp_list.append(db[0][t][row][col])
                            S_temp_list.append(db[0][t+1][row][col])
                            S_temp_list.append(db[0][t+2][row][col])
                            S_temp_list.append(db[0][t+3][row][col])
                            S_temp_list.append(db[1][t+3][row][col])
                            S_temp_list.append(db_ops[0][t+2][row][col])
                            S_temp_list.append(db_ops[4][t+2][row][col])
                            for S_index in range(len(S_temp_list)):
                                S_temp_list[S_index] = symbols('{}'.format(S_temp_list[S_index]))

                            S_first_st = Equivalent((S_temp_list[0] & S_temp_list[1] & S_temp_list[2]), S_temp_list[5])
                            S_second_st = Equivalent((S_temp_list[2] & S_temp_list[4]), S_temp_list[5])
                            S_third_st = Equivalent((S_temp_list[2] & S_temp_list[3]), S_temp_list[6])
                            S_st_list = [S_first_st, S_second_st, S_third_st]
                            for S_st in S_st_list:
                                S_st_output = sympy_to_pysat(S_st, True)
                                for S_i in S_st_output:
                                    sat_solver.add_clause(S_i)
                    
                    # H_noop & infect:
                    H_temp_list = []  # [S_row+1, S_row-1, S_col+1, S_col-1, H_t, H_t+1, S_t+1, infect, H_noop]
                    if row+1 == row_num:
                        H_temp_list.append(false_literal)
                    else: H_temp_list.append(db[0][t][row+1][col])  # Sick neighbor at previous time
                    if row-1 < 0:
                        H_temp_list.append(false_literal)
                    else: H_temp_list.append(db[0][t][row-1][col]) 
                    if col+1 == col_num:
                        H_temp_list.append(false_literal)
                    else: H_temp_list.append(db[0][t][row][col+1]) 
                    if col-1 < 0:
                        H_temp_list.append(false_literal)
                    else: H_temp_list.append(db[0][t][row][col-1])
                    sat_solver.add_clause([-false_literal])
                    
                    H_temp_list.append(db[1][t][row][col])
                    H_temp_list.append(db[1][t+1][row][col])
                    H_temp_list.append(db[0][t+1][row][col])
                    H_temp_list.append(db_ops[1][t][row][col])
                    H_temp_list.append(db_ops[2][t][row][col])
                    
                    for H_index in range(len(H_temp_list)):
                        H_temp_list[H_index] = symbols('{}'.format(H_temp_list[H_index]))
                    
                    H_first_st = Equivalent(((H_temp_list[0] | H_temp_list[1] | H_temp_list[2] | H_temp_list[3]) & H_temp_list[4]), H_temp_list[7])
                    H_second_st = Equivalent((H_temp_list[4] & H_temp_list[6]), H_temp_list[7])
                    H_third_st = Equivalent((H_temp_list[4] & H_temp_list[5]), H_temp_list[8])
                    H_st_list = [H_first_st, H_second_st, H_third_st]
                    for H_st in H_st_list:
                        H_st_output = sympy_to_pysat(H_st, True)
                        for H_i in H_st_output:
                            sat_solver.add_clause(H_i)
                    
                    # U_noop:
                    U_temp_list = [db[3][t][row][col], db[3][t+1][row][col], db_ops[3][t][row][col]]
                    for U_index in range(len(U_temp_list)):
                        U_temp_list[U_index] = symbols('{}'.format(U_temp_list[U_index]))
                        
                    U_st = Equivalent((U_temp_list[0] & U_temp_list[1]),U_temp_list[2])
                    st_output = sympy_to_pysat(U_st, True) 
                    for U_i in st_output:
                        sat_solver.add_clause(U_i)


def teams_operations(db, db_ops, dic, sat_solver):
    # The status order is S, H, Q, U, I
    # The operations order is recover, infect, H_noop, U_noop, S_noop, vac, quar, Q_noop, I_noop, end_of_Q
    maps = dic["observations"]
    police = dic["police"]
    medics = dic["medics"]
    maps_num = len(maps)
    row_num = len(maps[0])
    col_num = len(maps[0][0])
    false_literal = 15*(maps_num)*(row_num)*(col_num) + 2
    
    for t in range(maps_num-1):
        for row in range(row_num):
            for col in range(col_num):
                # vac & I_noop
                if t+1 < maps_num and medics > 0:  # At least 2 maps
                    I_temp_list = []  # [H_t, vac_t, I_t+1, I_noop_t+1, I_t+2, I_t, I_noop_t]
                    I_temp_list.append(db[1][t][row][col])
                    I_temp_list.append(db_ops[5][t][row][col])
                    I_temp_list.append(db[4][t+1][row][col])
                    for I_index in range(len(I_temp_list)):
                        I_temp_list[I_index] = symbols('{}'.format(I_temp_list[I_index]))
                        
                    I_first_st = Equivalent((I_temp_list[0] & I_temp_list[2]), I_temp_list[1])
                    I_st_list = [I_first_st]
                    if t+2 < maps_num:  # At least 3 maps
                        I_temp_list.append(db_ops[8][t+1][row][col])
                        I_temp_list.append(db[4][t+2][row][col])
                        for I_index in range(3,len(I_temp_list)):
                            I_temp_list[I_index] = symbols('{}'.format(I_temp_list[I_index]))
                            
                        I_second_st = Equivalent((I_temp_list[2] & I_temp_list[4]), I_temp_list[3])
                        I_st_list.append(I_second_st)
                        if t+3 < maps_num:  # At least 4 maps
                            I_temp_list.append(db[4][t][row][col])
                            I_temp_list.append(db_ops[8][t][row][col])
                            for I_index in range(5,len(I_temp_list)):
                                I_temp_list[I_index] = symbols('{}'.format(I_temp_list[I_index]))
                            
                            I_third_st = Equivalent((I_temp_list[5] & I_temp_list[2]),I_temp_list[6])
                            I_st_list.append(I_third_st)
                            I_forth_st = Equivalent(I_temp_list[6], I_temp_list[3])
                            I_st_list.append(I_forth_st)
                    
                    for I_st in I_st_list:
                        I_st_output = sympy_to_pysat(I_st, True)
                        for I_i in I_st_output:
                            sat_solver.add_clause(I_i)
                            
                
                # quar & Q_noop & end_of_Q
                if t+1 < maps_num and police > 0:  # At least 2 maps
                    Q_temp_list = []  # [S_t, quar_t, Q_t+1, Q_noop_t+1, Q_t+2, end_of_Q_t+2 , H_t+3]
                    Q_temp_list.append(db[0][t][row][col])
                    Q_temp_list.append(db_ops[6][t][row][col])
                    Q_temp_list.append(db[2][t+1][row][col])
                    for Q_index in range(len(Q_temp_list)):
                        Q_temp_list[Q_index] = symbols('{}'.format(Q_temp_list[Q_index]))
                    
                    Q_first_st = Equivalent((Q_temp_list[0] & Q_temp_list[2]), Q_temp_list[1])
                    Q_st_list = [Q_first_st]
                    if t+2 < maps_num:  # At least 3 maps
                        Q_temp_list.append(db_ops[7][t+1][row][col])
                        Q_temp_list.append(db[2][t+2][row][col])

                        for Q_index in range(3,len(Q_temp_list)):
                            Q_temp_list[Q_index] = symbols('{}'.format(Q_temp_list[Q_index]))
                        
                        Q_second_st = Equivalent((Q_temp_list[2] & Q_temp_list[4]), Q_temp_list[3])
                        Q_st_list.append(Q_second_st)
                        Q_third_st = Equivalent(Q_temp_list[1], Q_temp_list[3])
                        Q_st_list.append(Q_third_st)

                        if t+3 < maps_num:  # At least 4 maps
                            Q_temp_list.append(db_ops[9][t+2][row][col])
                            Q_temp_list.append(db[1][t+3][row][col])
                            
                            for Q_index in range(5,len(Q_temp_list)):
                                Q_temp_list[Q_index] = symbols('{}'.format(Q_temp_list[Q_index]))
                            
                            Q_forth_st = Equivalent((Q_temp_list[2] & Q_temp_list[4]), Q_temp_list[5])
                            Q_st_list.append(Q_forth_st)
                            Q_fifth_st = Equivalent((Q_temp_list[4] & Q_temp_list[6]), Q_temp_list[5])
                            Q_st_list.append(Q_fifth_st)
                            Q_six_st = Equivalent(Q_temp_list[3], Q_temp_list[5])
                            Q_st_list.append(Q_six_st)
                    
                    for Q_st in Q_st_list:
                        Q_st_output = sympy_to_pysat(Q_st, True)
                        for Q_i in Q_st_output:
                            sat_solver.add_clause(Q_i)
                
                # S_noop & recover:
                if maps_num <= 3:  # Just S_noop
                    S_temp_list = []  # [S_t, S_t+1, S_noop]
                    S_temp_list.append(db[0][t][row][col])
                    S_temp_list.append(db[0][t+1][row][col])
                    S_temp_list.append(db_ops[4][t][row][col])
                    for S_index in range(len(S_temp_list)):
                        S_temp_list[S_index] = symbols('{}'.format(S_temp_list[S_index]))

                    S_st = Equivalent((S_temp_list[0] & S_temp_list[1]), S_temp_list[2])
                    S_st_output = sympy_to_pysat(S_st, True) 
                    for S_i in S_st_output:
                        sat_solver.add_clause(S_i)
                else:
                    if t+3 < maps_num:
                        S_temp_list = []  # [S_t, S_t+1, S_t+2, S_t+3, H_t+3, recover_t+2, S_noop_t+2]
                        S_temp_list.append(db[0][t][row][col])
                        S_temp_list.append(db[0][t+1][row][col])
                        S_temp_list.append(db[0][t+2][row][col])
                        S_temp_list.append(db[0][t+3][row][col])
                        S_temp_list.append(db[1][t+3][row][col])
                        S_temp_list.append(db_ops[0][t+2][row][col])
                        S_temp_list.append(db_ops[4][t+2][row][col])
                        for S_index in range(len(S_temp_list)):
                            S_temp_list[S_index] = symbols('{}'.format(S_temp_list[S_index]))

                        S_first_st = Equivalent((S_temp_list[0] & S_temp_list[1] & S_temp_list[2]), S_temp_list[5])
                        S_second_st = Equivalent((S_temp_list[2] & S_temp_list[4]), S_temp_list[5])
                        S_third_st = Equivalent((S_temp_list[2] & S_temp_list[3]), S_temp_list[6])
                        S_st_list = [S_first_st, S_second_st, S_third_st]
                        for S_st in S_st_list:
                            S_st_output = sympy_to_pysat(S_st, True)
                            for S_i in S_st_output:
                                sat_solver.add_clause(S_i)
                    
                # H_noop & infect:
                H_temp_list = []  # [S_row+1, S_row-1, S_col+1, S_col-1, H_t, H_t+1, S_t+1, infect, H_noop]
                if row+1 == row_num:
                    H_temp_list.append(false_literal)
                else: H_temp_list.append(db[0][t][row+1][col])  # Sick neighbor at previous time
                if row-1 < 0:
                    H_temp_list.append(false_literal)
                else: H_temp_list.append(db[0][t][row-1][col]) 
                if col+1 == col_num:
                    H_temp_list.append(false_literal)
                else: H_temp_list.append(db[0][t][row][col+1]) 
                if col-1 < 0:
                    H_temp_list.append(false_literal)
                else: H_temp_list.append(db[0][t][row][col-1])
                sat_solver.add_clause([-false_literal])

                H_temp_list.append(db[1][t][row][col])
                H_temp_list.append(db[1][t+1][row][col])
                H_temp_list.append(db[0][t+1][row][col])
                H_temp_list.append(db_ops[1][t][row][col])
                H_temp_list.append(db_ops[2][t][row][col])

                for H_index in range(len(H_temp_list)):
                    H_temp_list[H_index] = symbols('{}'.format(H_temp_list[H_index]))
                    
                H_first_st = Equivalent(((H_temp_list[0] | H_temp_list[1] | H_temp_list[2] | H_temp_list[3]) & H_temp_list[4]), H_temp_list[7])
                H_second_st = Equivalent((H_temp_list[4] & H_temp_list[6]), H_temp_list[7])
                H_third_st = Equivalent((H_temp_list[4] & H_temp_list[5]), H_temp_list[8])
                H_st_list = [H_first_st, H_second_st, H_third_st]
                for H_st in H_st_list:
                    H_st_output = sympy_to_pysat(H_st, True)
                    for H_i in H_st_output:
                        sat_solver.add_clause(H_i)
                    
                # U_noop:
                U_temp_list = [db[3][t][row][col], db[3][t+1][row][col], db_ops[3][t][row][col]]
                for U_index in range(len(U_temp_list)):
                    U_temp_list[U_index] = symbols('{}'.format(U_temp_list[U_index]))

                U_st = Equivalent((U_temp_list[0] & U_temp_list[1]),U_temp_list[2])
                st_output = sympy_to_pysat(U_st, True) 
                for U_i in st_output:
                    sat_solver.add_clause(U_i)


def quarantine(db_ops, dic, sat_solver): # for each map we choose |police| "S" or "?" and exxecute quar_t
    maps = dic["observations"]
    maps_num = len(maps)
    row_num = len(maps[0])
    col_num = len(maps[0][0])
    police = dic["police"]

    list_of_quar = []
    if police > 0:
        for t in range(maps_num-1):
            for row in range(row_num):
                for col in range(col_num):
                    if maps[t][row][col] == 'S' or maps[t][row][col] == '?':  # The status order is S, H, Q, U, I
                        list_of_quar.append(db_ops[6][t][row][col])
            
            len_list = len(list_of_quar)
            if police > len_list:  # If we have more sick than medics, relate the police as its the exact sumber of sick
                 police = len_list
            
            if police == 1:
                sat_solver.add_clause(list_of_quar)
                c = 0
                for one in list_of_quar:
                    c += 1
                    for two in list_of_quar[c:]:
                        sat_solver.add_clause([-one,-two])        
                    
            elif police > 1:        
                for index in range(len_list):
                    list_of_quar[index] = symbols('{}'.format(list_of_quar[index]))

                # Now we have to mix all these optional actions, bounded by size of |police|
                Qaction_powerset_output = powerset(list_of_quar, police)

                Qoperations_powerset = [] #this list include the possible operations, by the exact size, cnfed
                for operation in Qaction_powerset_output: #operation = set of possible actions to take in a turn
                    if len(operation) == police: #make the Qaction_powerset_list only possible set of actions
                        operation_statement = operation[0]
                        for action in operation[1:]:
                            operation_statement = (operation_statement) & (action)

                        for obj in list_of_quar:
                            if obj not in operation:
                                operation_statement = (operation_statement) & ~(obj)

                        Qoperations_powerset.append(to_cnf(operation_statement))

                j = 0
                long_or = Qoperations_powerset[0]
                for one in Qoperations_powerset:
                    j += 1
                    if j < len(Qoperations_powerset):
                        long_or = (long_or) | (Qoperations_powerset[j])
                    for two in Qoperations_powerset[j:]:
                        or_st = ~(one) | ~(two)
                        temp_list_1 = sympy_to_pysat(or_st, True) 
                        for i in temp_list_1:
                            sat_solver.add_clause(i)
                temp_list_2 = sympy_to_pysat(long_or, True)
                for i in temp_list_2:
                    sat_solver.add_clause(i)

#                 long_or = Qoperations_powerset[0]
#                 for element in Qoperations_powerset[1:]:
#                     long_or = (long_or) | (element)
#                 temp_list_2 = sympy_to_pysat(long_or, True)
#                 for i in temp_list_2:
#                     sat_solver.add_clause(i)


def immune(db_ops, dic, sat_solver): # for each map we choose |medics| "H" or "?" and exxecute quar_t
    maps = dic["observations"]
    maps_num = len(maps)
    row_num = len(maps[0])
    col_num = len(maps[0][0])
    medics = dic["medics"]
    list_of_vac = [] #everywhere that could be vaccinated
    if medics > 0:
        for t in range(maps_num-1):
            for row in range(row_num):
                for col in range(col_num):
                    if maps[t][row][col] == 'H' or maps[t][row][col] == '?':  # The status order is S, H, Q, U, I
                        list_of_vac.append(db_ops[5][t][row][col])
                        
            len_list = len(list_of_vac)
            if medics > len_list:  # If we have more H than medics, relate the medics as its the exact sumber of H
                 medics = len_list

            if medics == 1:
                sat_solver.add_clause(list_of_vac)
                c = 0
                for one in list_of_vac:
                    c += 1
                    for two in list_of_vac[c:]:
                        sat_solver.add_clause([-one,-two])
            elif medics > 1:
                for index in range(len_list):
                    list_of_vac[index] = symbols('{}'.format(list_of_vac[index]))


                # Now we have to mix all these optional actions, bounded by size of |medics|
                Iaction_powerset_output = powerset(list_of_vac, medics) 
                Ioperations_powerset = [] #this list include the possible operations, by the exact size, cnfed
                
                for operation in Iaction_powerset_output: #operation = set of possible actions to take in a turn
                    if len(operation) == medics: #make the Iaction_powerset_list only possible set of actions
                        operation_statement = operation[0]
                        for action in operation[1:]:
                            operation_statement = (operation_statement) & (action)

                        for obj in list_of_vac:
                            if obj not in operation:
                                operation_statement = (operation_statement) & ~(obj)

                        if len(list_of_vac) > 8:
                            bool_val = False
                        else: bool_val = True
                        
                        Ioperations_powerset.append(to_cnf(operation_statement, simplify= bool_val, force= bool_val))

                j = 0
                long_or = Ioperations_powerset[0]
                for one in Ioperations_powerset:
                    j += 1
                    if j < len(Ioperations_powerset):
                        long_or = (long_or) | (Ioperations_powerset[j])
                    for two in Ioperations_powerset[j:]:
                        or_st = ~(one) | ~(two)
                        temp_list_1 = sympy_to_pysat(or_st, False) 
                        for i in temp_list_1:
                            sat_solver.add_clause(i)

                temp_list_2 = sympy_to_pysat(long_or, True)
                for i in temp_list_2:
                    sat_solver.add_clause(i)
                            
#                 long_or = Ioperations_powerset[0]
#                 for element in Ioperations_powerset[1:]:
#                     long_or = (long_or) | (element)
#                 temp_list_2 = sympy_to_pysat(long_or, True)
#                 for i in temp_list_2:
#                     sat_solver.add_clause(i)


def sympy_to_pysat(statement, bool_val):
    cnf_s = to_cnf(statement, simplify=bool_val, force= bool_val)

    cnf_args = cnf_s.args
    and_clause = []
    for arg in cnf_args:
        str_arg = str(arg)
        str_arg_splited = str_arg.split(" | ")
        or_clause = []
        for symbol in str_arg_splited:
            if "~" in symbol:
                or_clause.append(-int(symbol[1:]))  
            else: or_clause.append(int(symbol))

        and_clause.append(or_clause)
    
    return and_clause


def extract_literal(query,db):  # recieves a tuple of data and extracts its literal-id from the right db. (f: tuple -> int)
    status = query[2]  # The status order is S, H, Q, U, I
    if status == 'S':
        status = 0
    elif status == 'H':
        status = 1
    elif status == 'Q':
        status = 2
    elif status == 'U':
        status = 3
    elif status == 'I':
        status = 4
    time = query[1]
    row = query[0][0]
    column = query[0][1]
    return db[status][time][row][column]


def extract_other_literals(query,db):
    time = query[1]
    row = query[0][0]
    column = query[0][1]
    status = query[2]  # The status order is S, H, Q, U, I
    if status == 'S':
        other_literal_list = [db[1][time][row][column], db[2][time][row][column], db[3][time][row][column], db[4][time][row][column]]
    elif status == 'H':
        other_literal_list = [db[0][time][row][column], db[2][time][row][column], db[3][time][row][column], db[4][time][row][column]]
    elif status == 'Q':
        other_literal_list = [db[0][time][row][column], db[1][time][row][column], db[3][time][row][column], db[4][time][row][column]]
    elif status == 'U':
        other_literal_list = [db[0][time][row][column], db[1][time][row][column], db[2][time][row][column], db[4][time][row][column]]
    elif status == 'I':
        other_literal_list = [db[0][time][row][column], db[1][time][row][column], db[2][time][row][column], db[3][time][row][column]]
    
    return other_literal_list


ids = ['312360431', '307868208']
def solve_problem(input):
    
    sat_solver = Solver(name='g4')
    db = constructor_of_db(input["observations"])
    db_ops = constructor_of_ops(input["observations"])
    initial_clause(db, db_ops, input, sat_solver)
    if input["police"] + input["medics"] == 0:
        operations(db, db_ops, input, sat_solver)
    else:
        teams_operations(db, db_ops, input, sat_solver)
        quarantine(db_ops, input, sat_solver)
        immune(db_ops, input, sat_solver)
    queries = input["queries"]
    ans_dic = {}
    for query in queries:
        literal = extract_literal(query,db)
        ans = sat_solver.solve(assumptions = [literal])
        
        if ans:
            other_literal_list = extract_other_literals(query,db)
            ans_list = []
            for other_literal in other_literal_list:
                ans_list.append(sat_solver.solve(assumptions = [other_literal]))
            if sum(ans_list) >= 1:
                ans = '?'
            else: ans = 'T'
        else: 
            ans = 'F'
        ans_dic["{}".format(query)] = "{}".format(ans)
    
    for key, value in ans_dic.items():
        print("{}".format(key),":","'{}'".format(value))