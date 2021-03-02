ids = ['318801701', '211876644']
from pysat.solvers import Solver
from copy import deepcopy
import itertools
status_dict = {"S": 1, "H": 2, "Q": 3, "I": 4, "U": 5}


def calc_rep(turn, square_num, status, bool_indicator=True):
    val = 10000*turn + 10*square_num + status_dict[status]
    if bool_indicator:
        return val
    return -val


def calc_square_num(i, j, observations):
    return i * len(observations[0]) + j + 1


def map_tuple_list(observations):
    for j in range(len(observations)):
        observations[j] = list(observations[j])
        for i in range(len(observations[j])):
            observations[j][i] = list(observations[j][i])
    return observations


def find_neighbors(square_num, observations):
    neighbors = []
    if square_num > len(observations[0][0]):
        neighbors.append(square_num - len(observations[0][0]))
    if square_num < (len(observations[0])-1)*len(observations[0][0])+1:
        neighbors.append(square_num + len(observations[0][0]))
    if square_num%len(observations[0][0]) != 1:
        neighbors.append(square_num-1)
    if square_num%len(observations[0][0]) != 0:
        neighbors.append(square_num+1)
    return neighbors


def solve_u(square_num, turn):
    if turn != 0:
        return [[calc_rep(turn-1, square_num, "U")]]


def solve_s(square_num, turn, observations):
    neighbors = find_neighbors(square_num,observations)
    clauses = []
    if turn > 2:
        group_one = [calc_rep(turn-1, square_num, "S"), calc_rep(turn-2,square_num,"S",bool_indicator=False)]
        group_two = [calc_rep(turn-1, square_num, "S"), calc_rep(turn-3,square_num,"S",bool_indicator=False)]
        neighbors_are_sick_last_round = []
        neighbors_are_not_currently_quarantined = []
        for n in neighbors:
            neighbors_are_not_currently_quarantined.append(calc_rep(turn-1, n, "Q",bool_indicator=False))
            neighbors_are_sick_last_round.append(calc_rep(turn-1, n, "S"))
        all_binary_assignments = list(itertools.product([0,1],repeat = len(neighbors)))
        asdf = []
        for assignment in all_binary_assignments:
            possible = []
            for i,item in enumerate(assignment):
                if item == 1:
                    possible.append(neighbors_are_sick_last_round[i])
                else:
                    possible.append(neighbors_are_not_currently_quarantined[i])
            asdf.append(possible)
        group_three = [calc_rep(turn - 1, square_num, "H"), asdf]
        for item1 in group_one:
            for item2 in group_two:
                for item3 in group_three:
                    if isinstance(item3, list):
                        for item4 in item3:
                            clause = [item1, item2]
                            for item5 in item4:
                                clause.append(item5)
                            clauses.append(clause)
                    else:
                        clauses.append([item1, item2, item3])
    elif turn == 1 or turn == 2:
        group_one = [calc_rep(turn-1, square_num, "S")]
        asdf = []
        for n in neighbors:
            asdf.append(calc_rep(turn - 1, n, "S"))
        group_two = [calc_rep(turn - 1, square_num, "H"), asdf]
        for item in group_one:
            for item2 in group_two:
                if isinstance(item2, list):
                    clause = [item]
                    for item4 in item2:
                        clause.append(item4)
                    clauses.append(clause)
                else:
                    clauses.append([item,item2])
    for n in neighbors:
        clause = [calc_rep(turn+1,square_num,"Q"),calc_rep(turn+1,n,"S"),calc_rep(turn,n,"H",bool_indicator=False),calc_rep(turn+1,n,"I")]
        clauses.append(clause)

    return clauses


