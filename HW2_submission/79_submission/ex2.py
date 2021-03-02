from pysat.solvers import Glucose4

ids = ['320867781', '307841189']


def KB(input):
    num_of_turns = len(input["observations"])
    num_of_rows = len(input["observations"][0])
    num_of_cols = len(input["observations"][0][0])
    KB_list = list()
    for turn in range(num_of_turns):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                if input["observations"][turn][row][col] == "H":
                    KB_list.append([int(str(1) + str(row) + str(col) + str(turn))])
                elif input["observations"][turn][row][col] == "S":
                    KB_list.append([int(str(2) + str(row) + str(col) + str(turn))])
                elif input["observations"][turn][row][col] == "U":
                    KB_list.append([int(str(3) + str(row) + str(col) + str(turn))])
                elif input["observations"][turn][row][col] == "Q":
                    KB_list.append([int(str(4) + str(row) + str(col) + str(turn))])
                elif input["observations"][turn][row][col] == "I":
                    KB_list.append([int(str(5) + str(row) + str(col) + str(turn))])
                else:
                    continue
    return KB_list


def create_atoms(num_of_turns, num_of_rows, num_of_cols):
    atoms_list = list()
    at_most_one = list()
    for turn in range(num_of_turns):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                healthy = int(str(1) + str(row) + str(col) + str(turn))
                sick = int(str(2) + str(row) + str(col) + str(turn))
                unpopulated = int(str(3) + str(row) + str(col) + str(turn))
                quarantined = int(str(4) + str(row) + str(col) + str(turn))
                vaccinated = int(str(5) + str(row) + str(col) + str(turn))
                at_least_one = [healthy, sick, unpopulated, quarantined, vaccinated]
                atoms_list.append(at_least_one)
                for status_num, status in enumerate(at_least_one):
                    for i in range(status_num + 1, len(at_least_one)):
                        at_most_one.append([-status, -at_least_one[i]])
    atoms_list += at_most_one
    return atoms_list


'''define actions and make sure that no interference'''
def actions(num_of_turns, num_of_rows, num_of_cols):
    actions_list = list()
    at_most_one_action_per_entry_turn = list()
    for turn in range(num_of_turns - 1):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                healing = int(str(1) + str(row) + str(col) + str(turn) + str(turn + 1))
                infection = int(str(2) + str(row) + str(col) + str(turn) + str(turn + 1))
                quarantine = int(str(4) + str(row) + str(col) + str(turn) + str(turn + 1))
                vaccinate = int(str(5) + str(row) + str(col) + str(turn) + str(turn + 1))
                noop_H = int(str(6) + str(row) + str(col) + str(turn) + str(turn + 1))
                noop_S = int(str(7) + str(row) + str(col) + str(turn) + str(turn + 1))
                noop_U= int(str(3) + str(row) + str(col) + str(turn) + str(turn + 1))
                noop_Q = int(str(8) + str(row) + str(col) + str(turn) + str(turn + 1))
                noop_I = int(str(9) + str(row) + str(col) + str(turn) + str(turn + 1))
                at_least_one_action_per_entry_turn = [infection, healing, quarantine, vaccinate,
                                                      noop_H, noop_S, noop_U, noop_Q, noop_I]
                actions_list.append(at_least_one_action_per_entry_turn)
                for status_num, status in enumerate(at_least_one_action_per_entry_turn):
                    for i in range(status_num + 1, len(at_least_one_action_per_entry_turn)):
                        at_most_one_action_per_entry_turn.append([-status, -at_least_one_action_per_entry_turn[i]])
    actions_list += at_most_one_action_per_entry_turn
    return actions_list


'''ask how to  model that if no S that no quarantine'''
def quarantine_action(num_of_turns, num_of_rows, num_of_cols):
    quarantine_rules = list()
    at_most_one = list()
    for turn in range(num_of_turns - 1):
        at_least_one = list()
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                quarantine = int(str(4) + str(row) + str(col) + str(turn) + str(turn + 1))
                at_least_one.append(quarantine)
                for i in range(row + 1, num_of_rows):
                    for j in range(col + 1, num_of_cols):
                        at_most_one.append([-int(str(4) + str(row) + str(col) + str(turn) + str(turn + 1)),
                                            -int(str(4) + str(i) + str(j) + str(turn) + str(turn + 1))])
        quarantine_rules.append(at_least_one)
    quarantine_rules += at_most_one
    return quarantine_rules


