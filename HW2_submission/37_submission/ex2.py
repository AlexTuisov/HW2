from sympy import satisfiable
from itertools import combinations
from sympy import Symbol, to_cnf
import numpy as np

ids = ['208776559', '308558741']

# aux variables
H, S1, S2, S3, Q1, Q2, I, U = 0, 1, 2, 3, 4, 5, 6, 7
states_list = [H, S1, S2, S3, Q1, Q2, I, U]
states_dict = {
    H: 'H',
    S1: 'S1',
    S2: 'S2',
    S3: 'S3',
    Q1: 'Q1',
    Q2: 'Q2',
    I: 'I',
    U: 'U'
}
some_states_dict = {'H': H, 'I': I, 'U': U}
STATES = len(states_list)


def simp(f):
    return to_cnf(f, simplify=True)


def is_sat(formula, gt):
    return satisfiable(formula.subs(gt)) != False


def get_shapes(x):
    return x.shape[0], x.shape[1], x.shape[2]


def append(formulas):
    if len(formulas) == 1:
        return formulas[0]
    formula = formulas[0]
    for form in formulas[1:]:
        formula = formula & form
    return formula


def get_metadata(input):
    observations, observations_num = input['observations'], len(input['observations'])
    rows, cols = len(input['observations'][0]), len(input['observations'][0][0])
    police, medics, queries = input['police'], input['medics'], input['queries']
    return rows, cols, observations_num, police, medics, observations, queries


def init_variables(rows, cols, observations_num, observations, police, medics):
    x, police_vars, medic_vars = [], [], []
    for r in range(rows):
        for c in range(cols):
            for o in range(observations_num):
                for s in states_list:
                    x.append(Symbol(f'x_{r}_{c}_{o}_{states_dict[s]}'))
                if police > 0 and o < observations_num - 1:
                    if observations[o][r][c] == 'S' or observations[o][r][c] == '?':
                        police_vars.append(Symbol(f'POLICE_{r}_{c}_{o}'))
                    else:
                        police_vars.append(None)
                if medics > 0 and o < observations_num - 1:
                    if observations[o][r][c] == 'H' or observations[o][r][c] == '?':
                        medic_vars.append(Symbol(f'MEDICS_{r}_{c}_{o}'))
                    else:
                        medic_vars.append(None)
    x = np.array(x).reshape(rows, cols, observations_num, STATES)
    police_vars = np.array(police_vars).reshape(rows, cols, observations_num-1) if police > 0 else None
    medic_vars = np.array(medic_vars).reshape(rows, cols, observations_num-1) if medics > 0 else None
    return x, police_vars, medic_vars


def _exactly_one(variables):
    formula = variables[0]
    for v in variables[1:]:
        formula = formula | v
    pairs = list(combinations(variables, 2))
    pairs_forms = [(~a | ~b) for a, b in pairs]
    formula = append([formula] + pairs_forms)
    return formula


def _exactly_k(variables, k):
    if k == 1:
        return _exactly_one(variables)
    k_combinations = list(combinations(variables, k))
    formula = append(k_combinations[0])
    for comb in k_combinations[1:]:
        formula = formula | append(comb)
    k1_combinations = list(combinations(variables, k+1))
    pairs_forms = [simp(~append(comb)) for comb in k1_combinations]
    formula = append([formula] + pairs_forms)
    return formula


def create_team_formula(x, formula, team_vars, team_count):
    rows, cols, obs = get_shapes(x)
    formulas = []
    for o in range(obs-1):
        current_variables = []
        for i in range(rows):
            for j in range(cols):
                if team_vars[i][j][o]:
                    current_variables.append(team_vars[i][j][o])
        formulas.append(_exactly_k(current_variables, team_count))

    return append([formula] + formulas)


def one_true_rest_false(x, truths, r, c, o, true_state):
    for state in states_list:
        if state == true_state:
            truths[x[r][c][o][state]] = True
        else:
            truths[x[r][c][o][state]] = False


def all_false(x, truths, r, c, o, false_states):
    for state in false_states:
        truths[x[r][c][o][state]] = False


