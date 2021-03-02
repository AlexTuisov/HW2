from pysat.solvers import Glucose3
import numpy as np

ids = ['322723982', '322593377']

def add_observation(observation, solver, counter):
    # For each entry in the observation matrix we intend three atoms: U, H, S
    # If the entry is known(not ?), only one of the atoms is TRUE, while the other two are FALSE
    # If the entry is unknown(?), we don't know which of the three atoms is the correct one

    n, m = len(observation), len(observation[0])
    for i in range(n):
        for j in range(m):
            if observation[i][j] == 'U':
                solver.append([counter])
                counter += 1
                solver.append([-counter])
                counter += 1
                solver.append([-counter])
                counter += 1
            elif observation[i][j] == 'H':
                solver.append([-counter])
                counter += 1
                solver.append([counter])
                counter += 1
                solver.append([-counter])
                counter += 1
            elif observation[i][j] == 'S':
                solver.append([-counter])
                counter += 1
                solver.append([-counter])
                counter += 1
                solver.append([counter])
                counter += 1
            elif observation[i][j] == '?':
                solver.append([counter, -counter])
                counter += 1
                solver.append([counter, -counter])
                counter += 1
                solver.append([counter, -counter])
                counter += 1
    return counter


def add_observation2(observation, observation_num, total_observations, solver, counter, observations):
    # For each entry in the observation matrix we intend five atoms: U, H, S, Q, I
    # If the entry is known(not ?), only one of the atoms is TRUE, while the other four are FALSE
    # If the entry is unknown(?), we don't know which of the five atoms is the correct one

    n, m = len(observation), len(observation[0])
    for i in range(n):
        for j in range(m):
            if observation[i][j] == 'U':
                solver.append([counter])
                counter += 1
                solver.append([-counter])
                counter += 1
                solver.append([-counter])
                counter += 1
                solver.append([-counter])
                counter += 1
                solver.append([-counter])
                counter += 1
            elif observation[i][j] == 'H':
                solver.append([-counter])
                counter += 1
                solver.append([counter])
                counter += 1
                solver.append([-counter])
                counter += 1
                solver.append([-counter])
                counter += 1
                solver.append([-counter])
                counter += 1
            elif observation[i][j] == 'S':
                solver.append([-counter])
                counter += 1
                solver.append([-counter])
                counter += 1
                solver.append([counter])
                counter += 1
                solver.append([-counter])
                counter += 1
                solver.append([-counter])
                counter += 1
            elif observation[i][j] == 'Q':
                solver.append([-counter])
                counter += 1
                solver.append([-counter])
                counter += 1
                solver.append([-counter])
                counter += 1
                solver.append([counter])
                counter += 1
                solver.append([-counter])
                counter += 1
                if observations[observation_num-2][i][j] == 'S':
                    get_out_of_Q2(observation, solver, i, j, observation_num, total_observations)
            elif observation[i][j] == 'I':
                solver.append([-counter])
                counter += 1
                solver.append([-counter])
                counter += 1
                solver.append([-counter])
                counter += 1
                solver.append([-counter])
                counter += 1
                solver.append([counter])
                counter += 1
            elif observation[i][j] == '?':
                if observation_num == 1:
                    solver.append([counter, -counter])
                    counter += 1
                    solver.append([counter, -counter])
                    counter += 1
                    solver.append([counter, -counter])
                    counter += 1
                    solver.append([-counter])
                    counter += 1
                    solver.append([-counter])
                    counter += 1
                else:
                    solver.append([counter, -counter])
                    counter += 1
                    solver.append([counter, -counter])
                    counter += 1
                    solver.append([counter, -counter])
                    counter += 1
                    solver.append([counter, -counter])
                    counter += 1
                    solver.append([counter, -counter])
                    counter += 1
    return counter


