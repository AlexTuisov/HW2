from threading import Timer
from pysat.card import *
from pysat.formula import IDPool
from pysat.solvers import Solver
from pysat.formula import CNFPlus
from itertools import combinations

ids = ["207630658", "312236219"]

TIMEOUT = 295  # seconds


def solve_problem(input_):
    initial = input_
    vpool = IDPool()
    var = lambda t, pos, turn: vpool.id(f'{t}_({pos[0]},{pos[1]})_{turn}')
    cnf = _build_clauses(initial=initial, var=var, vpool=vpool)
    solution = sat_solver(cnf=cnf, queries=initial['queries'], vpool=vpool, var=var)
    return solution


def _build_clauses(initial, var, vpool):
    num_medics = initial['medics']
    num_police = initial['police']
    observations = initial['observations']
    num_turns = len(observations)
    map = initial['observations'][0]
    num_rows = len(map)
    num_cols = len(map[0])
    clauses = []
    cell_types = ['S', 'H', 'U']
    cell_types = cell_types + ['I'] if num_medics > 0 else cell_types
    cell_types = cell_types + ['Q'] if num_police > 0 else cell_types

    cnf = CNFPlus()

    observations = update_observations(observations, num_turns)

    for turn, obs in enumerate(observations):
        for i, row in enumerate(obs):
            for j, cell_type in enumerate(row):

                # always_relevant_clauses
                clauses.extend(_always_relevant_clauses(vpool, var, cell_types, cell_type, i, j, turn, num_turns, num_rows, num_cols))

                # ###################### End of always true clauses #######################

                # Make sure no I and Q on turn 0
                if turn == 0:
                    if num_medics > 0:
                        clauses.append([-var(t='I', pos=(i, j), turn=0)])
                    if num_police > 0:
                        clauses.append([-var(t='Q', pos=(i, j), turn=0)])

                # Handle S timer, clauses related to police
                if turn + 1 < num_turns:
                    s_timer_clauses = []
                    if num_police == 0:
                        # If S2 at turn x --> S1 at turn x+1
                        s_timer_clauses.append([-var(t='S2', pos=(i, j), turn=turn), var('S1', pos=(i, j), turn=turn + 1)])
                        # If S1 at turn x --> S0 at turn x+1
                        s_timer_clauses.append([-var(t='S1', pos=(i, j), turn=turn), var('S0', pos=(i, j), turn=turn + 1)])
                        # If S0 at turn x --> H at turn x+1
                        s_timer_clauses.append([-var(t='S0', pos=(i, j), turn=turn), var('H', pos=(i, j), turn=turn + 1)])

                    else:
                        # If S2 at turn x --> S1 or Q1 at turn x+1
                        s_timer_clauses.append([-var(t='S2', pos=(i, j), turn=turn),
                                                var('S1', pos=(i, j), turn=turn + 1), var('Q1', pos=(i, j), turn=turn + 1)])
                        # If S1 at turn x --> S0 or Q1 at turn x+1
                        s_timer_clauses.append([-var(t='S1', pos=(i, j), turn=turn),
                                                var('S0', pos=(i, j), turn=turn + 1), var('Q1', pos=(i, j), turn=turn + 1)])
                        # If S0 at turn x --> H or Q1 at turn x+1
                        s_timer_clauses.append([-var(t='S0', pos=(i, j), turn=turn),
                                                var('H', pos=(i, j), turn=turn + 1), var('Q1', pos=(i, j), turn=turn + 1)])
                    clauses.extend(s_timer_clauses)

                # Handle Q timer
                if num_police > 0:
                    if turn == 1:
                        # Q >> Q1
                        q_timer_clauses = [[-var('Q', pos=(i, j), turn=turn),
                                            var('Q1', pos=(i, j), turn=turn)]]
                    elif turn > 1:
                        # Q >> (Q0 | Q1)
                        q_timer_clauses = [[-var('Q', pos=(i, j), turn=turn),
                                            var('Q0', pos=(i, j), turn=turn),
                                            var('Q1', pos=(i, j), turn=turn)]]
                    if turn >= 1:
                        # (Q0 >> Q) & (Q1 >> Q)
                        for k in range(2):
                            q_timer_clauses.append([-var(t=f'Q{k}', pos=(i, j), turn=turn),
                                                    var(t='Q', pos=(i, j), turn=turn)])

                        # not both Q0 and Q1
                        q_timer_clauses.append([-var(t=f'Q0', pos=(i, j), turn=turn),
                                                -var(t=f'Q1', pos=(i, j), turn=turn)])

                        if turn + 1 < num_turns:
                            # If Q1 at turn x --> Q0 at turn x+1
                            q_timer_clauses.append([-var(t='Q1', pos=(i, j), turn=turn), var('Q0', pos=(i, j), turn=turn + 1)])
                            # If Q0 at turn x --> H at turn x+1
                            q_timer_clauses.append([-var(t='Q0', pos=(i, j), turn=turn), var('H', pos=(i, j), turn=turn + 1)])
                            # If Q0 at turn x+1 --> Q1 at turn x
                            q_timer_clauses.append([-var(t='Q0', pos=(i, j), turn=turn + 1), var('Q1', pos=(i, j), turn=turn)])
                            # If Q1 at turn x+1 --> S at turn x
                            clauses.append([-var('Q1', pos=(i, j), turn=turn + 1), var('S', pos=(i, j), turn=turn)])

                        clauses.extend(q_timer_clauses)

                if turn + 1 < num_turns:

                    # If I at turn x --> I at turn x+1
                    if num_medics > 0:
                        clauses.append([-var('I', pos=(i, j), turn=turn), var('I', pos=(i, j), turn=turn + 1)])

                    # if H at turn x --> I or S or H at turn x+1
                    if num_medics > 0:
                        clauses.append([-var('H', pos=(i, j), turn=turn), var('I', pos=(i, j), turn=turn + 1),
                                        var('S', pos=(i, j), turn=turn + 1), var('H', pos=(i, j), turn=turn + 1)])
                    else:
                        clauses.append([-var('H', pos=(i, j), turn=turn), var('S', pos=(i, j), turn=turn + 1),
                                        var('H', pos=(i, j), turn=turn + 1)])

                    add_H_clause = True
                    if add_H_clause:
                        """ H_clause
                        if H and all neighbours not S (after bound checking) at turn x --> H or I (if num medcis >0) at turn x+1
                        to_cnf((a & (b &c&d&e)) >> (f|g), simplify=True)
                        f∨g∨¬a∨¬b∨¬c∨¬d∨¬e
                        """
                        H_clause = [-var('H', pos=(i, j), turn=turn), var('H', pos=(i, j), turn=turn + 1)]
                        if num_medics > 0:
                            H_clause.append(var('I', pos=(i, j), turn=turn + 1))

                        if i + 1 < num_rows:
                            H_clause.append(var('S', pos=(i + 1, j), turn=turn))

                        if i - 1 >= 0:
                            H_clause.append(var('S', pos=(i - 1, j), turn=turn))

                        if j + 1 < num_cols:
                            H_clause.append(var('S', pos=(i, j + 1), turn=turn))

                        if j - 1 >= 0:
                            H_clause.append(var('S', pos=(i, j - 1), turn=turn))
                        clauses.append(H_clause)

                    add_S_clauses = True
                    if add_S_clauses:
                        """ S_clauses
                        if num police = 0 and num medic =0:
                        If H and atleast one neighbour is S at turn x --> S2 at turn x+1
                        
                        if num police > 0 and num medic =0:
                            If H and atleast one neighbour is S at turn x --> S2 or H at turn x+1
                        
                        if num police = 0 and num medic >0:
                            If H and atleast one neighbour is S at turn x --> S2 or I at turn x+1
                        
                        if num police > 0 and num medic >0:
                            If H and atleast one neighbour is S at turn x --> S2 or H or I at turn x+1
                         
                         to_cnf(((a & (b |c|d))) >> (f|g), simplify=True)
                            (f∨g∨¬a∨¬b)∧(f∨g∨¬a∨¬c)∧(f∨g∨¬a∨¬d)
                        """
                        S_clauses = []
                        if i + 1 < num_rows:
                            prop1 = [-var('S', pos=(i + 1, j), turn=turn), -var('H', pos=(i, j), turn=turn),
                                     var('S2', pos=(i, j), turn=turn + 1)]
                            if num_medics > 0:
                                prop1.append(var('I', pos=(i, j), turn=turn + 1))
                            if num_police > 0:
                                prop1.append(var('H', pos=(i, j), turn=turn + 1))
                            S_clauses.append(prop1)

                        if i - 1 >= 0:
                            prop2 = [-var('S', pos=(i - 1, j), turn=turn),
                                     -var('H', pos=(i, j), turn=turn),
                                     var('S2', pos=(i, j), turn=turn + 1)]
                            if num_medics > 0:
                                prop2.append(var('I', pos=(i, j), turn=turn + 1))
                            if num_police > 0:
                                prop2.append(var('H', pos=(i, j), turn=turn + 1))
                            S_clauses.append(prop2)

                        if j + 1 < num_cols:
                            prop3 = [-var('S', pos=(i, j + 1), turn=turn),
                                     -var('H', pos=(i, j), turn=turn),
                                     var('S2', pos=(i, j), turn=turn + 1)]
                            if num_medics > 0:
                                prop3.append(var('I', pos=(i, j), turn=turn + 1))
                            if num_police > 0:
                                prop3.append(var('H', pos=(i, j), turn=turn + 1))
                            S_clauses.append(prop3)

                        if j - 1 >= 0:
                            prop4 = [-var('S', pos=(i, j - 1), turn=turn),
                                     -var('H', pos=(i, j), turn=turn),
                                     var('S2', pos=(i, j), turn=turn + 1)]
                            if num_medics > 0:
                                prop4.append(var('I', pos=(i, j), turn=turn + 1))
                            if num_police > 0:
                                prop4.append(var('H', pos=(i, j), turn=turn + 1))
                            S_clauses.append(prop4)

                        clauses.extend(S_clauses)

                    add_h_then_h_clause = True
                    if add_h_then_h_clause:
                        # If H at turn x and H at turn x+1 --> each neighbour in turn x was:
                        #                                                   1. not S
                        #                                                   or
                        #                                                   2. was S at turn x
                        #                                                       but Q at turn x+1
                        h_then_h_clause = [-var('H', pos=(i, j), turn=turn),
                                           -var('H', pos=(i, j), turn=turn + 1)]

                        if i + 1 < num_rows:
                            h_then_h_clause_d = h_then_h_clause.copy()
                            h_then_h_clause_d.append(-var('S', pos=(i + 1, j), turn=turn))
                            if num_police > 0:
                                h_then_h_clause_d.append(var('Q', pos=(i + 1, j), turn=turn + 1))
                            clauses.append(h_then_h_clause_d)

                        if i - 1 >= 0:
                            h_then_h_clause_u = h_then_h_clause.copy()
                            h_then_h_clause_u.append(-var('S', pos=(i - 1, j), turn=turn))
                            if num_police > 0:
                                h_then_h_clause_u.append(var('Q', pos=(i - 1, j), turn=turn + 1))
                            clauses.append(h_then_h_clause_u)

                        if j + 1 < num_cols:
                            h_then_h_clause_r = h_then_h_clause.copy()
                            h_then_h_clause_r.append(-var('S', pos=(i, j + 1), turn=turn))
                            if num_police > 0:
                                h_then_h_clause_r.append(var('Q', pos=(i, j + 1), turn=turn + 1))
                            clauses.append(h_then_h_clause_r)

                        if j - 1 >= 0:
                            h_then_h_clause_l = h_then_h_clause.copy()
                            h_then_h_clause_l.append(-var('S', pos=(i, j - 1), turn=turn))
                            if num_police > 0:
                                h_then_h_clause_l.append(var('Q', pos=(i, j - 1), turn=turn + 1))
                            clauses.append(h_then_h_clause_l)

        if turn > 0:  # because there are no Q or I at turn 0

            if num_medics >= 1 or num_police >= 1:
                # parse map for ? (of different types) and Q cells
                unk_was_unk = []
                unk_was_not_s_nor_unk = []
                unk_was_s = []
                unk_was_s_or_unk = []
                it_is_q = []
                it_is_i = []
                unk_was_h = []
                new_i = []
                was_h = []
                was_s = []
                unk_was_not_h_nor_unk = []
                for i, row in enumerate(obs):
                    for j, cell_type in enumerate(row):
                        cell_in_prev_turn = observations[turn - 1][i][j]
                        if cell_type == '?':
                            if cell_in_prev_turn == 'S':
                                unk_was_s.append((cell_type, (i, j)))
                            elif cell_in_prev_turn == '?':
                                unk_was_unk.append((cell_type, (i, j)))
                            else:
                                unk_was_not_s_nor_unk.append((cell_type, (i, j)))

                            if cell_in_prev_turn == 'H':
                                unk_was_h.append((cell_type, (i, j)))
                            elif cell_in_prev_turn != '?':
                                unk_was_not_h_nor_unk.append((cell_type, (i, j)))

                        elif cell_type == 'Q':
                            it_is_q.append((cell_type, (i, j)))
                        elif cell_type == 'I':
                            it_is_i.append((cell_type, (i, j)))
                            if cell_in_prev_turn == 'H':
                                new_i.append((cell_type, (i, j)))
                        if cell_in_prev_turn == 'H':
                            was_h.append((cell_type, (i, j)))
                        elif cell_in_prev_turn == 'S':
                            was_s.append((cell_type, (i, j)))

                unk_was_s_or_unk.extend(unk_was_s)
                unk_was_s_or_unk.extend(unk_was_unk)

                if num_police >= 1:
                    # if Q and was S before, or if Q and is Q next turn
                    num_certain_q1 = 0
                    for i, row in enumerate(obs):
                        for j, cell_type in enumerate(row):
                            cell_in_prev_turn = observations[turn - 1][i][j]
                            if cell_type == 'Q' and \
                                    (cell_in_prev_turn == 'S' or
                                     (turn + 1 < num_turns and observations[turn + 1][i][j] == 'Q')):
                                num_certain_q1 += 1
                    num_possible_q = num_police - num_certain_q1

                    # Q1 at turn x --> S or ? at turn x-1
                    # Can be Q1 only if was S or ? the turn before
                    #  Translated to if it was not S and not ? then it is not Q1
                    for cell_type, cell_pos in unk_was_not_s_nor_unk:
                        clauses.append([-var('Q1', pos=cell_pos, turn=turn)])

                    # at most num_police cells are Q1 at this turn, among all cells that are Q or ?(that where S or ?)
                    possible_q1 = it_is_q.copy()
                    possible_q1.extend(unk_was_s_or_unk)
                    atmost_q1_among_possible_q = CardEnc.atmost(lits=[var('Q1', pos=(i, j), turn=turn) for _, (i, j) in possible_q1],
                                                                vpool=vpool,
                                                                bound=num_police).clauses
                    cnf.extend(atmost_q1_among_possible_q)

                    # If we didn't see the Q1 then any one of ? can be Q1 aka atmost num_possible_q is Q1.
                    atmost_q1_among_unk = CardEnc.atmost(lits=[var('Q1', pos=(i, j), turn=turn) for _, (i, j) in unk_was_s_or_unk],
                                                         vpool=vpool, bound=num_possible_q).clauses

                    cnf.extend(atmost_q1_among_unk)

                    # at turn x: atleast K cells are Q1 among all map - Q or (? that were (S or ?))t
                    # K = min(num_police, #S prev turn)
                    # possible_q1_among_unk = ? that was S or ?
                    num_atleast_possible_q = min(num_police, len(was_s))
                    atleast_q1 = CardEnc.atleast(lits=[var('Q1', pos=(i, j), turn=turn) for _, (i, j) in possible_q1],
                                                 vpool=vpool, bound=num_atleast_possible_q).clauses

                    cnf.extend(atleast_q1)

                    # at turn x: atleast K cells become Q1 among possible_q1_among_unk
                    # K = min(max(num_police - #new_Q1 - #is?was?, 0), #?_was_S)
                    # possible_i_among_unk = ? that was H or ?
                    possible_q1_among_unk = unk_was_s_or_unk
                    num_atleast_q1_among_unk = min(max(num_police-num_certain_q1-len(unk_was_unk), 0), len(unk_was_s))
                    atleast_q1_among_unk_clause = CardEnc.atleast(lits=[var('I', pos=(i, j), turn=turn) for _, (i, j) in possible_q1_among_unk],
                                                       vpool=vpool,
                                                       bound=num_atleast_q1_among_unk).clauses

                    cnf.extend(atleast_q1_among_unk_clause)

                if num_medics >= 1:
                    # at most turn*num_medics among possible_i_among_unk can be I
                    # possible_i_among_unk is ? that was H or ?
                    num_known_i = len(it_is_i)
                    num_new_i = len(new_i)

                    possible_i_among_unk = unk_was_unk.copy()
                    possible_i_among_unk.extend(unk_was_h)
                    num_atmost_i_among_unk = min(num_medics * turn - num_known_i, num_medics - num_new_i)

                    atmost_i_among_possible_i = CardEnc.atmost(lits=[var('I', pos=(i, j), turn=turn) for _, (i, j) in possible_i_among_unk],
                                                               vpool=vpool,
                                                               bound=num_atmost_i_among_unk).clauses

                    cnf.extend(atmost_i_among_possible_i)

                    # all other ? cannot be I
                    for cell_type, cell_pos in unk_was_not_h_nor_unk:
                        clauses.append([-var('I', pos=cell_pos, turn=turn)])

                    # at turn x: atleast K cells are I among all map (possible_i_among_unk and I)
                    # K = min(num_medics * x, #H prev turn)
                    # possible_i_among_unk = ? that was H or ?
                    num_atleast_i = min(num_medics * turn, len(was_h))
                    possible_i = possible_i_among_unk.copy()
                    possible_i.extend(it_is_i)
                    atleast_i_clause = CardEnc.atleast(lits=[var('I', pos=(i, j), turn=turn) for _, (i, j) in possible_i],
                                                       vpool=vpool,
                                                       bound=num_atleast_i).clauses

                    cnf.extend(atleast_i_clause)

                    # at turn x: atleast K cells become I among possible_i_among_unk
                    # K = min(max(num_medics - #new_I - #is?was?, 0), #?_was_h)
                    # possible_i_among_unk = ? that was H or ?
                    num_atleast_i_among_unk = min(max(num_medics-len(new_i)-len(unk_was_unk), 0), len(unk_was_h))
                    atleast_i_among_unk_clause = CardEnc.atleast(lits=[var('I', pos=(i, j), turn=turn) for _, (i, j) in possible_i_among_unk],
                                                       vpool=vpool,
                                                       bound=num_atleast_i_among_unk).clauses

                    cnf.extend(atleast_i_among_unk_clause)

    cnf.extend(clauses)
    return cnf


