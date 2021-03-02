from pysat.solvers import Glucose3
import itertools
import utils as ut

ids = ['208656165', '206609810']


def get_map_dim(map):
    return len(map), len(map[0]), len(map[0][0])


def parse_input_params(input):
    return input["police"], input["medics"], input["observations"], input["queries"]


def get_problem_indicators(p_crews, m_crews):
    if p_crews == 0 and m_crews == 0:
        return [0, 1, 2, 7], [0, 1, 2, 3, 7]
    if p_crews and m_crews:
        return [0, 1, 2, 4, 6, 7], [0, 1, 2, 3, 4, 5, 6, 7]
    if p_crews and m_crews == 0:
        return [0, 1, 2, 4, 7], [0, 1, 2, 3, 4, 5, 7]
    if p_crews == 0 and m_crews:
        return [0, 1, 2, 6, 7], [0, 1, 2, 3, 6, 7]


def map_to_atoms_map(rows, cols, turns, first, second):
    coord_atoms = ut.defaultkeydict()
    count = 1
    for i in range(rows):
        for j in range(cols):
            coord = (i, j)
            coord_atoms[coord] = [[count, count + 1, count + 2]]
            count += 3
    for day in range(turns - 1):
        for i in range(rows):
            for j in range(cols):
                list_of_states = []
                if day == 0:
                    day_prob = first
                else:
                    day_prob = second
                for k in range(len(day_prob)):
                    list_of_states.append(count + day_prob[k])
                count += 8
                coord_atoms[(i, j)] = coord_atoms[(i, j)] + [list_of_states]
    return coord_atoms


def get_state(map, t, i, j):
    return map[t][i][j]


def get_atoms_for_sick_state_on_other_turns(map, atoms_map, current_turn, coord_a, coord_b):
    if current_turn == 0:
        return [atoms_map[(coord_a, coord_b)][current_turn][1]]
    if current_turn == 1:
        last_turn = get_state(map, current_turn - 1, coord_a, coord_b)
        if last_turn == 'S':
            return [atoms_map[(coord_a, coord_b)][current_turn][2]]
        if last_turn == 'H':
            return [atoms_map[(coord_a, coord_b)][current_turn][1]]
        else:
            return [atoms_map[(coord_a, coord_b)][current_turn][1], atoms_map[(coord_a, coord_b)][current_turn][2]]

    else:
        # Current turn is 2+
        last_turn = get_state(map, current_turn - 1, coord_a, coord_b)
        if last_turn == 'H':
            return [atoms_map[(coord_a, coord_b)][current_turn][1]]
        if last_turn == 'S':
            two_turns_back = get_state(map, current_turn - 2, coord_a, coord_b)
            if two_turns_back == 'S':
                return [atoms_map[(coord_a, coord_b)][current_turn][3]]
            if two_turns_back == 'H':
                return [atoms_map[(coord_a, coord_b)][current_turn][2]]
        else:
            two_turns_back = get_state(map, current_turn - 2, coord_a, coord_b)
            if two_turns_back == 'H':
                return [atoms_map[(coord_a, coord_b)][current_turn][1], atoms_map[(coord_a, coord_b)][current_turn][2]]
            if two_turns_back == 'S':
                return [atoms_map[(coord_a, coord_b)][current_turn][1], atoms_map[(coord_a, coord_b)][current_turn][3]]
            if two_turns_back == 'Q':
                return [atoms_map[(coord_a, coord_b)][current_turn][1]]
            else:
                return [atoms_map[(coord_a, coord_b)][current_turn][1], atoms_map[(coord_a, coord_b)][current_turn][2],
                        atoms_map[(coord_a, coord_b)][current_turn][3]]


def get_atoms_for_Q_state_on_other_turns(map, atoms_map, current_turn, coord_a, coord_b):
    if current_turn == 1:
        return [atoms_map[(coord_a, coord_b)][current_turn][3]]
    if current_turn >= 2:
        last_turn = get_state(map, current_turn - 1, coord_a, coord_b)
        if last_turn == 'H' or last_turn == 'S':
            return [atoms_map[(coord_a, coord_b)][current_turn][4]]
        if last_turn == 'Q':
            return [atoms_map[(coord_a, coord_b)][current_turn][5]]
        else:
            return [atoms_map[(coord_a, coord_b)][current_turn][4], atoms_map[(coord_a, coord_b)][current_turn][5]]


