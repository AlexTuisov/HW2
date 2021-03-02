from utils import *

import itertools
from pysat.solvers import Glucose4
from pysat.card import *
from pysat.formula import IDPool
import copy


ids = ["314687815", "337579254"]


IS_PRINT = False


Unpopulated = 'U'
Healthy = 'H'

Immune_0 = 'I0'
Immune = 'I'

Sick = 'S'
Sick_0 = 'S0'
Sick_1 = 'S1'
Sick_2 = 'S2'

Quarantined = 'Q'
Quarantined_0 = 'Q0'
Quarantined_1 = 'Q1'


Police_action = 'P'
Medic_action = 'M'


UNKNOWN = "?"

possible_states_no_replicas = [Unpopulated, Healthy, Sick, Quarantined, Immune]

possible_states = [Unpopulated, Healthy, Sick_0, Sick_1, Sick_2, Quarantined_0, Quarantined_1, Immune_0, Immune]
possible_states_0 = [Unpopulated, Healthy, Sick_0]
possible_states_1 = [Unpopulated, Healthy, Sick_0, Sick_1, Quarantined_0, Immune_0]
non_sick_states = [Unpopulated, Healthy, Quarantined_0, Quarantined_1, Immune_0, Immune]
sick_states = [Sick_0, Sick_1, Sick_2]


def immune_dict_times(time):
    if time == 0:
        return []
    elif time == 1:
        return [Immune_0]

    return [Immune_0, Immune]


def quarantine_dict_times(time):
    if time == 0:
        return []
    elif time == 1:
        return [Quarantined_0]

    return [Quarantined_0, Quarantined_1]


def sick_dict_times(time):
    if time == 0:
        return [Sick_0]
    elif time == 1:
        return [Sick_0, Sick_1]

    return [Sick_0, Sick_1, Sick_2]



def get_all_problem_variables(observations, rows_num, cols_num):
    T = len(observations)

    index_by_variable = IDPool()

    for t in range(T):
        for row in range(rows_num):
            for col in range(cols_num):
                for state in possible_states:
                    index_by_variable.id(f'{state}_{row}_{col}_{t}')

    return index_by_variable



def get_my_neighbors(row, col, number_of_rows, number_of_cols):
    result = []

    if row > 0:
        result.append((row-1, col))
    if row < number_of_rows - 1:
        result.append((row+1, col))
    if col > 0:
        result.append((row, col - 1))
    if col < number_of_cols - 1:
        result.append((row, col + 1))

    return result



