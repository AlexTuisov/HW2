from pysat.solvers import Glucose3

ids = ['313471435', '206388266']


def initialize_variables(observations):
    """
    observations = input["observations"]
    """
    current_number = 1
    variable_to_num = {}
    length, width = len(observations[0][0]), len(observations[0][:])
    for i in range(length):
        for j in range(width):
            for t in range(len(observations)):
                for state in {"S", "H", "I", "Q", "U"}:
                    variable_to_num[(i, j, t, state)] = current_number
                    current_number += 1
    return variable_to_num


def the_healthy_neighbor(r_index, c_index, obs_t):
    col_len = len(obs_t[0])
    row_len = len(obs_t[:])
    res = []
    if 0 <= (c_index + 1) < col_len:
        if obs_t[r_index][c_index + 1] == 'H':
            res.append([r_index, c_index + 1])

    if 0 <= (c_index - 1):
        if obs_t[r_index][c_index - 1] == 'H':
            res.append([r_index, c_index - 1])

    if 0 <= (r_index + 1) < row_len:
        if obs_t[r_index + 1][c_index] == 'H':
            res.append([r_index + 1, c_index])

    if 0 <= r_index - 1:
        if obs_t[r_index - 1][c_index] == 'H':
            res.append([r_index - 1, c_index])

    return res

def has_sick_neighbor(r_index, c_index, obs_t):
    col_len = len(obs_t[0])
    row_len = len(obs_t[:])
    if 0 <= (c_index + 1) < col_len:
        if obs_t[r_index][c_index + 1] == 'S':
            return True

    if 0 <= (c_index - 1):
        if obs_t[r_index][c_index - 1] == 'S':
            return True

    if 0 <= (r_index + 1) < row_len:
        if obs_t[r_index + 1][c_index] == 'S':
            return True

    if 0 <= r_index - 1:
        if obs_t[r_index - 1][c_index] == 'S':
            return True

    return False


def the_infecting_neighbor(r_index, c_index, obs_t):
    col_len = len(obs_t[0])
    row_len = len(obs_t[:])
    res = []
    if 0 <= (c_index + 1) < col_len:
        if obs_t[r_index][c_index + 1] == 'S':
            res.append([r_index, c_index + 1])

    if 0 <= (c_index - 1):
        if obs_t[r_index][c_index - 1] == 'S':
            res.append([r_index, c_index - 1])

    if 0 <= (r_index + 1) < row_len:
        if obs_t[r_index + 1][c_index] == 'S':
            res.append([r_index + 1, c_index])

    if 0 <= r_index - 1:
        if obs_t[r_index - 1][c_index] == 'S':
            res.append([r_index - 1, c_index])

    return res


def has_question_mark_neighbor(r_index, c_index, obs_t):
    col_len = len(obs_t[0])
    row_len = len(obs_t[:])
    if 0 <= (c_index + 1) < col_len:
        if obs_t[r_index][c_index + 1] == '?':
            return True

    if 0 <= (c_index - 1):
        if obs_t[r_index][c_index - 1] == '?':
            return True

    if 0 <= (r_index + 1) < row_len:
        if obs_t[r_index + 1][c_index] == '?':
            return True

    if 0 <= r_index - 1:
        if obs_t[r_index - 1][c_index] == '?':
            return True

    return False


def has_been_immune_before(row_index, col_index, prev_obs):
    if prev_obs[row_index][col_index] == "I":
        return True
    else:
        return False

def teams_update(curr_obs, prev_obs, init_police, init_medics):
    length_t, width_t = len(curr_obs[0]), len(curr_obs[0][:])
    available_police = init_police
    available_medics = init_medics
    for i in range(length_t):
        for j in range(width_t):
            if prev_obs[i][j] == "H" and curr_obs[i][j] == "I":
                available_medics = available_medics - 1
            if prev_obs[i][j] == "S" and curr_obs[i][j] == "Q":
                available_police = available_police - 1
    return available_police, available_medics