def exactly_one_init(x, observations):
    rows, cols, obs = get_shapes(x)
    all_formulas = []
    truths = {}
    for o in range(obs):
        for r in range(rows):
            for c in range(cols):
                if observations[o][r][c] == 'H':
                    one_true_rest_false(x, truths, r, c, o, H)
                elif observations[o][r][c] == 'I':
                    one_true_rest_false(x, truths, r, c, o, I)
                elif observations[o][r][c] == 'U':
                    one_true_rest_false(x, truths, r, c, o, U)
                elif observations[o][r][c] == 'S':
                    if o == 0:
                        one_true_rest_false(x, truths, r, c, o, S1)
                    else:
                        all_possible_states_in_cell = [x[r][c][o][s] for s in [S1, S2, S3]]
                        all_formulas.append(_exactly_k(all_possible_states_in_cell, 1))
                        all_false(x, truths, r, c, o, [H, U, I, Q1, Q2])
                elif observations[o][r][c] == 'Q':
                    all_possible_states_in_cell = [x[r][c][o][s] for s in [Q1, Q2]]
                    all_formulas.append(_exactly_k(all_possible_states_in_cell, 1))
                    all_false(x, truths, r, c, o, [H, U, I, S1, S2, S3])
                else:
                    assert observations[o][r][c] == '?'
                    if o == 0:
                        all_possible_states_in_cell = [x[r][c][o][s] for s in [H, S1, U]]
                        all_formulas.append(_exactly_k(all_possible_states_in_cell, 1))
                        all_false(x, truths, r, c, o, [I, S2, S3, Q1, Q2])
                    else:
                        all_possible_states_in_cell = [x[r][c][o][s] for s in states_list]
                        all_formulas.append(_exactly_k(all_possible_states_in_cell, 1))
    return append(all_formulas), truths


def get_neighbors(x, i, j):
    rows, cols, obs = get_shapes(x)
    neighbors = []
    if i > 0:
        neighbors.append((i-1,j))
    if j > 0:
        neighbors.append((i,j-1))
    if i < rows-1:
        neighbors.append((i+1,j))
    if j < cols-1:
        neighbors.append((i,j+1))
    return neighbors


def sick_neighbors(x, formula, observations):
    rows, cols, obs = get_shapes(x)
    all_formulas = []
    for r in range(rows):
        for c in range(cols):
            neighbors = get_neighbors(x, r, c)
            for o in range(obs):
                # This one check if current cell is S and neighbor is H ===> S
                if (o < obs - 1) and (observations[o][r][c] == 'S' or observations[o][r][c] == '?'):
                    for i, j in neighbors:
                        form = simp(((x[r][c][o][S1] | x[r][c][o][S2] | x[r][c][o][S3]) & x[i][j][o][H]) >> x[i][j][o+1][S1])
                        all_formulas.append(form)
                # If current cell is H and no neighbor is S then next round it's H
                if (o < obs - 1) and (observations[o][r][c] == 'H' or observations[o][r][c] == '?'):
                    base_cnf_form = ~x[r][c][o][H] | x[r][c][o+1][H]
                    for i, j in neighbors:
                        base_cnf_form = base_cnf_form | x[i][j][o][S1] | x[i][j][o][S2] | x[i][j][o][S3]
                    all_formulas.append(base_cnf_form)
                # If current cell is H ==> previous round was H or S3 or Q2
                if (o > 0) and (observations[o][r][c] == 'H' or observations[o][r][c] == '?'):
                    all_formulas.append(~x[r][c][o][H] | (x[r][c][o-1][H] | x[r][c][o-1][Q2] | x[r][c][o-1][S3]))
    return append([formula] + all_formulas)