'''ask how to  model that if no H that no vaccinate'''
def vaccinate_action(num_of_turns, num_of_rows, num_of_cols):
    vaccinate_rules = list()
    at_most_one = list()
    for turn in range(num_of_turns - 1):
        at_least_ane = list()
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                vaccinate = int(str(5) + str(row) + str(col) + str(turn) + str(turn + 1))
                at_least_ane.append(vaccinate)
                for i in range(row + 1, num_of_rows):
                    for j in range(col + 1, num_of_cols):
                        at_most_one.append([-int(str(5) + str(row) + str(col) + str(turn) + str(turn + 1)),
                                            -int(str(5) + str(i) + str(j) + str(turn) + str(turn + 1))])
        vaccinate_rules.append(at_least_ane)
    vaccinate_rules += at_most_one
    return vaccinate_rules


def infection_action_precondition(num_of_turns, num_of_rows, num_of_cols):
    infection_preconditions = list()
    for turn in range(num_of_turns):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                infection = int(str(2) + str(row) + str(col) + str(turn) + str(turn + 1))
                '''preconditions: 1. i was H, 2. at least one of my neighbors was S'''
                infection_preconditions.append([-infection, int(str(1) + str(row) + str(col) + str(turn))])
                if row == 0 and col == 0: # top-left corner
                    infection_preconditions.append([-infection, int(str(2) + str(row + 1) + str(col) + str(turn)),
                                                    int(str(2) + str(row) + str(col + 1) + str(turn))])
                elif row == 0 and col == num_of_cols - 1: # top-right corner
                    infection_preconditions.append([-infection, int(str(2) + str(row + 1) + str(col) + str(turn)),
                                                    int(str(2) + str(row) + str(col - 1) + str(turn))])
                elif row == 0: # rest of first row
                    infection_preconditions.append([-infection, int(str(2) + str(row + 1) + str(col) + str(turn)),
                                                    int(str(2) + str(row) + str(col + 1) + str(turn)),
                                                    int(str(2) + str(row) + str(col - 1) + str(turn))])
                elif row == num_of_rows - 1 and col == 0: # bottom-left corner
                    infection_preconditions.append([-infection, int(str(2) + str(row - 1) + str(col) + str(turn)),
                                                    int(str(2) + str(row) + str(col + 1) + str(turn))])
                elif row == num_of_rows - 1 and col == num_of_cols - 1: # bottom-right corner
                    infection_preconditions.append([-infection, int(str(2) + str(row - 1) + str(col) + str(turn)),
                                                    int(str(2) + str(row) + str(col - 1) + str(turn))])
                elif row == num_of_rows - 1: # rest of last row
                    infection_preconditions.append([-infection, int(str(2) + str(row - 1) + str(col) + str(turn)),
                                                    int(str(2) + str(row) + str(col + 1) + str(turn)),
                                                    int(str(2) + str(row) + str(col - 1) + str(turn))])
                elif col == 0: # rest of first column
                    infection_preconditions.append([-infection, int(str(2) + str(row) + str(col + 1) + str(turn)),
                                                    int(str(2) + str(row + 1) + str(col) + str(turn)),
                                                    int(str(2) + str(row - 1) + str(col) + str(turn))])
                elif col == num_of_cols - 1: # rest of last row
                    infection_preconditions.append([-infection, int(str(2) + str(row) + str(col - 1) + str(turn)),
                                                    int(str(2) + str(row + 1) + str(col) + str(turn)),
                                                    int(str(2) + str(row - 1) + str(col) + str(turn))])
                else: # rest of the grid
                    infection_preconditions.append([-infection, int(str(2) + str(row) + str(col + 1) + str(turn)),
                                                    int(str(2) + str(row) + str(col - 1) + str(turn)),
                                                    int(str(2) + str(row + 1) + str(col) + str(turn)),
                                                    int(str(2) + str(row - 1) + str(col) + str(turn))])
    return infection_preconditions


