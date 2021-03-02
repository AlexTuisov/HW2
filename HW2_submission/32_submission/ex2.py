from sympy import to_cnf, symbols, true, false
from collections import defaultdict
from math import floor
from itertools import combinations
from json import loads
from pysat.solvers import Glucose3

ids = ['207217589']

def solve_problem(problem):
    # Get all the problem parameters
    # The code below is a patchwork based on faulty logic, but it kinda works
    police_teams = problem["police"]
    medical_teams = problem["medics"]
    observations = problem["observations"]
    queries = problem["queries"]
    num_of_time_steps = len(observations)
    num_of_rows = len(observations[0])
    num_of_columns = len(observations[0][0])
    var_to_data = {}
    

    # Map all possible assignments to either true/false or a variable
    P = defaultdict(lambda: defaultdict(dict))
    current_variable_name = 1
    for code in ['U', 'H', 'S', 'Q', 'I']:
        for t in range(num_of_time_steps):
            for l in range(num_of_rows * num_of_columns):
                i = floor(l / num_of_rows)
                j = l - i * num_of_rows
                if observations[t][i][j] == '?':
                    P[code][t][l] = symbols(str(current_variable_name))
                    var_to_data[current_variable_name] = (code, t, l)
                    current_variable_name += 1
                else:
                    P[code][t][l] = true if observations[t][i][j] == code else false

    
    expression = true
    # U
    # Check if the tile hasn't ever been a wall
    for t1 in range(num_of_time_steps):
        for l in range(num_of_rows * num_of_columns):
            was_ever = false
            for t2 in range(num_of_time_steps):
                was_ever = was_ever | P['U'][t2][l]
            if was_ever == true:
                for t2 in range(num_of_time_steps):
                    expression = expression & P['U'][t2][l] & (P['U'][t2][l] >> (~P['S'][t2][l] & ~P['H'][t2][l] & ~P['Q'][t2][l] & ~P['I'][t2][l]))
                continue
            # Can be nothing else
            expression = expression & (P['U'][t1][l] >> (~P['S'][t1][l] & ~P['H'][t1][l] & ~P['Q'][t1][l] & ~P['I'][t1][l]))
    # Check if the tile has ever been anything but wall
    for t1 in range(num_of_time_steps):
        for l in range(num_of_rows * num_of_columns):
            for code in ['H', 'S', 'Q', 'I']:
                if P[code][t1][l] == true:
                    for t2 in range(num_of_time_steps):
                        expression = expression & ~P['U'][t2][l]
    # If the tile is ever going to be a wall, he cant be anything else, ever
    for t1 in range(num_of_time_steps):
        for l in range(num_of_rows * num_of_columns):
            right_hand = true
            for t2 in range(num_of_time_steps):
                for code in ['H', 'S', 'Q', 'I']:
                    right_hand = right_hand & ~P[code][t2][l]
            expression = expression & (P['U'][t1][l] >> right_hand) & (P['U'][t1][l] << right_hand)

    # H
    for t in range(1, num_of_time_steps):
        for l in range(num_of_rows * num_of_columns):
            was_previously_healthy = P['H'][t-1][l]
            # Create a list of all valid neighbors
            i = floor(l / num_of_columns)
            j = l - i * num_of_rows
            above_pos = l - num_of_columns if i != 0 else None
            left_pos = l - 1 if j != 0 else None
            right_pos = l + 1 if j != (num_of_columns - 1) else None
            below_pos =  l + num_of_columns if i != (num_of_rows - 1) else None
            neighbors = [above_pos, left_pos, right_pos, below_pos]
            neighbors = set(neighbors)
            neighbors.discard(None)
            no_sick_neighbors = true
            # Check if any neighbor is sick
            for neighbor in neighbors:
                no_sick_neighbors = no_sick_neighbors & ~P['S'][t-1][neighbor]
            # The only way to be an H tile at time t without recovery or quarantine
            # Also make sure you didn't just get vaccinated
            non_recovery_option = no_sick_neighbors & was_previously_healthy & ~P['I'][t][l]
            # Apply different cluases based on the possibility of recovery or quarantine
            if t >= 3:
                recovery = P['S'][t-1][l] & P['S'][t-2][l] & P['S'][t-3][l]
                finished_qurantine = P['Q'][t-2][l] & P['Q'][t-1][l]
                expression = expression & (P['H'][t][l] >> (recovery | non_recovery_option | finished_qurantine)) & (P['H'][t][l] << (recovery | non_recovery_option | finished_qurantine))
            if t == 2:
                finished_qurantine = P['Q'][t-2][l] & P['Q'][t-1][l] 
                expression = expression & (P['H'][t][l] >> (non_recovery_option | finished_qurantine)) & (P['H'][t][l] << (non_recovery_option | finished_qurantine))
            if t == 1:
                expression = expression & (P['H'][t][l] >> non_recovery_option) & (P['H'][t][l] << non_recovery_option)
            # Can be nothing else
            expression = expression & (P['H'][t][l] >> (~P['S'][t][l] & ~P['U'][t][l] & ~P['Q'][t][l] & ~P['I'][t][l]))

    # S
    for t in range(1, num_of_time_steps):
        for l in range(num_of_rows * num_of_columns):
            was_previously_sick = P['S'][t-1][l]
            # Create a list of all valid neighbors
            i = floor(l / num_of_columns)
            j = l - i * num_of_rows
            above_pos = l - num_of_columns if i != 0 else None
            left_pos = l - 1 if j != 0 else None
            right_pos = l + 1 if j != (num_of_columns - 1) else None
            below_pos =  l + num_of_columns if i != (num_of_rows - 1) else None
            neighbors = [above_pos, left_pos, right_pos, below_pos] 
            neighbors = set(neighbors)
            neighbors.discard(None)
            sick_neighbors = false
            # Check if any neighbor is sick
            for neighbor in neighbors:
                sick_neighbors = sick_neighbors | P['S'][t-1][neighbor]
            # The only way to be an S tile at time t
            # Also make sure you aren't another tile
            expression = expression & (P['S'][t][l] >> ((sick_neighbors | was_previously_sick) & ~P['Q'][t][l] & ~P['U'][t][l] & ~P['I'][t][l] & ~P['H'][t][l])) & (P['S'][t][l] << ((sick_neighbors | was_previously_sick) & ~P['Q'][t][l] & ~P['U'][t][l] & ~P['I'][t][l] & ~P['H'][t][l]))
            # Can be nothing else
            expression = expression & (P['S'][t][l] >> (~P['H'][t][l] & ~P['U'][t][l] & ~P['Q'][t][l] & ~P['I'][t][l]))
    
    # Q
    # Probably will have difficulties with teams with size over 1
    if police_teams != 0:
        # Cannot be present at the start
        for l in range(num_of_rows * num_of_columns):
            expression = expression & ~P['Q'][0][l]
        for t in range(1, num_of_time_steps):
            # Go over every possible way to choose tiles for quarantine
            # Im not going to even try to explain whats below, I'm not sure myself
            for comb in combinations(range(num_of_rows* num_of_columns), police_teams):
                right_hand = true
                left_hand = true
                for l1 in comb:
                    left_hand = left_hand & P['Q'][t][l1]
                    if t >= 2:
                        was_quarantiend = P['Q'][t-1][l1] & ~P['Q'][t-2][l1]
                    else:
                        was_quarantiend = P['Q'][t-1][l1]
                    was_sick = P['S'][t-1][l1]
                    right_hand = right_hand & (was_quarantiend | was_sick)
                choose_k = (left_hand >> right_hand)
                choose_no_one_else = true
                for l in range(num_of_rows * num_of_columns):
                    if l in comb:
                        continue
                    choose_no_one_else = choose_no_one_else & ~P['Q'][t][l]
                expression = expression & choose_k & (left_hand >> choose_no_one_else)
                # Can be nothing else
                for l1 in comb:
                    expression = expression & (P['Q'][t][l1] >> (~P['H'][t][l1] & ~P['U'][t][l1] & ~P['S'][t][l1] & ~P['I'][t][l1]))
    # No teams means no possible Q tiles
    else:
        for t in range(num_of_time_steps):
            for l in range(num_of_rows * num_of_columns):
                expression = expression & ~P['Q'][t][l]

    # I
    # Probably doesnt work
    if medical_teams != 0:
        # Cannot be present at the start
        for l in range(num_of_rows * num_of_columns):
            expression = expression & ~P['I'][0][l]
        for t in range(1, num_of_time_steps):
            # Go over every possible way to choose tiles for quarantine
            # Im not going to even try to explain whats below, I'm not sure myself
            for comb in combinations(range(num_of_rows* num_of_columns), medical_teams):
                right_hand = true
                left_hand = true
                for l1 in comb:
                    left_hand = left_hand & P['I'][t][l1]
                    was_vaccinated = P['I'][t-1][l1]
                    was_healthy = P['H'][t-1][l1]
                    right_hand = right_hand & (was_vaccinated | was_healthy)
                choose_k = (left_hand >> right_hand)
                choose_no_one_else = true
                for l in range(num_of_rows * num_of_columns):
                    if l in comb:
                        continue
                    choose_no_one_else = choose_no_one_else & ~P['I'][t][l]
                expression = expression & (choose_k & (left_hand >> choose_no_one_else))
                # Can be nothing else
                for l1 in comb:
                    expression = expression & (P['I'][t][l1] >> (~P['H'][t][l1] & ~P['U'][t][l1] & ~P['S'][t][l1] & ~P['Q'][t][l1]))
    # No teams means no possible I tiles
    else:
        for t in range(num_of_time_steps):
            for l in range(num_of_rows * num_of_columns):
                expression = expression & ~P['I'][t][l]

    
    # Make sure every tile at a point in time can only have a single assignment
    for t in range(num_of_time_steps):
        for l in range(num_of_rows * num_of_columns):
            for code1 in ['U', 'H', 'S', 'Q', 'I']:
                right_hand = true
                for code2 in ['U', 'H', 'S', 'Q', 'I']:
                    if code1 == code2:
                        continue
                    right_hand = right_hand & ~P[code2][t][l]
                expression = expression & (P[code1][t][l] >> right_hand) & (P[code1][t][l] << right_hand)

    
    # Convert to CNF
    cnf = to_cnf(expression)
    return_dict = {}
    # Go over queries
    for query in queries:
        # A catch all in case of a logical mishap
        if cnf == true:
            return_dict[query] = '?'
            continue
        if not cnf:
            return_dict[query] = 'F'
            continue

        (i, j) = query[0]
        time_step = query[1]
        code = query[2]
        # Check if the query is true
        pos_query_cnf = cnf & P[code][time_step][i * num_of_columns + j]
        # Check if the query is false
        neg_query_cnf = cnf & ~P[code][time_step][i * num_of_columns + j]
        pos_input_cnf = []
        neg_input_cnf = []
        # Parse the cnf from the sympolab equation object
        for clause in str(pos_query_cnf).replace('~', '-').replace('(', '[').replace(')', ']').replace('|', ',').split('&'):
            try:
                res = int(clause)
                pos_input_cnf.append([res])
            except ValueError:
                res = loads(clause)
                pos_input_cnf.append(res)
        for clause in str(neg_query_cnf).replace('~', '-').replace('(', '[').replace(')', ']').replace('|', ',').split('&'):
            try:
                res = int(clause)
                neg_input_cnf.append([res])
            except ValueError:
                res = loads(clause)
                neg_input_cnf.append(res)
        
        # Start solving
        g_pos = Glucose3()
        for clause in pos_input_cnf:
            g_pos.add_clause(clause)
        g_neg = Glucose3()
        for clause in neg_input_cnf:
            g_neg.add_clause(clause)
        pos_found_sol = g_pos.solve()
        neg_found_sol = g_neg.solve()
        return_symbol = ''
        if pos_found_sol:
            return_symbol = "T"
        else:
            return_symbol = "F"
        if pos_found_sol and neg_found_sol:
            return_symbol = '?'
        return_dict[query] = return_symbol

    return return_dict