def spread_disease(observation, solver, observation_num, total_observations):
    # For each 'U' entry in the observation matrix we update all of its appearances to be also 'U'
    # For each 'H' entry in the observation matrix we check if one of its neighbors is 'S'
    # If one of its neighbors is 'S', this entry becomes 'S' for three turns, starting from the next observation
    # WE also check if one of its neighbors is '?', and if its false we update its next appearance
    # to be 'H'

    n, m = len(observation), len(observation[0])
    for i in range(n):
        for j in range(m):
            if observation[i][j] == 'U':
                all_U(observation, solver, i, j, total_observations)
            if observation[i][j] == 'H' and observation_num < total_observations:
                if check_infected(observation, i, j, 'S'):
                    solver.append([-(3 * (n * m * observation_num + n * i + j) + 1)])
                    solver.append([-(3*(n*m*observation_num + n*i + j) + 2)])
                    solver.append([3 * (n * m * observation_num + n * i + j) + 3])
                    get_healthy(observation, solver, i, j, observation_num + 1, total_observations)
                elif not check_infected(observation, i, j, '?'):
                    solver.append([-(3 * (n * m * observation_num + n * i + j) + 1)])
                    solver.append([3 * (n * m * observation_num + n * i + j) + 2])
                    solver.append([-(3 * (n * m * observation_num + n * i + j) + 3)])


def all_U(observation, solver, i, j, total_observations):
    n, m = len(observation), len(observation[0])
    for t in range(1, total_observations + 1):
        solver.append([3 * (n * m * t + n * i + j) + 1])
        solver.append([-(3 * (n * m * t + n * i + j) + 2)])
        solver.append([-(3 * (n * m * t + n * i + j) + 3)])


def all_U_2(observation, solver, i, j, total_observations):
    n, m = len(observation), len(observation[0])
    for t in range(0, total_observations):
        solver.append([5 * (n * m * t + n * i + j) + 1])
        solver.append([-(5 * (n * m * t + n * i + j) + 2)])
        solver.append([-(5 * (n * m * t + n * i + j) + 3)])
        solver.append([-(5 * (n * m * t + n * i + j) + 4)])
        solver.append([-(5 * (n * m * t + n * i + j) + 5)])


def all_I(observation, observation_num, solver, i, j, total_observations):
    n, m = len(observation), len(observation[0])
    for t in range(observation_num, total_observations):
        solver.append([-(5 * (n * m * t + n * i + j) + 1)])
        solver.append([-(5 * (n * m * t + n * i + j) + 2)])
        solver.append([-(5 * (n * m * t + n * i + j) + 3)])
        solver.append([-(5 * (n * m * t + n * i + j) + 4)])
        solver.append([5 * (n * m * t + n * i + j) + 5])