def healing_action_precondition(num_of_turns, num_of_rows, num_of_cols):
    healing_preconditions = list()
    for turn in range(2, num_of_turns):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                healing = int(str(1) + str(row) + str(col) + str(turn) + str(turn + 1))
                '''pre-conditions: i'm S for last 3 turns or i'm Q for last 2 turns'''
                healing_preconditions.append([-healing, int(str(2) + str(row) + str(col) + str(turn)),
                                              int(str(4) + str(row) + str(col) + str(turn))])
                healing_preconditions.append([-healing, int(str(2) + str(row) + str(col) + str(turn - 1)),
                                              int(str(4) + str(row) + str(col) + str(turn - 1))])
                healing_preconditions.append([-healing, int(str(2) + str(row) + str(col) + str(turn - 2))])
    return healing_preconditions


def quarantine_action_precondition(num_of_turns, num_of_rows, num_of_cols):
    quarantine_precondition = list()
    for turn in range(num_of_turns - 1):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                quarantine = int(str(4) + str(row) + str(col) + str(turn) + str(turn + 1))
                '''pre-condition: i was S in this turn'''
                quarantine_precondition.append([-quarantine, int(str(2) + str(row) + str(col) + str(turn))])
    return quarantine_precondition


def vaccinate_action_precondition(num_of_turns, num_of_rows, num_of_cols):
    vaccinate_precondition = list()
    for turn in range(num_of_turns - 1):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                vaccinate = int(str(5) + str(row) + str(col) + str(turn) + str(turn + 1))
                '''pre-condition: i was H in this turn'''
                vaccinate_precondition.append([-vaccinate, int(str(1) + str(row) + str(col) + str(turn))])
    return vaccinate_precondition


def noop_H_action_precondition(num_of_turns, num_of_rows, num_of_cols):
    noop_H_precondition = list()
    for turn in range(num_of_turns - 1):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                noop_H = int(str(6) + str(row) + str(col) + str(turn) + str(turn + 1))
                '''preconditions: i was H in this turn and that are nobody from my the neighbors S'''
                noop_H_precondition.append([-noop_H, int(str(1) + str(row) + str(col) + str(turn))])
                if row == 0 and col == 0:
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row + 1) + str(col) + str(turn))])
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row) + str(col + 1) + str(turn))])
                elif row == 0 and col == num_of_cols - 1:
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row + 1) + str(col) + str(turn))])
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row) + str(col - 1) + str(turn))])
                elif row == num_of_rows - 1 and col == 0:
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row - 1) + str(col) + str(turn))])
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row) + str(col + 1) + str(turn))])
                elif row == num_of_rows - 1 and col == num_of_cols - 1:
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row - 1) + str(col) + str(turn))])
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row) + str(col - 1) + str(turn))])
                elif row == 0:
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row + 1) + str(col) + str(turn))])
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row) + str(col + 1) + str(turn))])
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row) + str(col - 1) + str(turn))])
                elif row == num_of_rows - 1:
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row - 1) + str(col) + str(turn))])
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row) + str(col + 1) + str(turn))])
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row) + str(col - 1) + str(turn))])
                elif col == 0:
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row + 1) + str(col) + str(turn))])
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row - 1) + str(col) + str(turn))])
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row) + str(col + 1) + str(turn))])
                elif col == num_of_cols - 1:
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row + 1) + str(col) + str(turn))])
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row - 1) + str(col) + str(turn))])
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row) + str(col - 1) + str(turn))])
                else:
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row + 1) + str(col) + str(turn))])
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row - 1) + str(col) + str(turn))])
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row) + str(col + 1) + str(turn))])
                    noop_H_precondition.append([-noop_H, -int(str(2) + str(row) + str(col - 1) + str(turn))])
    return noop_H_precondition


