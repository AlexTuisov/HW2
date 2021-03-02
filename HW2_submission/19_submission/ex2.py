ids = ['206202731']
from sympy import *
from pysat.solvers import Glucose3

def states_ids(observations):
    num_observations = len(observations)
    length_row = len(observations[0])
    length_column = len(observations[0][0])
    state_id = 3
    data_base = ()
    for _ in range(5):  # Order of status: S,H,U,I,Q
        map_ = ()
        for t in range(num_observations):
            matrix_t = ()
            for i in range(length_row):
                tuple_row = ()
                for j in range(length_column):
                    tuple_row += (state_id,)
                    state_id += 1
                matrix_t += ((tuple_row,))
            map_ += ((matrix_t,))
        data_base +=((map_,))
    return data_base

def sympy_to_cnf_pysat(statement, sat_solver):  # change sympy to cnf and pysat
    cnf_s = to_cnf(statement, simplify=False)
    str_cnf_s = str(cnf_s)
    cnf_args = cnf_s.args
    and_clause = []
    #print("before", cnf_s)
    if "&" in str_cnf_s:  # if more than one or_clause
        for arg in cnf_args:
            str_arg = str(arg)
            str_arg_splited = str_arg.split(" | ")
            or_clause = []
            for symbol in str_arg_splited:
                if "~" in symbol:
                    or_clause.append(int(-int(symbol[1:])))
                else:
                    or_clause.append(int(symbol))
            and_clause.append(or_clause)
        #print("after_&", and_clause)

    else:  # if just one clause
        or_clause = []
        for arg in cnf_args:
            str_arg = str(arg)
            if "~" in str_arg:
                or_clause.append(int(-int(str_arg[1:])))
            else:
                or_clause.append(int(str_arg))
        and_clause.append(or_clause)
        #print("after_|", and_clause)

    for clause in and_clause:
        #print("add", clause)
        sat_solver.add_clause(clause)

def one_sympy_to_pysat(statement, sat_solver):  # if there is just one argument
    str_arg = str(statement)
    if "~" in str_arg:
        sat_solver.add_clause([int(-int(str_arg[1:]))])
    else:
        sat_solver.add_clause([int(str_arg)])


def one_police(t, db, states_Q_I, sat_solver, num_S, num_Q, max_Q, observations):
    # polices == 1=> no more than one Qurentie acttion in each turn t
    # medics == 1=> no more than one Immune acttion in each turn t
    num_of_observations = len(observations)
    len_states_Q = len(states_Q_I)
    there_is_S = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
    there_is_Q_next_turn = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
    next_turn_Q = 0
    if t+1 < num_of_observations:
        for s1 in range(len_states_Q):
            s1_i, s1_j = int(states_Q_I[s1][0]), int(states_Q_I[s1][1])
            if observations[t + 1][s1_i][s1_j] == "Q":
                next_turn_Q += 1
    if num_Q == max_Q:  # if num_Q == max_Q => ALL TEAMS USED proparely
        for s1 in range(len_states_Q):
            s1_i, s1_j = int(states_Q_I[s1][0]), int(states_Q_I[s1][1])
            if t == 0:  # at t ==0 there is no I on the board !
                e = ~symbols(str(db[4][0][s1_i][s1_j]))  # ~expr('Q' + str(state_s1) + str(t))
                one_sympy_to_pysat(e, sat_solver)
            elif observations[t][s1_i][s1_j] != "Q":
                e = ~symbols(str(db[4][t][s1_i][s1_j]))  # there is enough Q
                one_sympy_to_pysat(e, sat_solver)
            if next_turn_Q != (max_Q + 1) and (t + 1 < num_of_observations):
                there_is_S |= symbols(str(db[0][t][s1_i][s1_j]))
                there_is_Q_next_turn |= (symbols(str(db[4][t + 1][s1_i][s1_j])) & symbols(str(db[0][t][s1_i][s1_j])))
            # if t>0 there is a new Qurentie, that wasnt there before
        if next_turn_Q != (max_Q + 1) and (t + 1 < num_of_observations):
            if num_S >= 1:
                e = there_is_Q_next_turn
                sympy_to_cnf_pysat(e, sat_solver)
            else:
                e = ~there_is_S | there_is_Q_next_turn  # there_is_S => there_is_Q_next_turn
                sympy_to_cnf_pysat(e, sat_solver)

    else:
        for s1 in range(len_states_Q):
            s1_i, s1_j = int(states_Q_I[s1][0]), int(states_Q_I[s1][1])
            if t > 0:
                for s2 in range(s1 + 1, len_states_Q):
                    s2_i, s2_j = int(states_Q_I[s2][0]), int(states_Q_I[s2][1])
                    e = ~(symbols(str(db[0][t - 1][s1_i][s1_j])) & symbols(str(db[4][t][s1_i][s1_j]))) | \
                        ~(symbols(str(db[0][t - 1][s2_i][s2_j])) & symbols(str(db[4][t][s2_i][s2_j])))
                    sympy_to_cnf_pysat(e, sat_solver)
                    # ~expr('Q' + str(states_Q_S[s1]) + str(t)) | ~expr('Q' + str(states_Q_S[s2]) + str(t))
            # police == 1 & there_is_S in turn t=> at least one Qurentie acttion Will be activated in turn t+1
            if t == 0:  # at t ==0 there is no Q and I on the board !
                e = ~symbols(str(db[4][0][s1_i][s1_j]))  # ~expr('Q' + str(state_s1) + str(t))
                one_sympy_to_pysat(e, sat_solver)
            if next_turn_Q != (max_Q + 1) and (t + 1 < num_of_observations):
                there_is_S |= symbols(str(db[0][t][s1_i][s1_j]))
                there_is_Q_next_turn |= (symbols(str(db[4][t + 1][s1_i][s1_j])) & symbols(str(db[0][t][s1_i][s1_j])))
            # if t>0 there is a new Qurentie, that wasnt there before
        if next_turn_Q != (max_Q + 1) and (t + 1 < num_of_observations):
            if num_S >= 1:
                e = there_is_Q_next_turn
                sympy_to_cnf_pysat(e, sat_solver)
            else:
                e = ~there_is_S | there_is_Q_next_turn  # there_is_S => there_is_Q_next_turn
                sympy_to_cnf_pysat(e, sat_solver)

def one_medics(t, db, states_Q_I, sat_solver, num_H, num_I, max_I, observations):
    num_of_observations = len(observations)
    len_states_Q = len(states_Q_I)
    there_is_H = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
    there_is_I_next_turn = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
    next_turn_I = 0
    if t+1 < num_of_observations:
        for s1 in range(len_states_Q):
            s1_i, s1_j = int(states_Q_I[s1][0]), int(states_Q_I[s1][1])
            if observations[t + 1][s1_i][s1_j] == "I":
                next_turn_I += 1
    if num_I == max_I:  # if num_I == max_I => ALL TEAMS USED proparely
        for s1 in range(len_states_Q):
            s1_i, s1_j = int(states_Q_I[s1][0]), int(states_Q_I[s1][1])
            if t == 0:  # at t ==0 there is no I on the board !
                e = ~symbols(str(db[3][0][s1_i][s1_j]))  # ~expr('I' + str(state_s1) + str(t))
                one_sympy_to_pysat(e, sat_solver)
            elif observations[t][s1_i][s1_j] != "I":
                e = ~symbols(str(db[3][t][s1_i][s1_j]))  # there is enough I
                one_sympy_to_pysat(e, sat_solver)
            if next_turn_I != (max_I + 1) and (t + 1 < num_of_observations):
                there_is_H |= symbols(str(db[1][t][s1_i][s1_j]))
                there_is_I_next_turn |= (symbols(str(db[3][t + 1][s1_i][s1_j])) & symbols(str(db[1][t][s1_i][s1_j])))
            # if t>0 there is a new Qurentie, that wasnt there before
        if (next_turn_I != (max_I + 1)) and (t + 1 < num_of_observations):
            if num_H >= 1:
                e = there_is_I_next_turn
                sympy_to_cnf_pysat(e, sat_solver)
            else:
                e = ~there_is_H | there_is_I_next_turn  # there_is_H => there_is_I_next_turn
                sympy_to_cnf_pysat(e, sat_solver)

    else:
        for s1 in range(len_states_Q):
            s1_i, s1_j = int(states_Q_I[s1][0]), int(states_Q_I[s1][1])
            if t > 0:
                for s2 in range(s1 + 1, len_states_Q):
                    s2_i, s2_j = int(states_Q_I[s2][0]), int(states_Q_I[s2][1])
                    e = ~(symbols(str(db[1][t - 1][s1_i][s1_j])) & symbols(str(db[3][t][s1_i][s1_j]))) | \
                        ~(symbols(str(db[1][t - 1][s2_i][s2_j])) & symbols(str(db[3][t][s2_i][s2_j])))
                    sympy_to_cnf_pysat(e, sat_solver)
                    # ~expr('Q' + str(states_Q_S[s1]) + str(t)) | ~expr('Q' + str(states_Q_S[s2]) + str(t))
            # police == 1 & there_is_S in turn t=> at least one Qurentie acttion Will be activated in turn t+1
            # medics == 1 & there_is_H in turn t=> at least one Imune acttion Will be activated in turn t+1
            if t == 0:  # at t ==0 there is no Q and I on the board !
                e = ~symbols(str(db[3][0][s1_i][s1_j]))  # ~expr('I' + str(state_s1) + str(t))
                one_sympy_to_pysat(e, sat_solver)
            if (next_turn_I != (max_I + 1)) and (t + 1 < num_of_observations):
                there_is_H |= symbols(str(db[1][t][s1_i][s1_j]))
                there_is_I_next_turn |= (symbols(str(db[3][t + 1][s1_i][s1_j])) & symbols(str(db[1][t][s1_i][s1_j])))
            # if t>0 there is a new Qurentie, that wasnt there before
        if (next_turn_I != (max_I + 1)) and (t + 1 < num_of_observations):
            if num_H >= 1:
                e = there_is_I_next_turn
                sympy_to_cnf_pysat(e, sat_solver)
            else:
                e = ~there_is_H | there_is_I_next_turn  # there_is_H => there_is_I_next_turn
                sympy_to_cnf_pysat(e, sat_solver)