def find_neibohrs(coord_a, coord_b, rows, cols):
    neibohrs = ut.Stack()
    if (coord_a == 0):
        neibohrs.append((coord_a + 1, coord_b))
    elif (coord_a + 1 == rows):
        neibohrs.append((coord_a - 1, coord_b))
    else:
        neibohrs.append((coord_a + 1, coord_b))
        neibohrs.append((coord_a - 1, coord_b))
    if (coord_b == 0):
        neibohrs.append((coord_a, coord_b + 1))
    elif (coord_b + 1 == cols):
        neibohrs.append((coord_a, coord_b - 1))
    else:
        neibohrs.append((coord_a, coord_b + 1))
        neibohrs.append((coord_a, coord_b - 1))
    return neibohrs


def return_sick_neibohrs(atom_map, neibohrs, p_crews, turn, cand):
    if p_crews == 0:
        sick_neibohrs = ut.Stack()
        for n in neibohrs:
            if turn == 1:
                sick_neibohrs.append(atom_map[n][turn - 1][1])
            elif turn == 2:
                sick_neibohrs.append(atom_map[n][turn - 1][1])
                sick_neibohrs.append(atom_map[n][turn - 1][2])
            else:
                sick_neibohrs.append(atom_map[n][turn - 1][1])
                sick_neibohrs.append(atom_map[n][turn - 1][2])
                sick_neibohrs.append(atom_map[n][turn - 1][3])
    for i in sick_neibohrs:
        cand.append(i)

    return cand


def get_list(arg1, arg2):
    n = ut.Stack()
    n.append([arg1])
    n.append([arg2])
    return n


def get_atom(map, t, i, j, n):
    return map[(i, j)][t][n]


def build_sub(sick, s_neibohrs, size):
    sub = ut.Stack()
    l = ut.Stack()
    for i in sick:
        l.append(i)
    for i in range(size):
        l.append(s_neibohrs[i + 1])
    sub.append(l)
    return sub


def treat_sick_neibohrs(k_base, map, atom_map, rows, cols, p_crews, turns):
    for j in range(cols):
        for i in range(rows):
            for turn in range(turns):
                neibohrs = find_neibohrs(i, j, rows, cols)
                if turn == 0:
                    continue
                if p_crews == 0:
                    sick_neibohrs = return_sick_neibohrs(atom_map, neibohrs, p_crews, turn,
                                                         [(-1) * get_atom(atom_map, turn, i, j, 1)])
                    k_base.append(sick_neibohrs)

                elif p_crews > 0:
                    s_neibohrs = {}
                    sick = [[(-1) * atom_map[(i, j)][turn][1]]]
                    for ne in range(len(neibohrs)):
                        if turn == 1:
                            n = get_list(atom_map[neibohrs[ne]][turn - 1][1], (-1) * atom_map[neibohrs[ne]][turn][3])
                            s_neibohrs[ne + 1] = n
                        if turn == 2:
                            n = get_list(atom_map[neibohrs[ne]][turn - 1][1:3], (-1) * atom_map[neibohrs[ne]][turn][4])
                            s_neibohrs[ne + 1] = n
                        else:
                            n = get_list(atom_map[neibohrs[ne]][turn - 1][1:4], (-1) * atom_map[neibohrs[ne]][turn][4])
                            s_neibohrs[ne + 1] = n
                    sub = build_sub(sick, s_neibohrs, len(neibohrs))
                    for atom in sub:
                        l = [val for sublist in atom for val in sublist]
                        obs = flatten(l)
                        k_base.append(obs)
    return k_base


def list_append(l, map, coord, turn, n):
    l.append(map[coord][turn][n])
    return l