def interrupt(solver):
    solver.interrupt()


def sat_solver(cnf, queries, vpool, var):
    with Solver('Minicard') as s:
        timer = Timer(TIMEOUT, interrupt, [s])
        timer.start()
        s.append_formula(cnf.clauses)


        result_dict = {}
        for query in queries:

            parsed_query = var(pos=query[0], turn=int(query[1]), t=query[2])  # parse query

            is_query_true = s.solve_limited(assumptions=[parsed_query], expect_interrupt=True)  # query
            s.clear_interrupt()

            is_query_false = s.solve_limited(assumptions=[-parsed_query], expect_interrupt=True)  # query
            s.clear_interrupt()

            if not is_query_true:
                query_res = 'F'
            elif not is_query_false:
                query_res = 'T'
            else:
                query_res = '?'

            result_dict[query] = query_res
        timer.cancel()
    return result_dict


def update_observations(map, num_turns):
    # List of tuples of tuples to list of list of list
    updated_map = []
    for obs in map:
        obs_updated = []
        for row in obs:
            row_updated = []
            for cell_type in row:
                row_updated.append(cell_type)
            obs_updated.append(row_updated)
        updated_map.append(obs_updated)

    for turn, obs in enumerate(map):
        for i, row in enumerate(obs):
            for j, cell_type in enumerate(row):
                if cell_type == "I":
                    for inner_turn in range(turn + 1, num_turns):
                        updated_map[inner_turn][i][j] = cell_type

                if cell_type == "U":
                    for inner_turn in range(turn + 1, num_turns):
                        updated_map[inner_turn][i][j] = cell_type
                    for inner_turn in range(turn, -1, -1):
                        updated_map[inner_turn][i][j] = cell_type

                if cell_type == 'Q' and turn + 1 < num_turns and turn > 0:
                    if map[turn - 1][i][j] not in '?Q':
                        updated_map[turn + 1][i][j] = 'Q'
                    if map[turn + 1][i][j] not in '?Q':
                        updated_map[turn - 1][i][j] = 'Q'
    return updated_map


