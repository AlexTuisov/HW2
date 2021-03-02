import utils
import sympy

ids = ['204485601', '304995715']

def count_x_in_the_turn(x,observation, turn_number):
    current_turn,count_x = 0,0
    for turn in observation:
        if current_turn == turn_number:
            for line in turn:
                for letter in line:
                    if letter == x:
                        count_x = count_x + 1
        current_turn = current_turn + 1
    return count_x

def check_if_it_I(observation, turn_number, index):
    letter_number,line_number,current_turn = 0,0,0
    for turn in observation:
        if current_turn == turn_number:
            for line in turn:
                if line_number == index[0]:
                    for letter in line:
                        if letter_number == index[1]:
                            if letter == "I":
                                return True
                            else:
                                return False
                        letter_number = letter_number + 1
                line_number = line_number + 1
        current_turn = current_turn + 1
    return False

def count_H_changed_to_I(observation, turn_number):
    count_H_to_I,letter_number,line_number,current_turn = 0,0,0,0
    for turn in observation:
        if current_turn == turn_number:
            for line in turn:
                for letter in line:
                    if letter == "H" and check_if_it_I(observation, turn_number + 1, (line_number, letter_number)):
                        count_H_to_I = count_H_to_I + 1
                    letter_number = letter_number + 1
                line_number = line_number + 1
        current_turn = current_turn + 1
    return count_H_to_I

def check_S_neighbors(observation, turn_number, index):
    min_row,min_col = 0,0
    max_row = (len(observation[0]) - 1)
    max_col = (len(observation[0][0]) - 1)

    if index[0] > min_row and observation[turn_number][index[0] - 1][index[1]] == 'S':
        return True
    if index[1] > min_col and observation[turn_number][index[0]][index[1] - 1] == 'S':
        return True
    if index[0] < max_row and observation[turn_number][index[0] + 1][index[1]] == 'S':
        return True
    if index[1] < max_col and observation[turn_number][index[0]][index[1] + 1] == 'S':
        return True
    return False

def check_S_is_Q(observation, index):
    for turn in observation:
        if turn[index[0]][index[1]] == "Q":
            return True
    return False

def check_H_neighbors(observation, turn_number, index):
    min_row,min_col = 0,0
    max_row = (len(observation[0]) - 1)
    max_col = (len(observation[0][0]) - 1)
    H_neighbors = []

    if index[0] > min_row and observation[turn_number][index[0] - 1][index[1]] == 'H':
        if (not check_S_neighbors(observation, turn_number, (index[0] - 1, index[1])) or 
        	(check_S_neighbors(observation, turn_number, (index[0] - 1, index[1])) and 
        		check_S_is_Q(observation, (index[0] - 1, index[1])))):
                H_neighbors.append((index[0] - 1, index[1]))

    if index[1] > min_col and observation[turn_number][index[0]][index[1] - 1] == 'H':
        if (not check_S_neighbors(observation, turn_number, (index[0], index[1] - 1)) or 
        	(check_S_neighbors(observation, turn_number,(index[0], index[1] - 1)) and 
        		check_S_is_Q(observation, (index[0], index[1] - 1)))):
                H_neighbors.append((index[0], index[1] - 1))

    if index[0] < max_row and observation[turn_number][index[0] + 1][index[1]] == 'H':
        if (not check_S_neighbors(observation, turn_number, (index[0] + 1, index[1])) or 
        	(check_S_neighbors(observation, turn_number, (index[0] + 1, index[1])) and 
        		check_S_is_Q(observation, (index[0] + 1, index[1])))):
                H_neighbors.append((index[0] + 1, index[1]))

    if index[1] != max_col and observation[turn_number][index[0]][index[1] + 1] == 'H':
        if (not check_S_neighbors(observation, turn_number, (index[0], index[1] + 1)) or 
        	(check_S_neighbors(observation, turn_number, (index[0], index[1] + 1)) and 
        		check_S_is_Q(observation, (index[0], index[1] + 1)))):
                H_neighbors.append((index[0], index[1] + 1))
    
    if len(H_neighbors) == 0:
        return 0
    else:
        return H_neighbors