def treat_healthy(k_base, map, atom_map, rows, cols, m_crews, turns):
    for day in range(turns):
        for i in range(rows):
            for j in range(cols):
                neibohrs = find_neibohrs(i, j, rows, cols)
                ll = []
                if m_crews == 0:
                    if day == turns - 1:
                        continue
                    atom = [(-1) * get_atom(atom_map, day, i, j, 0), get_atom(atom_map, day + 1, i, j, 0)]
                elif m_crews > 0:
                    if day == turns - 1:
                        continue
                    atom = [(-1) * get_atom(atom_map, day, i, j, 0), get_atom(atom_map, day + 1, i, j, 0),
                            get_atom(atom_map, day + 1, i, j, -2)]
                if day == 0:
                    for k in neibohrs:
                        ll.append(atom_map[k][day][1])
                elif day >= turns - 1:
                    continue
                elif day == 1 and day != turns - 1:
                    for k in neibohrs:
                        ll.append(atom_map[k][day][1])
                        ll.append(atom_map[k][day][2])
                elif day >= 2 and day != turns - 1:
                    for k in neibohrs:
                        ll.append(atom_map[k][day][1])
                        ll.append(atom_map[k][day][2])
                        ll.append(atom_map[k][day][3])
                for a in ll:
                    atom.append(a)
                k_base.append(atom)
    return k_base


def treating_advanced_sickness(k_base, atom_map, rows, cols, turns, p_crews):
    for day in range(turns):
        for i in range(rows):
            for j in range(cols):
                if day == 0:
                    continue
                elif day == 1:
                    first = [atom_map[(i, j)][day - 1][0], (-1) * atom_map[(i, j)][day][1]]
                    second = [atom_map[(i, j)][day - 1][1], (-1) * atom_map[(i, j)][day][2]]
                    k_base.append(first)
                    k_base.append(second)
                else:
                    first = [atom_map[(i, j)][day - 1][0], (-1) * atom_map[(i, j)][day][1]]
                    second = [atom_map[(i, j)][day - 1][1], (-1) * atom_map[(i, j)][day][2]]
                    third = [atom_map[(i, j)][day - 1][2], (-1) * atom_map[(i, j)][day][3]]
                    k_base.append(first)
                    k_base.append(second)
                    k_base.append(third)

                if p_crews > 0:
                    if day == 0 or day == turns - 1:
                        continue

                    elif day == 1:
                        first = [atom_map[(i, j)][day + 1][5], (-1) * atom_map[(i, j)][day][3]]
                        k_base.append(first)

                    elif day >= 2:
                        first = [atom_map[(i, j)][day + 1][5], (-1) * atom_map[(i, j)][day][4]]
                        second = [atom_map[(i, j)][day + 1][0], (-1) * atom_map[(i, j)][day][5]]
                        k_base.append(first)
                        k_base.append(second)
    return k_base


def treating_advanced_q(k_base, atom_map, rows, cols, turns, p_crews):
    for day in range(turns):
        for i in range(rows):
            for j in range(cols):
                if p_crews > 0:
                    if day < 2:
                        continue
                    elif day == 2:
                        atom = [atom_map[(i, j)][day - 1][3], (-1) * atom_map[(i, j)][day][5]]
                    elif day > 2:
                        atom = [atom_map[(i, j)][day - 1][4], (-1) * atom_map[(i, j)][day][5]]
                    k_base.append(atom)
    return k_base