def spread_disease2(police, medics, observation, solver, observation_num, total_observations, all_observations):
    # For each 'U' entry in the observation matrix we update all its appearence to be also 'U'
    # For each 'I' entry in the observation matrix we update its next appearence to be also 'I'
    # For each 'H' entry in the observation matrix we check if one of its neighbors is 'S'
    # If one of its neighbors is 'S', this entry becomes 'S' for three turns (or not...),
    # starting from the next observation
    # WE also check if one of its neighbors is '?', and if its false we update its next appearence
    # to be 'H' or 'I' (if medics > 0)

    n, m = len(observation), len(observation[0])
    for i in range(n):
        for j in range(m):
            if observation[i][j] == 'U' and observation_num < total_observations:
                all_U_2(observation, solver, i, j, total_observations)
            if observation[i][j] == 'I' and observation_num < total_observations:
                all_I(observation, observation_num, solver, i, j, total_observations)
            if observation[i][j] == 'H' and observation_num < total_observations:
                if check_infected(observation, i, j, 'S'):
                    solver.append([-(5 * (n * m * observation_num + n * i + j) + 1)])
                    solver.append([-(5*(n * m * observation_num + n*i + j) + 4)])
                    if police > 0:
                        if medics > 0:
                            solver.append([5 * (n * m * observation_num + n * i + j) + 2,
                                           5 * (n * m * observation_num + n * i + j) + 3,
                                           5 * (n * m * observation_num + n * i + j) + 5])
                        else:
                            solver.append([5 * (n * m * observation_num + n * i + j) + 2,
                                           5 * (n * m * observation_num + n * i + j) + 3])
                            solver.append([-(5 * (n * m * observation_num + n * i + j) + 5)])
                    else:
                        solver.append([-(5 * (n * m * observation_num + n * i + j) + 2)])
                        solver.append([5 * (n * m * observation_num + n * i + j) + 3,
                                       5 * (n * m * observation_num + n * i + j) + 5])
                    if observation_num < total_observations:
                        if all_observations[observation_num][i][j] == 'S':
                            get_healthy2(police, observation, solver, i, j, observation_num + 1, total_observations)
                        if all_observations[observation_num][i][j] == '?':
                            if medics == 0:
                                if not check_infected(all_observations[observation_num], i, j, 'S'):
                                    if not check_infected(all_observations[observation_num], i, j, '?'):
                                        get_healthy2(police, observation, solver, i, j, observation_num + 1,
                                                     total_observations)
                elif not check_infected(observation, i, j, '?'):
                    if medics > 0:
                        solver.append([-(5 * (n * m * observation_num + n * i + j) + 1)])
                        solver.append([-(5 * (n * m * observation_num + n * i + j) + 3)])
                        solver.append([5 * (n * m * observation_num + n * i + j) + 2,
                                       5 * (n * m * observation_num + n * i + j) + 5])
                        solver.append([-(5 * (n * m * observation_num + n * i + j) + 4)])
                    else:
                        solver.append([-(5 * (n * m * observation_num + n * i + j) + 1)])
                        solver.append([(5 * (n * m * observation_num + n * i + j) + 2)])
                        solver.append([-(5 * (n * m * observation_num + n * i + j) + 3)])
                        solver.append([-(5 * (n * m * observation_num + n * i + j) + 4)])
                        solver.append([-(5 * (n * m * observation_num + n * i + j) + 5)])

def check_infected(observation, i, j, char):
    # This function gets an observation and checks whether one of (i,j) entry's neighbors is 'S'

    n, m = len(observation), len(observation[0])
    if i != 0:
        if observation[i-1][j] == char:
            return True
    if j != 0:
        if observation[i][j-1] == char:
            return True
    if i != n-1:
        if observation[i+1][j] == char:
            return True
    if j != m-1:
        if observation[i][j+1] == char:
            return True
    return False


def find_firstSicks(observation, solver, total_observations):
    # This function gets the first observation, find the 'S' entries
    # and call the function get_healty with those 'S' entries it found

    n, m = len(observation), len(observation[0])
    for i in range(n):
        for j in range(m):
            if observation[i][j] == 'S':
                get_healthy(observation, solver, i, j, 1, total_observations)


def find_firstSicks2(police, medics, observation, solver, total_observations):
    # This function gets the first observation, find the 'S' entries
    # and call the function get_healty2 with those 'S' entries it found

    n, m = len(observation), len(observation[0])
    for i in range(n):
        for j in range(m):
            if observation[i][j] == 'S':
                get_healthy2(police, observation, solver, i, j, 1, total_observations)


def get_healthy(observation, solver, i, j, observation_num, total_observations):
    # This function gets an entry in an observation, known to be 'S', and updates it to be 'S' in the next two
    # observations, then 'H' in the third next one, given that those observations exist

    counter = observation_num
    n, m = len(observation), len(observation[0])
    if counter < total_observations:
        solver.append([-(3 * (n * m * observation_num + n * i + j) + 1)])
        solver.append([-(3 * (n * m * observation_num + n * i + j) + 2)])
        solver.append([3 * (n * m * observation_num + n * i + j) + 3])
        counter += 1
    if counter < total_observations:
        solver.append([-(3 * (n * m * counter + n * i + j) + 1)])
        solver.append([-(3 * (n * m * counter + n * i + j) + 2)])
        solver.append([3 * (n * m * counter + n * i + j) + 3])
        counter += 1
    if counter < total_observations:
        solver.append([-(3 * (n * m * counter + n * i + j) + 1)])
        solver.append([3 * (n * m * counter + n * i + j) + 2])
        solver.append([-(3 * (n * m * counter + n * i + j) + 3)])