def count_S_changed_to_Q(observation, turn):
    count_S_to_Q = 0
    for line in observation[turn]:
        for letter in observation[turn][line]:
            if letter == "S" and observation[turn + 1][line][letter] == "Q":
                count_S_to_Q = count_S_to_Q + 1
    return count_S_to_Q

def check_if_S(police_team, observation, turn_number, index):
    for turn in observation:
        if turn[index[0]][index[1]] == "U":
            return 'F'
        elif (turn[index[0]][index[1]] == "I") and (turn < turn_number):
            return 'F'
    H_neighbors1 = check_H_neighbors(observation, turn_number - 1, index)
    H_neighbors2 = check_H_neighbors(observation, turn_number - 2, index)
    H_neighbors3 = check_H_neighbors(observation, turn_number - 3, index)
    S_neighbors = check_S_neighbors(observation, turn_number, index)
    S_neighbors1 = check_S_neighbors(observation, turn_number - 1, index)
    S_neighbors2 = check_S_neighbors(observation, turn_number-2, index)

    if police_team == 0:
        if (turn_number > 0) and (turn_number <= 2):
            if observation[turn_number - 1][index[0]][index[1]] == "S":
                return 'T'
            elif (observation[turn_number - 1][index[0]][index[1]] == "?") and (turn_number > 1):
                if observation[turn_number - 2][index[0]][index[1]] == "S":
                    return 'T'
                elif observation[turn_number - 2][index[0]][index[1]] == "?" and H_neighbors2 != 0:
                    for neighbor in H_neighbors2:
                        if observation[turn_number - 1][neighbor[0]][neighbor[1]] == "S":
                            return 'T'
                        if observation[turn_number - 1][neighbor[0]][neighbor[1]] == "H":
                            return 'F'
        if turn_number != 0:
            if observation[turn_number - 1][index[0]][index[1]] == "S":
                if observation[turn_number - 2][index[0]][index[1]] == "S":
                    if observation[turn_number - 3][index[0]][index[1]] == "S":
                        return 'F'
                    elif observation[turn_number - 3][index[0]][index[1]] == "?":
                        if H_neighbors3 != 0:
                            for neighbor in H_neighbors3:
                                if observation[turn_number-2][neighbor[0]][neighbor[1]] == "S":
                                    return 'F'
                                elif observation[turn_number-2][neighbor[0]][neighbor[1]] == "H":
                                    return 'T'
                    elif observation[turn_number - 3][index[0]][index[1]] == "H":
                        return 'T'
                elif observation[turn_number - 2][index[0]][index[1]] == "?":
                    if turn_number == 3:
                        if observation[turn_number - 3][index[0]][index[1]] == "S":
                            return 'F'
                        elif observation[turn_number - 3][index[0]][index[1]] != "S" and observation[turn_number - 3][index[0]][index[1]] != "?" :
                            return 'T'
                        elif observation[turn_number - 4][index[0]][index[1]] == "S":
                            return 'T'
                        elif observation[turn_number - 3][index[0]][index[1]] == "?" and observation[turn_number - 4][index[0]][index[1]] == "H":
                            return 'F'
            elif observation[turn_number - 1][index[0]][index[1]] != "S" and observation[turn_number - 1][index[0]][index[1]] != "H":
                if observation[turn_number - 1][index[0]][index[1]] == "?":
                    if observation[turn_number - 2][index[0]][index[1]] == "?":
                        if H_neighbors1 != 0:
                            for neighbor in H_neighbors1:
                                if observation[turn_number][neighbor[0]][neighbor[1]] == "S":
                                    return 'T'
                                if observation[turn_number][neighbor[0]][neighbor[1]] == "H":
                                    return 'F'
                    elif observation[turn_number - 2][index[0]][index[1]] == "S":
                        if observation[turn_number - 3][index[0]][index[1]] == "S":
                            if observation[turn_number - 4][index[0]][index[1]] == "S":
                                if S_neighbors1 and S_neighbors:
                                    return 'T'
                                else:
                                    return 'F'
                    elif observation[turn_number - 2][index[0]][index[1]] == "H":
                        if observation[turn_number - 3][index[0]][index[1]] == "?":
                            if S_neighbors2 and S_neighbors1:
                                return 'T'
                        elif observation[turn_number - 3][index[0]][index[1]] == "S":
                            return 'T'
                        elif observation[turn_number - 3][index[0]][index[1]] == "H":
                            if check_S_neighbors(observation, turn_number-3, index) and S_neighbors2:
                                return 'T'
                            if S_neighbors2 and S_neighbors1:
                                return 'T'
                            else:
                                return 'F'
                        else:
                            return 'F'
                    else:
                        return 'F'
                else:
                    return 'F'

    if observation[turn_number - 1][index[0]][index[1]] == "H":
        if S_neighbors1 and S_neighbors:
            return 'T'
        else:
            return 'F'

    if H_neighbors1 != 0:
        for neighbor in H_neighbors1:
            if observation[turn_number][neighbor[0]][neighbor[1]] == "S":
                return 'T'
            if observation[turn_number][neighbor[0]][neighbor[1]] == "H" and not S_neighbors1:
                return 'F'

    elif police_team != 0:
        if observation[turn_number - 1][index[0]][index[1]] == "S":
            if police_team >= (count_x_in_the_turn("S", observation,turn_number-1) + count_x_in_the_turn("?",observation, turn_number-1)):
                return 'F'
            elif police_team == count_S_changed_to_Q(observation, turn_number-1) and turn_number >=2:
                return 'T'
        elif observation[turn_number - 1][index[0]][index[1]] == "H":
            if S_neighbors1 and S_neighbors:
                return 'T'
            else:
                return 'F'
        elif observation[turn_number - 1][index[0]][index[1]] == "?":
            if H_neighbors1 != 0:
                for neighbor in H_neighbors1:
                    if observation[turn_number][neighbor[0]][neighbor[1]] == "S":
                        return 'T'
                    if observation[turn_number][neighbor[0]][neighbor[1]] == "H" and not S_neighbors1:
                        return 'F'
            if observation[turn_number - 2][index[0]][index[1]] == "S":
                if police_team >= (count_x_in_the_turn("S",observation, turn_number - 1) + count_x_in_the_turn("?",observation, turn_number - 1)):
                    return 'F'
                elif police_team == count_S_changed_to_Q(observation, turn_number - 1) and turn_number >= 2:
                    return 'T'
            elif observation[turn_number - 2][index[0]][index[1]] == "H":
                if S_neighbors2 and S_neighbors1:
                    if police_team >= (count_x_in_the_turn("S",observation, turn_number - 1) + count_x_in_the_turn("?",observation, turn_number - 1)):
                        return 'F'
                    elif police_team == count_S_changed_to_Q(observation, turn_number - 1) and turn_number >= 2:
                        return 'T'
                else:
                    return 'F'
            elif observation[turn_number - 2][index[0]][index[1]] == "?":
                if H_neighbors2 != 0:
                    for neighbor in H_neighbors2:
                        if observation[turn_number-1][neighbor[0]][neighbor[1]] == "S":
                            return 'T'
                        if observation[turn_number-1][neighbor[0]][neighbor[1]] == "H" and not S_neighbors1:
                            return 'F'
            else:
                return 'F'
        else:
            return 'F'
    return '?'