def noop_S_action_precondition(num_of_turns, num_of_rows, num_of_cols):
    noop_S_precondition = list()
    for turn in range(num_of_turns - 1):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                noop_S = int(str(7) + str(row) + str(col) + str(turn) + str(turn + 1))
                '''precondition: i'm S now and i'm not S for last 3 turns, including this'''
                noop_S_precondition.append([-noop_S, int(str(2) + str(row) + str(col) + str(turn))])
                if turn <= 1:
                    continue
                else:
                    noop_S_precondition.append([-noop_S, -int(str(2) + str(row) + str(col) + str(turn - 1)),
                                                -int(str(2) + str(row) + str(col) + str(turn - 2))])
    return noop_S_precondition


def noop_U_action_precondition(num_of_turns, num_of_rows, num_of_cols):
    noop_U_precondition = list()
    for turn in range(num_of_turns - 1):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                noop_U = int(str(3) + str(row) + str(col) + str(turn) + str(turn + 1))
                '''precondition: i'm' U in this turn'''
                noop_U_precondition.append([-noop_U, int(str(3) + str(row) + str(col) + str(turn))])
    return noop_U_precondition


def noop_Q_action_precondition(num_of_turns, num_of_rows, num_of_cols):
    noop_Q_precondition = list()
    for turn in range(num_of_turns - 1):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                noop_Q = int(str(8) + str(row) + str(col) + str(turn) + str(turn + 1))
                '''preconditions: i'm Q now and i wasn't Q in turn - 1'''
                if turn == 0: # maybe it should be <= 1
                    continue
                else:
                    noop_Q_precondition.append([-noop_Q, int(str(4) + str(row) + str(col) + str(turn))])
                    noop_Q_precondition.append([-noop_Q, -int(str(4) + str(row) + str(col) + str(turn - 1))])
    return noop_Q_precondition


def noop_I_action_precondition(num_of_turns, num_of_rows, num_of_cols):
    noop_I_precondition = list()
    for turn in range(num_of_turns - 1):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                noop_I = int(str(9) + str(row) + str(col) + str(turn) + str(turn + 1))
                '''precondition: i'm I in this turn'''
                noop_I_precondition.append([-noop_I, int(str(5) + str(row) + str(col) + str(turn))])
    return noop_I_precondition


def infection_action_fact_achievement(num_of_turns, num_of_rows, num_of_cols):
    infection_fact_achievement = list()
    for turn in range(num_of_turns, 0, -1):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                infection_fact_achievement.append([-int(str(2) + str(row) + str(col) + str(turn)),
                                                   int(str(2) + str(row) + str(col) + str(turn - 1) + str(turn)),
                                                   int(str(7) + str(row) + str(col) + str(turn - 1) + str(turn))])
    return infection_fact_achievement


def healing_action_fact_achievement(num_of_turns, num_of_rows, num_of_cols):
    healing_fact_achievement = list()
    for turn in range(num_of_turns, 2, -1):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                healing_fact_achievement.append([-int(str(1) + str(row) + str(col) + str(turn)),
                                                 int(str(1) + str(row) + str(col) + str(turn - 1) + str(turn)),
                                                 int(str(6) + str(row) + str(col) + str(turn - 1) + str(turn))])
    for row in range(num_of_rows):
        for col in range(num_of_cols):
            healing_fact_achievement.append([-int(str(1) + str(row) + str(col) + str(1)),
                                             int(str(6) + str(row) + str(col) + str(0) + str(1))])
            healing_fact_achievement.append([-int(str(1) + str(row) + str(col) + str(2)),
                                             int(str(6) + str(row) + str(col) + str(1) + str(2))])
    return healing_fact_achievement


def unpopulated_action_fact_achievement(num_of_turns, num_of_rows, num_of_cols):
    unpopulated_fact_achievement = list()
    for turn in range(num_of_turns, 0, -1):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                unpopulated_fact_achievement.append([-int(str(3) + str(row) + str(col) + str(turn)),
                                                     int(str(3) + str(row) + str(col) + str(turn - 1) + str(turn))])
    return unpopulated_fact_achievement