def initialize_formula(times, number_of_rows, number_of_cols, index_by_variable, num_police, num_medics, observations):
    formula = CNF()

    for time in range(times):

        all_Q0_or_unknown = []
        all_I0_or_unknown = []

        all_Q0_or_unknown_next_time = []
        all_I0_or_unknown_next_time = []

        num_healthy_or_unknown_tiles = 0
        num_sick_or_unknown_tiles = 0

        all_healthy_or_unknown = []
        all_sick_or_unknown = []

        all_row_col = []


        for row in range(number_of_rows):
            for col in range(number_of_cols):

                observed_state = observations[time][row][col]

                all_row_col.append((row, col))

                if observed_state in [Healthy, UNKNOWN]:
                    all_healthy_or_unknown.append((row, col))

                num_healthy_or_unknown_tiles = len(all_healthy_or_unknown)


                if observed_state in [Sick, UNKNOWN]:
                    all_sick_or_unknown.append((row, col))

                num_sick_or_unknown_tiles = len(all_sick_or_unknown)


                if observed_state in [Quarantined, UNKNOWN]:
                    all_Q0_or_unknown.append(index_by_variable.id(f'{Quarantined_0}_{row}_{col}_{time}'))

                if observed_state in [Immune, UNKNOWN]:
                    all_I0_or_unknown.append(index_by_variable.id(f'{Immune_0}_{row}_{col}_{time}'))


                if time < times - 1:
                    observed_state_next_time = observations[time+1][row][col]

                    if observed_state_next_time in [Quarantined, UNKNOWN]:
                        all_Q0_or_unknown_next_time.append(index_by_variable.id(f'{Quarantined_0}_{row}_{col}_{time+1}'))

                    if observed_state_next_time in [Immune, UNKNOWN]:
                        all_I0_or_unknown_next_time.append(index_by_variable.id(f'{Immune_0}_{row}_{col}_{time+1}'))


                my_neighbors = get_my_neighbors(row, col, number_of_rows, number_of_cols)


                if observed_state == UNKNOWN:

                    if time == 0:
                        literals = [index_by_variable.id(f'{state}_{row}_{col}_{time}') for state in possible_states_0]
                        clause = CardEnc.equals(lits=literals, bound=1, vpool=index_by_variable)

                        formula.extend(clause)

                        for other_state in possible_states:
                            if other_state not in possible_states_0:
                                formula.append([-index_by_variable.id(f'{other_state}_{row}_{col}_{time}')])

                    elif time == 1:
                        literals = [index_by_variable.id(f'{state}_{row}_{col}_{time}') for state in possible_states_1]
                        clause = CardEnc.equals(lits=literals, bound=1, vpool=index_by_variable)

                        formula.extend(clause)

                        for other_state in possible_states:
                            if other_state not in possible_states_1:
                                formula.append([-index_by_variable.id(f'{other_state}_{row}_{col}_{time}')])

                    else:
                        literals = [index_by_variable.id(f'{state}_{row}_{col}_{time}') for state in possible_states]
                        clause = CardEnc.equals(lits=literals, bound=1, vpool=index_by_variable)

                        formula.extend(clause)


                else:

                    if observed_state == Sick:

                        literals = [index_by_variable.id(f'{state}_{row}_{col}_{time}') for state in sick_dict_times(time)]
                        clause = CardEnc.equals(lits=literals, bound=1, vpool=index_by_variable)

                        formula.extend(clause)

                        for other_state in possible_states:
                            if other_state not in sick_dict_times(time):
                                formula.append([-index_by_variable.id(f'{other_state}_{row}_{col}_{time}')])


                    elif observed_state == Quarantined:

                        # assert time > 0

                        literals = [index_by_variable.id(f'{state}_{row}_{col}_{time}') for state in quarantine_dict_times(time)]
                        clause = CardEnc.equals(lits=literals, bound=1, vpool=index_by_variable)

                        formula.extend(clause)

                        for other_state in possible_states:
                            if other_state not in quarantine_dict_times(time):
                                formula.append([-index_by_variable.id(f'{other_state}_{row}_{col}_{time}')])


                    elif observed_state == Immune:

                        # assert time > 0

                        literals = [index_by_variable.id(f'{state}_{row}_{col}_{time}') for state in immune_dict_times(time)]
                        clause = CardEnc.equals(lits=literals, bound=1, vpool=index_by_variable)

                        formula.extend(clause)

                        for other_state in possible_states:
                            if other_state not in immune_dict_times(time):
                                formula.append([-index_by_variable.id(f'{other_state}_{row}_{col}_{time}')])

                    else:
                        formula.append([index_by_variable.id(f'{observed_state}_{row}_{col}_{time}')])

                        for other_state in possible_states:
                            if other_state != observed_state:
                                formula.append([-index_by_variable.id(f'{other_state}_{row}_{col}_{time}')])




                clauses_dynamics = []

                # Unpopulated, Healthy, Sick_0, Sick_1, Sick_2, Quarantined_0, Quarantined_1, Immune_0, Immune

                if time < times - 1:

                    observed_state_next_time = observations[time+1][row][col]

                    # U_i_j_t => U_i_j_t+1
                    if observed_state in [Unpopulated, UNKNOWN] and observed_state_next_time in [Unpopulated, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Unpopulated}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Unpopulated}_{row}_{col}_{time+1}')])

                    # Q0_i_j_t => Q1_i_j_t
                    if observed_state in [Quarantined, UNKNOWN] and observed_state_next_time in [Quarantined, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Quarantined_0}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Quarantined_1}_{row}_{col}_{time+1}')])

                    # Q1_i_j_t => H_i_j_t+1
                    if observed_state in [Quarantined, UNKNOWN] and observed_state_next_time in [Healthy, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Quarantined_1}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Healthy}_{row}_{col}_{time + 1}')])

                    # I_i_j_t => I_i_j_t+1
                    if observed_state in [Immune, UNKNOWN] and observed_state_next_time in [Immune, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Immune}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Immune}_{row}_{col}_{time + 1}')])

                    # I0_i_j_t => I_i_j_t+1
                    if observed_state in [Immune, UNKNOWN] and observed_state_next_time in [Immune, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Immune_0}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Immune}_{row}_{col}_{time + 1}')])


                    # S0_i_j_t =>S1_i_j_t+1 | Q0_i_j_t+1
                    if observed_state in [Sick, UNKNOWN] and observed_state_next_time in [Sick, Quarantined, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Sick_0}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Sick_1}_{row}_{col}_{time + 1}'),
                                         index_by_variable.id(f'{Quarantined_0}_{row}_{col}_{time + 1}')])


                    # S1_i_j_t => S2_i_j_t+1 | Q0_i_j_t+1
                    if observed_state in [Sick, UNKNOWN] and observed_state_next_time in [Sick, Quarantined, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Sick_1}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Sick_2}_{row}_{col}_{time + 1}'),
                                         index_by_variable.id(f'{Quarantined_0}_{row}_{col}_{time + 1}')])


                    #S2_i_j_t => H_i_j_t+1 | Q0_i_j_t+1
                    if observed_state in [Sick, UNKNOWN] and observed_state_next_time in [Healthy, Quarantined, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Sick_2}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Healthy}_{row}_{col}_{time + 1}'),
                                         index_by_variable.id(f'{Quarantined_0}_{row}_{col}_{time + 1}')])


                    # H_i_j_t => H_i_j_t+1 | I0_i_j_t+1 | S0_i_j_t+1
                    if observed_state in [Healthy, UNKNOWN] and observed_state_next_time in [Healthy, Immune, Sick, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Healthy}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Healthy}_{row}_{col}_{time + 1}'),
                                         index_by_variable.id(f'{Immune_0}_{row}_{col}_{time + 1}'),
                                         index_by_variable.id(f'{Sick_0}_{row}_{col}_{time + 1}')])


                    # H_i_j_t & Sick neighbor at t & no Quarantine on neighbor at t+1 & no Immunity on me=> S0_i_j_t+1

                    for row_n, col_n in my_neighbors:

                        observed_neighbor = observations[time][row_n][col_n]
                        observed_neighbor_next_time = observations[time+1][row_n][col_n]

                        if observed_state not in [Healthy, UNKNOWN]:
                            continue

                        if observed_neighbor not in [Sick, UNKNOWN]:
                            continue

                        if observed_neighbor_next_time == Quarantined:
                            continue

                        if observed_state_next_time not in [Sick, UNKNOWN]:
                            continue


                        clauses_dynamics.append([-index_by_variable.id(f'{Healthy}_{row}_{col}_{time}'),
                                                 -index_by_variable.id(f'{Sick_0}_{row_n}_{col_n}_{time}'),
                                                 index_by_variable.id(f'{Quarantined_0}_{row_n}_{col_n}_{time + 1}'),
                                                 index_by_variable.id(f'{Immune_0}_{row}_{col}_{time + 1}'),
                                                 index_by_variable.id(f'{Sick_0}_{row}_{col}_{time + 1}')]
                                                )

                        clauses_dynamics.append([-index_by_variable.id(f'{Healthy}_{row}_{col}_{time}'),
                                                 -index_by_variable.id(f'{Sick_1}_{row_n}_{col_n}_{time}'),
                                                 index_by_variable.id(f'{Quarantined_0}_{row_n}_{col_n}_{time + 1}'),
                                                 index_by_variable.id(f'{Immune_0}_{row}_{col}_{time + 1}'),
                                                 index_by_variable.id(f'{Sick_0}_{row}_{col}_{time + 1}')]
                                                )

                        clauses_dynamics.append([-index_by_variable.id(f'{Healthy}_{row}_{col}_{time}'),
                                                 -index_by_variable.id(f'{Sick_2}_{row_n}_{col_n}_{time}'),
                                                 index_by_variable.id(f'{Quarantined_0}_{row_n}_{col_n}_{time + 1}'),
                                                 index_by_variable.id(f'{Immune_0}_{row}_{col}_{time + 1}'),
                                                 index_by_variable.id(f'{Sick_0}_{row}_{col}_{time + 1}')]
                                                )


                if time > 0:

                    observed_state_last_time = observations[time - 1][row][col]


                    # U_i_j_t => U_i_j_t-1
                    if observed_state in [Unpopulated, UNKNOWN] and observed_state_last_time in [Unpopulated, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Unpopulated}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Unpopulated}_{row}_{col}_{time - 1}')])

                    # Q1_i_j_t => Q0_i_j_t-1
                    if observed_state in [Quarantined, UNKNOWN] and observed_state_last_time in [Quarantined, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Quarantined_1}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Quarantined_0}_{row}_{col}_{time - 1}')])


                    # Q0_i_j_t => (S0_i_j_t-1 | S1_i_j_t-1 | S2_i_j_t-1) === ~Q0_i_j_t | S0_i_j_t-1 | S1_i_j_t-1 | S2_i_j_t-1

                    if observed_state in [Quarantined, UNKNOWN] and observed_state_last_time in [Sick, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Quarantined_0}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Sick_0}_{row}_{col}_{time - 1}'),
                                         index_by_variable.id(f'{Sick_1}_{row}_{col}_{time - 1}'),
                                         index_by_variable.id(f'{Sick_2}_{row}_{col}_{time - 1}')])


                    # I_i_j_t => I_i_j_t-1 | I0_i_j_t-1 = ~I_i_j_t | I_i_j_t-1 | I0_i_j_t-1

                    if observed_state in [Immune, UNKNOWN] and observed_state_last_time in [Immune, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Immune}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Immune}_{row}_{col}_{time - 1}'),
                                         index_by_variable.id(f'{Immune_0}_{row}_{col}_{time - 1}')])


                    # I0_i_j_t -> H_i_j_t-1
                    if observed_state in [Immune, UNKNOWN] and observed_state_last_time in [Healthy, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Immune_0}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Healthy}_{row}_{col}_{time - 1}')])



                    #S0_i_j_t => U_(Sk_i-1_j_t-1 | Sk_i+1_j_t-1 | Sk_i_j-1_t-1 | S0_i_j+1_t-1) for k = 0,1,2
                    #there was at least one sick neighbor:


                    if observed_state in [Sick, UNKNOWN]:

                        clause_sick_neighbors = [-index_by_variable.id(f'{Sick_0}_{row}_{col}_{time}')]

                        for row_n, col_n in my_neighbors:

                            observed_neighbor_last_time = observations[time - 1][row_n][col_n]

                            if observed_neighbor_last_time in [Sick, UNKNOWN]:
                                clause_sick_neighbors.append(index_by_variable.id(f'{Sick_0}_{row_n}_{col_n}_{time-1}'))
                                clause_sick_neighbors.append(index_by_variable.id(f'{Sick_1}_{row_n}_{col_n}_{time-1}'))
                                clause_sick_neighbors.append(index_by_variable.id(f'{Sick_2}_{row_n}_{col_n}_{time-1}'))


                        clauses_dynamics.append(clause_sick_neighbors)



                    # S0_i_j_t => H_i_j_t-1
                    if observed_state in [Sick, UNKNOWN] and observed_state_last_time in [Healthy, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Sick_0}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Healthy}_{row}_{col}_{time - 1}')])

                    # S1_i_j_t => S0_i_j_t-1
                    if observed_state in [Sick, UNKNOWN] and observed_state_last_time in [Sick, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Sick_1}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Sick_0}_{row}_{col}_{time - 1}')])

                    # S2_i_j_t => S1_i_j_t-1
                    if observed_state in [Sick, UNKNOWN] and observed_state_last_time in [Sick, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Sick_2}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Sick_1}_{row}_{col}_{time - 1}')])

                    # H_i_j_t => H_i_j_t-1 | Q1_i_j_t-1 | S2_i_j_t-1
                    if observed_state in [Healthy, UNKNOWN] and observed_state_last_time in [Sick, Healthy, Quarantined, UNKNOWN]:
                        clauses_dynamics.append([-index_by_variable.id(f'{Healthy}_{row}_{col}_{time}'),
                                         index_by_variable.id(f'{Healthy}_{row}_{col}_{time - 1}'),
                                         index_by_variable.id(f'{Quarantined_1}_{row}_{col}_{time - 1}'),
                                         index_by_variable.id(f'{Sick_2}_{row}_{col}_{time - 1}')])


                formula.extend(clauses_dynamics)




        # at most police_num police, at most medics_num medics

        if time > 0:
            if num_police > 0:
                police_clause = CardEnc.atmost(lits=all_Q0_or_unknown, bound=num_police, vpool=index_by_variable)
                formula.extend(police_clause)
            else:
                for clause_q0 in all_Q0_or_unknown:
                    formula.append([-clause_q0])


            if num_medics > 0:
                medics_clause = CardEnc.atmost(lits=all_I0_or_unknown, bound=num_medics, vpool=index_by_variable)
                formula.extend(medics_clause)
            else:
                for clause_i0 in all_I0_or_unknown:
                    formula.append([-clause_i0])



        if time < times - 1:

            if num_healthy_or_unknown_tiles > 0:

                if num_medics == 1:

                    at_least_one_medic = CardEnc.atleast(lits=all_I0_or_unknown_next_time, bound=num_medics, vpool=index_by_variable)

                    for row_c, col_c in all_healthy_or_unknown:

                        new_clause = []

                        new_clause.append(-index_by_variable.id(f'{Healthy}_{row_c}_{col_c}_{time}'))

                        for clause in at_least_one_medic.clauses:
                            clause_copy = copy.deepcopy(new_clause)
                            clause_copy = clause_copy + clause
                            formula.extend([clause_copy])


                if num_medics > 1:

                    # k <= num medics
                    # (k squares are H and all others are not) => (those k squares will be I0 and others will not)
                    for k in range(min(num_medics, num_healthy_or_unknown_tiles) + 1):

                        for cur_healthy_squares in itertools.combinations(all_healthy_or_unknown, k):


                            cur_non_healthy_squares = [(row_n, col_n) for (row_n, col_n) in all_row_col if (row_n, col_n) not in cur_healthy_squares]

                            new_clause = []

                            for (row_c, col_c) in cur_healthy_squares:
                                new_clause.append(-index_by_variable.id(f'{Healthy}_{row_c}_{col_c}_{time}'))

                            for (row_n, col_n) in cur_non_healthy_squares:
                                new_clause.append(index_by_variable.id(f'{Healthy}_{row_n}_{col_n}_{time}'))


                            for (row_c, col_c) in cur_healthy_squares:
                                clause_copy = copy.deepcopy(new_clause)
                                clause_copy.append(index_by_variable.id(f'{Immune_0}_{row_c}_{col_c}_{time + 1}'))
                                formula.extend([clause_copy])


                            # for (row_n, col_n) in cur_non_healthy_squares:
                            #     clause_copy = copy.deepcopy(new_clause)
                            #     clause_copy.append(-index_by_variable.id(f'{Immune_0}_{row_n}_{col_n}_{time + 1}'))
                            #     formula.extend([clause_copy])


                    # # k > num medics
                    # # (k squares are H and all others are not) => (exactly (num medics) squares will be I0 and others will not)

                    if num_healthy_or_unknown_tiles > num_medics:

                        for k in range(num_medics + 1, num_healthy_or_unknown_tiles + 1):

                            for cur_healthy_squares in itertools.combinations(all_healthy_or_unknown, k):


                                cur_non_healthy_squares = [(row_n, col_n) for (row_n, col_n) in all_row_col if
                                                           (row_n, col_n) not in cur_healthy_squares]

                                new_clause = []
                                curr_possible_I0 = []

                                for (row_c, col_c) in cur_healthy_squares:
                                    new_clause.append(-index_by_variable.id(f'{Healthy}_{row_c}_{col_c}_{time}'))
                                    curr_possible_I0.append(index_by_variable.id(f'{Immune_0}_{row_c}_{col_c}_{time + 1}'))

                                for (row_n, col_n) in cur_non_healthy_squares:
                                    new_clause.append(index_by_variable.id(f'{Healthy}_{row_n}_{col_n}_{time}'))


                                exactly_num_medics_IO = CardEnc.atleast(lits=curr_possible_I0, bound=num_medics, vpool=index_by_variable)


                                for clause in exactly_num_medics_IO.clauses:
                                    clause_copy = copy.deepcopy(new_clause)
                                    clause_copy = clause_copy + clause
                                    formula.extend([clause_copy])


            if num_sick_or_unknown_tiles > 0:

                if num_police == 1:

                    at_least_one_police = CardEnc.atleast(lits=all_Q0_or_unknown_next_time, bound=num_police, vpool=index_by_variable)

                    for row_c, col_c in all_sick_or_unknown:


                        new_clause = []
                        new_clause.append(-index_by_variable.id(f'{Sick_0}_{row_c}_{col_c}_{time}'))
                        for clause in at_least_one_police.clauses:
                            clause_copy = copy.deepcopy(new_clause)
                            clause_copy = clause_copy + clause
                            formula.extend([clause_copy])


                        new_clause = []
                        new_clause.append(-index_by_variable.id(f'{Sick_1}_{row_c}_{col_c}_{time}'))
                        for clause in at_least_one_police.clauses:
                            clause_copy = copy.deepcopy(new_clause)
                            clause_copy = clause_copy + clause
                            formula.extend([clause_copy])


                        new_clause = []
                        new_clause.append(-index_by_variable.id(f'{Sick_2}_{row_c}_{col_c}_{time}'))
                        for clause in at_least_one_police.clauses:
                            clause_copy = copy.deepcopy(new_clause)
                            clause_copy = clause_copy + clause
                            formula.extend([clause_copy])


                if num_police > 0:

                    # k <= num police
                    # (k squares are S0/S1/S2 (choose all combinations of k squares of S0/S1/S2) and all others are not S0/S1/S2)
                    # => (those k squares will be Q0 and others will not)
                    for k in range(min(num_police, num_sick_or_unknown_tiles) + 1):

                        for cur_sick_squares in itertools.combinations(all_sick_or_unknown, k):


                            cur_non_sick_squares = [(row_n, col_n) for (row_n, col_n) in all_row_col if
                                                    (row_n, col_n) not in cur_sick_squares]

                            for sickness_combinations in itertools.combinations_with_replacement(sick_dict_times(time), k):

                                new_clause = []

                                current_possible_Q0 = []

                                for S_c, (row_c, col_c) in zip(sickness_combinations, cur_sick_squares):
                                    new_clause.append(-index_by_variable.id(f'{S_c}_{row_c}_{col_c}_{time}'))
                                    current_possible_Q0.append(index_by_variable.id(f'{Quarantined_0}_{row_c}_{col_c}_{time}'))


                                for sick_state in sick_states:
                                    for (row_n, col_n) in cur_non_sick_squares:
                                        new_clause.append(index_by_variable.id(f'{sick_state}_{row_n}_{col_n}_{time}'))


                                for (row_c, col_c) in cur_sick_squares:
                                    clause_copy = copy.deepcopy(new_clause)
                                    clause_copy.append(index_by_variable.id(f'{Quarantined_0}_{row_c}_{col_c}_{time + 1}'))
                                    formula.extend([clause_copy])


                                # for (row_n, col_n) in cur_non_sick_squares:
                                #     clause_copy = copy.deepcopy(new_clause)
                                #     clause_copy.append(-index_by_variable.id(f'{Quarantined_0}_{row_n}_{col_n}_{time + 1}'))
                                #     formula.extend([clause_copy])



                    # k > num police
                    # (k squares are S0/S1/S2 and all others are not) => (exactly (num police) squares will be Q0 and others will not)

                    if num_sick_or_unknown_tiles > num_police:

                        for k in range(num_police + 1, num_sick_or_unknown_tiles + 1):

                            for cur_sick_squares in itertools.combinations(all_sick_or_unknown, k):

                                cur_non_sick_squares = [(row_n, col_n) for (row_n, col_n) in all_row_col if
                                                        (row_n, col_n) not in cur_sick_squares]

                                for sickness_combinations in itertools.combinations_with_replacement(sick_dict_times(time), k):

                                    new_clause = []
                                    curr_possible_Q0 = []


                                    for S_c, (row_c, col_c) in zip(sickness_combinations, cur_sick_squares):
                                        new_clause.append(-index_by_variable.id(f'{S_c}_{row_c}_{col_c}_{time}'))
                                        curr_possible_Q0.append(index_by_variable.id(f'{Quarantined_0}_{row_c}_{col_c}_{time+1}'))

                                    for sick_state in sick_states:
                                        for (row_n, col_n) in cur_non_sick_squares:
                                            new_clause.append(index_by_variable.id(f'{sick_state}_{row_n}_{col_n}_{time}'))

                                    exactly_num_police_QO = CardEnc.atleast(lits=curr_possible_Q0, bound=num_police, vpool=index_by_variable)

                                    for clause in exactly_num_police_QO.clauses:
                                        clause_copy = copy.deepcopy(new_clause)
                                        clause_copy = clause_copy + clause
                                        formula.extend([clause_copy])

    return formula