def solve_h(square_num, turn, observations):
    clauses = []
    neighbors = find_neighbors(square_num, observations)
    if turn > 2:
        group_one = []
        group_two = []
        group_three = []
        group_one.append(calc_rep(turn-1, square_num, "Q"))
        group_two.append(calc_rep(turn - 1, square_num, "S"))
        group_three.append(calc_rep(turn - 1, square_num, "H"))
        for n in neighbors:
            group_three.append(calc_rep(turn - 1, n, "S", bool_indicator=False))
        group_one.append(calc_rep(turn - 2, square_num, "Q"))
        group_two.append(calc_rep(turn - 2, square_num, "S"))
        group_two.append(calc_rep(turn - 3, square_num, "S"))
        group_four = [calc_rep(turn-1,square_num,'H')]
        for n in neighbors:
            group_four.append([calc_rep(turn-1, n, 'S', bool_indicator=False),calc_rep(turn,n,'Q')])
        for item1 in group_one:
            for item2 in group_two:
                for item3 in group_three:
                    for item4 in group_four:
                        if isinstance(item4,list):
                            clause = [item1,item2,item3]
                            for item5 in item4:
                                clause.append(item5)
                        else:
                            clause = [item1,item2,item3,item4]
                        clauses.append(clause)
    elif turn == 1 or turn == 2:
        group_three = []
        group_three.append(calc_rep(turn - 1, square_num, "H"))
        for n in neighbors:
            group_three.append(calc_rep(turn - 1, n, "S", bool_indicator=False))
        group_four = [calc_rep(turn - 1, square_num, 'H')]
        for n in neighbors:
            group_four.append([calc_rep(turn - 1, n, 'S', bool_indicator=False), calc_rep(turn, n, 'Q')])
        for item3 in group_three:
            for item4 in group_four:
                clause = [item3]
                if isinstance(item4, list):
                    for item5 in item4:
                        clause.append(item5)
                else:
                    clause.append(item4)
                clauses.append(clause)
    return clauses


def solve_q(square_num, turn):
    clauses = []
    if turn > 1:
        clauses.append([calc_rep(turn - 1, square_num, "S"), calc_rep(turn - 1, square_num, "Q")])
        clauses.append([calc_rep(turn - 1, square_num, "S"), calc_rep(turn - 2, square_num, "Q", bool_indicator=False)])
    elif turn == 1:
        clauses.append([calc_rep(turn-1,square_num,"S")])
    return clauses


def solve_i(square_num, turn):
    clauses = []
    if turn != 0:
        clauses.append([calc_rep(turn-1, square_num, "I"), calc_rep(turn-1, square_num, "H")])
    return clauses


def solve_unknown(square_num, turn, observations, assumptions_li):
    literals = []
    for s, _ in status_dict.items():
        literals.append(calc_rep(turn, square_num, s))
    temp = cardinality_equals(literals, 1)
    clauses = []
    for c in temp:
        clauses.append(c)
    for s, _ in status_dict.items():
        if turn == 0:
            assumptions_li.append([calc_rep(turn,square_num,"I",bool_indicator=False)])
            assumptions_li.append([calc_rep(turn,square_num,"Q",bool_indicator=False)])
        status_clauses = solve_square(square_num, s, turn, observations,assumptions_li)
        if status_clauses:
            for clause in status_clauses:
                clause.append(calc_rep(turn, square_num, s, bool_indicator=False))
                clauses.append(clause)
    return clauses


def solve_square(square_num, status, turn, observations,assumptions):
    if status == "H":
        clauses = solve_h(square_num, turn, observations)
    elif status == "Q":
        clauses = solve_q(square_num, turn)
    elif status == "S":
        clauses = solve_s(square_num, turn, observations)
    elif status == "I":
        clauses = solve_i(square_num, turn)
    elif status == "U":
        clauses = solve_u(square_num, turn)
    else:
        clauses = solve_unknown(square_num, turn, observations,assumptions)

    if clauses:
        return clauses


def assumptions_for_s(turn_assumptions, turn, square_num, assumptions):
    flag = False
    for i in range(len(assumptions)):
        if calc_rep(turn-1, square_num, "S", bool_indicator=False) in assumptions[i]:
            flag = True
    if turn == 0 or flag:
        for progress in range(1, 3):
            for status in ["I", "U", "H"]:
                turn_assumptions.append(calc_rep(turn + progress, square_num, status, bool_indicator=False))
        for status in ["S", "I", "U"]:
            turn_assumptions.append(calc_rep(turn + 3, square_num, status, bool_indicator=False))

    for turnnum in range(len(assumptions)):
        assumptions[turnnum].append(calc_rep(turnnum, square_num, "U", bool_indicator=False))
        assumptions[turnnum].append(calc_rep(turnnum, square_num, "I", bool_indicator=False))


def assumptions_for_q(turn_assumptions, turn, square_num, assumptions):
    flag = False
    for i in range(len(assumptions)):
        if calc_rep(turn-1, square_num, "Q", bool_indicator=False) in assumptions[i]:
            flag = True
    if flag:
        for progress in range(1, 2):
            for status in ["I", "U", "H"]:
                turn_assumptions.append(calc_rep(turn+progress, square_num, status, bool_indicator=False))
        turn_assumptions.append(calc_rep(turn+2, square_num, "H"))
        append_all_false_statuses(turn_assumptions, turn+2, square_num, "H")
        if turn>0:
            turn_assumptions.append(calc_rep(turn-1, square_num, "S"))
            append_all_false_statuses(turn_assumptions, turn-1, square_num, "S")

    for turnnum in range(len(assumptions)):
        assumptions[turnnum].append(calc_rep(turnnum, square_num, "U", bool_indicator=False))
        assumptions[turnnum].append(calc_rep(turnnum, square_num, "I", bool_indicator=False))