def two_polices(t, db, states_Q_I, sat_solver, num_S, num_Q, max_Q, observations):
    num_of_observations = len(observations)
    len_states_Q = len(states_Q_I)
    there_is_one_S = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
    there_is_one_Q_next_turn = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
    there_is_two_S = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
    there_is_two_Q_next_turn = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
    next_turn_Q = 0
    if t + 1 < num_of_observations:
        for s1 in range(len_states_Q):
            s1_i, s1_j = int(states_Q_I[s1][0]), int(states_Q_I[s1][1])
            if observations[t + 1][s1_i][s1_j] == "Q":
                next_turn_Q += 1
    if num_Q == max_Q:  # if num_Q == max_Q => ALL TEAMS USED proparely
        for s1 in range(len_states_Q):
            s1_i, s1_j = int(states_Q_I[s1][0]), int(states_Q_I[s1][1])
            if t == 0:  # at t ==0 there is no I on the board !
                e = ~symbols(str(db[4][0][s1_i][s1_j]))  # ~expr('Q' + str(state_s1) + str(t))
                one_sympy_to_pysat(e, sat_solver)
            elif observations[t][s1_i][s1_j] != "Q":
                e = ~symbols(str(db[4][t][s1_i][s1_j]))  # there is enough Q
                one_sympy_to_pysat(e, sat_solver)
            if next_turn_Q != (max_Q + 2) and (t + 1 < num_of_observations):
                for s2 in range(s1 + 1, len_states_Q):
                    s2_i, s2_j = int(states_Q_I[s2][0]), int(states_Q_I[s2][1])
                    there_is_two_S |= (symbols(str(db[0][t][s1_i][s1_j])) & symbols(str(db[0][t][s2_i][s2_j])))
                    there_is_two_Q_next_turn |= (symbols(str(db[4][t + 1][s1_i][s1_j])) &
                                                 symbols(str(db[4][t + 1][s2_i][s2_j])) &
                                                 symbols(str(db[0][t][s1_i][s1_j])) &
                                                 symbols(str(db[0][t][s2_i][s2_j])))
            if next_turn_Q != (max_Q + 2) and (t + 1 < num_of_observations):
                there_is_one_S |= symbols(str(db[0][t][s1_i][s1_j]))
                there_is_one_Q_next_turn |= (
                            symbols(str(db[4][t + 1][s1_i][s1_j])) & symbols(str(db[0][t][s1_i][s1_j])))
            # if t>0 there is a new Qurentie, that wasnt there before
        if next_turn_Q != (max_Q + 2) and (t + 1 < num_of_observations):
            if num_S >= 2:
                e = there_is_two_Q_next_turn
                sympy_to_cnf_pysat(e, sat_solver)
            elif num_S == 1:  # at least one Q , and if 2 S => at least 2 Q
                e = there_is_one_Q_next_turn
                sympy_to_cnf_pysat(e, sat_solver)
                e1 = ~there_is_two_S | there_is_two_Q_next_turn
                sympy_to_cnf_pysat(e1, sat_solver)
            else:
                e1 = ~there_is_two_S | there_is_two_Q_next_turn
                e2 = ~there_is_one_S | there_is_one_Q_next_turn  # there_is_S => there_is_Q_next_turn
                sympy_to_cnf_pysat(e1, sat_solver)
                sympy_to_cnf_pysat(e2, sat_solver)

    else:
        for s1 in range(len_states_Q):
            s1_i, s1_j = int(states_Q_I[s1][0]), int(states_Q_I[s1][1])
            for s2 in range(s1 + 1, len_states_Q):
                s2_i, s2_j = int(states_Q_I[s2][0]), int(states_Q_I[s2][1])
                for s3 in range(s2 + 1, len_states_Q):
                    s3_i, s3_j = int(states_Q_I[s3][0]), int(states_Q_I[s3][1])
                    if t > 0:
                        e = ((symbols(str(db[0][t - 1][s1_i][s1_j])) & symbols(str(db[4][t][s1_i][s1_j]))) & \
                             (symbols(str(db[0][t - 1][s2_i][s2_j])) & symbols(str(db[4][t][s2_i][s2_j])))) >> \
                            (symbols(str(db[0][t - 1][s3_i][s3_j])) & symbols(str(db[4][t][s3_i][s3_j])))
                        sympy_to_cnf_pysat(e, sat_solver)
                if next_turn_Q != (max_Q + 2) and (t + 1 < num_of_observations):  # if there is at least two S => at least two Q
                    there_is_two_S |= (symbols(str(db[0][t][s1_i][s1_j])) & symbols(str(db[0][t][s2_i][s2_j])))
                    there_is_two_Q_next_turn |= (symbols(str(db[4][t + 1][s1_i][s1_j])) &
                                                 symbols(str(db[4][t + 1][s2_i][s2_j])) &
                                                 symbols(str(db[0][t][s1_i][s1_j])) &
                                                 symbols(str(db[0][t][s2_i][s2_j])))
            # police == 1 & there_is_S in turn t=> at least one Qurentie acttion Will be activated in turn t+1
            if t == 0:  # at t ==0 there is no Q and I on the board !
                e = ~symbols(str(db[4][0][s1_i][s1_j]))  # ~expr('Q' + str(state_s1) + str(t))
                one_sympy_to_pysat(e, sat_solver)
            if next_turn_Q != (max_Q + 2) and (t + 1 < num_of_observations):
                there_is_one_S |= symbols(str(db[0][t][s1_i][s1_j]))
                there_is_one_Q_next_turn |= (
                            symbols(str(db[4][t + 1][s1_i][s1_j])) & symbols(str(db[0][t][s1_i][s1_j])))
            # if t>0 there is a new Qurentie, that wasnt there before
        if next_turn_Q != (max_Q + 2) and (t + 1 < num_of_observations):
            if num_S >= 2:
                e = there_is_two_Q_next_turn
                sympy_to_cnf_pysat(e, sat_solver)
            elif num_S == 1:  # at least one Q , and if 2 S => at least 2 Q
                e = there_is_one_Q_next_turn
                sympy_to_cnf_pysat(e, sat_solver)
                e1 = ~there_is_two_S | there_is_two_Q_next_turn
                sympy_to_cnf_pysat(e1, sat_solver)
            else:
                e1 = ~there_is_two_S | there_is_two_Q_next_turn
                e2 = ~there_is_one_S | there_is_one_Q_next_turn  # there_is_S => there_is_Q_next_turn
                sympy_to_cnf_pysat(e1, sat_solver)
                sympy_to_cnf_pysat(e2, sat_solver)


def two_medics(t, db, states_Q_I, sat_solver, num_H, num_I, max_I, observations):
    num_of_observations = len(observations)
    len_states_Q = len(states_Q_I)
    there_is_one_H = symbols(str(2)) & ~symbols(str(2))
    there_is_one_I_next_turn = symbols(str(2)) & ~symbols(str(2))
    there_is_two_H = symbols(str(2)) & ~symbols(str(2))
    there_is_two_I_next_turn = symbols(str(2)) & ~symbols(str(2))
    next_turn_I = 0
    if t + 1 < num_of_observations:
        for s1 in range(len_states_Q):
            s1_i, s1_j = int(states_Q_I[s1][0]), int(states_Q_I[s1][1])
            if observations[t + 1][s1_i][s1_j] == "I":
                next_turn_I += 1
    if num_I == max_I:  # if num_I == max_I => ALL TEAMS USED proparely
        for s1 in range(len_states_Q):
            s1_i, s1_j = int(states_Q_I[s1][0]), int(states_Q_I[s1][1])
            if t == 0:  # at t ==0 there is no I on the board !
                e = ~symbols(str(db[3][0][s1_i][s1_j]))  # ~expr('I' + str(state_s1) + str(t))
                one_sympy_to_pysat(e, sat_solver)
            elif observations[t][s1_i][s1_j] != "I":
                e = ~symbols(str(db[3][t][s1_i][s1_j]))  # there is enough I
                one_sympy_to_pysat(e, sat_solver)
            if (next_turn_I != (max_I + 2)) and (t + 1 < num_of_observations):  # if at least two H => at least two I
                for s2 in range(s1 + 1, len_states_Q):
                    s2_i, s2_j = int(states_Q_I[s2][0]), int(states_Q_I[s2][1])
                    there_is_two_H |= (symbols(str(db[1][t][s1_i][s1_j])) & symbols(str(db[1][t][s2_i][s2_j])))
                    there_is_two_I_next_turn |= (symbols(str(db[3][t + 1][s1_i][s1_j])) &
                                                 symbols(str(db[3][t + 1][s2_i][s2_j])) &
                                                 symbols(str(db[1][t][s1_i][s1_j])) &
                                                 symbols(str(db[1][t][s2_i][s2_j])))
            if (next_turn_I != (max_I + 2)) and (t + 1 < num_of_observations):
                there_is_one_H |= symbols(str(db[1][t][s1_i][s1_j]))
                there_is_one_I_next_turn |= (
                            symbols(str(db[3][t + 1][s1_i][s1_j])) & symbols(str(db[1][t][s1_i][s1_j])))
        if (next_turn_I != (max_I + 2)) and (t + 1 < num_of_observations):
            if num_H >= 2:
                e = there_is_two_I_next_turn
                sympy_to_cnf_pysat(e, sat_solver)
            elif num_H == 1:  # at least one Q , and if 2 S => at least 2 Q
                e = there_is_one_I_next_turn
                sympy_to_cnf_pysat(e, sat_solver)
                e1 = ~there_is_two_H | there_is_two_I_next_turn
                sympy_to_cnf_pysat(e1, sat_solver)
            else:
                e1 = ~there_is_two_H | there_is_two_I_next_turn
                e2 = ~there_is_one_H | there_is_one_I_next_turn  # there_is_S => there_is_Q_next_turn
                sympy_to_cnf_pysat(e1, sat_solver)
                sympy_to_cnf_pysat(e2, sat_solver)

    else:
        for s1 in range(len_states_Q):
            s1_i, s1_j = int(states_Q_I[s1][0]), int(states_Q_I[s1][1])
            for s2 in range(s1 + 1, len_states_Q):
                s2_i, s2_j = int(states_Q_I[s2][0]), int(states_Q_I[s2][1])
                for s3 in range(s2 + 1, len_states_Q):
                    s3_i, s3_j = int(states_Q_I[s3][0]), int(states_Q_I[s3][1])
                    if t > 0:
                        e = ((symbols(str(db[1][t - 1][s1_i][s1_j])) & symbols(str(db[3][t][s1_i][s1_j]))) & \
                             (symbols(str(db[1][t - 1][s2_i][s2_j])) & symbols(str(db[3][t][s2_i][s2_j])))) >> \
                            (symbols(str(db[1][t - 1][s3_i][s3_j])) & symbols(str(db[3][t][s3_i][s3_j])))
                        sympy_to_cnf_pysat(e, sat_solver)
                if (next_turn_I != (max_I + 2)) and (t + 1 < num_of_observations):
                    there_is_two_H |= (symbols(str(db[1][t][s1_i][s1_j])) & symbols(str(db[1][t][s2_i][s2_j])))
                    there_is_two_I_next_turn |= (symbols(str(db[3][t + 1][s1_i][s1_j])) &
                                                 symbols(str(db[3][t + 1][s2_i][s2_j])) &
                                                 symbols(str(db[1][t][s1_i][s1_j])) &
                                                 symbols(str(db[1][t][s2_i][s2_j])))
            if t == 0:  # at t ==0 there is no Q and I on the board !
                e = ~symbols(str(db[3][0][s1_i][s1_j]))  # ~expr('I' + str(state_s1) + str(t))
                one_sympy_to_pysat(e, sat_solver)
            if (next_turn_I != (max_I + 2)) and (t + 1 < num_of_observations):
                there_is_one_H |= symbols(str(db[1][t][s1_i][s1_j]))
                there_is_one_I_next_turn |= (
                            symbols(str(db[3][t + 1][s1_i][s1_j])) & symbols(str(db[1][t][s1_i][s1_j])))
        if (next_turn_I != (max_I + 2)) and (t + 1 < num_of_observations):
            if num_H >= 2:
                e = there_is_two_I_next_turn
                sympy_to_cnf_pysat(e, sat_solver)
            elif num_H == 1:  # at least one Q , and if 2 S => at least 2 Q
                e = there_is_one_I_next_turn
                sympy_to_cnf_pysat(e, sat_solver)
                e1 = ~there_is_two_H | there_is_two_I_next_turn
                sympy_to_cnf_pysat(e1, sat_solver)
            else:
                e1 = ~there_is_two_H | there_is_two_I_next_turn
                e2 = ~there_is_one_H | there_is_one_I_next_turn  # there_is_S => there_is_Q_next_turn
                sympy_to_cnf_pysat(e1, sat_solver)
                sympy_to_cnf_pysat(e2, sat_solver)