def police_actions(k_base, atom_map, rows, cols, turns, p_crews):
    for turn in range(turns):
        for i in range(rows):
            for j in range(cols):
                if p_crews > 0:
                    if turn == 0:
                        first = [(-1) * atom_map[(i, j)][turn][1], atom_map[(i, j)][turn + 1][2],
                                 atom_map[(i, j)][turn + 1][3]]
                        k_base.append(first)
                    elif turn == turns - 1:
                        continue
                    elif turn == 1:
                        first = [(-1) * atom_map[(i, j)][turn][1], atom_map[(i, j)][turn + 1][2],
                                 atom_map[(i, j)][turn + 1][4]]
                        second = [(-1) * atom_map[(i, j)][turn][2], atom_map[(i, j)][turn + 1][3],
                                  atom_map[(i, j)][turn + 1][4]]
                        k_base.append(first)
                        k_base.append(second)
                    elif turn >= 2:
                        first = [(-1) * atom_map[(i, j)][turn][1], atom_map[(i, j)][turn + 1][2],
                                 atom_map[(i, j)][turn + 1][4]]
                        second = [(-1) * atom_map[(i, j)][turn][2], atom_map[(i, j)][turn + 1][3],
                                  atom_map[(i, j)][turn + 1][4]]
                        third = [(-1) * atom_map[(i, j)][turn][3], atom_map[(i, j)][turn + 1][0],
                                 atom_map[(i, j)][turn + 1][4]]
                        k_base.append(first)
                        k_base.append(second)
                        k_base.append(third)

                elif p_crews == 0:
                    if turn == 0:
                        first = [atom_map[(i, j)][turn + 1][2], (-1) * atom_map[(i, j)][turn][1]]
                        k_base.append(first)
                    elif turn == turns - 1:
                        continue
                    elif turn == 1:
                        first = [atom_map[(i, j)][turn + 1][2], (-1) * atom_map[(i, j)][turn][1]]
                        second = [atom_map[(i, j)][turn + 1][3], (-1) * atom_map[(i, j)][turn][2]]
                        k_base.append(first)
                        k_base.append(second)
                    elif turn >= 2:
                        first = [atom_map[(i, j)][turn + 1][2], (-1) * atom_map[(i, j)][turn][1]]
                        second = [atom_map[(i, j)][turn + 1][3], (-1) * atom_map[(i, j)][turn][2]]
                        third = [atom_map[(i, j)][turn + 1][0], (-1) * atom_map[(i, j)][turn][3]]
                        k_base.append(first)
                        k_base.append(second)
                        k_base.append(third)
    return k_base


def check_healthy_states_with_p(k_base, atom_map, rows, cols, turns, p_crews):
    for turn in range(turns):
        for i in range(rows):
            for j in range(cols):
                if p_crews == 0:
                    if turn == 0:
                        continue
                    elif turn == 1 or turn == 2:
                        k_base.append([atom_map[(i, j)][turn - 1][0], (-1) * atom_map[(i, j)][turn][0]])
                    else:
                        k_base.append([atom_map[(i, j)][turn - 1][3],
                                       atom_map[(i, j)][turn - 1][0], (-1) * atom_map[(i, j)][turn][0]])
                elif p_crews > 0:
                    if turn == 0:
                        continue
                    elif turn == 1 or turn == 2:
                        k_base.append([atom_map[(i, j)][turn - 1][0], (-1) * atom_map[(i, j)][turn][0]])

                    else:
                        k_base.append([atom_map[(i, j)][turn - 1][3], atom_map[(i, j)][turn - 1][5],
                                       atom_map[(i, j)][turn - 1][0], (-1) * atom_map[(i, j)][turn][0]])
    return k_base