def _get_neighbour_was_S_clause(var, i, j, turn, num_rows, num_cols):
    """ neighbour_was_S_clause
        if cell is H at turn x and cell is S2 at turn x+1 then one of neighbours is S at turn x

        to_cnf((a&b)>>(c|d|e|f))
        c∨d∨e∨f∨¬a∨¬b
    """
    neighbour_was_S_clause = [-var('H', pos=(i, j), turn=turn), -var('S2', pos=(i, j), turn=turn + 1)]

    if i + 1 < num_rows:
        neighbour_was_S_clause.append(var('S', pos=(i + 1, j), turn=turn))

    if i - 1 >= 0:
        neighbour_was_S_clause.append(var('S', pos=(i - 1, j), turn=turn))

    if j + 1 < num_cols:
        neighbour_was_S_clause.append(var('S', pos=(i, j + 1), turn=turn))

    if j - 1 >= 0:
        neighbour_was_S_clause.append(var('S', pos=(i, j - 1), turn=turn))

    return neighbour_was_S_clause


def _get_s_timer_clauses(var, i, j, turn, num_turns):
    # Handle S timer
    s_timer_clauses = []
    if turn == 0:
        # S >> (S2)
        s_timer_clauses.append([-var('S', pos=(i, j), turn=turn),
                                var('S2', pos=(i, j), turn=turn)])
    else:
        # S >> (S0 | S1 | S2)
        s_timer_clauses.append([-var('S', pos=(i, j), turn=turn),
                                var('S0', pos=(i, j), turn=turn),
                                var('S1', pos=(i, j), turn=turn),
                                var('S2', pos=(i, j), turn=turn)])

    for k in range(3):
        # (S0 >> S) & (S1 >> S) & (S2 >> S)
        s_timer_clauses.append([-var(t=f'S{k}', pos=(i, j), turn=turn),
                                var(t='S', pos=(i, j), turn=turn)])

    # not both Si and Sj
    for (m, n) in combinations([0, 1, 2], r=2):
        s_timer_clauses.append([-var(t=f'S{m}', pos=(i, j), turn=turn),
                                -var(t=f'S{n}', pos=(i, j), turn=turn)])
    if turn + 1 < num_turns:
        # If S1 at turn x+1 --> S2 at turn x
        s_timer_clauses.append([-var(t='S1', pos=(i, j), turn=turn + 1), var('S2', pos=(i, j), turn=turn)])
        # If S0 at turn x+1 --> S1 at turn x
        s_timer_clauses.append([-var(t='S0', pos=(i, j), turn=turn + 1), var('S1', pos=(i, j), turn=turn)])

    return s_timer_clauses