def sick_neighbors_plus(x, formula, observations, police_vars, police_count, medics_vars, medics_count):
    rows, cols, obs = get_shapes(x)
    all_formulas = []
    for r in range(rows):
        for c in range(cols):
            neighbors = get_neighbors(x, r, c)
            for o in range(obs):
                # This one check if current cell is S and neighbor is H ===> S
                if (o < obs - 1) and (observations[o][r][c] == 'S' or observations[o][r][c] == '?'):
                    if police_count == 0:
                        assert medics_count > 0
                        for i, j in neighbors:
                            if observations[o][i][j] == 'H' or observations[o - 1][r][c] == '?':
                                form = simp(((x[r][c][o][S1] | x[r][c][o][S2] | x[r][c][o][S3]) & (x[i][j][o][H] & ~medics_vars[i][j][o])) >> x[i][j][o+1][S1])
                                all_formulas.append(form)
                    elif medics_count == 0:
                        assert police_count > 0
                        for i, j in neighbors:
                            if observations[o][i][j] == 'H' or observations[o - 1][r][c] == '?':
                                form = simp(((x[r][c][o][S1] | x[r][c][o][S2] | x[r][c][o][S3]) & (x[i][j][o][H] & ~police_vars[r][c][o])) >> x[i][j][o + 1][S1])
                                all_formulas.append(form)
                    else:
                        for i, j in neighbors:
                            if observations[o][i][j] == 'H' or observations[o - 1][r][c] == '?':
                                form = simp(
                                    ((x[r][c][o][S1] | x[r][c][o][S2] | x[r][c][o][S3]) &
                                     (x[i][j][o][H] & ~police_vars[r][c][o]) & ~medics_vars[i][j][o]) >> x[i][j][o + 1][S1])
                                all_formulas.append(form)
                # If current cell is H and no neighbor is S then next round it's H
                if (o < obs - 1) and (observations[o][r][c] == 'H' or observations[o][r][c] == '?'):
                    if medics_count > 0:
                        base_cnf_form = ~x[r][c][o][H] | x[r][c][o + 1][H] | medics_vars[r][c][o]
                        for i, j in neighbors:
                            base_cnf_form = base_cnf_form | x[i][j][o][S1] | x[i][j][o][S2] | x[i][j][o][S3]
                        all_formulas.append(base_cnf_form)

                    else:
                        base_cnf_form = ~x[r][c][o][H] | x[r][c][o + 1][H]
                        for i, j in neighbors:
                            base_cnf_form = base_cnf_form | x[i][j][o][S1] | x[i][j][o][S2] | x[i][j][o][S3]
                        all_formulas.append(base_cnf_form)
                # If current cell is H ==> previous round was H or S3 or Q2
                if (o > 0) and (observations[o][r][c] == 'H' or observations[o][r][c] == '?'):
                    if police_count == 0:
                        assert medics_count > 0
                        if observations[o-1][r][c] == 'H' or observations[o-1][r][c] == '?':
                            all_formulas.append(simp(x[r][c][o][H] >> ((x[r][c][o-1][H] & ~medics_vars[r][c][o-1]) | x[r][c][o-1][Q2] | x[r][c][o-1][S3])))
                        else:
                            all_formulas.append(x[r][c][o][H] >> (x[r][c][o - 1][Q2] | x[r][c][o - 1][S3]))
                    elif medics_count == 0:
                        assert police_count > 0
                        if observations[o-1][r][c] == 'S' or observations[o-1][r][c] == '?':
                            all_formulas.append(simp(x[r][c][o][H] >> x[r][c][o-1][H] | x[r][c][o-1][Q2] | (x[r][c][o-1][S3] & ~police_vars[r][c][o-1])))
                        else:
                            all_formulas.append(simp(x[r][c][o][H] >> (x[r][c][o - 1][Q2] | x[r][c][o - 1][H])))
                    else:
                        if observations[o - 1][r][c] == 'S':
                            all_formulas.append(x[r][c][o-1][S3] & ~police_vars[r][c][o-1])
                        elif observations[o - 1][r][c] == 'H':
                            all_formulas.append(x[r][c][o - 1][H] & ~medics_vars[r][c][o - 1])
                        elif observations[o - 1][r][c] == '?':
                            all_formulas.append(simp(x[r][c][o][H] >> ((x[r][c][o - 1][H] & ~medics_vars[r][c][o-1]) | x[r][c][o - 1][Q2] | (x[r][c][o - 1][S3] & ~police_vars[r][c][o-1]))))

    return append([formula] + all_formulas)


def add_IU(x, org_formula, observations):
    rows, cols, obs = get_shapes(x)
    formulas = []
    for i in range(rows):
        for j in range(cols):
            for o in range(obs-1):
                if o > 0 and (observations[o][i][j] == 'I' or observations[o][i][j] == '?'):
                    formulas.append(simp(x[i][j][o][I] >> x[i][j][o + 1][I]))
                formulas.append(simp(x[i][j][o][U] >> x[i][j][o + 1][U]))
                formulas.append(simp(x[i][j][o][U] << x[i][j][o + 1][U]))
    return append([org_formula] + formulas)