def my_neighbors_will_be_infected_by_me(row_index, col_index, curr_obs, next_obs):
    col_len = len(curr_obs[0])
    row_len = len(curr_obs[:])
    if 0 <= (col_index + 1) < col_len:
        # or the neighb is not S or the neighb is S but yesterday he wasn't S and there was another neighb that infect him
        if curr_obs[row_index][col_index + 1] == 'H' and next_obs[row_index][col_index + 1] == 'H':
            return False
        if curr_obs[row_index][col_index + 1] == 'H' and next_obs[row_index][col_index + 1] == 'S':
            if not has_sick_neighbor(row_index, col_index + 1, curr_obs):
                # for sure i was the one who infected this neighbor
                return True
            else:
                return False

    if 0 <= (col_index - 1):
        # or the neighb is not S or the neighb is S but yesterday he wasn't S and there was another neighb that infect him
        if curr_obs[row_index][col_index - 1] == 'H' and next_obs[row_index][col_index - 1] == 'H':
            return False
        if curr_obs[row_index][col_index - 1] == 'H' and next_obs[row_index][col_index - 1] == 'S':
            if not has_sick_neighbor(row_index, col_index - 1, curr_obs):
                # for sure i was the one who infected this neighbor
                return True
            else:
                return False

    if 0 <= (row_index + 1) < row_len:
        # or the neighb is not S or the neighb is S but yesterday he wasn't S and there was another neighb that infect him
        if curr_obs[row_index + 1][col_index] == 'H' and next_obs[row_index + 1][col_index] == 'H':
            return False
        if curr_obs[row_index + 1][col_index] == 'H' and next_obs[row_index + 1][col_index] == 'S':
            if not has_sick_neighbor(row_index + 1, col_index, curr_obs):
                # for sure i was the one who infected this neighbor
                return True
            else:
                return False

    if 0 <= row_index - 1:
        # or the neighb is not S or the neighb is S but yesterday he wasn't S and there was another neighb that infect him
        if curr_obs[row_index - 1][col_index] == 'H' and next_obs[row_index - 1][col_index] == 'H':
            return False
        if curr_obs[row_index - 1][col_index] == 'H' and next_obs[row_index - 1][col_index] == 'S':
            if not has_sick_neighbor(row_index - 1, col_index, curr_obs):
                # for sure i was the one who infected this neighbor
                return True
            else:
                return False