def get_healthy2(police, observation, solver, i, j, observation_num, total_observations):
    # This function gets an entry in an observation, known to be 'S', and updates it to be 'S' or 'Q' in the next two
    # observations, then 'H' or 'Q' in the third next one, given that those observations exist

    counter = observation_num
    n, m = len(observation), len(observation[0])
    if counter < total_observations:
        if police > 0:
            solver.append([-(5 * (n * m * counter + n * i + j) + 1)])
            solver.append([-(5 * (n * m * counter + n * i + j) + 2)])
            solver.append([5 * (n * m * counter + n * i + j) + 3,
                           5 * (n * m * counter + n * i + j) + 4])
            solver.append([-(5 * (n * m * counter + n * i + j) + 5)])
        else:
            solver.append([-(5 * (n * m * counter + n * i + j) + 1)])
            solver.append([-(5 * (n * m * counter + n * i + j) + 2)])
            solver.append([(5 * (n * m * counter + n * i + j) + 3)])
            solver.append([-(5 * (n * m * counter + n * i + j) + 4)])
            solver.append([-(5 * (n * m * counter + n * i + j) + 5)])
        counter += 1
    if counter < total_observations:
        if police > 0:
            solver.append([-(5 * (n * m * counter + n * i + j) + 1)])
            solver.append([-(5 * (n * m * counter + n * i + j) + 2)])
            solver.append([5 * (n * m * counter + n * i + j) + 3,
                           5 * (n * m * counter + n * i + j) + 4])
            solver.append([-(5 * (n * m * counter + n * i + j) + 5)])
        else:
            solver.append([-(5 * (n * m * counter + n * i + j) + 1)])
            solver.append([-(5 * (n * m * counter + n * i + j) + 2)])
            solver.append([(5 * (n * m * counter + n * i + j) + 3)])
            solver.append([-(5 * (n * m * counter + n * i + j) + 4)])
            solver.append([-(5 * (n * m * counter + n * i + j) + 5)])
        counter += 1
    if counter < total_observations:
        if police > 0:
            solver.append([-(5 * (n * m * counter + n * i + j) + 1)])
            solver.append([-(5 * (n * m * counter + n * i + j) + 3)])
            solver.append([5 * (n * m * counter + n * i + j) + 2,
                           5 * (n * m * counter + n * i + j) + 4])
            solver.append([-(5 * (n * m * counter + n * i + j) + 5)])
        else:
            solver.append([-(5 * (n * m * counter + n * i + j) + 1)])
            solver.append([5 * (n * m * counter + n * i + j) + 2])
            solver.append([-(5 * (n * m * counter + n * i + j) + 3)])
            solver.append([-(5 * (n * m * counter + n * i + j) + 4)])
            solver.append([-(5 * (n * m * counter + n * i + j) + 5)])


def get_out_of_Q2(observation, solver, i, j, observation_num, total_observations):
    # This function gets an entry in an observation, known to be 'S', and updates it to be 'S' in the next two
    # observations, then 'H' in the third next one, given that those observations exist

    counter = observation_num
    n, m = len(observation), len(observation[0])
    if counter < total_observations:
        solver.append([-(5 * (n * m * observation_num + n * i + j) + 1)])
        solver.append([-(5 * (n * m * observation_num + n * i + j) + 2)])
        solver.append([-(5 * (n * m * observation_num + n * i + j) + 3)])
        solver.append([5 * (n * m * observation_num + n * i + j) + 4])
        solver.append([-(5 * (n * m * observation_num + n * i + j) + 5)])
        counter += 1
    if counter < total_observations:
        solver.append([-(5 * (n * m * observation_num + n * i + j) + 1)])
        solver.append([5 * (n * m * observation_num + n * i + j) + 2])
        solver.append([-(5 * (n * m * observation_num + n * i + j) + 3)])
        solver.append([-(5 * (n * m * observation_num + n * i + j) + 4)])
        solver.append([-(5 * (n * m * observation_num + n * i + j) + 5)])