def check_if_H(police_team, medics_team, observation, turn_number, index):
    check = '?'
    for turn in observation:
        if turn[index[0]][index[1]] == "U":
            return 'F'
    
    H_neighbors = check_H_neighbors(observation, turn_number, index)
    count_QM = count_x_in_the_turn("?",observation, turn_number - 1)
    count_H = count_x_in_the_turn("H",observation, turn_number - 1)
    H_changed_to_I = count_H_changed_to_I(observation, turn_number - 1)
    S_neighbors = check_S_neighbors(observation, turn_number, index)
    S_neighbors1 = check_S_neighbors(observation, turn_number - 1, index)

    if (turn_number + 1) < len(observation):
        if observation[turn_number + 1][index[0]][index[1]] == "Q":
            return 'F'
        elif observation[turn_number + 1][index[0]][index[1]] == "H":
            if turn_number < 2:
                return 'T'
            elif observation[turn_number - 1][index[0]][index[1]] == "H":
                return 'T'
        elif observation[turn_number + 1][index[0]][index[1]] == "I":
            if turn_number == 0:
                return 'T'
            elif observation[turn_number - 1][index[0]][index[1]] == "I":
                return 'F'
            elif observation[turn_number - 1][index[0]][index[1]] == "H":
                if medics_team >= (count_H + count_QM):
                    return 'F'
                elif medics_team == H_changed_to_I:
                    return 'T'
        elif observation[turn_number + 1][index[0]][index[1]] == "S":
            if not S_neighbors:
                check = 'F'
            elif S_neighbors and H_neighbors != 0:
                for neighbor in H_neighbors:
                    if observation[turn_number + 1][neighbor[0]][neighbor[1]] == "S":
                        return 'F'
                    if observation[turn_number + 1][neighbor[0]][neighbor[1]] == "H":
                        return 'T'
        elif observation[turn_number + 1][index[0]][index[1]] == "?":
            if (turn_number + 2) < len(observation):
                if observation[turn_number + 2][index[0]][index[1]] == "S":
                    if not S_neighbors:
                        check = 'F'
                    elif S_neighbors and H_neighbors != 0:
                        for neighbor in H_neighbors:
                            if observation[turn_number + 1][neighbor[0]][neighbor[1]] == "S":
                                return 'F'
                            if observation[turn_number + 1][neighbor[0]][neighbor[1]] == "H":
                                return 'T'
            elif H_neighbors != 0:
                for neighbor in H_neighbors:
                    if observation[turn_number + 1][neighbor[0]][neighbor[1]] == "S":
                        return 'F'

    if turn_number != 0:
        if (observation[turn_number - 1][index[0]][index[1]] == "U") or (observation[turn_number - 1][index[0]][index[1]] == "I"):
            return 'F'
        elif observation[turn_number - 1][index[0]][index[1]] == "H":
            if medics_team == 0:
                if (not S_neighbors1) or (S_neighbors1 and not S_neighbors):
                    return 'T'
                else:
                    return 'F'            
            if medics_team >= (count_H + count_QM):
                return 'F'
            elif medics_team == H_changed_to_I:
                if not S_neighbors:
                    check = 'T'
                elif turn_number != (len(observation) - 1):
                    if check_S_neighbors(observation, turn_number + 1, index):
                        return 'F'

        elif observation[turn_number - 1][index[0]][index[1]] == "Q":
            if turn_number > 2 and observation[turn_number - 2][index[0]][index[1]] == "Q":
            	return 'T'
            else:
                return 'F'
        elif observation[turn_number - 1][index[0]][index[1]] == "S":
            if turn_number > 3 and observation[turn_number - 2][index[0]][index[1]] == "S" and observation[turn_number - 3][index[0]][index[1]] == "S":
                return 'T'
            else:
                return 'F'
        elif observation[turn_number - 1][index[0]][index[1]] == "?" and S_neighbors1 and S_neighbors:
                return 'F'
    if turn_number != (len(observation) - 1) and S_neighbors and check_S_neighbors(observation, turn_number + 1, index) and check_if_S(
    	police_team, observation, turn_number + 1, index) == 'F':
        return 'F'
    return check