def get_query_formula(query, index_by_variable):

    (row, col), time, state = query

    formula = CNF()

    if state == Sick:
        formula.append([index_by_variable.id(f'{state}_{row}_{col}_{time}') for state in sick_dict_times(time)])

    elif state == Quarantined:
        formula.append([index_by_variable.id(f'{state}_{row}_{col}_{time}') for state in quarantine_dict_times(time)])

    elif state == Immune:
        formula.append([index_by_variable.id(f'{state}_{row}_{col}_{time}') for state in immune_dict_times(time)])

    else:
        formula.append([index_by_variable.id(f'{state}_{row}_{col}_{time}')])

    return formula


def get_all_other_possible_queries(query):
    (row, col), time, state = query

    possible_queries = []

    for other_state in possible_states_no_replicas:
        if other_state != state:
            possible_queries.append(((row, col), time, other_state))

    return possible_queries


def print_state(state, columns_no, rows_no):

    moves = [" "] + [str(col) for col in range(columns_no)]

    print(('\t').join(moves))

    for row in range(rows_no):
        print()

        moves = [str(row)]
        for col in range(columns_no):
            moves.append(state[row][col])

        print(('\t').join(moves))


def printable_solution(solution, times, number_of_rows, number_of_cols , query, index_by_variable):

    print(f"query {query} :")

    if solution is None:
        print("No solution\n")
        return

    observations = []
    for time in range(times):
        observations.append([])
        for row in range(number_of_rows):
            observations[-1].append([])
            for col in range(number_of_cols):
                observations[-1][-1].append(0)


    all_ones = []
    for index in solution:
        if index > 0:

            if index_by_variable.obj(abs(index)) is not None:

                all_ones.append(str(index_by_variable.obj(abs(index))))

                state, row, col, time = str(index_by_variable.obj(abs(index))).split("_")

                row = int(row)
                col = int(col)
                time = int(time)

                observations[time][row][col] = state


    for time in range(times):
        print(f"time {time}:")
        print_state(observations[time], number_of_cols, number_of_rows)
        print(f"\n")