def check_healthy_states_with_p_and_m(k_base, atom_map, rows, cols, turns, p_crews, m_crews):
    for turn in range(turns):
        for j in range(cols):
            for i in range(rows):
                neibohrs = find_neibohrs(i, j, rows, cols)
                list_sick = []
                if p_crews == 0:
                    for k in neibohrs:
                        if turn == 0:
                            list_sick.append((-1) * atom_map[k][turn][1])
                        elif turn == turns - 1:
                            continue
                        elif turn == 1:
                            list_sick.append((-1) * atom_map[k][turn][1])
                            list_sick.append((-1) * atom_map[k][turn][2])
                        elif turn >= 2:
                            list_sick.append((-1) * atom_map[k][turn][1])
                            list_sick.append((-1) * atom_map[k][turn][2])
                            list_sick.append((-1) * atom_map[k][turn][3])
                    if m_crews == 0:
                        for foo in list_sick:
                            x = [(-1) * atom_map[(i, j)][turn][0], atom_map[(i, j)][turn + 1][1]]
                            x.append(foo)
                            k_base.append(x)
                            x = [(-1) * atom_map[(i, j)][turn][0], atom_map[(i, j)][turn + 1][1]]
                    elif m_crews > 0:
                        for foo in list_sick:
                            x = [(-1) * atom_map[(i, j)][turn][0], atom_map[(i, j)][turn + 1][1],
                                 atom_map[(i, j)][turn + 1][-2]]
                            x.append(foo)
                            k_base.append(x)
                            x = [(-1) * atom_map[(i, j)][turn][0], atom_map[(i, j)][turn + 1][1],
                                 atom_map[(i, j)][turn + 1][-2]]
                elif p_crews > 0:
                    for k in neibohrs:
                        if turn == 0:
                            list_sick.append([(-1) * atom_map[k][turn][1], atom_map[k][turn + 1][3]])
                        elif turn == turns - 1:
                            continue
                        elif turn == 1:
                            list_sick.append([(-1) * atom_map[k][turn][1], atom_map[k][turn + 1][4]])
                            list_sick.append([(-1) * atom_map[k][turn][2], atom_map[k][turn + 1][4]])
                        elif turn >= 2:
                            list_sick.append([(-1) * atom_map[k][turn][1], atom_map[k][turn + 1][4]])
                            list_sick.append([(-1) * atom_map[k][turn][2], atom_map[k][turn + 1][4]])
                            list_sick.append([(-1) * atom_map[k][turn][3], atom_map[k][turn + 1][4]])
                    if m_crews == 0:
                        for foo in list_sick:
                            x = [(-1) * atom_map[(i, j)][turn][0], atom_map[(i, j)][turn + 1][1]]
                            x.append(foo[0])
                            x.append(foo[1])
                            k_base.append(x)
                    elif m_crews > 0:
                        for foo in list_sick:
                            x = [(-1) * atom_map[(i, j)][turn][0], atom_map[(i, j)][turn + 1][1],
                                 atom_map[(i, j)][turn + 1][-2]]
                            x.append(foo[0])
                            x.append(foo[1])
                            k_base.append(x)
    return k_base


def check_healthy_state_with_m(k_base, atom_map, rows, cols, turns, m_crews):
    for turn in range(turns):
        for i in range(rows):
            for j in range(cols):
                if m_crews > 0:
                    if turn < turns - 1:
                        k_base.append([(-1) * atom_map[(i, j)][turn][0], atom_map[(i, j)][turn + 1][0],
                                       atom_map[(i, j)][turn + 1][1], atom_map[(i, j)][turn + 1][-2]])
                    elif turn == turns - 1:
                        continue
                elif m_crews == 0:
                    if turn < turns - 1:
                        k_base.append([(-1) * atom_map[(i, j)][turn][0], atom_map[(i, j)][turn + 1][0],
                                       atom_map[(i, j)][turn + 1][1]])
                    elif turn == turns - 1:
                        continue
    return k_base


def check_p_capacity(k_base, atom_map, rows, cols, turns, p_crews):
    for turn in range(turns):
        if p_crews > 0:
            if turn == 0:
                continue
            else:
                qlist = []

                for i in range(rows):
                    for j in range(cols):
                        if turn == 1:
                            qlist.append((-1) * atom_map[(i, j)][turn][3])
                        else:
                            qlist.append((-1) * atom_map[(i, j)][turn][4])
                for x in itertools.combinations(qlist, p_crews + 1):
                    k_base.append(list(x))
    return k_base


def check_m_capacity(k_base, atom_map, rows, cols, turns, m_crews):
    for day in range(1, turns):
        if m_crews > 0 and m_crews * day <= rows * cols:
            Ilist = []
            for i in range(rows):
                for j in range(cols):
                    if m_crews > 0:
                        if day == 0:
                            continue
                        elif day == 1:
                            Ilist.append((-1) * atom_map[(i, j)][day][4])
                        else:
                            try:
                                Ilist.append((-1) * atom_map[(i, j)][day][6])
                            except IndexError:
                                pass
                    else:
                        if day == 1:
                            Ilist.append((-1) * atom_map[(i, j)][day][3])
                        else:
                            Ilist.append((-1) * atom_map[(i, j)][day][4])
            for x in itertools.combinations(Ilist, m_crews * day + 1):
                k_base.append(list(x))

    return k_base