def check_if_Q(police_team, observation, turn_number, index):
    if turn_number == 0 or police_team == 0:
        return 'F'        

    for turn in observation:
        if turn[index[0]][index[1]] == "U":
            return 'F'
        elif (turn[index[0]][index[1]] == "I") and (turn < turn_number):
            return 'F'
    if observation[turn_number - 1][index[0]][index[1]] == "H":
        return 'F'
    
    count_QM = count_x_in_the_turn("?",observation, turn_number - 1)
    count_Q1 = count_x_in_the_turn("Q",observation, turn_number - 1)
    count_Q = count_x_in_the_turn("Q",observation, turn_number)

    if observation[turn_number - 1][index[0]][index[1]] == "S":
        if police_team >= (count_Q1 + count_QM):
            return 'T'
        elif count_S_changed_to_Q(observation, turn_number) == police_team:
            return 'F'

    if observation[turn_number - 1][index[0]][index[1]] == "Q":
        if observation[turn_number - 2][index[0]][index[1]] == "Q":
            return 'F'
        elif observation[turn_number - 2][index[0]][index[1]] == "S":
            return 'T'

    H_neighbors = check_H_neighbors(observation, turn_number - 1, index)
    if observation[turn_number - 1][index[0]][index[1]] == "?" and H_neighbors != 0:
        for neighbor in H_neighbors:
            if observation[turn_number][neighbor[0]][neighbor[1]] != "S":
                if turn_number - 1 == 0:
                    return 'F'
                elif (count_Q1 + police_team) == count_Q:
                    return 'F'
            elif observation[turn_number][neighbor[0]][neighbor[1]] == "S" and (count_Q1 + police_team) == count_Q:
                return 'F'
    return '?'