def qur_action_fact_achievement(num_of_turns, num_of_rows, num_of_cols):
    qur_fact_achievement = list()
    for turn in range(num_of_turns, 0, -1):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                qur_fact_achievement.append([-int(str(4) + str(row) + str(col) + str(turn)),
                                             int(str(4) + str(row) + str(col) + str(turn - 1) + str(turn)),
                                             int(str(8) + str(row) + str(col) + str(turn - 1) + str(turn))])
    return qur_fact_achievement


def vac_action_fact_achievement(num_of_turns, num_of_rows, num_of_cols):
    vac_fact_achievement = list()
    for turn in range(num_of_turns, 0, -1):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                vac_fact_achievement.append([-int(str(5) + str(row) + str(col) + str(turn)),
                                             int(str(5) + str(row) + str(col) + str(turn - 1) + str(turn)),
                                             int(str(9) + str(row) + str(col) + str(turn - 1) + str(turn))])
    return vac_fact_achievement


def additional_rules(num_of_turns, num_of_rows, num_of_cols, num_of_police, num_of_medics):
    additional_rules_list = list()
    for turn in range(num_of_turns):
        for row in range(num_of_rows):
            for col in range(num_of_cols):
                '''no Q or I in first turn'''
                if turn == 0:
                    additional_rules_list.append([-int(str(4) + str(row) + str(col) + str(turn))])
                    additional_rules_list.append([-int(str(5) + str(row) + str(col) + str(turn))])

                else:
                    '''if no police there are no Q and no quarantine action'''
                    if num_of_police == 0:
                        additional_rules_list.append([-int(str(4) + str(row) + str(col) + str(turn))])
                        additional_rules_list.append([-int(str(4) + str(row) + str(col) + str(turn) + str(turn + 1))])
                    '''if no medics there are no I and no vaccinate action'''
                    if num_of_medics == 0:
                        additional_rules_list.append([-int(str(5) + str(row) + str(col) + str(turn))])
                        additional_rules_list.append([-int(str(5) + str(row) + str(col) + str(turn) + str(turn + 1))])
    return additional_rules_list