def create_knowledge_base(map, rows, cols, turns, atoms_map, p_crews, m_crews):
    k_base = ut.Stack()
    # Iterating over the map status per turn.
    for day in range(turns):
        for i in range(rows):
            for j in range(cols):
                # on the current turn - the state of the coord is S
                current_state = get_state(map, day, i, j)
                if current_state == 'S':
                    k_base.append(get_atoms_for_sick_state_on_other_turns(map, atoms_map, day, i, j))
                if current_state == 'H':
                    k_base.append([atoms_map[(i, j)][day][0]])
                if current_state == 'U':
                    for k in range(turns):
                        k_base.append([atoms_map[(i, j)][k][-1]])
                if current_state == 'Q':
                    k_base.append(get_atoms_for_Q_state_on_other_turns(map, atoms_map, day, i, j))
                if current_state == 'I':
                    for k in range(day, turns):
                        k_base.append([atoms_map[(i, j)][k][-2]])
                if current_state == '?':
                    daylist = []
                    for foo in range(len(atoms_map[(i, j)][day])):
                        daylist.append(atoms_map[(i, j)][day][foo])
                    k_base.append(daylist)
    mul_map(atoms_map, turns)
    for i in atoms_map:
        for j in range(turns):
            for x in itertools.combinations(atoms_map[i][j], 2):
                k_base.append(list(x))
    mul_map(atoms_map, turns)
    k_base = treat_sick_neibohrs(k_base, map, atoms_map, rows, cols, p_crews, turns)
    k_base = treat_healthy(k_base, map, atoms_map, rows, cols, m_crews, turns)
    k_base = treating_advanced_sickness(k_base, atoms_map, rows, cols, turns, p_crews)
    k_base = treating_advanced_q(k_base, atoms_map, rows, cols, turns, p_crews)
    k_base = police_actions(k_base, atoms_map, rows, cols, turns, p_crews)
    k_base = check_healthy_states_with_p(k_base, atoms_map, rows, cols, turns, p_crews)
    k_base = check_healthy_states_with_p_and_m(k_base, atoms_map, rows, cols, turns, p_crews, m_crews)
    k_base = check_healthy_state_with_m(k_base, atoms_map, rows, cols, turns, m_crews)
    k_base = check_p_capacity(k_base, atoms_map, rows, cols, turns, p_crews)
    k_base = check_m_capacity(k_base, atoms_map, rows, cols, turns, m_crews)
    return k_base


def run_solve(k_base):
    with Glucose3(bootstrap_with=k_base) as m:
        return m.solve()