def check_unknown(observation, solver, i, j, observation_num, total_observations, placement):
    # this function get some placement and an observation to place it in and add all the clauses attached to it

    n, m = len(observation), len(observation[0])
    new_observation = [list(x) for x in observation]
    new_observation[i][j] = placement
    add_observation(new_observation, solver, 1+3*n*m*observation_num)
    if placement == 'S' and observation_num == 1:
        find_firstSicks(new_observation, solver, total_observations)
    spread_disease(new_observation, solver, 1 + observation_num, total_observations)

def check_unknown2(police, medics, observation, solver, i, j, observation_num, total_observations,
                   placement, observations):
    # this function get some placement and an observation to place it in and add all the clauses attached to it

    n, m = len(observation), len(observation[0])
    new_observation = [list(x) for x in observation]
    new_observation[i][j] = placement
    add_observation2(new_observation, observation_num + 1, total_observations, solver,
                     1+5*n*m*observation_num, observations)
    if placement == 'S' and observation_num == 1:
        find_firstSicks2(police, medics, new_observation, solver, total_observations)
    if placement == 'Q' and observation_num == 1:
        get_out_of_Q2(observation, solver, i, j, observation_num + 1, total_observations)
    spread_disease2(police, medics, new_observation, solver, 1 + observation_num, total_observations, observations)


def update_solver(g: Glucose3, clauses_list):
    for clause in clauses_list:
        g.add_clause(clause)


def no_police_and_medics(input):
    # answer the query if there are not medics and there are not police

    police_num, med_num, observations = input['police'], input['medics'], input['observations']
    queries = input['queries']
    total_observations = len(observations)
    solver = []
    counter = 1
    for i in range(total_observations):
        counter = add_observation(observations[i], solver, counter)
    find_firstSicks(observations[0], solver, total_observations)
    for i in range(total_observations):
        spread_disease(observations[i], solver, i + 1, total_observations)
    answers = {}
    for query in queries:
        indexes = ['U', 'H', 'S']
        values = []
        gs = []
        g1 = Glucose3()
        g2 = Glucose3()
        g3 = Glucose3()
        update_solver(g1, solver)
        update_solver(g2, solver)
        update_solver(g3, solver)
        gs.append(g1)
        gs.append(g2)
        gs.append(g3)
        for i in range(3):
            updates = []
            check_unknown(observations[query[1]], updates, query[0][0], query[0][1], query[1], total_observations,
                          indexes[i])
            update_solver(gs[i], updates)
            values.append(gs[i].solve())
        if query[2] == 'U':
            if not values[0]:
                answers[query] = 'F'
            elif values[1] or values[2]:
                answers[query] = '?'
            else:
                answers[query] = 'T'
        if query[2] == 'H':
            if not values[1]:
                answers[query] = 'F'
            elif values[0] or values[2]:
                answers[query] = '?'
            else:
                answers[query] = 'T'
        if query[2] == 'S':
            if not values[2]:
                answers[query] = 'F'
            elif values[0] or values[1]:
                answers[query] = '?'
            else:
                answers[query] = 'T'
    return answers


def check_possible(power_num, power_name, observation, observation_num, observations):
    # This function gets an observation and medics or police andchecks whehter all forces have been used

    n, m = len(observation), len(observation[0])
    count = 0
    if observation_num == 0:
        return False
    for i in range(n):
        for j in range(m):
            if power_name == "police" and observation[i][j] == 'Q' and observations[observation_num-1][i][j] != 'Q':
                count += 1
            if power_name == "medics" and observation[i][j] == 'I' and observations[observation_num-1][i][j] != 'I':
                count += 1
    if count < power_num:
        return True
    return False


def check_others(power_num, power_name, observation, observation_num, observations):

    n, m = len(observation), len(observation[0])
    counter = 0
    for i in range(n):
        for j in range(m):
            if check_possible(power_num, power_name, observation, observation_num, observations) and observation_num > 0:
                if power_name == 'police':
                    if observation[i][j] == 'S':
                        counter += 1
                if power_name == 'medics':
                    if observation[i][j] == 'H':
                        counter += 1
    if counter > 1:
        return False
    return True