def generate_base_clause(user_input):
    var_to_int = {}
    police = user_input["police"]
    medics = user_input["medics"]
    var_to_int = initialize_variables(user_input["observations"])
    col = len(user_input["observations"][0][0])
    row_dim = len(user_input["observations"][0][:])
    clause = []
    observations = user_input["observations"]  # get the number of the matrix in the input
    for t, matrix in enumerate(observations):
        if t == 0:  # if there is no observations for the next turn
            available_police = police
            available_medics = medics
        else:
            available_police, available_medics = teams_update(observations[t], observations[t - 1], police, medics)

        for row_index, row in enumerate(matrix):
            for col_index, cell in enumerate(row):
                if cell == 'S':
                    clause.append(var_to_int[(row_index, col_index, t, 'S')])
                    clause.append(-var_to_int[(row_index, col_index, t, 'H')])
                    clause.append(-var_to_int[(row_index, col_index, t, 'I')])
                    clause.append(-var_to_int[(row_index, col_index, t, 'Q')])
                    clause.append(-var_to_int[(row_index, col_index, t, 'U')])
                    # add a clause of x_{i,j,t,S} and X'_{i,j,t,C} where C is {H, U, I, Q}
                    # note var_to_int[(i,j,t,'S')] is the variable we send to pysat
                    # TODO: add clauses related to police.

                    if t == 0 or (observations[t - 1][row_index][col_index] != "S"):
                        if police == 0:
                            if t + 1 < len(observations):
                                clause.append(var_to_int[(row_index, col_index, t + 1, 'S')])
                                clause.append(-var_to_int[(row_index, col_index, t + 1, 'H')])
                                clause.append(-var_to_int[(row_index, col_index, t + 1, 'I')])
                                clause.append(-var_to_int[(row_index, col_index, t + 1, 'Q')])
                                clause.append(-var_to_int[(row_index, col_index, t + 1, 'U')])

                            if t + 2 < len(observations):
                                clause.append(var_to_int[(row_index, col_index, t + 2, 'S')])
                                clause.append(-var_to_int[(row_index, col_index, t + 2, 'H')])
                                clause.append(-var_to_int[(row_index, col_index, t + 2, 'I')])
                                clause.append(-var_to_int[(row_index, col_index, t + 2, 'Q')])
                                clause.append(-var_to_int[(row_index, col_index, t + 2, 'U')])

                            if t + 3 < len(observations):
                                clause.append(var_to_int[(row_index, col_index, t + 3, 'H')])
                                clause.append(-var_to_int[(row_index, col_index, t + 3, 'S')])
                                clause.append(-var_to_int[(row_index, col_index, t + 3, 'I')])
                                clause.append(-var_to_int[(row_index, col_index, t + 3, 'Q')])
                                clause.append(-var_to_int[(row_index, col_index, t + 3, 'U')])
                        else:  # there is police
                            # if police  didnt quarentine this cell
                            if t + 1 < len(observations):
                                if observations[t + 1][row_index][col_index] != "Q":
                                    clause.append(var_to_int[(row_index, col_index, t + 1, 'S')])
                                    clause.append(-var_to_int[(row_index, col_index, t + 1, 'H')])
                                    clause.append(-var_to_int[(row_index, col_index, t + 1, 'I')])
                                    clause.append(-var_to_int[(row_index, col_index, t + 1, 'Q')])
                                    clause.append(-var_to_int[(row_index, col_index, t + 1, 'U')])

                                    if t + 2 < len(observations):
                                        if observations[t + 2][row_index][col_index] != "Q":
                                            clause.append(var_to_int[(row_index, col_index, t + 2, 'S')])
                                            clause.append(-var_to_int[(row_index, col_index, t + 2, 'H')])
                                            clause.append(-var_to_int[(row_index, col_index, t + 2, 'I')])
                                            clause.append(-var_to_int[(row_index, col_index, t + 2, 'Q')])
                                            clause.append(-var_to_int[(row_index, col_index, t + 2, 'U')])

                                    if t + 3 < len(observations):
                                        if observations[t + 3][row_index][col_index] != "Q":
                                            clause.append(var_to_int[(row_index, col_index, t + 3, 'H')])
                                            clause.append(-var_to_int[(row_index, col_index, t + 3, 'S')])
                                            clause.append(-var_to_int[(row_index, col_index, t + 3, 'I')])
                                            clause.append(-var_to_int[(row_index, col_index, t + 3, 'Q')])
                                            clause.append(-var_to_int[(row_index, col_index, t + 3, 'U')])

                        # לא נכון לבצע השמה של ~  Q/~H כי חולה יכול להכנס לבידוד ולהבריא
                        # add a clause of x_{i,j,t,S} and X'_{i,j,t,C} where C is {H, U, I, Q}, for t+1, t+2, t+3 (if they exist)

                    if t >= 3 and observations[t - 1][row_index][col_index] == "S" and observations[t - 2][row_index][col_index] == "S" and observations[t - 3][row_index][col_index] == "S":
                        # add a clause of x_{i,j,t+1, H} and x'_{i,j,t+1,C} where C is {S, U, I, Q}.
                        if t + 1 < len(observations):
                            clause.append(var_to_int[(row_index, col_index, t + 1, 'H')])
                            clause.append(-var_to_int[(row_index, col_index, t + 1, 'S')])
                            clause.append(-var_to_int[(row_index, col_index, t + 1, 'I')])
                            clause.append(-var_to_int[(row_index, col_index, t + 1, 'Q')])
                            clause.append(-var_to_int[(row_index, col_index, t + 1, 'U')])

                if cell == "H":
                    clause.append(var_to_int[(row_index, col_index, t, 'H')])
                    clause.append(-var_to_int[(row_index, col_index, t, 'S')])
                    clause.append(-var_to_int[(row_index, col_index, t, 'I')])
                    clause.append(-var_to_int[(row_index, col_index, t, 'Q')])
                    clause.append(-var_to_int[(row_index, col_index, t, 'U')])

                    # add a clause of x_{i,j,t,H} and X'_{i,j,t,C} where C is {S, U, I, Q}
                    # note d[(i,j,t,'H')] is the variable we send to pysat
                    # TODO: add clauses related to medic.
                    if t + 1 < len(observations):
                        if has_sick_neighbor(row_index, col_index, observations[t]) and police == 0:
                            clause.append(-var_to_int[(row_index, col_index, t + 1, 'H')])
                            clause.append(-var_to_int[(row_index, col_index, t + 1, 'Q')])
                            clause.append(-var_to_int[(row_index, col_index, t + 1, 'U')])
                            if medics == 0:
                                clause.append(var_to_int[(row_index, col_index, t + 1, 'S')])

                        if not has_sick_neighbor(row_index, col_index, observations[t]):
                            if not has_question_mark_neighbor(row_index, col_index, observations[t]):
                                clause.append(-var_to_int[(row_index, col_index, t + 1, 'S')])
                                clause.append(-var_to_int[(row_index, col_index, t + 1, 'Q')])
                                clause.append(-var_to_int[(row_index, col_index, t + 1, 'U')])
                                if medics == 0:
                                    clause.append(-var_to_int[(row_index, col_index, t + 1, 'I')])
                                    clause.append(var_to_int[(row_index, col_index, t + 1, 'H')])
                        # add clause of x_{i,j,t+1,S} and x'_{i,j,t+1,C} where C is {H, Q, U, I}.

                if cell == "Q":
                    if observations[t - 1][row_index][col_index] != "Q":
                        clause.append(var_to_int[(row_index, col_index, t, 'Q')])
                        clause.append(-var_to_int[(row_index, col_index, t, 'S')])
                        clause.append(-var_to_int[(row_index, col_index, t, 'I')])
                        clause.append(-var_to_int[(row_index, col_index, t, 'H')])
                        clause.append(-var_to_int[(row_index, col_index, t, 'U')])

                        if t + 1 < len(observations):
                            clause.append(var_to_int[(row_index, col_index, t + 1, 'Q')])
                            clause.append(-var_to_int[(row_index, col_index, t + 1, 'S')])
                            clause.append(-var_to_int[(row_index, col_index, t + 1, 'I')])
                            clause.append(-var_to_int[(row_index, col_index, t + 1, 'H')])
                            clause.append(-var_to_int[(row_index, col_index, t + 1, 'U')])
                        # add clause that x_{i,j,t+2,H} and x'_{i,j,t+2,C} where C is {......}.

                        if t + 2 < len(observations):
                            clause.append(var_to_int[(row_index, col_index, t + 2, 'H')])
                            clause.append(-var_to_int[(row_index, col_index, t + 2, 'S')])
                            clause.append(-var_to_int[(row_index, col_index, t + 2, 'I')])
                            clause.append(-var_to_int[(row_index, col_index, t + 2, 'Q')])
                            clause.append(-var_to_int[(row_index, col_index, t + 2, 'U')])

                if cell == "I":
                    if not has_been_immune_before(row_index, col_index, observations[t - 1]):
                        for k in range(len(observations)):
                            if k >= t:
                                clause.append(var_to_int[(row_index, col_index, k, 'I')])
                                clause.append(-var_to_int[(row_index, col_index, k, 'S')])
                                clause.append(-var_to_int[(row_index, col_index, k, 'Q')])
                                clause.append(-var_to_int[(row_index, col_index, k, 'H')])
                                clause.append(-var_to_int[(row_index, col_index, k, 'U')])
                        # add clause that x_{i,j,t+k,I} for every k>=0 (until the limit)
                        # #and x'_{i,j,t+k,C} where C {.....}

                if cell == "U":
                    if t == 0:
                        for k in range(len(observations)):
                            clause.append(var_to_int[(row_index, col_index, k, 'U')])
                            clause.append(-var_to_int[(row_index, col_index, k, 'S')])
                            clause.append(-var_to_int[(row_index, col_index, k, 'Q')])
                            clause.append(-var_to_int[(row_index, col_index, k, 'H')])
                            clause.append(-var_to_int[(row_index, col_index, k, 'I')])
                        # x_{i,j,t,U} for every t>=0 (until len(observations))
                        # and x'_{i,j,t,C} for every t>=0, where C {......}

                if cell == "?":
                    # at the begining there is no Q or I
                    if t == 0:
                        clause.append(-var_to_int[(row_index, col_index, t, 'I')])
                        clause.append(-var_to_int[(row_index, col_index, t, 'Q')])
                    # if yesterday the cell was H and there were not neighbors S then today he will not be S
                    if t - 1 >= 0:
                        if observations[t - 1][row_index][col_index] == 'H':
                            if not has_sick_neighbor(row_index, col_index, observations[t - 1]):
                                clause.append(-var_to_int[(row_index, col_index, t, 'S')])
                                clause.append(-var_to_int[(row_index, col_index, t, 'U')])
                                clause.append(-var_to_int[(row_index, col_index, t, 'Q')])

                    if available_medics == 0:
                        clause.append(-var_to_int[(row_index, col_index, t, 'I')])

                    if has_sick_neighbor(row_index, col_index, observations[t]):
                        the_healthy_neighbors = the_healthy_neighbor(row_index, col_index, observations[t])
                        if len(the_healthy_neighbors) > 0:
                            this_neighb_will_be_s = False
                            if t + 1 < len(observations):
                                for neighb in the_healthy_neighbors:
                                    if observations[t + 1][neighb[0]][neighb[1]] == 'S':
                                        this_neighb_will_be_s = True
                                if not this_neighb_will_be_s:
                                    clause.append(-var_to_int[(row_index, col_index, t, 'H')])
                                    clause.append(-var_to_int[(row_index, col_index, t, 'S')])
                            else:
                                if available_medics == 0:
                                    if -var_to_int[(row_index, col_index, t - 1, 'H')] in clause and -var_to_int[(row_index, col_index, t - 1, 'S')] in clause:
                                        clause.append(-var_to_int[(row_index, col_index, t, 'H')])

                    # if this cell was U
                    for time in range(len(observations)):
                        if observations[time][row_index][col_index] != '?' and observations[time][row_index][col_index] != 'U':
                            for k in range(len(observations)):
                                clause.append(-var_to_int[(row_index, col_index, k, 'U')])
                        if observations[time][row_index][col_index] == 'U':
                            for k in range(len(observations)):
                                clause.append(var_to_int[(row_index, col_index, k, 'U')])

                    if 0 <= (col_index + 1) < col:
                        if observations[t][row_index][col_index + 1] == 'S':
                            if t - 1 >= 0:
                                if observations[t - 1][row_index][col_index + 1] == 'H':
                                    if not has_sick_neighbor(row_index, col_index + 1, observations[t - 1]):
                                        clause.append(var_to_int[(row_index, col_index, t, 'S')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'U')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'Q')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'H')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'I')])

                        elif observations[t][row_index][col_index + 1] == 'H':
                            if t - 1 >= 0:
                                if observations[t - 1][row_index][col_index + 1] == 'H':
                                    if not has_sick_neighbor(row_index, col_index + 1, observations[t - 1]):
                                        clause.append(-var_to_int[(row_index, col_index, t - 1, 'S')])
                            if t + 1 < len(observations):
                                if observations[t + 1][row_index][col_index + 1] == 'H':
                                    if not has_sick_neighbor(row_index, col_index + 1, observations[t]):
                                        clause.append(-var_to_int[(row_index, col_index, t, 'S')])
                                    else:
                                        infecting_neighbors = the_infecting_neighbor(row_index, col_index + 1, observations[t])
                                        there_is_potional_S_neighb = False
                                        for neighb in infecting_neighbors:
                                            if observations[t + 1][neighb[0]][neighb[1]] != 'Q':
                                                there_is_potional_S_neighb = True
                                        if not there_is_potional_S_neighb:
                                            clause.append(-var_to_int[(row_index, col_index, t, 'S')])

                                if observations[t + 1][row_index][col_index + 1] == 'S':
                                    if not has_sick_neighbor(row_index, col_index + 1, observations[t]):
                                        clause.append(var_to_int[(row_index, col_index, t, 'S')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'U')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'Q')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'H')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'I')])

                    if 0 <= (col_index - 1) < col:
                        if observations[t][row_index][col_index - 1] == 'S':
                            if t - 1 >= 0:
                                if observations[t - 1][row_index][col_index - 1] == 'H':
                                    if not has_sick_neighbor(row_index, col_index - 1, observations[t - 1]):
                                        clause.append(var_to_int[(row_index, col_index, t, 'S')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'U')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'Q')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'H')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'I')])
                        elif observations[t][row_index][col_index - 1] == 'H':
                            if t - 1 >= 0:
                                if observations[t - 1][row_index][col_index - 1] == 'H':
                                    if not has_sick_neighbor(row_index, col_index - 1, observations[t - 1]):
                                        clause.append(-var_to_int[(row_index, col_index, t - 1, 'S')])
                            if t + 1 < len(observations):
                                if observations[t + 1][row_index][col_index - 1] == 'H':
                                    if not has_sick_neighbor(row_index, col_index - 1, observations[t]):
                                        clause.append(-var_to_int[(row_index, col_index, t, 'S')])
                                if observations[t + 1][row_index][col_index - 1] == 'S':
                                    if not has_sick_neighbor(row_index, col_index - 1, observations[t]):
                                        clause.append(var_to_int[(row_index, col_index, t, 'S')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'U')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'Q')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'H')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'I')])

                    if 0 <= (row_index + 1) < row_dim:
                        if observations[t][row_index + 1][col_index] == 'S':
                            if t - 1 >= 0:
                                if observations[t - 1][row_index + 1][col_index] == 'H':
                                    if not has_sick_neighbor(row_index + 1, col_index, observations[t - 1]):
                                        clause.append(var_to_int[(row_index, col_index, t, 'S')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'U')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'Q')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'H')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'I')])
                        elif observations[t][row_index + 1][col_index] == 'H':
                            if t - 1 >= 0:
                                if observations[t - 1][row_index + 1][col_index] == 'H':
                                    if not has_sick_neighbor(row_index + 1, col_index, observations[t - 1]):
                                        clause.append(-var_to_int[(row_index, col_index, t - 1, 'S')])
                            if t + 1 < len(observations):
                                if observations[t + 1][row_index + 1][col_index] == 'H':
                                    if not has_sick_neighbor(row_index + 1, col_index, observations[t]):
                                        clause.append(-var_to_int[(row_index, col_index, t, 'S')])
                                if observations[t + 1][row_index + 1][col_index] == 'S':
                                    if not has_sick_neighbor(row_index + 1, col_index, observations[t]):
                                        clause.append(var_to_int[(row_index, col_index, t, 'S')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'U')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'Q')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'H')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'I')])

                    if 0 <= row_index - 1:
                        if observations[t][row_index - 1][col_index] == 'S':
                            if t - 1 >= 0:
                                if observations[t - 1][row_index - 1][col_index] == 'H':
                                    if not has_sick_neighbor(row_index - 1, col_index, observations[t - 1]):
                                        clause.append(var_to_int[(row_index, col_index, t, 'S')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'U')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'Q')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'H')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'I')])
                        elif observations[t][row_index - 1][col_index] == 'H':
                            if t - 1 >= 0:
                                if observations[t - 1][row_index - 1][col_index] == 'H':
                                    if not has_sick_neighbor(row_index - 1, col_index, observations[t - 1]):
                                        clause.append(-var_to_int[(row_index, col_index, t - 1, 'S')])
                            if t + 1 < len(observations):
                                if observations[t + 1][row_index - 1][col_index] == 'H':
                                    if not has_sick_neighbor(row_index - 1, col_index, observations[t]):
                                        clause.append(-var_to_int[(row_index, col_index, t, 'S')])
                                if observations[t + 1][row_index - 1][col_index] == 'S':
                                    if not has_sick_neighbor(row_index - 1, col_index, observations[t]):
                                        clause.append(var_to_int[(row_index, col_index, t, 'S')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'U')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'Q')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'H')])
                                        clause.append(-var_to_int[(row_index, col_index, t, 'I')])

                    if not has_sick_neighbor(row_index, col_index, observations[t]) and available_police == 0 and observations[t - 1][row_index][col_index] != "S":
                        if t + 1 < len(observations):
                            # if the neighbors are not s or they s but there was another neighbher that infect them then, the current cell is for sure not S
                            clause.append(-var_to_int[(row_index, col_index, t, 'S')])
                            clause.append(-var_to_int[(row_index, col_index, t + 1, 'S')])

                    if available_police > 0:
                        if t + 1 < len(observations):
                            # if i ever decided that this ? is not H then it is not possible that he will be Q next turn
                            if var_to_int[(row_index, col_index, t, 'S')] in clause:
                                # there is the possibilty that i will Quarntine this cell
                                if not my_neighbors_will_be_infected_by_me(row_index, col_index, observations[t], observations[t + 1]):
                                    clause.append(var_to_int[(row_index, col_index, t + 1, 'Q')])
                                    clause.append(-var_to_int[(row_index, col_index, t + 1, 'H')])
                                    clause.append(-var_to_int[(row_index, col_index, t + 1, 'I')])
                                    clause.append(-var_to_int[(row_index, col_index, t + 1, 'S')])
                                    clause.append(-var_to_int[(row_index, col_index, t + 1, 'U')])
                                    available_police = available_police - 1

                    if available_police == 0 and t != 0:
                        if observations[t - 1][row_index][col_index] != 'Q':
                            clause.append(-var_to_int[(row_index, col_index, t, 'Q')])

                    if available_medics > 0:
                        if t + 1 < len(observations):
                            if var_to_int[(row_index, col_index, t, 'H')] in clause:
                                clause.append(var_to_int[(row_index, col_index, t + 1, 'I')])
                                clause.append(-var_to_int[(row_index, col_index, t + 1, 'H')])
                                clause.append(-var_to_int[(row_index, col_index, t + 1, 'Q')])
                                clause.append(-var_to_int[(row_index, col_index, t + 1, 'S')])
                                clause.append(-var_to_int[(row_index, col_index, t + 1, 'U')])
                                available_medics = available_medics - 1

                    if available_medics == 0 and t != 0:
                        if observations[t - 1][row_index][col_index] != 'I':
                            clause.append(-var_to_int[(row_index, col_index, t, 'I')])

    return clause, var_to_int