def assumptions_for_u(turn_assumptions, turn, square_num, assumptions):
    for turnnum in range(len(assumptions)):
        assumptions[turnnum].append(calc_rep(turnnum, square_num, "U"))
        append_all_false_statuses(assumptions[turnnum], turnnum, square_num, "U")


def assumptions_for_h(turn_assumptions, turn, square_num, assumptions):
    for turnnum in range(len(assumptions)):
        assumptions[turnnum].append(calc_rep(turnnum, square_num, "U", bool_indicator=False))
        assumptions[turnnum].append(calc_rep(turnnum, square_num, "I", bool_indicator=False))


def assumptions_for_i(turn_assumptions, turn, square_num, assumptions):
    flag = False
    for i in range(len(assumptions)):
        if calc_rep(turn-1, square_num, "I", bool_indicator=False) in assumptions[i]:
            flag = True
    if flag:
        if turn>0:
            turn_assumptions.append(calc_rep(turn-1, square_num, "H"))
            append_all_false_statuses(turn_assumptions, turn-1, square_num, "H")


def append_all_false_statuses(turn_assumptions, turn, square_num, status):
    for key, _ in status_dict.items():
        if key != status:
            turn_assumptions.append(calc_rep(turn, square_num, key, bool_indicator=False))


def assumptions_for_status(square_num, status, turn, status_func, turn_assumptions, assumptions):
    status_func(turn_assumptions, turn, square_num, assumptions)


def create_assumptions(observations):
    assumptions = []
    for turn in range(len(observations)):
        turn_assumptions = []
        for i in range(len(observations[0])):
            for j in range(len(observations[0][0])):
                square_num = calc_square_num(i, j, observations)
                if observations[turn][i][j] != "?":
                    turn_assumptions.append(calc_rep(turn, square_num, observations[turn][i][j]))
                    append_all_false_statuses(turn_assumptions, turn, square_num, observations[turn][i][j])
                    if observations[turn][i][j] == "S":
                        assumptions_for_status(square_num, "S", turn, assumptions_for_s, turn_assumptions, assumptions)
                    elif observations[turn][i][j] == "Q":
                        assumptions_for_status(square_num, "Q", turn, assumptions_for_q, turn_assumptions, assumptions)
                    elif observations[turn][i][j] == "U":
                        assumptions_for_status(square_num, "U", turn, assumptions_for_u, turn_assumptions, assumptions)
                    elif observations[turn][i][j] == "H":
                        assumptions_for_status(square_num, "H", turn, assumptions_for_h, turn_assumptions, assumptions)
                    elif observations[turn][i][j] == "I":
                        assumptions_for_status(square_num, "I", turn, assumptions_for_i, turn_assumptions, assumptions)
                else:
                    if turn != 0:
                        if calc_rep(turn-1, square_num, "I") in assumptions[turn - 1]:
                            turn_assumptions.append(calc_rep(turn, square_num, "I"))
                            append_all_false_statuses(turn_assumptions, turn, square_num, "I")
                        if calc_rep(turn-1, square_num, "U") in assumptions[turn - 1]:
                            turn_assumptions.append(calc_rep(turn, square_num, "U"))
                            append_all_false_statuses(turn_assumptions, turn, square_num, "U")

        assumptions.append(turn_assumptions)
    return assumptions


def cardinality_equals(literals, bound):
    at_most_combs = itertools.combinations(literals, bound+1)
    at_least_combs = itertools.combinations(literals, len(literals)-bound+1)
    clauses = []
    for c in at_least_combs:
        clauses.append(list(c))
    for c in at_most_combs:
        temp = []
        for item in c:
            temp.append(-item)
        clauses.append(temp)
    return clauses