def solve(k_base, query_list, atoms_map, p_crews):
    res = {}
    for query in query_list:
        if query[2] == 'H':
            k_base.append([atoms_map[query[0]][query[1]][0]])
            sol = run_solve(k_base)
            k_base.pop(-1)
            if sol:
                k_base.append([(-1) * atoms_map[query[0]][query[1]][0]])
                sol = run_solve(k_base)
                k_base.pop(-1)
                if sol:
                    res[query] = '?'
                else:
                    res[query] = 'T'
            else:
                res[query] = 'F'
        elif query[2] == 'S':
            if query[1] == 0:
                k_base.append([atoms_map[query[0]][query[1]][1]])
                sol = run_solve(k_base)
                k_base.pop(-1)
                if sol:
                    k_base.append([(-1) * atoms_map[query[0]][query[1]][1]])
                    sol = run_solve(k_base)
                    k_base.pop(-1)
                    if sol == True:
                        res[query] = '?'
                    else:
                        res[query] = 'T'
                else:
                    res[query] = 'F'
            elif query[1] == 1:
                k_base.append([atoms_map[query[0]][query[1]][1], atoms_map[query[0]][query[1]][2]])
                sol = run_solve(k_base)

                k_base.pop(-1)
                if sol:
                    k_base.append([(-1) * atoms_map[query[0]][query[1]][1]])
                    k_base.append([(-1) * atoms_map[query[0]][query[1]][2]])
                    sol = run_solve(k_base)

                    k_base.pop(-1)
                    k_base.pop(-1)
                    if sol:
                        res[query] = '?'
                    else:
                        res[query] = 'T'
                else:
                    res[query] = 'F'
            else:
                k_base.append([atoms_map[query[0]][query[1]][1], atoms_map[query[0]][query[1]][2],
                               atoms_map[query[0]][query[1]][3]])
                sol = run_solve(k_base)

                k_base.pop(-1)
                if sol:
                    k_base.append([(-1) * atoms_map[query[0]][query[1]][1]])
                    k_base.append([(-1) * atoms_map[query[0]][query[1]][2]])
                    k_base.append([(-1) * atoms_map[query[0]][query[1]][3]])
                    sol = run_solve(k_base)

                    k_base.pop(-1)
                    k_base.pop(-1)
                    k_base.pop(-1)
                    if sol:
                        res[query] = '?'
                    else:
                        res[query] = 'T'
                else:
                    res[query] = 'F'
        elif query[2] == 'Q':
            if query[1] == 0:
                res[query] = 'F'
            elif query[1] == 1:
                k_base.append([atoms_map[query[0]][query[1]][3]])
                sol = run_solve(k_base)

                k_base.pop(-1)
                if sol:
                    k_base.append([(-1) * atoms_map[query[0]][query[1]][3]])
                    sol = run_solve(k_base)

                    k_base.pop(-1)
                    if sol:
                        res[query] = '?'
                    else:
                        res[query] = 'T'
                else:
                    res[query] = 'F'
            else:
                k_base.append([atoms_map[query[0]][query[1]][4], atoms_map[query[0]][query[1]][5]])
                sol = run_solve(k_base)

                k_base.pop(-1)
                if sol:
                    k_base.append([(-1) * atoms_map[query[0]][query[1]][4]])
                    k_base.append([(-1) * atoms_map[query[0]][query[1]][5]])
                    sol = run_solve(k_base)

                    k_base.pop(-1)
                    k_base.pop(-1)
                    if sol:
                        res[query] = '?'
                    else:
                        res[query] = 'T'
                else:
                    res[query] = 'F'
        elif query[2] == 'I':

            if p_crews > 0:
                a, b = 4, 6
            else:
                a, b = 3, 4
            if query[1] == 0:
                res[query] = 'F'
            elif query[1] == 1:
                k_base.append([atoms_map[query[0]][query[1]][a]])
                sol = run_solve(k_base)

                k_base.pop(-1)
                if sol:
                    k_base.append([(-1) * atoms_map[query[0]][query[1]][a]])
                    sol = run_solve(k_base)

                    k_base.pop(-1)
                    if sol:
                        res[query] = '?'
                    else:
                        res[query] = 'T'
                else:
                    res[query] = 'F'
            else:
                k_base.append([atoms_map[query[0]][query[1]][b]])
                sol = run_solve(k_base)

                k_base.pop(-1)
                if sol:
                    k_base.append([(-1) * atoms_map[query[0]][query[1]][a]])
                    sol = run_solve(k_base)

                    k_base.pop(-1)
                    if sol:
                        res[query] = '?'
                    else:
                        res[query] = 'T'
                else:
                    res[query] = 'F'
        else:
            k_base.append([atoms_map[query[0]][query[1]][-1]])
            sol = run_solve(k_base)

            k_base.pop(-1)
            if sol:
                k_base.append([(-1) * atoms_map[query[0]][query[1]][-1]])
                sol = run_solve(k_base)

                k_base.pop(-1)
                if sol:
                    res[query] = '?'
                else:
                    res[query] = 'T'
            else:
                res[query] = 'F'
    return res


def mul_map(map, turns):
    for i in map:
        for j in range(turns):
            vec = map[i][j]
            vec[:] = ut.scalar_vector_product(-1, vec)


def flatten(list_of_lists):
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flatten(list_of_lists[0]) + flatten(list_of_lists[1:])
    return list_of_lists[:1] + flatten(list_of_lists[1:])


def solve_problem(input):
    p_crews, m_crews, maps_list, query_list = parse_input_params(input)
    turns, rows, colls = get_map_dim(maps_list)
    first, second = get_problem_indicators(p_crews, m_crews)
    atoms_map = map_to_atoms_map(rows, colls, turns, first, second)
    k_base = create_knowledge_base(maps_list, rows, colls, turns, atoms_map, p_crews, m_crews)
    res = solve(k_base, query_list, atoms_map, p_crews)
    return res