def add_IU_plus(x, org_formula, observations, medic_vars):
    rows, cols, obs = get_shapes(x)
    formulas = []
    for i in range(rows):
        for j in range(cols):
            for o in range(obs-1):
                if o > 0 and (observations[o][i][j] == 'I' or observations[o][i][j] == '?'):
                    formulas.append(simp(x[i][j][o][I] >> x[i][j][o + 1][I]))
                formulas.append(simp(x[i][j][o][U] >> x[i][j][o + 1][U]))
                formulas.append(simp(x[i][j][o][U] << x[i][j][o + 1][U]))
                if observations[o][i][j] == 'H' or observations[o][i][j] == '?':
                    formulas.append(simp((x[i][j][o][H] & medic_vars[i][j][o]) >> x[i][j][o + 1][I]))
                if observations[o+1][i][j] == 'I' or observations[o+1][i][j] == '?':
                    if observations[o][i][j] == '?' or observations[o][i][j] == 'H':
                        formulas.append(simp(x[i][j][o + 1][I] >> ((x[i][j][o][H] & medic_vars[i][j][o]) | x[i][j][o][I])))

    return append([org_formula] + formulas)

def add_SQ(x, org_formula, observations):
    rows, cols, obs = get_shapes(x)
    formulas = []
    for i in range(rows):
        for j in range(cols):
            for o in range(obs-1):
                if observations[o][i][j] == 'S' or observations[o][i][j] == '?':
                    formulas.append(simp(x[i][j][o][S1] >> x[i][j][o + 1][S2]))
                    formulas.append(simp(x[i][j][o][S1] << x[i][j][o + 1][S2]))
                    formulas.append(simp(x[i][j][o][S2] >> x[i][j][o + 1][S3]))
                    formulas.append(simp(x[i][j][o][S2] << x[i][j][o + 1][S3]))
                    formulas.append(simp(x[i][j][o][S3] >> x[i][j][o + 1][H]))
                if o > 0 and (observations[o][i][j] == 'Q' or observations[o][i][j] == '?'):
                    formulas.append(simp(x[i][j][o][Q1] >> x[i][j][o + 1][Q2]))
                    formulas.append(simp(x[i][j][o][Q1] << x[i][j][o + 1][Q2]))
                    formulas.append(simp(x[i][j][o][Q2] >> x[i][j][o + 1][H]))
    return append([org_formula] + formulas)


def add_SQ_plus(x, org_formula, observations, police_vars, police_count ,gt):
    rows, cols, obs = get_shapes(x)
    formulas = []
    for i in range(rows):
        for j in range(cols):
            for o in range(obs-1):
                if observations[o][i][j] == 'S' or observations[o][i][j] == '?':
                    if police_count == 0:
                        formulas.append(simp(x[i][j][o][S1] >> x[i][j][o + 1][S2]))
                        formulas.append(simp(x[i][j][o][S1] << x[i][j][o + 1][S2]))
                        formulas.append(simp(x[i][j][o][S2] >> x[i][j][o + 1][S3]))
                        formulas.append(simp(x[i][j][o][S2] << x[i][j][o + 1][S3]))
                        formulas.append(simp(x[i][j][o][S3] >> x[i][j][o + 1][H]))
                    else:
                        formulas.append(simp((x[i][j][o][S1] & ~police_vars[i][j][o]) >> x[i][j][o + 1][S2]))
                        formulas.append(simp((x[i][j][o][S1] & ~police_vars[i][j][o]) << x[i][j][o + 1][S2]))
                        formulas.append(simp((x[i][j][o][S2] & ~police_vars[i][j][o]) >> x[i][j][o + 1][S3]))
                        formulas.append(simp((x[i][j][o][S2] & ~police_vars[i][j][o]) << x[i][j][o + 1][S3]))
                        formulas.append(simp((x[i][j][o][S3] & ~police_vars[i][j][o]) >> x[i][j][o + 1][H]))

                        formulas.append(simp((x[i][j][o][S1] & police_vars[i][j][o]) >> x[i][j][o + 1][Q1]))
                        formulas.append(simp((x[i][j][o][S2] & police_vars[i][j][o]) >> x[i][j][o + 1][Q1]))
                        formulas.append(simp((x[i][j][o][S3] & police_vars[i][j][o]) >> x[i][j][o + 1][Q1]))
                        formulas.append(simp(((x[i][j][o][S1] | x[i][j][o][S2] | x[i][j][o][S3])& police_vars[i][j][o]) << x[i][j][o + 1][Q1]))

                if o > 0 and (observations[o][i][j] == 'Q' or observations[o][i][j] == '?'):
                    formulas.append(simp(x[i][j][o][Q1] >> x[i][j][o + 1][Q2]))
                    formulas.append(simp(x[i][j][o][Q1] << x[i][j][o + 1][Q2]))
                    formulas.append(simp(x[i][j][o][Q2] >> x[i][j][o + 1][H]))
    return append([org_formula] + formulas)