def yes_police_and_medics(input):
    # answer the query if there are medics or police forces

    police_num, med_num, observations = input['police'], input['medics'], input['observations']
    queries = input['queries']
    total_observations = len(observations)
    solver = []
    counter = 1
    for i in range(total_observations):
        counter = add_observation2(observations[i], i+1, total_observations, solver, counter, observations)
    find_firstSicks2(police_num, med_num, observations[0], solver, total_observations)
    for i in range(total_observations):
        spread_disease2(police_num, med_num, observations[i], solver, i + 1, total_observations, observations)
    answers = {}
    for query in queries:
        indexes = ['U', 'H', 'S', 'Q', 'I']
        values = []
        gs = []
        g1 = Glucose3()
        g2 = Glucose3()
        g3 = Glucose3()
        g4 = Glucose3()
        g5 = Glucose3()
        update_solver(g1, solver)
        update_solver(g2, solver)
        update_solver(g3, solver)
        update_solver(g4, solver)
        update_solver(g5, solver)
        gs.append(g1)
        gs.append(g2)
        gs.append(g3)
        gs.append(g4)
        gs.append(g5)
        for i in range(3):
            if i == 1:
                if check_possible(med_num, "medics", observations[query[1]], query[1], observations) and query[1] > 0:
                    if observations[query[1]-1][query[0][0]][query[0][1]] == 'H' and \
                            check_others(med_num, "medics", observations[query[1]], query[1], observations):
                        values.append(False)
                        continue
            if i == 2:
                if check_possible(police_num, "police", observations[query[1]], query[1], observations) and query[1] >0:
                    if observations[query[1] - 1][query[0][0]][query[0][1]] == 'S' and \
                            check_others(police_num, "police", observations[query[1]], query[1], observations):
                        values.append(False)
                        continue
            updates = []
            check_unknown2(police_num, med_num, observations[query[1]], updates, query[0][0], query[0][0],
                           query[1], total_observations, indexes[i], observations)
            update_solver(gs[i], updates)
            values.append(gs[i].solve())
        if check_possible(police_num, "police", observations[query[1]], query[1], observations):
            updates = []
            check_unknown2(police_num, med_num, observations[query[1]], updates, query[0][0], query[0][1],
                           query[1], total_observations, indexes[3], observations)
            update_solver(gs[3], updates)
            values.append(gs[3].solve())
        else:
            values.append(False)
        if check_possible(med_num, "medics", observations[query[1]], query[1], observations):
            updates = []
            check_unknown2(police_num, med_num, observations[query[1]], updates, query[0][0], query[0][1],
                           query[1], total_observations, indexes[4], observations)
            update_solver(gs[4], updates)
            values.append(gs[4].solve())
        else:
            values.append(False)
        if query[2] == 'U':
            if not values[0]:
                answers[query] = 'F'
            elif values[1] or values[2] or values[3] or values[4]:
                answers[query] = '?'
            else:
                answers[query] = 'T'
        if query[2] == 'H':
            if not values[1]:
                answers[query] = 'F'
            elif values[0] or values[2] or values[3] or values[4]:
                answers[query] = '?'
            else:
                answers[query] = 'T'
        if query[2] == 'S':
            if not values[2]:
                answers[query] = 'F'
            elif values[0] or values[1] or values[3] or values[4]:
                answers[query] = '?'
            else:
                answers[query] = 'T'
        if query[2] == 'Q':
            if not values[3]:
                answers[query] = 'F'
            elif values[0] or values[1] or values[2] or values[4]:
                answers[query] = '?'
            else:
                answers[query] = 'T'
        if query[2] == 'I':
            if not values[4]:
                answers[query] = 'F'
            elif values[0] or values[1] or values[2] or values[3]:
                answers[query] = '?'
            else:
                answers[query] = 'T'
    return answers


def solve_problem(input):
    police_num, med_num, observations = input['police'], input['medics'], input['observations']
    if police_num == 0 and med_num == 0:
        return no_police_and_medics(input)
    else:
        return yes_police_and_medics(input)