def check_if_I(medics_team, observation, turn_number, index):
    if medics_team == 0 or turn_number == 0:
        return 'F'

    for turn in observation:
        if turn[index[0]][index[1]] == "U":
            return 'F'
    current_turn = 0
    count_QM = count_x_in_the_turn("?",observation, turn_number - 1)
    count_H = count_x_in_the_turn("H",observation, turn_number - 1)

    for turn in observation:
        if (turn[index[0]][index[1]] == "I") and (current_turn < turn_number):
            return 'T'
        elif (turn[index[0]][index[1]] != "?") and (turn[index[0]][index[1]] != "I") and (current_turn > turn_number):
            return 'F'
        if observation[turn_number - 1][index[0]][index[1]] == "H":
            if medics_team >= (count_H + count_QM):
                return 'T'
            elif medics_team == (count_H_changed_to_I(observation, turn_number - 1)):
                return 'F'
        current_turn = current_turn + 1

    if observation[turn_number - 1][index[0]][index[1]] == "Q":
        return 'F'
    if observation[turn_number - 1][index[0]][index[1]] == "?":
        if check_S_neighbors(observation, turn_number - 1, index) and check_S_neighbors(observation, turn_number, index):
            return 'F'
        elif count_x_in_the_turn("I",observation, turn_number - 1) + medics_team == count_x_in_the_turn("I",observation, turn_number):
            return 'F'
    return '?'

def check_if_U(police_team, medics_team, observation, turn_number, index):
    for turn in observation:
        if turn[index[0]][index[1]] == "U":
            return 'T'
        elif (turn[index[0]][index[1]] != "U") and (turn[index[0]][index[1]] != "?"):
            return 'F'

    if (check_if_S(police_team, observation, turn_number, index) == 'F') and (
            check_if_I(medics_team, observation, turn_number, index) == 'F') and (
            check_if_Q(police_team, observation, turn_number, index) == 'F') and (
            check_if_H(police_team, medics_team, observation, turn_number, index) == 'F'):
        return 'T'

    elif (check_if_S(police_team, observation, turn_number, index) == 'T') or (
            check_if_I(medics_team, observation, turn_number, index) == 'T') or (
            check_if_Q(police_team, observation, turn_number, index) == 'T') or (
            check_if_H(police_team, medics_team, observation, turn_number, index) == 'T'):
        return 'F'
    return '?'

def solve_problem(input):
    answers_dict = {}
    for query in input["queries"]:
        if query[2] == 'S':
            answers_dict[query] = check_if_S(input["police"], input["observations"], query[1], query[0])
        elif query[2] == 'H':
            answers_dict[query] = check_if_H(input["police"], input["medics"], input["observations"], query[1], query[0])        
        elif query[2] == 'Q':
            answers_dict[query] = check_if_Q(input["police"], input["observations"], query[1], query[0])
        elif query[2] == 'I':
            answers_dict[query] = check_if_I(input["police"], input["observations"], query[1], query[0])    
        elif query[2] == 'U':
            answers_dict[query] = check_if_U(input["police"], input["medics"], input["observations"], query[1], query[0])
        else:
            answers_dict[query] = '?'
    return answers_dict