def solve_given_query(query, all_given_clauses, times, number_of_rows, number_of_cols, index_by_variable, original_query=False, print_flag=False):
    g = Glucose4()

    for c in all_given_clauses:
        g.add_clause(c)

    query_formula = get_query_formula(query, index_by_variable)

    for c in query_formula.clauses:
        g.add_clause(c)

    query_sol = g.solve()

    if print_flag:

        if query_sol:
            if original_query:
                print(f"Original query: {query}")
            else:
                print(f"Not original query: {query}")

            printable_solution(g.get_model(), times, number_of_rows, number_of_cols, query, index_by_variable)

        else:
            if original_query:
                print(f"Original query: {query}: No solution\n")
            else:
                print(f"Not original query: {query}: No solution\n")

    return query_sol


def solve_problem(input, *args, **kwargs):

    print_flag = kwargs.get("print_flag", IS_PRINT)
    if print_flag:
        print("\n")

    result_dict = {}

    num_police = input["police"]
    num_medics = input["medics"]

    observations = input["observations"]
    times = len(observations)
    number_of_rows = len(observations[0])
    number_of_cols = len(observations[0][0])


    index_by_variable = get_all_problem_variables(observations, number_of_rows, number_of_cols)

    formula = initialize_formula(times, number_of_rows, number_of_cols, index_by_variable, num_police, num_medics, observations)


    for query in input["queries"]:

        query_sol = solve_given_query(query, formula.clauses, times, number_of_rows, number_of_cols, index_by_variable, original_query=True, print_flag=print_flag)

        if query_sol == False:
            result_dict[query] = 'F'
            continue

        else:

            flag = True
            for other_query in get_all_other_possible_queries(query):
                if solve_given_query(other_query, formula.clauses, times, number_of_rows, number_of_cols, index_by_variable, print_flag=print_flag):
                    result_dict[query] = '?'
                    flag = False
                    break

            if flag:
                result_dict[query] = 'T'


    return result_dict