def solve_problem(input):
    polices = input["police"]
    medics = input["medics"]
    observations = input["observations"]
    queries = input["queries"]
    num_of_observations = len(observations)
    length_row = len(observations[0])
    length_column = len(observations[0][0])
    db = states_ids(observations)
    sat_solver = Glucose3()

    if polices == 0 and medics == 0:
        #kb_not_filled = True
        states = ('H', 'S', 'U')
        for t in range(num_of_observations):
            for i in range(length_row):
                for j in range(length_column):
                    for s1 in range(3):
                        for s2 in range(s1+1, 3):
                            e = ~symbols(str(db[s1][t][i][j])) | ~symbols(str(db[s2][t][i][j]))
                            sympy_to_cnf_pysat(e, sat_solver)

        for t in range(num_of_observations):
            for i in range(length_row):
                for j in range(length_column):
                    if observations[t][i][j] == "U":  # => this cell was before and will stay until the end 'U'
                        for t1 in range(num_of_observations):  # for all t!!(even before, different from 'I')
                            one_sympy_to_pysat(symbols(str(db[2][t1][i][j])), sat_solver)
                            # sympy_to_cnf_pysat(symbols(str(db[2][t1][i][j])), sat_solver)  # 'U' + str(i) + str(j) + str(t1)

                    elif observations[t][i][j] == "S":
                        one_sympy_to_pysat(symbols(str(db[0][t][i][j])), sat_solver)
                        # sympy_to_cnf_pysat(symbols(str(db[0][t][i][j])), sat_solver)  # 'S' + str(i) + str(j) + str(t)

                    elif observations[t][i][j] == "H":
                        one_sympy_to_pysat(symbols(str(db[1][t][i][j])), sat_solver)
                        # sympy_to_cnf_pysat(symbols(str(db[1][t][i][j])), sat_solver)  # 'H' + str(i) + str(j) + str(t)

                        there_is_a_neighbor_S = False
                        there_is_unknown_neighbor = False  # == if there is a neighbor '?'
                        if j != 0:  # checking neighbor from left
                            if observations[t][i][j - 1] == "S":
                                there_is_a_neighbor_S = True
                            elif observations[t][i][j - 1] == "?":
                                there_is_unknown_neighbor = True
                        if j != len(observations[t][0]) - 1:  # checking neighbor from right
                            if observations[t][i][j + 1] == "S":
                                there_is_a_neighbor_S = True
                            elif observations[t][i][j + 1] == "?":
                                there_is_unknown_neighbor = True
                        if i != 0:  # checking neighbor from up
                            if observations[t][i - 1][j] == "S":
                                there_is_a_neighbor_S = True
                            elif observations[t][i - 1][j] == "?":
                                there_is_unknown_neighbor = True
                        if i != len(observations[t]) - 1:  # checking neighbor from down
                            if observations[t][i + 1][j] == "S":
                                there_is_a_neighbor_S = True
                            elif observations[t][i + 1][j] == "?":
                                there_is_unknown_neighbor = True

                        if (not there_is_a_neighbor_S) and t+1 < num_of_observations:
                            if not there_is_unknown_neighbor:
                                # == if there is not neighbor S or ?: next time(at t+1) this cell will stay H
                                e = symbols(str(db[1][t + 1][i][j]))  # 'H' + str(i) + str(j) + str(t + 1)
                                one_sympy_to_pysat(e, sat_solver)
                            else:  # == if there is not neighbor S but yes ?:
                                # this cell will be or H or S(for 3 turns and then H)
                                e = symbols(str(db[1][t + 1][i][j])) | symbols(str(db[0][t + 1][i][j]))
                                sympy_to_cnf_pysat(e, sat_solver)
                                # (expr('H' + str(i) + str(j) + str(t + 1)) |(expr('S' + str(i) + str(j) + str(t + 1)) &
                                # expr('S' + str(i) + str(j) + str(t + 2))& expr('S' + str(i) + str(j) + str(t + 3)) &
                                # expr('H' + str(i) + str(j) + str(t + 4))))


                    # if observations[t][i][j] == "U" => this cell will always be U
                    is_U = symbols(str(db[2][t][i][j]))  # expr('U' + str(i) + str(j) + str(t))
                    exp_result = symbols(str(db[2][0][i][j]))   # expr('U' + str(i) + str(j) + str(0))
                    for t1 in range(1, num_of_observations):
                        exp_result &= symbols(str(db[2][t1][i][j]))  # expr('U' + str(i) + str(j) + str(t1))
                    e = ~is_U | exp_result  # is_U => exp_result
                    sympy_to_cnf_pysat(e, sat_solver)

                    is_S = symbols(str(db[0][t][i][j]))  # expr('S' + str(i) + str(j) + str(t))
                    is_H = symbols(str(db[1][t][i][j]))  # expr('H' + str(i) + str(j) + str(t))
                    if t+1 < num_of_observations:
                        # 1.if its H and there_is_a_neighbor_S => from t+1 until t+3 this cell will become to be S,
                        #  and at t+4 will return to be H
                        has_neighbor_s = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
                        if j != 0:  # checking neighbor from left
                            has_neighbor_s |= symbols(
                                str(db[0][t][i][j - 1]))  # expr('S' + str(i) + str(j - 1) + str(t))
                        if j != len(observations[t][0]) - 1:  # checking neighbor from right
                            has_neighbor_s |= symbols(
                                str(db[0][t][i][j + 1]))  # expr('S' + str(i) + str(j + 1) + str(t))
                        if i != 0:  # checking neighbor from up
                            has_neighbor_s |= symbols(
                                str(db[0][t][i - 1][j]))  # expr('S' + str(i - 1) + str(j) + str(t))
                        if i != len(observations[t]) - 1:  # checking neighbor from down
                            has_neighbor_s |= symbols(
                                str(db[0][t][i + 1][j]))  # expr('S' + str(i + 1) + str(j) + str(t))

                        exp_result = symbols(str(db[0][t + 1][i][j]))
                        if t+2 < num_of_observations:
                            exp_result &= symbols(str(db[0][t + 2][i][j]))
                        if t+3 < num_of_observations:
                            exp_result &= symbols(str(db[0][t + 3][i][j]))
                        if t+4 < num_of_observations:
                            exp_result &= symbols(str(db[1][t + 4][i][j]))
                        # (expr('S' + str(i) + str(j) + str(t + 1)) & expr('S' + str(i) + str(j) + str(t + 2))
                        # & expr('S' + str(i) + str(j) + str(t + 3)) & expr('H' + str(i) + str(j) + str(t + 4)))
                        # (a & b) => c =in cnf= (~a|~b|c)
                        e = (~is_H | ~has_neighbor_s | exp_result)
                        sympy_to_cnf_pysat(e, sat_solver)

                        # if observations[t][i][j] == "S" => stay S from t -> until t+2 , at t+=3 become H
                        # (if t==0, or observations[t - 1][i][j] == "H")
                        stay_S_become_H = symbols(str(db[0][t + 1][i][j]))
                        if t+2 < num_of_observations:
                            stay_S_become_H &= symbols(str(db[0][t + 2][i][j]))
                        if t+3 < num_of_observations:
                            stay_S_become_H &= symbols(str(db[1][t + 3][i][j]))
                        # expr('S' + str(i) + str(j) + str(t + 1)) & expr('S' + str(i) + str(j) + str(t + 2)) & expr('H' + str(i) + str(j) + str(t + 3))
                        if t == 0:  # it will stay S for 3 turns, and then become to H
                            e = ~is_S | stay_S_become_H  # is_S in t==0 => stay_S_become_H
                            sympy_to_cnf_pysat(e, sat_solver)
                        else:  # if t>=1
                            was_H = symbols(str(db[1][t - 1][i][j]))  # expr('H' + str(i) + str(j) + str(t - 1))
                            e = ~is_S | ~was_H | stay_S_become_H  # if it was H and & now it is S => stay_S_become_H
                            sympy_to_cnf_pysat(e, sat_solver)

                    if t > 0:
                        was_H = symbols(str(db[1][t - 1][i][j]))  # expr('H' + str(i) + str(j) + str(t - 1))
                        was_S = symbols(str(db[0][t - 1][i][j]))  # expr('S' + str(i) + str(j) + str(t - 1))
                        # this cell was H at t-1 (and at t-2 if t==2) OR if t>=3 it was S at t-1 & t-2 & t-3:
                        before_H = symbols(str(db[1][t-1][i][j])) # expr('H' + str(i) + str(j) + str(t - 1))
                        if t == 2:  # this cell must to be H before 2 turns-
                            #  Because 2 turns will not be enough time to change from S to H (need at last 3)
                            before_H &= symbols(str(db[1][t-2][i][j]))  # expr('H' + str(i) + str(j) + str(t - 2))
                        if t >= 3:
                            before_H |= (symbols(str(db[0][t-1][i][j])) & symbols(str(db[0][t-2][i][j])) &
                                         symbols(str(db[0][t-3][i][j])))
                                #(expr('S' + str(i) + str(j) + str(t - 1)) & expr('S' + str(i) + str(j) + str(t - 2))
                                 #        & expr('S' + str(i) + str(j) + str(t - 3)))

                        e = (~is_H | before_H)  # is_H => before_H
                        sympy_to_cnf_pysat(e, sat_solver)

                        # if it is t<=2 or it was before H too => *no* one of his neighbors was S at t-1
                        no_neighbor_S = symbols(str(1))
                        if j != 0:  # checking neighbor from left
                            no_neighbor_S &= ~symbols(str(db[0][t-1][i][j-1]))  # ~expr('S' + str(i) + str(j - 1) + str(t - 1))
                            if t == 2:  # no S neighbors 2 turns before, because this cell must be H before 2 turns
                                no_neighbor_S &= ~symbols(str(db[0][t-2][i][j-1]))  # ~expr('S' + str(i) + str(j - 1) + str(t - 2))
                        if j != len(observations[t][0]) - 1:  # checking neighbor from right
                            no_neighbor_S &= ~symbols(str(db[0][t-1][i][j+1]))  # ~expr('S' + str(i) + str(j + 1) + str(t - 1))
                            if t == 2:
                                no_neighbor_S &= ~symbols(str(db[0][t-2][i][j+1])) # ~expr('S' + str(i) + str(j + 1) + str(t - 2))
                        if i != 0:  # checking neighbor from up
                            no_neighbor_S &= ~symbols(str(db[0][t-1][i-1][j])) # ~expr('S' + str(i - 1) + str(j) + str(t - 1))
                            if t == 2:
                                no_neighbor_S &= ~symbols(str(db[0][t-2][i-1][j]))  # ~expr('S' + str(i - 1) + str(j) + str(t - 2))
                        if i != len(observations[t]) - 1:  # checking neighbor from down
                            no_neighbor_S &= ~symbols(str(db[0][t-1][i+1][j]))  # ~expr('S' + str(i + 1) + str(j) + str(t - 1))
                            if t == 2:
                                no_neighbor_S &= ~symbols(str(db[0][t-2][i+1][j]))  # ~expr('S' + str(i + 1) + str(j) + str(t - 2))

                        if t <= 2:
                            e = ~is_H | no_neighbor_S  # is_H => no_neighbor_S
                            sympy_to_cnf_pysat(e, sat_solver)
                        is_H_before = symbols(str(db[1][t-1][i][j])) # expr('H' + str(i) + str(j) + str(t - 1))
                        e = ~is_H | ~is_H_before | no_neighbor_S  # (is_H & is_H_before) => no_neighbor_S
                        sympy_to_cnf_pysat(e, sat_solver)


                        # t>=1: this cell was S at t-1 OR (was_H and at least one of its neighbors was S at t-1):
                        had_neighbor_s = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
                        if j != 0:  # checking neighbor from left
                            had_neighbor_s |= symbols(
                                str(db[0][t - 1][i][j - 1]))  # expr('S' + str(i) + str(j - 1) + str(t - 1))
                        if j != len(observations[t][0]) - 1:  # checking neighbor from right
                            had_neighbor_s |= symbols(
                                str(db[0][t - 1][i][j + 1]))  # expr('S' + str(i) + str(j + 1) + str(t - 1))
                        if i != 0:  # checking neighbor from up
                            had_neighbor_s |= symbols(
                                str(db[0][t - 1][i - 1][j]))  # expr('S' + str(i - 1) + str(j) + str(t - 1))
                        if i != len(observations[t]) - 1:  # checking neighbor from down
                            had_neighbor_s |= symbols(
                                str(db[0][t - 1][i + 1][j]))  # expr('S' + str(i + 1) + str(j) + str(t - 1))
                        # is_S => it was_S | was_H at t-1 & (at at least one of its neighbors was S at t-1)
                        e = is_S >> (was_S | (was_H & had_neighbor_s))
                        sympy_to_cnf_pysat(e, sat_solver)


    elif polices == 0 and medics == 1:
        #kb_not_filled = True
        states = ('H', 'S', 'U', 'I')
        for t in range(num_of_observations):
            states_I_H = ()
            for i in range(length_row):
                for j in range(length_column):
                    states_I_H += ((str(i), str(j)),)
                    for s1 in range(4):
                        for s2 in range(s1+1, 4):
                            e = ~symbols(str(db[s1][t][i][j])) | ~symbols(str(db[s2][t][i][j]))
                            sympy_to_cnf_pysat(e, sat_solver)

        # General rules
        max_I = -1
        for t in range(num_of_observations):
            num_H = 0
            num_I = 0
            max_I += 1  # at t=0 -> max_I ==0, at t=1 => max_I =1 .....
            for i in range(length_row):
                for j in range(length_column):
                    if observations[t][i][j] == "U":  # => this cell was before and will stay until the end 'U'
                        one_sympy_to_pysat(symbols(str(db[2][t][i][j])), sat_solver)
                        #KB &= symbols(str(db[2][t][i][j])) # expr('U' + str(i) + str(j) + str(t))

                    if observations[t][i][j] == "I":  # => this cell will stay 'I' from now until the end
                        one_sympy_to_pysat(symbols(str(db[3][t][i][j])), sat_solver)
                        #KB &= symbols(str(db[3][t][i][j]))  # expr('I' + str(i) + str(j) + str(t))
                        num_I += 1

                    if observations[t][i][j] == "S":
                        one_sympy_to_pysat(symbols(str(db[0][t][i][j])), sat_solver)
                        #KB &= symbols(str(db[0][t][i][j]))  # expr('S' + str(i) + str(j) + str(t))

                    if observations[t][i][j] == "H":
                        one_sympy_to_pysat(symbols(str(db[1][t][i][j])), sat_solver)
                        #KB &= symbols(str(db[1][t][i][j]))  # expr('H' + str(i) + str(j) + str(t))
                        num_H += 1

                        there_is_a_neighbor_S = False
                        there_is_unknown_neighbor = False  # == if there is a neighbor '?'
                        if j != 0:  # checking neighbor from left
                            if observations[t][i][j - 1] == "S":
                                there_is_a_neighbor_S = True
                            elif observations[t][i][j - 1] == "?":
                                there_is_unknown_neighbor = True
                        if j != len(observations[t][0]) - 1:  # checking neighbor from right
                            if observations[t][i][j + 1] == "S":
                                there_is_a_neighbor_S = True
                            elif observations[t][i][j + 1] == "?":
                                there_is_unknown_neighbor = True
                        if i != 0:  # checking neighbor from up
                            if observations[t][i - 1][j] == "S":
                                there_is_a_neighbor_S = True
                            elif observations[t][i - 1][j] == "?":
                                there_is_unknown_neighbor = True
                        if i != len(observations[t]) - 1:  # checking neighbor from down
                            if observations[t][i + 1][j] == "S":
                                there_is_a_neighbor_S = True
                            elif observations[t][i + 1][j] == "?":
                                there_is_unknown_neighbor = True

                        if (not there_is_a_neighbor_S) and t + 1 < num_of_observations:
                            if not there_is_unknown_neighbor:
                                # == if there is not neighbor S or ?: next time(at t+1) this cell will stay H or become I
                                e = symbols(str(db[1][t + 1][i][j])) | symbols(str(db[3][t + 1][i][j]))
                                sympy_to_cnf_pysat(e, sat_solver)
                                # KB &= (symbols(str(db[1][t+1][i][j])) | symbols(str(db[3][t+1][i][j])))
                                # expr('H' + str(i) + str(j) + str(t + 1)) | expr('I' + str(i) + str(j) + str(t + 1))
                            else:
                                # == if no neighbor S but yes ? => this cell will be or H or I or S(for 3 turns and then H)
                                e = symbols(str(db[1][t + 1][i][j])) | symbols(str(db[3][t + 1][i][j]))
                                become_S = symbols(str(db[0][t + 1][i][j]))
                                if t + 2 < num_of_observations:
                                    become_S &= symbols(str(db[0][t + 2][i][j]))
                                if t + 3 < num_of_observations:
                                    become_S &= symbols(str(db[0][t + 3][i][j]))
                                if t + 4 < num_of_observations:
                                    become_S &= symbols(str(db[1][t + 4][i][j]))
                                sympy_to_cnf_pysat(e | become_S, sat_solver)
                                # (expr('H' + str(i) + str(j) + str(t + 1)) | expr('I' + str(i) + str(j) + str(t + 1)) |
                                # (expr('S' + str(i) + str(j) + str(t + 1)) & expr('S' + str(i) + str(j) + str(t + 2))
                                # & expr('S' + str(i) + str(j) + str(t + 3)) & expr('H' + str(i) + str(j) + str(t + 4))))


                    # if observations[t][i][j] == "U" => this cell will always be U
                    is_U = symbols(str(db[2][t][i][j]))  # expr('U' + str(i) + str(j) + str(t))
                    exp_result = symbols(str(db[2][0][i][j]))  # expr('U' + str(i) + str(j) + str(0))
                    for t1 in range(1, num_of_observations):
                        exp_result &= symbols(str(db[2][t1][i][j]))  # expr('U' + str(i) + str(j) + str(t1))
                    e = ~is_U | exp_result  # is_U => exp_result
                    sympy_to_cnf_pysat(e, sat_solver)

                    #if observations[t][i][j] == "I" => this cell will stay 'I' from now until the end
                    is_I = symbols(str(db[3][t][i][j])) # expr('I' + str(i) + str(j) + str(t))
                    if t+1 < num_of_observations:
                        exp_result = symbols(str(db[3][t + 1][i][j]))  # expr('I' + str(i) + str(j) + str(t+1))
                        for t1 in range(t + 2, num_of_observations):
                            exp_result &= symbols(str(db[3][t1][i][j]))  # expr('I' + str(i) + str(j) + str(t1))
                        e = ~is_I | exp_result  # is_I => exp_result
                        sympy_to_cnf_pysat(e, sat_solver)

                    # if its H(t) and ~I(t+1) and there_is_a_neighbor_S =>
                    #  from t+1 until t+3 this cell will become to be S, and at t+4 will return to be H
                    is_S = symbols(str(db[0][t][i][j]))  # expr('S' + str(i) + str(j) + str(t))
                    is_H = symbols(str(db[1][t][i][j]))  # expr('H' + str(i) + str(j) + str(t))
                    if t+1 < num_of_observations:
                        will_not_be_I = ~symbols(str(db[3][t + 1][i][j]))  # ~expr('I' + str(i) + str(j) + str(t + 1))
                        has_neighbor_s = symbols(str(2)) & ~symbols(str(2))
                        if j != 0:  # checking neighbor from left
                            has_neighbor_s |= symbols(
                                str(db[0][t][i][j - 1]))  # expr('S' + str(i) + str(j - 1) + str(t))
                        if j != len(observations[t][0]) - 1:  # checking neighbor from right
                            has_neighbor_s |= symbols(
                                str(db[0][t][i][j + 1]))  # expr('S' + str(i) + str(j + 1) + str(t))
                        if i != 0:  # checking neighbor from up
                            has_neighbor_s |= symbols(
                                str(db[0][t][i - 1][j]))  # expr('S' + str(i - 1) + str(j) + str(t))
                        if i != len(observations[t]) - 1:  # checking neighbor from down
                            has_neighbor_s |= symbols(
                                str(db[0][t][i + 1][j]))  # expr('S' + str(i + 1) + str(j) + str(t))

                        exp_result = symbols(str(db[0][t + 1][i][j]))
                        if t + 2 < num_of_observations:
                            exp_result &= symbols(str(db[0][t + 2][i][j]))
                        if t + 3 < num_of_observations:
                            exp_result &= symbols(str(db[0][t + 3][i][j]))
                        if t + 4 < num_of_observations:
                            exp_result &= symbols(str(db[1][t + 4][i][j]))
                        # (expr('S' + str(i) + str(j) + str(t + 1)) & expr('S' + str(i) + str(j) + str(t + 2))
                        # & expr('S' + str(i) + str(j) + str(t + 3)) & expr('H' + str(i) + str(j) + str(t + 4)))
                        e = (is_H & will_not_be_I & has_neighbor_s) >> exp_result
                        sympy_to_cnf_pysat(e, sat_solver)


                        # if observations[t][i][j] == "S" => stay S from t -> until t+2 , at t+=3 become H (
                        # if t==0, or observations[t - 1][i][j] == "H")
                        stay_S_become_H = symbols(str(db[0][t + 1][i][j]))
                        if t + 2 < num_of_observations:
                            stay_S_become_H &= symbols(str(db[0][t + 2][i][j]))
                        if t + 3 < num_of_observations:
                            stay_S_become_H &= symbols(str(db[1][t + 3][i][j]))
                        # expr('S' + str(i) + str(j) + str(t + 1)) & expr('S' + str(i) + str(j) + str(t + 2)) &
                        # expr('H' + str(i) + str(j) + str(t + 3))
                        if t == 0:  # it will stay S for 3 turns, and then become to H
                            e = ~is_S | stay_S_become_H  # is_S in t==0 => stay_S_become_H
                            sympy_to_cnf_pysat(e, sat_solver)
                        else:  # if t>=1
                            was_H = symbols(str(db[1][t - 1][i][j]))  # expr('H' + str(i) + str(j) + str(t - 1))
                            e = ~is_S | ~was_H | stay_S_become_H  # if it was H and & now it is S => stay_S_become_H
                            sympy_to_cnf_pysat(e, sat_solver)
                        if t >= 2:
                            stay_S_or_become_H = symbols(str(db[0][t + 1][i][j])) | (symbols(str(db[0][t-1][i][j])) &
                                                symbols(str(db[0][t-2][i][j])) & symbols(str(db[1][t+1][i][j])))
                            e = ~is_S | stay_S_or_become_H  # is_S => stay_S_or_become_H_or_Q
                            # e = is_S >> symbols(str(db[0][t+1][i][j])) | symbols(str(db[1][t+1][i][j])) | symbols(str(db[3][t+1][i][j]))
                            sympy_to_cnf_pysat(e, sat_solver)

                    # if S for 3 turns and not become Q => then H
                    if t+3 < num_of_observations:
                        is_S_3_turns = symbols(str(db[0][t][i][j])) & symbols(str(db[0][t + 1][i][j])) &\
                                       symbols(str(db[0][t + 2][i][j]))
                        #expr('S' + str(i) + str(j) + str(t)) & expr('S' + str(i) + str(j) + str(t + 1))&\
                        #expr('S' + str(i) + str(j) + str(t + 2))
                        become_H = symbols(str(db[1][t+3][i][j]))  # expr('H' + str(i) + str(j) + str(t + 3))
                        e = ~is_S_3_turns | become_H  # ~is_S_3_turns | become_H  # is_S_3_turns => become_H
                        sympy_to_cnf_pysat(e, sat_solver)


                    if t > 0:
                        was_H = symbols(str(db[1][t - 1][i][j]))  # expr('H' + str(i) + str(j) + str(t - 1))
                        # if it is I =>this cell was I at t-1 OR was H at t-1:
                        is_I = symbols(str(db[3][t][i][j]))  # expr('I' + str(i) + str(j) + str(t))
                        before_I = symbols(str(db[1][t-1][i][j])) | symbols(str(db[3][t-1][i][j]))
                        # expr('H' + str(i) + str(j) + str(t - 1)) | expr('I' + str(i) + str(j) + str(t-1))
                        e = (~is_I | before_I)  # is_I => before_I
                        sympy_to_cnf_pysat(e, sat_solver)

                        # if it is H=>this cell was H at t-1(and at t-2 if t==2) OR if t>=3 it was S at t-1 & t-2 & t-3:
                        before_H = symbols(str(db[1][t-1][i][j]))  # expr('H' + str(i) + str(j) + str(t - 1))
                        if t == 2:  # this cell must to be H before 2 turns-
                            #  Because 2 turns will not be enough time to change from S to H (need at last 3)
                            before_H &= symbols(str(db[1][t-2][i][j])) # expr('H' + str(i) + str(j) + str(t - 2))
                        if t >= 3:
                            before_H |= (symbols(str(db[0][t-1][i][j])) & symbols(str(db[0][t-2][i][j])) & symbols(str(db[0][t-3][i][j])))
                            # (expr('S' + str(i) + str(j) + str(t - 1)) & expr('S' + str(i) + str(j) + str(t - 2))
                            # & expr('S' + str(i) + str(j) + str(t - 3)))
                        e = (~is_H | before_H)  # is_H => before_H
                        sympy_to_cnf_pysat(e, sat_solver)


                        # if it is H and t<=2 or it was before H too => *no* one of his neighbors was S at t-1
                        no_neighbor_S = symbols(str(1))  # expr('T')
                        if j != 0:  # checking neighbor from left
                            no_neighbor_S &= ~symbols(str(db[0][t-1][i][j-1]))  # ~expr('S' + str(i) + str(j - 1) + str(t - 1))
                            if t == 2:  # no S neighbors 2 turns before, because this cell must be H before 2 turns
                                no_neighbor_S &= ~symbols(str(db[0][t-2][i][j-1]))  # ~expr('S' + str(i) + str(j - 1) + str(t - 2))
                        if j != len(observations[t][0]) - 1:  # checking neighbor from right
                            no_neighbor_S &= ~symbols(str(db[0][t-1][i][j+1]))  # ~expr('S' + str(i) + str(j + 1) + str(t - 1))
                            if t == 2:
                                no_neighbor_S &= ~symbols(str(db[0][t-2][i][j+1]))  # ~expr('S' + str(i) + str(j + 1) + str(t - 2))
                        if i != 0:  # checking neighbor from up
                            no_neighbor_S &= ~symbols(str(db[0][t-1][i-1][j]))  # ~expr('S' + str(i - 1) + str(j) + str(t - 1))
                            if t == 2:
                                no_neighbor_S &= ~symbols(str(db[0][t-2][i-1][j]))  # ~expr('S' + str(i - 1) + str(j) + str(t - 2))
                        if i != len(observations[t]) - 1:  # checking neighbor from down
                            no_neighbor_S &= ~symbols(str(db[0][t-1][i+1][j]))  # ~expr('S' + str(i + 1) + str(j) + str(t - 1))
                            if t == 2:
                                no_neighbor_S &= ~symbols(str(db[0][t-2][i+1][j]))  # ~expr('S' + str(i + 1) + str(j) + str(t - 2))

                        if t <= 2:
                            e = ~is_H | no_neighbor_S  # is_H => no_neighbor_S
                            sympy_to_cnf_pysat(e, sat_solver)
                        is_H_before = symbols(str(db[1][t-1][i][j]))  # expr('H' + str(i) + str(j) + str(t - 1))
                        e = ~is_H | ~is_H_before | no_neighbor_S  # (is_H & is_H_before) => no_neighbor_S
                        sympy_to_cnf_pysat(e, sat_solver)

                        # t>=1: this cell was S at t-1 OR (was_H and at least one of its neighbors was S at t-1):
                        was_S = symbols(str(db[0][t - 1][i][j]))  # expr('S' + str(i) + str(j) + str(t - 1))
                        had_neighbor_s = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
                        if j != 0:  # checking neighbor from left
                            had_neighbor_s |= symbols(
                                str(db[0][t - 1][i][j - 1]))  # expr('S' + str(i) + str(j - 1) + str(t - 1))
                        if j != len(observations[t][0]) - 1:  # checking neighbor from right
                            had_neighbor_s |= symbols(
                                str(db[0][t - 1][i][j + 1]))  # expr('S' + str(i) + str(j + 1) + str(t - 1))
                        if i != 0:  # checking neighbor from up
                            had_neighbor_s |= symbols(
                                str(db[0][t - 1][i - 1][j]))  # expr('S' + str(i - 1) + str(j) + str(t - 1))
                        if i != len(observations[t]) - 1:  # checking neighbor from down
                            had_neighbor_s |= symbols(
                                str(db[0][t - 1][i + 1][j]))  # expr('S' + str(i + 1) + str(j) + str(t - 1))
                        # is_S => it was_S | was_H at t-1 & (at at least one of its neighbors was S at t-1)
                        e = is_S >> (was_S | (was_H & had_neighbor_s))
                        sympy_to_cnf_pysat(e, sat_solver)



            there_is_H = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
            there_is_I_next_turn = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
            len_states_I = len(states_I_H)
            next_turn_I = 0
            if t + 1 < num_of_observations:
                for s1 in range(len_states_I):
                    s1_i, s1_j = int(states_I_H[s1][0]), int(states_I_H[s1][1])
                    if observations[t + 1][s1_i][s1_j] == "I":
                        next_turn_I += 1
            if num_I == max_I:  #if num_I == max_I => ALL TEAMS USED proparely
                for s1 in range(len_states_I):
                    s1_i, s1_j = int(states_I_H[s1][0]), int(states_I_H[s1][1])
                    if t == 0:  # at t ==0 there is no I on the board !
                        e = ~symbols(str(db[3][0][s1_i][s1_j]))  # ~expr('I' + str(state_s1) + str(t))
                        one_sympy_to_pysat(e, sat_solver)
                    elif observations[t][s1_i][s1_j] != "I":
                        e = ~symbols(str(db[3][t][s1_i][s1_j]))  # there is enough I
                        one_sympy_to_pysat(e, sat_solver)
                    if (next_turn_I != (max_I + 1)) and (t + 1 < num_of_observations):
                        there_is_H |= symbols(str(db[1][t][s1_i][s1_j]))  # expr('H' + str(state_s1) + str(t))
                        there_is_I_next_turn |= symbols(str(db[3][t + 1][s1_i][s1_j])) & \
                                                symbols(str(db[1][t][s1_i][s1_j]))
                        # expr('I' + str(state_s1) + str(t + 1)) & (expr('H' + str(state_s1) + str(t)))
                if (next_turn_I != (max_I + 1)) and (t + 1 < num_of_observations):
                    if num_H >= 1:
                        e = there_is_I_next_turn  # there_is_H => there_is_I_next_turn
                        sympy_to_cnf_pysat(e, sat_solver)
                    else:
                        e = ~there_is_H | there_is_I_next_turn  # there_is_H => there_is_I_next_turn
                        sympy_to_cnf_pysat(e, sat_solver)

            else:  #== if num_I != max_I
                # medics == 1=> no more than one Imune acttion in each turn t
                for s1 in range(len_states_I):
                    s1_i, s1_j = int(states_I_H[s1][0]), int(states_I_H[s1][1])
                    if t > 0:
                        for s2 in range(s1 + 1, len_states_I):
                            s2_i, s2_j = int(states_I_H[s2][0]), int(states_I_H[s2][1])
                            e = ~(symbols(str(db[1][t - 1][s1_i][s1_j])) & symbols(str(db[3][t][s1_i][s1_j]))) | \
                                ~(symbols(str(db[1][t - 1][s2_i][s2_j])) & symbols(str(db[3][t][s2_i][s2_j])))
                            sympy_to_cnf_pysat(e, sat_solver)
                            # ~(expr('H' + str(state_s1) + str(t - 1)) & expr('I' + str(state_s1) + str(t))) | \
                            # ~(expr('H' + str(state_s2) + str(t - 1)) & expr('I' + str(state_s2) + str(t)))

                    # medics == 1 & there_is_H in turn t=> at least one Imune acttion Will be activated in turn t+1
                    if t == 0:  # at t ==0 there is no I on the board !
                        e = ~symbols(str(db[3][0][s1_i][s1_j]))  # ~expr('I' + str(state_s1) + str(t))
                        one_sympy_to_pysat(e, sat_solver)
                    if (next_turn_I != (max_I + 1)) and (t + 1 < num_of_observations):
                        there_is_H |= symbols(str(db[1][t][s1_i][s1_j]))  # expr('H' + str(state_s1) + str(t))
                        there_is_I_next_turn |= symbols(str(db[3][t + 1][s1_i][s1_j])) & symbols(
                            str(db[1][t][s1_i][s1_j]))
                        # expr('I' + str(state_s1) + str(t + 1)) & (expr('H' + str(state_s1) + str(t)))
                if (next_turn_I != (max_I + 1)) and (t + 1 < num_of_observations):
                    if num_H >= 1:
                        e = there_is_I_next_turn  # there_is_H => there_is_I_next_turn
                        sympy_to_cnf_pysat(e, sat_solver)
                    else:
                        e = ~there_is_H | there_is_I_next_turn  # there_is_H => there_is_I_next_turn
                        sympy_to_cnf_pysat(e, sat_solver)


    elif polices == 1 and medics == 0:
        states = ('H', 'S', 'U', 'Q')  # db[3] == Q instead of I (there isn't I here)
        for t in range(num_of_observations):
            states_Q_S = ()
            for i in range(length_row):
                for j in range(length_column):
                    states_Q_S += ((str(i), str(j)),)
                    for s1 in range(4):
                        for s2 in range(s1+1, 4):
                            e = ~symbols(str(db[s1][t][i][j])) | ~symbols(str(db[s2][t][i][j]))
                            sympy_to_cnf_pysat(e, sat_solver)


        # General rules & observations
        max_Q = -1
        for t in range(num_of_observations):
            num_S = 0
            num_Q = 0
            max_Q += 1
            for i in range(length_row):
                for j in range(length_column):
                    if observations[t][i][j] == "U":  # => this cell was before and will stay until the end 'U'
                        one_sympy_to_pysat(symbols(str(db[2][t][i][j])), sat_solver)

                    if observations[t][i][j] == "Q":
                        one_sympy_to_pysat(symbols(str(db[3][t][i][j])), sat_solver)
                        num_Q += 1

                    if observations[t][i][j] == "S":
                        one_sympy_to_pysat(symbols(str(db[0][t][i][j])), sat_solver)
                        num_S += 1

                    if observations[t][i][j] == "H":
                        one_sympy_to_pysat(symbols(str(db[1][t][i][j])), sat_solver)

                        if t < num_of_observations - 1:
                            there_is_a_neighbor_S = False
                            there_is_unknown_neighbor = False  # == if there is a neighbor '?'
                            if j != 0:  # checking neighbor from left
                                if observations[t + 1][i][j - 1] == "S":
                                    there_is_a_neighbor_S = True
                                elif observations[t + 1][i][j - 1] == "?":
                                    there_is_unknown_neighbor = True
                            if j != len(observations[t][0]) - 1:  # checking neighbor from right
                                if observations[t + 1][i][j + 1] == "S":
                                    there_is_a_neighbor_S = True
                                elif observations[t + 1][i][j + 1] == "?":
                                    there_is_unknown_neighbor = True
                            if i != 0:  # checking neighbor from up
                                if observations[t + 1][i - 1][j] == "S":
                                    there_is_a_neighbor_S = True
                                elif observations[t + 1][i - 1][j] == "?":
                                    there_is_unknown_neighbor = True
                            if i != len(observations[t]) - 1:  # checking neighbor from down
                                if observations[t + 1][i + 1][j] == "S":
                                    there_is_a_neighbor_S = True
                                elif observations[t + 1][i + 1][j] == "?":
                                    there_is_unknown_neighbor = True

                            if (not there_is_a_neighbor_S) and t+1 < num_of_observations:
                                if not there_is_unknown_neighbor:
                                    # == if there is not neighbor S and no ? => next time(at t+1) this cell will stay H
                                    e = symbols(str(db[1][t + 1][i][j]))  # 'H' + str(i) + str(j) + str(t + 1)
                                    one_sympy_to_pysat(e, sat_solver)
                                else:  # == if no neighbor S but yes ? => this cell will be or H or S
                                    e = symbols(str(db[1][t + 1][i][j])) | symbols(str(db[0][t + 1][i][j]))
                                    sympy_to_cnf_pysat(e, sat_solver)


                    # if observations[t][i][j] == "U" => this cell will always be U
                    is_U = symbols(str(db[2][t][i][j]))  # expr('U' + str(i) + str(j) + str(t))
                    exp_result = symbols(str(db[2][0][i][j]))  # expr('U' + str(i) + str(j) + str(0))
                    for t1 in range(1, num_of_observations):
                        exp_result &= symbols(str(db[2][t1][i][j]))  # expr('U' + str(i) + str(j) + str(t1))
                    e = ~is_U | exp_result  # is_U => exp_result
                    sympy_to_cnf_pysat(e, sat_solver)


                    is_S = symbols(str(db[0][t][i][j]))  # expr('S' + str(i) + str(j) + str(t))
                    is_H = symbols(str(db[1][t][i][j]))  # expr('H' + str(i) + str(j) + str(t))
                    is_Q = symbols(str(db[3][t][i][j]))  # expr('Q' + str(i) + str(j) + str(t))
                    if t > 0:
                        was_S = symbols(str(db[0][t-1][i][j]))  # expr('S' + str(i) + str(j) + str(t - 1))
                        # if Q => was Q or was S
                        was_Q = symbols(str(db[3][t-1][i][j]))  # expr('Q' + str(i) + str(j) + str(t-1))
                        wasnt_Q = ~was_Q
                        e = ~is_Q | ~wasnt_Q | was_S  # is_Q & wasnt_Q => was_S
                        sympy_to_cnf_pysat(e, sat_solver)
                        e = is_Q >> (was_Q | was_S)  # is_Q => was_S | was_Q
                        sympy_to_cnf_pysat(e, sat_solver)

                        # if its Q and before was S <=> Q for 2 turns, and then H
                        if t + 1 < num_of_observations:
                            Q_then_H = symbols(str(db[3][t + 1][i][j]))  # expr('Q' + str(i) + str(j) + str(t + 1))
                            if t + 2 < num_of_observations:
                                Q_then_H &= symbols(str(db[1][t + 2][i][j]))  # expr('H' + str(i) + str(j) + str(t + 2))
                                e2 = (is_Q & was_S) << Q_then_H
                                sympy_to_cnf_pysat(e2, sat_solver)
                            e1 = (is_Q & was_S) >> Q_then_H  # (is_Q & was_S) <=> Q_then_H
                            sympy_to_cnf_pysat(e1, sat_solver)


                        # if it was H(t-1) and there_is now(t)_a_neighbor_S that was before S too
                        #  (and no just now infected itself) => this cell will become S
                        before_H = symbols(str(db[1][t-1][i][j]))  # expr('H' + str(i) + str(j) + str(t-1))
                        # not_will_be_Q = ~expr('Q' + str(i) + str(j) + str(t+1))
                        has_neighbor_s = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
                        if j != 0:  # checking neighbor from left
                            has_neighbor_s |= (symbols(str(db[0][t][i][j-1])) & symbols(str(db[0][t-1][i][j-1])))
                            #(expr('S' + str(i) + str(j - 1) + str(t)) & expr('S' + str(i) + str(j - 1) + str(t - 1)))
                        if j != len(observations[t][0]) - 1:  # checking neighbor from right
                            has_neighbor_s |= (symbols(str(db[0][t][i][j+1])) & symbols(str(db[0][t-1][i][j+1])))
                            #(expr('S' + str(i) + str(j + 1) + str(t)) &expr('S' + str(i) + str(j + 1) + str(t - 1)))
                        if i != 0:  # checking neighbor from up
                            has_neighbor_s |= (symbols(str(db[0][t][i-1][j])) & symbols(str(db[0][t-1][i-1][j])))
                            #(expr('S' + str(i - 1) + str(j) + str(t)) & expr('S' + str(i - 1) + str(j) + str(t - 1)))
                        if i != len(observations[t]) - 1:  # checking neighbor from down
                            has_neighbor_s |= (symbols(str(db[0][t][i+1][j])) & symbols(str(db[0][t-1][i+1][j])))
                            #(expr('S' + str(i + 1) + str(j) + str(t)) & expr('S' + str(i + 1) + str(j) + str(t - 1)))
                        exp_result = symbols(str(db[0][t][i][j]))  # expr('S' + str(i) + str(j) + str(t))
                        e = ~before_H | ~has_neighbor_s | exp_result  # ((before_H & has_neighbor_s) | '==>' | exp_result)
                        sympy_to_cnf_pysat(e, sat_solver)

                        # if it is H=>this cell was H at t-1(and at t-2 if t==2) OR
                        # (if t>=3; it was S at t-1 & t-2 & t-3 OR was Q at t-1 & t-2):
                        if t == 2:  # this cell must to be H before 2 turns-
                            #  Because 2 turns will not be enough time to change from S to H (need at last 3)
                            # and no for Q become H (in turn 0 there isnt Q and need 2 turns to become H)
                            before_H &= symbols(str(db[1][t-2][i][j]))  # expr('H' + str(i) + str(j) + str(t - 2))
                        if t >= 3:
                            before_H |= (symbols(str(db[0][t-1][i][j])) &
                                         symbols(str(db[0][t-2][i][j])) & symbols(str(db[0][t-3][i][j]))) |\
                                        (symbols(str(db[3][t-1][i][j])) & symbols(str(db[3][t-2][i][j])))
                                        #(expr('S' + str(i) + str(j) + str(t - 1)) &
                                        #expr('S' + str(i) + str(j) + str(t - 2)) &
                                        # expr('S' + str(i) + str(j) + str(t - 3))) | \
                                        #(expr('Q' + str(i) + str(j) + str(t - 1)) &
                                        # expr('Q' + str(i) + str(j) + str(t - 2)))

                        e = ~is_H | before_H  # (~is_H | before_H)  # is_H => before_H
                        sympy_to_cnf_pysat(e, sat_solver)

                        # if it is H AND (t<=2 OR it was before H too=>*no* one of his neighbors is *twice* S at t and at t-1!)
                        # (and no at t-1!! because it can be turned on to Q next turn at t.)
                        is_H_before = symbols(str(db[1][t-1][i][j]))  # expr('H' + str(i) + str(j) + str(t - 1))
                        no_neighbor_S = symbols(str(1))  # expr('T')
                        if j != 0:  # checking neighbor from left
                            no_neighbor_S &= ~symbols(str(db[0][t][i][j-1])) | ~symbols(str(db[0][t-1][i][j-1]))
                            #~expr('S' + str(i) + str(j - 1) + str(t)) | ~expr('S' + str(i) + str(j - 1) + str(t - 1))

                        if j != len(observations[t][0]) - 1:  # checking neighbor from right
                            no_neighbor_S &= ~symbols(str(db[0][t][i][j+1])) | ~symbols(str(db[0][t-1][i][j+1]))
                            #~expr('S' + str(i) + str(j + 1) + str(t)) | ~expr('S' + str(i) + str(j + 1) + str(t - 1))

                        if i != 0:  # checking neighbor from up
                            no_neighbor_S &= ~symbols(str(db[0][t][i-1][j])) | ~symbols(str(db[0][t-1][i-1][j]))
                            #~expr('S' + str(i - 1) + str(j) + str(t)) | ~expr('S' + str(i - 1) + str(j) + str(t - 1))

                        if i != len(observations[t]) - 1:  # checking neighbor from down
                            no_neighbor_S &= ~symbols(str(db[0][t][i+1][j])) | ~symbols(str(db[0][t-1][i+1][j]))
                            #~expr('S' + str(i + 1) + str(j) + str(t)) | ~expr('S' + str(i + 1) + str(j) + str(t - 1))

                        if t <= 2:
                            e = ~is_H | no_neighbor_S  # is_H => no_neighbor_S
                            sympy_to_cnf_pysat(e, sat_solver)
                        else:
                            e = (is_H & is_H_before) >> no_neighbor_S  # ~is_H | ~is_H_before | no_neighbor_S
                            sympy_to_cnf_pysat(e, sat_solver)
                        # (is_H & is_H_before) => no_neighbor_S


                        # t>=1: is_S=> this cell was S at t-1 OR
                        # (was_H and at least one of its neighbors is S at t and was S at t-1):
                        had_neighbor_s = symbols(str(2)) & ~symbols(str(2)) # expr('A') & ~expr('A')
                        if j != 0:  # checking neighbor from left
                            had_neighbor_s |= symbols(str(db[0][t][i][j-1])) & symbols(str(db[0][t-1][i][j-1]))
                            #expr('S' + str(i) + str(j - 1) + str(t)) & expr('S' + str(i) + str(j - 1) + str(t - 1))
                        if j != len(observations[t][0]) - 1:  # checking neighbor from right
                            had_neighbor_s |= symbols(str(db[0][t][i][j+1])) & symbols(str(db[0][t-1][i][j+1]))
                            #expr('S' + str(i) + str(j + 1) + str(t)) & expr('S' + str(i) + str(j + 1) + str(t - 1))
                        if i != 0:  # checking neighbor from up
                            had_neighbor_s |= symbols(str(db[0][t][i-1][j])) & symbols(str(db[0][t-1][i-1][j]))
                            #expr('S' + str(i - 1) + str(j) + str(t)) & expr('S' + str(i - 1) + str(j) + str(t - 1))
                        if i != len(observations[t]) - 1:  # checking neighbor from down
                            had_neighbor_s |= symbols(str(db[0][t][i+1][j])) & symbols(str(db[0][t-1][i+1][j]))
                            #expr('S' + str(i + 1) + str(j) + str(t)) & expr('S' + str(i + 1) + str(j) + str(t - 1))
                        # is_S => it was_S | was_H at t-1 & (at at least one of its neighbors was S at t-1)
                        e = is_S >> (was_S | (is_H_before & had_neighbor_s))
                        sympy_to_cnf_pysat(e, sat_solver)


                    if t+1 < num_of_observations:
                        # if "S" => become Q or stay S or H(if t>=2 and was 3 times S)
                        stay_S_or_become_H_or_Q = symbols(str(db[0][t+1][i][j]))
                        become_Q = symbols(str(db[3][t+1][i][j]))
                        if t+2 < num_of_observations:
                            become_Q &= symbols(str(db[3][t + 2][i][j]))
                        if t+3 < num_of_observations:
                            become_Q &= symbols(str(db[1][t + 3][i][j]))
                        stay_S_or_become_H_or_Q |= become_Q
                        #(expr('Q' + str(i) + str(j) + str(t + 1)) & expr('Q' + str(i) + str(j) + str(t + 2)) & \
                        #expr('H' + str(i) + str(j) + str(t + 3))) | expr('S' + str(i) + str(j) + str(t + 1))
                        if t >= 2:
                            stay_S_or_become_H_or_Q |= (symbols(str(db[0][t-1][i][j])) & symbols(str(db[0][t-2][i][j]))
                                                        & symbols(str(db[1][t+1][i][j])))
                            #(expr('S' + str(i) + str(j) + str(t - 1)) & expr('S' + str(i) + str(j) + str(t - 2)) & \
                            #expr('H' + str(i) + str(j) + str(t + 1)))
                        e = is_S >> stay_S_or_become_H_or_Q  # is_S => stay_S_or_become_H_or_Q
                        #e = is_S >> symbols(str(db[0][t+1][i][j])) | symbols(str(db[1][t+1][i][j])) | symbols(str(db[3][t+1][i][j]))
                        sympy_to_cnf_pysat(e, sat_solver)

                    # if S for 3 turns and not become Q => then H
                    if t+3 < num_of_observations:
                        not_become_Q = ~symbols(str(db[3][t+3][i][j]))
                        is_S_3_turns = symbols(str(db[0][t][i][j])) & symbols(str(db[0][t + 1][i][j])) &\
                                       symbols(str(db[0][t + 2][i][j]))
                        #expr('S' + str(i) + str(j) + str(t)) & expr('S' + str(i) + str(j) + str(t + 1))&\
                        #expr('S' + str(i) + str(j) + str(t + 2))
                        become_H = symbols(str(db[1][t+3][i][j]))  # expr('H' + str(i) + str(j) + str(t + 3))
                        e = (not_become_Q & is_S_3_turns) >> become_H  # ~is_S_3_turns | become_H  # is_S_3_turns => become_H
                        sympy_to_cnf_pysat(e, sat_solver)

            # polices == 1=> no more than one Qurentie acttion in each turn t
            len_states_Q = len(states_Q_S)
            there_is_S = symbols(str(2)) & ~symbols(str(2)) #  expr('A') & ~expr('A')
            there_is_Q_next_turn = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
            next_turn_Q = 0
            if t + 1 < num_of_observations:
                for s1 in range(len_states_Q):
                    s1_i, s1_j = int(states_Q_S[s1][0]), int(states_Q_S[s1][1])
                    if observations[t + 1][s1_i][s1_j] == "Q":
                        next_turn_Q += 1
            if num_Q == max_Q:  #if num_Q == max_Q => ALL TEAMS USED proparely
                for s1 in range(len_states_Q):
                    s1_i, s1_j = int(states_Q_S[s1][0]), int(states_Q_S[s1][1])
                    if t == 0:  # at t ==0 there is no I on the board !
                        e = ~symbols(str(db[3][0][s1_i][s1_j]))  # ~expr('Q' + str(state_s1) + str(t))
                        one_sympy_to_pysat(e, sat_solver)
                    elif observations[t][s1_i][s1_j] != "Q":
                        e = ~symbols(str(db[3][t][s1_i][s1_j]))  # there is enough Q
                        one_sympy_to_pysat(e, sat_solver)
                    if next_turn_Q != (max_Q + 1) and (t + 1 < num_of_observations):
                        there_is_S |= symbols(str(db[0][t][s1_i][s1_j]))  # expr('S' + str(state_s1) + str(t))
                        there_is_Q_next_turn |= (symbols(str(db[3][t + 1][s1_i][s1_j])) &
                                                 symbols(str(db[0][t][s1_i][s1_j])))
                        # if there is S => there is a new Qurentie, that wasnt there before
                if next_turn_Q != (max_Q + 1) and (t + 1 < num_of_observations):
                    if num_S >= 1:
                        e = there_is_Q_next_turn
                        sympy_to_cnf_pysat(e, sat_solver)
                    else:
                        e = ~there_is_S | there_is_Q_next_turn  # there_is_S => there_is_Q_next_turn
                        sympy_to_cnf_pysat(e, sat_solver)

            else:
                for s1 in range(len_states_Q):
                    s1_i, s1_j = int(states_Q_S[s1][0]), int(states_Q_S[s1][1])
                    if t > 0:
                        for s2 in range(s1 + 1, len_states_Q):
                            s2_i, s2_j = int(states_Q_S[s2][0]), int(states_Q_S[s2][1])
                            e = ~(symbols(str(db[0][t - 1][s1_i][s1_j])) & symbols(str(db[3][t][s1_i][s1_j]))) | \
                                ~(symbols(str(db[0][t - 1][s2_i][s2_j])) & symbols(str(db[3][t][s2_i][s2_j])))
                            sympy_to_cnf_pysat(e, sat_solver)
                            # KB &= expr('S' + str(state_s1) + str(t - 1)) & expr('Q' + str(state_s1) + str(t)) | '==>' |\
                            #      ~(expr('S' + str(state_s2) + str(t - 1)) & expr('Q' + str(state_s2) + str(t)))

                    # police == 1 & there_is_S in turn t=> at least one Qurentie acttion Will be activated in turn t+1
                    if t == 0:  # at t ==0 there is no Q on the board !
                        e = ~symbols(str(db[3][0][s1_i][s1_j]))  # ~expr('Q' + str(state_s1) + str(t))
                        one_sympy_to_pysat(e, sat_solver)
                    if next_turn_Q != (max_Q + 1) and (t + 1 < num_of_observations):
                        there_is_S |= symbols(str(db[0][t][s1_i][s1_j]))  # expr('S' + str(state_s1) + str(t))
                        there_is_Q_next_turn |= (symbols(str(db[3][t + 1][s1_i][s1_j])) &
                                                 symbols(str(db[0][t][s1_i][s1_j])))
                        # if there is S => there is a new Qurentie, that wasnt there before

                if next_turn_Q != (max_Q + 1) and (t + 1 < num_of_observations):
                    if num_S >= 1:
                        e = there_is_Q_next_turn
                        sympy_to_cnf_pysat(e, sat_solver)
                    else:
                        e = ~there_is_S | there_is_Q_next_turn  # there_is_S => there_is_Q_next_turn
                        sympy_to_cnf_pysat(e, sat_solver)


    else:
        states = ('H', 'S', 'U', 'I', 'Q')
        for t in range(num_of_observations):
            states_Q_I = ()
            for i in range(length_row):
                for j in range(length_column):
                    states_Q_I += ((str(i), str(j)),)
                    for s1 in range(5):
                        for s2 in range(s1+1, 5):
                            e = ~symbols(str(db[s1][t][i][j])) | ~symbols(str(db[s2][t][i][j]))
                            sympy_to_cnf_pysat(e, sat_solver)

    
        # General rules and observations
        max_I = -int(medics)
        max_Q = -int(polices)
        for t in range(num_of_observations):
            num_H = 0
            num_S = 0
            num_I = 0
            num_Q = 0
            max_I += int(medics)  # at t=0 -> max_I ==0, at t=1 => max_I =num_of_medics, t=2 => max_I = 2*num_of_medics .....
            max_Q += int(polices)
            for i in range(length_row):
                for j in range(length_column):
                    if observations[t][i][j] == "U":  # => this cell was before and will stay until the end 'U'
                        one_sympy_to_pysat(symbols(str(db[2][t][i][j])), sat_solver)

                    if observations[t][i][j] == "I":  # => this cell will stay 'I' from now until the end
                        one_sympy_to_pysat(symbols(str(db[3][t][i][j])), sat_solver)
                        num_I += 1

                    if observations[t][i][j] == "S":
                        one_sympy_to_pysat(symbols(str(db[0][t][i][j])), sat_solver)
                        num_S += 1

                    if observations[t][i][j] == "H":
                        one_sympy_to_pysat(symbols(str(db[1][t][i][j])), sat_solver)
                        num_H += 1

                    if observations[t][i][j] == "Q":
                        one_sympy_to_pysat(symbols(str(db[4][t][i][j])), sat_solver)
                        num_Q += 1

                        if t < num_of_observations - 1:
                            there_is_a_neighbor_S = False
                            there_is_unknown_neighbor = False  # == if there is a neighbor '?'
                            if j != 0:  # checking neighbor from left
                                if observations[t + 1][i][j - 1] == "S":
                                    there_is_a_neighbor_S = True
                                elif observations[t + 1][i][j - 1] == "?":
                                    there_is_unknown_neighbor = True
                            if j != len(observations[t][0]) - 1:  # checking neighbor from right
                                if observations[t + 1][i][j + 1] == "S":
                                    there_is_a_neighbor_S = True
                                elif observations[t + 1][i][j + 1] == "?":
                                    there_is_unknown_neighbor = True
                            if i != 0:  # checking neighbor from up
                                if observations[t + 1][i - 1][j] == "S":
                                    there_is_a_neighbor_S = True
                                elif observations[t + 1][i - 1][j] == "?":
                                    there_is_unknown_neighbor = True
                            if i != len(observations[t]) - 1:  # checking neighbor from down
                                if observations[t + 1][i + 1][j] == "S":
                                    there_is_a_neighbor_S = True
                                elif observations[t + 1][i + 1][j] == "?":
                                    there_is_unknown_neighbor = True

                            if (not there_is_a_neighbor_S) and t + 1 < num_of_observations:
                                if not there_is_unknown_neighbor:
                                    # == if there is not neighbor S or ?: next time(at t+1) this cell will stay H or become I
                                    e = symbols(str(db[1][t + 1][i][j])) | symbols(str(db[3][t + 1][i][j]))
                                else:
                                    # == if no neighbor S but yes ? => this cell will be or H or I or S(for 3 turns and then H)
                                    e = (symbols(str(db[1][t + 1][i][j])) | symbols(str(db[3][t + 1][i][j])) |
                                         symbols(str(db[0][t + 1][i][j])))
                                sympy_to_cnf_pysat(e, sat_solver)


                    # if observations[t][i][j] == "U" => this cell will always be U
                    is_U = symbols(str(db[2][t][i][j]))  # expr('U' + str(i) + str(j) + str(t))
                    exp_result = symbols(str(db[2][0][i][j]))  # expr('U' + str(i) + str(j) + str(0))
                    for t1 in range(1, num_of_observations):
                        exp_result &= symbols(str(db[2][t1][i][j]))  # expr('U' + str(i) + str(j) + str(t1))
                    e = ~is_U | exp_result  # is_U => exp_result
                    sympy_to_cnf_pysat(e, sat_solver)

                    is_S = symbols(str(db[0][t][i][j]))  # expr('S' + str(i) + str(j) + str(t))
                    is_H = symbols(str(db[1][t][i][j]))  # expr('H' + str(i) + str(j) + str(t))
                    is_Q = symbols(str(db[4][t][i][j]))  # expr('Q' + str(i) + str(j) + str(t))
                    is_I = symbols(str(db[3][t][i][j]))  # expr('I' + str(i) + str(j) + str(t))
                    if t > 0:
                        # if observations[t][i][j] == "I" => this cell will stay 'I' from now until the end
                        if t + 1 < num_of_observations:
                            exp_result = symbols(str(db[3][t + 1][i][j]))  # expr('I' + str(i) + str(j) + str(t+1))
                            for t1 in range(t + 2, num_of_observations):
                                exp_result &= symbols(str(db[3][t1][i][j]))  # expr('I' + str(i) + str(j) + str(t1))
                            e = ~is_I | exp_result  # is_I => exp_result
                            sympy_to_cnf_pysat(e, sat_solver)

                        was_H = symbols(str(db[1][t - 1][i][j]))  # expr('H' + str(i) + str(j) + str(t - 1))

                        # if it is I =>this cell was I at t-1 OR was H at t-1:
                        before_I = symbols(str(db[1][t - 1][i][j])) | symbols(str(db[3][t - 1][i][j]))
                        e = (~is_I | before_I)  # is_I => before_I
                        sympy_to_cnf_pysat(e, sat_solver)

                        # if Q => was Q or was S
                        was_S = symbols(str(db[0][t - 1][i][j]))  # expr('S' + str(i) + str(j) + str(t - 1))
                        was_Q = symbols(str(db[4][t - 1][i][j]))  # expr('Q' + str(i) + str(j) + str(t-1))
                        wasnt_Q = ~was_Q
                        e = ~is_Q | ~wasnt_Q | was_S  # is_Q & wasnt_Q => was_S
                        sympy_to_cnf_pysat(e, sat_solver)
                        e = is_Q >> (was_Q | was_S)  # is_Q => was_S | was_Q
                        sympy_to_cnf_pysat(e, sat_solver)

                        # if its Q and before was S <=> Q for 2 turns, and then H
                        if t + 1 < num_of_observations:
                            Q_then_H = symbols(str(db[4][t + 1][i][j]))  # expr('Q' + str(i) + str(j) + str(t + 1))
                            if t + 2 < num_of_observations:
                                Q_then_H &= symbols(str(db[1][t + 2][i][j]))  # expr('H' + str(i) + str(j) + str(t + 2))
                                e2 = (is_Q & was_S) << Q_then_H
                                sympy_to_cnf_pysat(e2, sat_solver)
                            e1 = (is_Q & was_S) >> Q_then_H  # (is_Q & was_S) <=> Q_then_H
                            sympy_to_cnf_pysat(e1, sat_solver)


                        # if it was H(t-1) and not I(t) and there_is now(t)_a_neighbor_S that was before S too
                        #  (and no just now infected itself) => this cell will become S
                        before_H = symbols(str(db[1][t - 1][i][j]))
                        is_not_I = ~is_I
                        has_neighbor_s = symbols(str(2)) & ~symbols(str(2))
                        # not_will_be_Q = ~expr('Q' + str(i) + str(j) + str(t+1))
                        if j != 0:  # checking neighbor from left
                            has_neighbor_s |= (symbols(str(db[0][t][i][j - 1])) & symbols(str(db[0][t - 1][i][j - 1])))
                            # (expr('S' + str(i) + str(j - 1) + str(t)) & expr('S' + str(i) + str(j - 1) + str(t - 1)))
                        if j != len(observations[t][0]) - 1:  # checking neighbor from right
                            has_neighbor_s |= (symbols(str(db[0][t][i][j + 1])) & symbols(str(db[0][t - 1][i][j + 1])))
                            # (expr('S' + str(i) + str(j + 1) + str(t)) &expr('S' + str(i) + str(j + 1) + str(t - 1)))
                        if i != 0:  # checking neighbor from up
                            has_neighbor_s |= (symbols(str(db[0][t][i - 1][j])) & symbols(str(db[0][t - 1][i - 1][j])))
                            # (expr('S' + str(i - 1) + str(j) + str(t)) & expr('S' + str(i - 1) + str(j) + str(t - 1)))
                        if i != len(observations[t]) - 1:  # checking neighbor from down
                            has_neighbor_s |= (symbols(str(db[0][t][i + 1][j])) & symbols(str(db[0][t - 1][i + 1][j])))
                            # (expr('S' + str(i + 1) + str(j) + str(t)) & expr('S' + str(i + 1) + str(j) + str(t - 1)))
                        exp_result = symbols(str(db[0][t][i][j]))  # expr('S' + str(i) + str(j) + str(t))

                        e = ~before_H | ~is_not_I | ~has_neighbor_s | exp_result  # ((before_H & is_not_I & has_neighbor_s) | '==>' | exp_result)
                        sympy_to_cnf_pysat(e, sat_solver)


                        # if it is H=>this cell was H at t-1(and at t-2 if t==2) OR
                        # (if t>=3; it was S at t-1 & t-2 & t-3 OR was Q at t-1 & t-2):
                        if t == 2:  # this cell must to be H before 2 turns-
                            #  Because 2 turns will not be enough time to change from S to H (need at last 3)
                            # and no for Q become H (in turn 0 there isnt Q and need 2 turns to become H)
                            before_H &= symbols(str(db[1][t - 2][i][j]))  # expr('H' + str(i) + str(j) + str(t - 2))
                        if t >= 3:
                            before_H |= (symbols(str(db[0][t - 1][i][j])) &
                                         symbols(str(db[0][t - 2][i][j])) & symbols(str(db[0][t - 3][i][j]))) | \
                                        (symbols(str(db[4][t - 1][i][j])) & symbols(str(db[4][t - 2][i][j])))
                            # (expr('S' + str(i) + str(j) + str(t - 1)) &
                            # expr('S' + str(i) + str(j) + str(t - 2)) &
                            # expr('S' + str(i) + str(j) + str(t - 3))) | \
                            # (expr('Q' + str(i) + str(j) + str(t - 1)) &
                            # expr('Q' + str(i) + str(j) + str(t - 2)))
                        e = ~is_H | before_H  # (~is_H | before_H)  # is_H => before_H
                        sympy_to_cnf_pysat(e, sat_solver)

                        # if it is H AND (t<=2 OR it was before H too=>*no* one of his neighbors is *twice* S at t and at t-1!)
                        # (and no at t-1!! because it can be turned on to Q next turn at t.)
                        is_H_before = symbols(str(db[1][t - 1][i][j]))  # expr('H' + str(i) + str(j) + str(t - 1))
                        no_neighbor_S = symbols(str(1))  # expr('T')
                        if j != 0:  # checking neighbor from left
                            no_neighbor_S &= ~symbols(str(db[0][t][i][j - 1])) | ~symbols(
                                str(db[0][t - 1][i][j - 1]))
                            # ~expr('S' + str(i) + str(j - 1) + str(t)) | ~expr('S' + str(i) + str(j - 1) + str(t - 1))

                        if j != len(observations[t][0]) - 1:  # checking neighbor from right
                            no_neighbor_S &= ~symbols(str(db[0][t][i][j + 1])) | ~symbols(
                                str(db[0][t - 1][i][j + 1]))
                            # ~expr('S' + str(i) + str(j + 1) + str(t)) | ~expr('S' + str(i) + str(j + 1) + str(t - 1))

                        if i != 0:  # checking neighbor from up
                            no_neighbor_S &= ~symbols(str(db[0][t][i - 1][j])) | ~symbols(
                                str(db[0][t - 1][i - 1][j]))
                            # ~expr('S' + str(i - 1) + str(j) + str(t)) | ~expr('S' + str(i - 1) + str(j) + str(t - 1))

                        if i != len(observations[t]) - 1:  # checking neighbor from down
                            no_neighbor_S &= ~symbols(str(db[0][t][i + 1][j])) | ~symbols(
                                str(db[0][t - 1][i + 1][j]))
                            # ~expr('S' + str(i + 1) + str(j) + str(t)) | ~expr('S' + str(i + 1) + str(j) + str(t - 1))

                        if t <= 2:
                            e = ~is_H | no_neighbor_S  # is_H => no_neighbor_S
                            sympy_to_cnf_pysat(e, sat_solver)
                        else:
                            e = (is_H & is_H_before) >> no_neighbor_S  # ~is_H | ~is_H_before | no_neighbor_S
                            sympy_to_cnf_pysat(e, sat_solver)
                        # (is_H & is_H_before) => no_neighbor_S


                        # t>=1: is_S=> this cell was S at t-1 OR
                        # (was_H and at least one of its neighbors is S at t and was S at t-1):
                        had_neighbor_s = symbols(str(2)) & ~symbols(str(2))  # expr('A') & ~expr('A')
                        if j != 0:  # checking neighbor from left
                            had_neighbor_s |= symbols(str(db[0][t][i][j - 1])) & symbols(str(db[0][t - 1][i][j - 1]))
                            # expr('S' + str(i) + str(j - 1) + str(t)) & expr('S' + str(i) + str(j - 1) + str(t - 1))
                        if j != len(observations[t][0]) - 1:  # checking neighbor from right
                            had_neighbor_s |= symbols(str(db[0][t][i][j + 1])) & symbols(str(db[0][t - 1][i][j + 1]))
                            # expr('S' + str(i) + str(j + 1) + str(t)) & expr('S' + str(i) + str(j + 1) + str(t - 1))
                        if i != 0:  # checking neighbor from up
                            had_neighbor_s |= symbols(str(db[0][t][i - 1][j])) & symbols(str(db[0][t - 1][i - 1][j]))
                            # expr('S' + str(i - 1) + str(j) + str(t)) & expr('S' + str(i - 1) + str(j) + str(t - 1))
                        if i != len(observations[t]) - 1:  # checking neighbor from down
                            had_neighbor_s |= symbols(str(db[0][t][i + 1][j])) & symbols(str(db[0][t - 1][i + 1][j]))
                            # expr('S' + str(i + 1) + str(j) + str(t)) & expr('S' + str(i + 1) + str(j) + str(t - 1))
                        # is_S => it was_S | was_H at t-1 & (at at least one of its neighbors was S at t-1)
                        e = is_S >> (was_S | (is_H_before & had_neighbor_s))
                        sympy_to_cnf_pysat(e, sat_solver)


                    if t+1 < num_of_observations:
                        # if "S" => become Q or stay S or H(if t>=2 and was 3 times S)
                        stay_S_or_become_H_or_Q = symbols(str(db[0][t+1][i][j]))
                        become_Q = symbols(str(db[4][t+1][i][j]))
                        if t+2 < num_of_observations:
                            become_Q &= symbols(str(db[4][t + 2][i][j]))
                        if t+3 < num_of_observations:
                            become_Q &= symbols(str(db[1][t + 3][i][j]))
                        stay_S_or_become_H_or_Q |= become_Q
                        #(expr('Q' + str(i) + str(j) + str(t + 1)) & expr('Q' + str(i) + str(j) + str(t + 2)) & \
                        #expr('H' + str(i) + str(j) + str(t + 3))) | expr('S' + str(i) + str(j) + str(t + 1))
                        if t >= 2:
                            stay_S_or_become_H_or_Q |= (symbols(str(db[0][t-1][i][j])) & symbols(str(db[0][t-2][i][j]))
                                                        & symbols(str(db[1][t+1][i][j])))
                            #(expr('S' + str(i) + str(j) + str(t - 1)) & expr('S' + str(i) + str(j) + str(t - 2)) & \
                            #expr('H' + str(i) + str(j) + str(t + 1)))
                        e = is_S >> stay_S_or_become_H_or_Q  # is_S => stay_S_or_become_H_or_Q
                        #e = is_S >> symbols(str(db[0][t+1][i][j])) | symbols(str(db[1][t+1][i][j])) | symbols(str(db[3][t+1][i][j]))
                        sympy_to_cnf_pysat(e, sat_solver)

                    # if S for 3 turns and not become Q => then H
                    if t+3 < num_of_observations:
                        not_become_Q = ~symbols(str(db[4][t+3][i][j]))
                        is_S_3_turns = symbols(str(db[0][t][i][j])) & symbols(str(db[0][t + 1][i][j])) &\
                                       symbols(str(db[0][t + 2][i][j]))
                        #expr('S' + str(i) + str(j) + str(t)) & expr('S' + str(i) + str(j) + str(t + 1))&\
                        #expr('S' + str(i) + str(j) + str(t + 2))
                        become_H = symbols(str(db[1][t+3][i][j]))  # expr('H' + str(i) + str(j) + str(t + 3))
                        e = (not_become_Q & is_S_3_turns) >> become_H  # ~is_S_3_turns | become_H  # is_S_3_turns => become_H
                        sympy_to_cnf_pysat(e, sat_solver)


            #if polices == 1 and medics == 1 and (num_Q != max_Q) and (num_I != max_I):
            #    one_police_one_medics(t, db, states_Q_I, sat_solver, num_H, num_S, num_of_observations)
            if polices == 1:
                one_police(t, db, states_Q_I, sat_solver, num_S, num_Q, max_Q, observations)
            if medics == 1:
                one_medics(t, db, states_Q_I, sat_solver, num_H, num_I, max_I, observations)
            if polices == 2:
                two_polices(t, db, states_Q_I, sat_solver, num_S, num_Q, max_Q, observations)
            if medics == 2:
                two_medics(t, db, states_Q_I, sat_solver, num_H, num_I, max_I, observations)
            if polices == 3:
                pass
            if medics == 3:
                pass



   # print(KB)
    dict_ans = {}
    for querie in queries:  # shape of querie: ((0, 1), 0, "H")
        i = int(querie[0][0])
        j = int(querie[0][1])
        t = int(querie[1])
        state = querie[2]
        num_state = -1
        if state == "S":
            num_state = 0
        elif state == "H":
            num_state = 1
        elif state == "U":
            num_state = 2
        elif polices == 1 and (medics == 0):
            if state == "Q":
                num_state = 3
        else:
            if state == "I":
                num_state = 3
            elif state == "Q":
                num_state = 4

        if num_state == -1:
            dict_ans[querie] = 'F'
        else:
            question = int(db[num_state][t][i][j])  # expr(state + str(i) + str(j) + str(t))
            if not sat_solver.solve(assumptions=[
                -question]):  # TRUE if (KB |= e)  ==  if (~e&KB) is not satisfied == if dpll(~e&KB)= False
                dict_ans[querie] = 'T'
            elif not sat_solver.solve(assumptions=[question]):  # else, FALSE if (e & KB) not satisfied
                dict_ans[querie] = 'F'
            else:  # else, ? if (e & KB) satisfied but not (KB |= e) (not always true)
                dict_ans[querie] = '?'
    return dict_ans