def evaluate_query(q, x, formula, ground_truth):
    (i, j), stage, state_char = q

    # If it's H,I,U then there's one possible state variable
    if state_char in some_states_dict:
        state = some_states_dict[state_char]
        if x[i][j][stage][state] in ground_truth:
            if ground_truth[x[i][j][stage][state]] == True:
                return 'T'
            else:
                return 'F'
        else:
            modified_gt = ground_truth.copy()
            modified_gt[x[i][j][stage][state]] = True
            is_true_sat = is_sat(formula,modified_gt)
            modified_gt[x[i][j][stage][state]] = False
            is_false_sat = is_sat(formula, modified_gt)
            if is_true_sat and not is_false_sat:
                return 'T'
            if not is_true_sat and is_false_sat:
                return 'F'
            print(is_true_sat, is_false_sat)
            return '?'
    else:
        if state_char == 'S':
            if x[i][j][stage][S1] in ground_truth and ground_truth[x[i][j][stage][S1]] == True or \
                    x[i][j][stage][S2] in ground_truth and ground_truth[x[i][j][stage][S2]] == True or \
                    x[i][j][stage][S3] in ground_truth and ground_truth[x[i][j][stage][S3]] == True:
                return 'T'
            else:
                modified_gt = ground_truth.copy()
                modified_gt[x[i][j][stage][S1]] = True
                is_s1_sat = is_sat(formula, modified_gt)
                modified_gt[x[i][j][stage][S1]] = False
                modified_gt[x[i][j][stage][S2]] = True
                is_s2_sat = is_sat(formula, modified_gt)
                modified_gt[x[i][j][stage][S2]] = False
                modified_gt[x[i][j][stage][S3]] = True
                is_s3_sat = is_sat(formula, modified_gt)
                modified_gt[x[i][j][stage][S3]] = False
                is_none_sat = is_sat(formula, modified_gt)
                is_s_sat = is_s1_sat or is_s2_sat or is_s3_sat
                if is_s_sat and not is_none_sat:
                    return 'T'
                if not is_s_sat and is_none_sat:
                    return 'F'
                return '?'
        else:
            assert state_char == 'Q'
            if x[i][j][stage][Q1] in ground_truth and ground_truth[x[i][j][stage][Q1]] == True or \
                    x[i][j][stage][Q2] in ground_truth and ground_truth[x[i][j][stage][Q2]] == True:
                return 'T'
            else:
                modified_gt = ground_truth.copy()
                modified_gt[x[i][j][stage][Q1]] = True
                is_q1_sat = is_sat(formula, modified_gt)
                modified_gt[x[i][j][stage][Q1]] = False
                modified_gt[x[i][j][stage][Q2]] = True
                is_q2_sat = is_sat(formula, modified_gt)
                modified_gt[x[i][j][stage][Q2]] = False
                is_none_sat = is_sat(formula, modified_gt)
                is_q_sat = is_q1_sat or is_q2_sat
                if is_q_sat and not is_none_sat:
                    return 'T'
                if not is_q_sat and is_none_sat:
                    return 'F'
                return '?'


def solve_problem(input):
    rows, cols, observations_num, police, medics, observations, queries = get_metadata(input)
    x, police_vars, medic_vars = init_variables(rows, cols, observations_num, observations, police, medics)
    formula, ground_truth = exactly_one_init(x, observations)

    if medics > 0:
        formula = create_team_formula(x, formula, medic_vars, medics)
        formula = add_IU_plus(x, formula, observations, medic_vars)
    else:
        formula = add_IU(x, formula, observations)

    if police > 0:
        formula = create_team_formula(x, formula, police_vars, police)
        formula = add_SQ_plus(x, formula, observations, police_vars, police, ground_truth)
    else:
        formula = add_SQ(x, formula, observations)

    if police == 0 and medics == 0:
        formula = sick_neighbors(x, formula, observations)
    else:
        formula = sick_neighbors_plus(x, formula, observations, police_vars, police, medic_vars, medics)

    q_dict = {}
    for q in queries:
        q_dict[q] = evaluate_query(q, x, formula, ground_truth)
    return q_dict