def assign_workers(affected_squares_per_turn, unknown_squares, status, num_workers, assumption_li, solver, observations):
    for turn, s_list in affected_squares_per_turn.items():
        num_turned_into_q = 0
        possible_q_turns = []
        if turn < len(observations) - 1:
            for (i, j) in s_list:
                if observations[turn+1][i][j] == status:
                    num_turned_into_q += 1
                elif observations[turn+1][i][j] == "?":
                    possible_q_turns.append((i, j))

            if num_workers > num_turned_into_q:
                num_transforms_left = num_workers - num_turned_into_q
                unknown_maybe_transformed = []
                if turn in unknown_squares.keys():
                    for (i,j) in unknown_squares[turn]:
                        if observations[turn+1][i][j] in ["?", status]:
                            unknown_maybe_transformed.append((i, j))
                all_possible_transforms = unknown_maybe_transformed + possible_q_turns
                groups = []
                literals_current_turn, literals_next_turn = [], []
                for (i,j) in all_possible_transforms:
                    literals_current_turn.append(calc_rep(turn,calc_square_num(i,j,observations),status))
                    literals_next_turn.append(calc_rep(turn+1,calc_square_num(i,j,observations),status))
                for num_are_q in range(len(all_possible_transforms)):
                    clauses1 = cardinality_equals(literals_current_turn,num_are_q)
                    clauses2 = cardinality_equals(literals_next_turn, num_are_q+num_transforms_left)
                    temp = clauses1 + clauses2
                    groups.append(temp)
                product_output = itertools.product(*groups)
                for clause_combs in product_output:
                    new_clause = []
                    for clause in clause_combs:
                        new_clause += clause
                    solver.add_clause(new_clause)

            elif num_workers == num_turned_into_q:
                temp = []
                for (i,j) in possible_q_turns:
                    square_num = calc_square_num(i,j,observations)
                    temp.append(calc_rep(turn+1, square_num, status, bool_indicator=False))
                assumption_li.append(temp)
                clauses = []
                if turn in unknown_squares.keys():
                    for (i, j) in unknown_squares[turn]:
                        square_num = calc_square_num(i, j, observations)
                        clauses.append([calc_rep(turn, square_num, status), calc_rep(turn+1, square_num, status, bool_indicator=False)])
                    for c in clauses:
                        solver.add_clause(c)
            else:
                temp = []
                temp.append(calc_rep(turn, 1, "I"))
                temp.append(calc_rep(turn, 1, "I", bool_indicator=False))
                assumption_li.append(temp)


def check_sat(observations, num_medics, num_police):
    s = Solver(name='g4', with_proof= True)
    assumptions = create_assumptions(observations)
    h_squares, s_squares, unknown_squares = {}, {}, {}
    for i in range(len(observations[0])):
        for j in range(len(observations[0][0])):
            for turn in range(len(observations)):
                status = observations[turn][i][j]
                if turn == 0 and status in ["I", "Q"]:
                    return False
                square_num = calc_square_num(i, j, observations)
                clauses = solve_square(square_num, status, turn, observations,assumptions)
                if clauses:
                    for c in clauses:
                        s.add_clause(c)
                if status == 'H':
                    if turn not in h_squares.keys():
                        h_squares[turn] = [(i,j)]
                    else:
                        h_squares[turn].append((i,j))
                elif status == 'S':
                    if turn not in s_squares.keys():
                        s_squares[turn] = [(i,j)]
                    else:
                        s_squares[turn].append((i,j))
                elif status == "?":
                    if turn not in unknown_squares.keys():
                        unknown_squares[turn] = [(i,j)]
                    else:
                        unknown_squares[turn].append((i,j))

    assign_workers(h_squares, unknown_squares, "I", num_medics, assumptions, s, observations)
    assign_workers(s_squares, unknown_squares, "Q", num_police, assumptions, s, observations)
    final_assumptions = []
    for li in assumptions:
        final_assumptions += li
    final_assumptions = list(dict.fromkeys(final_assumptions))
    ans = s.solve(assumptions=final_assumptions)
    return ans


def solve_query(query, game, num_police, num_medics):
    q_square, q_turn, q_status = query
    observations = map_tuple_list(deepcopy(game))
    observations[q_turn][q_square[0]][q_square[1]] = q_status
    q_status_pos = check_sat(observations, num_medics, num_police)
    if q_status_pos:
        for s in status_dict.keys():
            if s != q_status:
                observations[q_turn][q_square[0]][q_square[1]] = s
                not_q_status_pos = check_sat(observations, num_medics, num_police)
                if not_q_status_pos:
                    break
        if not_q_status_pos:
            return "?"
        else:
            return "T"
    else:
        return "F"


def solve_problem(input_problem):
    sol = {}
    for query in input_problem['queries']:
        sol[query] = solve_query(query, input_problem['observations'], input_problem['police'], input_problem['medics'])
    return sol