def solve_problem(input):
    num_of_turns = len(input["observations"])
    num_of_rows = len(input["observations"][0])
    num_of_cols = len(input["observations"][0][0])
    num_of_police = input["police"]
    num_of_medics = input["medics"]
    clauses = list()
    clauses += KB(input)
    clauses += create_atoms(num_of_turns, num_of_rows, num_of_cols)
    clauses += actions(num_of_turns, num_of_rows, num_of_cols)
    clauses += infection_action_precondition(num_of_turns, num_of_rows, num_of_cols)
    if num_of_turns > 3:
        clauses += healing_action_precondition(num_of_turns, num_of_rows, num_of_cols)
    clauses += noop_H_action_precondition(num_of_turns, num_of_rows, num_of_cols)
    clauses += noop_S_action_precondition(num_of_turns, num_of_rows, num_of_cols)
    clauses += noop_U_action_precondition(num_of_turns, num_of_rows, num_of_cols)
    clauses += infection_action_fact_achievement(num_of_turns, num_of_rows, num_of_cols)
    clauses += healing_action_fact_achievement(num_of_turns, num_of_rows, num_of_cols)
    clauses += unpopulated_action_fact_achievement(num_of_turns, num_of_rows, num_of_cols)
    clauses += additional_rules(num_of_turns, num_of_rows, num_of_cols, num_of_police, num_of_medics)
    if num_of_police == 0 and num_of_medics == 0:
        queries_dict = dict()
        for query in input["queries"]:
            if query[2] == "H":
                assumption = int(str(1) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            elif query[2] == "S":
                assumption = int(str(2) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            else:  # query[2] == "U"
                assumption = int(str(3) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            g1 = Glucose4(bootstrap_with=clauses + [[-assumption]])
            g2 = Glucose4(bootstrap_with=clauses + [[assumption]])
            solver1 = g1.solve()
            solver2 = g2.solve()
            if solver1 and solver2:
                queries_dict[query] = '?'
            elif not solver1 and solver2:
                queries_dict[query] = 'T'
            else:
                queries_dict[query] = 'F'
        return queries_dict
    elif num_of_police == 1 and num_of_medics == 0:
        clauses += quarantine_action(num_of_turns, num_of_rows, num_of_cols)
        clauses += quarantine_action_precondition(num_of_turns, num_of_rows, num_of_cols)
        clauses += noop_Q_action_precondition(num_of_turns, num_of_rows, num_of_cols)
        clauses += qur_action_fact_achievement(num_of_turns, num_of_rows, num_of_cols)
        queries_dict = dict()
        for query in input["queries"]:
            if query[2] == "H":
                assumption = int(str(1) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            elif query[2] == "S":
                assumption = int(str(2) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            elif query[2] == "U":
                assumption = int(str(3) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            else: # query[2] == "Q"
                assumption = int(str(4) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            g1 = Glucose4(bootstrap_with=clauses + [[-assumption]])
            g2 = Glucose4(bootstrap_with=clauses + [[assumption]])
            solver1 = g1.solve()
            solver2 = g2.solve()
            if solver1 and solver2:
                queries_dict[query] = '?'
            elif not solver1 and solver2:
                queries_dict[query] = 'T'
            else:
                queries_dict[query] = 'F'
        return queries_dict
    elif num_of_police == 0 and num_of_medics == 1:
        clauses += vaccinate_action(num_of_turns, num_of_rows, num_of_cols)
        clauses += vaccinate_action_precondition(num_of_turns, num_of_rows, num_of_cols)
        clauses += noop_I_action_precondition(num_of_turns, num_of_rows, num_of_cols)
        clauses += vac_action_fact_achievement(num_of_turns, num_of_rows, num_of_cols)
        queries_dict = dict()
        for query in input["queries"]:
            if query[2] == "H":
                assumption = int(str(1) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            elif query[2] == "S":
                assumption = int(str(2) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            elif query[2] == "U":
                assumption = int(str(3) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            else:  # query[2] == "I"
                assumption = int(str(5) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            g1 = Glucose4(bootstrap_with=clauses + [[-assumption]])
            g2 = Glucose4(bootstrap_with=clauses + [[assumption]])
            solver1 = g1.solve()
            solver2 = g2.solve()
            if solver1 and solver2:
                queries_dict[query] = '?'
            elif not solver1 and solver2:
                queries_dict[query] = 'T'
            else:
                queries_dict[query] = 'F'
        return queries_dict
    else:
        clauses += quarantine_action(num_of_turns, num_of_rows, num_of_cols)
        clauses += quarantine_action_precondition(num_of_turns, num_of_rows, num_of_cols)
        clauses += noop_Q_action_precondition(num_of_turns, num_of_rows, num_of_cols)
        clauses += qur_action_fact_achievement(num_of_turns, num_of_rows, num_of_cols)
        clauses += vaccinate_action(num_of_turns, num_of_rows, num_of_cols)
        clauses += vaccinate_action_precondition(num_of_turns, num_of_rows, num_of_cols)
        clauses += noop_I_action_precondition(num_of_turns, num_of_rows, num_of_cols)
        clauses += vac_action_fact_achievement(num_of_turns, num_of_rows, num_of_cols)
        queries_dict = dict()
        for query in input["queries"]:
            if query[2] == "H":
                assumption = int(str(1) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            elif query[2] == "S":
                assumption = int(str(2) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            elif query[2] == "U":
                assumption = int(str(3) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            elif query[2] == "Q":
                assumption = int(str(4) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            else:  # query[2] == "I"
                assumption = int(str(5) + str(query[0][0]) + str(query[0][1]) + str(query[1]))
            g1 = Glucose4(bootstrap_with=clauses + [[-assumption]])
            g2 = Glucose4(bootstrap_with=clauses + [[assumption]])
            solver1 = g1.solve()
            solver2 = g2.solve()
            if solver1 and solver2:
                queries_dict[query] = '?'
            elif not solver1 and solver2:
                queries_dict[query] = 'T'
            else:
                queries_dict[query] = 'F'
        return queries_dict