def answer_query(query, base_clause, var_to_int_dict):
    cell, t, state = query
    i, j = cell
    clause_for_curr_q = []
    # add to base_clause:
    # x_{i,j,t,state} and x'_{i,j,t,C} for every other C (other than state).
    clause_for_curr_q.append(var_to_int_dict[(i, j, t, state)])
    for state2 in {"S", "H", "I", "Q", "U"}:
        if state2 != state:
            clause_for_curr_q.append(-var_to_int_dict[(i, j, t, state2)])

    # Solving the SAT folrmula and check if satisfiyable.
    g1 = Glucose3()
    if not g1.solve(base_clause + clause_for_curr_q):
        return "F"

    # here if the assumption of the query is optional, we want to check if more than one is possible
    for other_state in {"S", "I", "Q", "U", "H"}:
        clause_for_curr_state = []
        if other_state != state:
            clause_for_curr_state.append(var_to_int_dict[(i, j, t, other_state)])
            for state2 in {"S", "H", "I", "Q", "U"}:
                if state2 != other_state:
                    clause_for_curr_state.append(-var_to_int_dict[(i, j, t, state2)])
            g2 = Glucose3()
            if g2.solve(base_clause + clause_for_curr_state):
                return "?"
    return "T"

def solve_problem(user_input):
    base_clause, var_to_int = generate_base_clause(user_input)
    answers = dict()
    for query in user_input["queries"]:
        answers[query] = answer_query(query, base_clause, var_to_int)

    return answers