def _always_relevant_clauses(vpool, var, cell_types, cell_type, i, j, turn, num_turns, num_rows, num_cols):
    always_relevant_clauses = []
    # Observation into clauses
    if cell_type != '?':
        always_relevant_clauses.append([var(t=cell_type, pos=(i, j), turn=turn)])

    # make sure each cell_type is one of 'S', 'H', 'U' (and 'I' and 'Q' if relevant)
    # and that each cell_type is not both a and b.
    unique_type_clauses = CardEnc.equals(lits=[var(x, pos=(i, j), turn=turn) for x in cell_types], vpool=vpool).clauses

    always_relevant_clauses.extend(unique_type_clauses)
    always_relevant_clauses.extend(_get_s_timer_clauses(var=var, i=i, j=j, turn=turn, num_turns=num_turns))

    if turn + 1 < num_turns:
        # If U at turn x --> U at turn x+1 and if U at turn x+1 --> U at turn x
        always_relevant_clauses.append([var('U', pos=(i, j), turn=turn), -var('U', pos=(i, j), turn=turn + 1)])
        always_relevant_clauses.append([-var('U', pos=(i, j), turn=turn), var('U', pos=(i, j), turn=turn + 1)])

        # If S at turn x+1 and was H at turn x --> S2 at turn x+1
        always_relevant_clauses.append([-var('S', pos=(i, j), turn=turn + 1),
                                        -var('H', pos=(i, j), turn=turn),
                                        var('S2', pos=(i, j), turn=turn + 1)])

        # if  H at turn x and  S2 at turn x+1 -- one of neighbours is S at turn x
        always_relevant_clauses.append(_get_neighbour_was_S_clause(var=var, i=i, j=j, turn=turn, num_rows=num_rows, num_cols=num_cols))

    return always_relevant_clauses

