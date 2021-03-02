from pysat.formula import CNF
from pysat.solvers import Solver
from itertools import chain, combinations, product

ids = ['059238717']

def solve_problem(problem):
    p_atoms, last = enumerate_states(problem, 1)
    a_atoms, last = enumerate_agent_actions(last, problem)
    spa_atoms, last = enumerate_spread_actions(problem, last)
    agea_atoms, last = enumerate_states(problem, last)
    noopa_atoms, last = enumerate_states(problem, last)
    observation_clauses = gen_observation_clauses(p_atoms, problem['observations'])
    action_preconditions_clauses = gen_precondition_clauses(p_atoms, a_atoms, spa_atoms, noopa_atoms, agea_atoms)
    fact_acheivement_clauses = gen_fact_acheivement_clauses(p_atoms, a_atoms, spa_atoms, noopa_atoms, agea_atoms)
    action_interefernce_clauses = gen_action_interefernce_clauses(a_atoms, spa_atoms, noopa_atoms, agea_atoms)
    must_spread_clauses = gen_must_spread_clauses(p_atoms, a_atoms, spa_atoms)
    must_age_clauses = gen_must_age_clauses(p_atoms, a_atoms, agea_atoms)
    S_representation_clauses = gen_S_representation_clauses(p_atoms)
    must_use_teams_clauses = gen_must_use_teams_clauses(p_atoms, a_atoms, problem['medics'], problem['police'])
    limited_teams_clauses = gen_limited_teams_clauses(p_atoms, a_atoms, problem['medics'], problem['police'])
    all_clauses = observation_clauses + action_preconditions_clauses + fact_acheivement_clauses + action_interefernce_clauses + must_spread_clauses + must_age_clauses + S_representation_clauses + must_use_teams_clauses + limited_teams_clauses
    answer = {}
    non_starter_list = ['I', 'Q']
    for query in problem['queries']:
        row = query[0][0]
        col = query[0][1]
        step = query[1]
        status = query[2]
        if step == 0 and status in non_starter_list:
            answer[query] = 'F'  # a query about a state that can't be in step 0 returns 'F' instantly
        else:
            if status == 'S':
                query_clause = [p_atoms['S3'][step][row][col], p_atoms['S2'][step][row][col], p_atoms['S1'][step][row][col]]
            elif status == 'Q':
                if step == 0: # can't have Q in initial conditions
                    query_clause = [False]
                else:
                    query_clause = [p_atoms['Q2'][step][row][col], p_atoms['Q1'][step][row][col]]
            elif status == 'I':
                if step == 0: # can't have I in initial conditions
                    query_clause = [False]
                else:
                    query_clause = [p_atoms['I'][step][row][col]]
            else:
                query_clause = [p_atoms[status][step][row][col]]
            cnf_formula1 = CNF()
            sat_solver = Solver()
            cnf_formula1.clauses = all_clauses + [query_clause]
            #cnf_formula.clauses = all_clauses + [[21, 29, 37]]
            sat_solver.append_formula(cnf_formula1)
            res1 = sat_solver.solve()
            #res2 = sat_solver.get_model()
            sat_solver.delete()
            res1_other = False
            if res1 == True:
                # try to solve again- with any otehr possible status instead of status
                # If there is a solution- then it means there could be another status
                # It this case the result can;t be conclusive
                sat_solver = Solver()
                negative_query_clauses = []
                for q in query_clause:
                    negative_query_clauses.append([-q])
                cnf_formula2 = CNF()
                cnf_formula2.clauses = all_clauses + negative_query_clauses

                sat_solver.append_formula(cnf_formula2)
                res1_other = sat_solver.solve()
                model = sat_solver.get_model()
                sat_solver.delete()


            if res1 and not res1_other: # The query status is possible and no other status is possible
                answer[query] = 'T'
            elif res1 and res1_other: # The query status is possible but also at least one more status can be
                answer[query] = '?'
            else:
                answer[query] = 'F' # The query status is not possible
            sat_solver.delete()

    return answer

def gen_limited_teams_clauses(p_atoms, a_atoms, medics, police):
    # number of 'V' actions in one step can not exceed medics
    # number of 'Q' actions in one step can not exceed police
    rows = len(p_atoms['H'][0][0])
    columns = len(p_atoms['H'][0])
    steps = len(p_atoms['H'])
    limited_teams_clauses = []
    for step_indx in range(0, steps - 1):
        x1 = a_atoms['V'][step_indx]
        all_actions = set(chain(*x1))
        limited_actions = set(combinations(all_actions, medics))  # all combination of actions with length medics
        for a in limited_actions:
            non_actions = all_actions - set(chain(a))
            p=[] # need to negate elements in a
            for x in list(a):
                p.append(-x)
            for na in list(non_actions):
                x = p + [-na]
                limited_teams_clauses.append(x)
        x1 = a_atoms['Q'][step_indx]
        all_actions = set(chain(*x1))
        limited_actions = set(combinations(all_actions, police))  # all combination of actions with length police
        for a in limited_actions:
            non_actions = all_actions - set(chain(a))
            p = []  # need to negate elements in a
            for x in list(a):
                p.append(-x)
            for na in list(non_actions):
                x = p + [-na]
                limited_teams_clauses.append(x)
    return limited_teams_clauses


def gen_must_use_teams_clauses(p_atoms, a_atoms, medics, police):
    # Any combination of tiles which has k H tiles implies that all combinations of V operations having more than N-k+1 non vaccination tiles are forbiden
    # K ranges from 1 to medics. N is the total number of tiles (rwos*columns)
    # [H(1) and H(2) and ... H(k)] => -[V(1) and V(2) and ... V(N-k)] for any k p_atoms combination H(1..k) amd any N-k a_atoms('V') H(1..N-k)
    # For example- for k=1 and N=4 (2x2):
    # H(1,1) => -[-V(1,1) and -V(1,2) and -V(2,1) and -V(2,2)] therefore
    # [-H(1,1),V(1,1),V(1,2),V(2,1),V(2,2)]
    # [-H(1,2), V(1,1), V(1,2), V(2,1), V(2,2)]
    # [-H(2,1),V(1,1),V(1,2),V(2,1),V(2,2)]
    # [-H(2,2), V(1,1), V(1,2), V(2,1), V(2,2)]
    # For example- for k=2 and N=4 (2x2):
    # H(1,1) and H(1,2) => -[-V(1,1) and -V(1,2) and -V(2,1)] therefore [-H(1,1),-H(1,2), V(1,1), V(1,2), V(2,1)]
    # H(1,1) and H(1,2) => -[-V(1,1) and -V(1,2) and -V(2,2)] therefore [-H(1,1),-H(1,2), V(1,1), V(1,2), V(2,2)]
    # H(1,1) and H(1,2) => -[-V(1,1) and -V(2,2) and -V(2,1)] therefore [-H(1,1),-H(1,2), V(1,1), V(2,2), V(2,1)]
    # H(1,1) and H(1,2) => -[-V(1,2) and -V(2,2) and -V(2,1)] therefore [-H(1,1),-H(1,2), V(1,2), V(2,2), V(2,1)]
    # and this repeats for all other pairs [H(1,1) H(2,1)] [H(1,1) H(2,2)] and [H(1,2) H(2,2)]
    rows = len(p_atoms['H'][0][0])
    columns = len(p_atoms['H'][0])
    N = rows * columns
    steps = len(p_atoms['H'])
    must_use_teams_clauses = []
    for step_indx in range(0, steps - 1):
        h = list(product(range(0, rows), range(0, columns))) # all combination of indices
        if medics > 0:
            for k in range(1,medics+1):
                all_combinations_k = list(combinations(h, k))  # all combinations with k tiles which are H
                no_medics_combinations = list(combinations(h, N-k+1))  # all combinations of V with N-k+1 vax
                for c in all_combinations_k:
                    for a in no_medics_combinations:
                        temp_clause = []
                        for c1 in c:
                            temp_clause.append(-p_atoms['H'][step_indx][c1[0]][c1[1]])
                        for a1 in a:
                            temp_clause.append(a_atoms['V'][step_indx][a1[0]][a1[1]])
                        must_use_teams_clauses.append(temp_clause)
        if police > 0:
            for k in range(1,police+1):
                all_combinations_k = list(combinations(h, k))  # all combinations with k tiles which are H
                no_police_combinations = list(combinations(h, N-k+1))  # all combinations of V with N-k+1 vax
                for c in all_combinations_k:
                    for a in no_police_combinations:
                        temp_clause = []
                        for c1 in c:
                            temp_clause.append(-p_atoms['S'][step_indx][c1[0]][c1[1]])
                        for a1 in a:
                            temp_clause.append(a_atoms['Q'][step_indx][a1[0]][a1[1]])
                        must_use_teams_clauses.append(temp_clause)
    return must_use_teams_clauses

def gen_must_age_clauses(p_atoms, a_atoms, agea_atoms):
    # if a tile is in 'Q2', 'Q1' it must age
    # if a tile is in 'S3', 'S2', 'S1' and there is no vacc operation on it then it must age
    # p[Q2][i][j] => agea_atoms[Q2][i][j] meaning ~p[Q2][i][j] or agea_atoms[Q2][i][j]
    # let a1, a2, a3,.. be all action atoms that vaccinate (i,j) then
    # p[S3][i][j] and ~(a1 or a2 or a3 or ..) => agea_atoms[S3][i][j] meaning that
    # ~(p[S3][i][j] and ~(a1 or a2 or a3 or ..)) or agea_atoms[S3][i][j]
    # ~p[S3][i][j] or (a1 or a2 or a3 or ..) or agea_atoms[S3][i][j]
    rows = len(agea_atoms['H'][0][0])
    columns = len(agea_atoms['H'][0])
    steps = len(agea_atoms['H'])
    clauses = []
    for step_indx in range(0, steps-1):
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                p = p_atoms['Q2'][step_indx][row_indx][col_indx]
                a = agea_atoms['Q2'][step_indx][row_indx][col_indx]
                clauses.append([-p, a])
                p = p_atoms['Q1'][step_indx][row_indx][col_indx]
                a = agea_atoms['Q1'][step_indx][row_indx][col_indx]
                clauses.append([-p, a])
                vax = a_atoms['Q'][step_indx][row_indx][col_indx]
                p = p_atoms['S3'][step_indx][row_indx][col_indx]
                a = agea_atoms['S3'][step_indx][row_indx][col_indx]
                conjunction = [-p, a, vax]
                clauses.append(conjunction)
                p = p_atoms['S2'][step_indx][row_indx][col_indx]
                a = agea_atoms['S2'][step_indx][row_indx][col_indx]
                conjunction = [-p, a, vax]
                clauses.append(conjunction)
                p = p_atoms['S1'][step_indx][row_indx][col_indx]
                a = agea_atoms['S1'][step_indx][row_indx][col_indx]
                conjunction = [-p, a, vax]
                clauses.append(conjunction)
    return clauses



def gen_must_spread_clauses(p_atoms, a_atoms, spa_atoms):
    # If spreader tile is (S1 or S2 or S3) and infected tile is H and there is no quar on spreader tile or vax on infected tile then spread from sp to inf must happen
    # (p[S3][i][j] or p[S2][i][j] or p[S1][i][j]) and p[H][i-1][j] and ~vaccine(i-1,j) and ~quarantine(i,j) => spa_atoms['U'][i][j]
    # not ((p[S3][i][j] or p[S2][i][j] or p[S1][i][j]) and p[H][i-1][j] and ~vaccine(i-1,j) and ~quarantine(i,j)) or spa_atoms['U'][i][j]
    # ~(p[S3][i][j] or p[S2][i][j] or p[S1][i][j]) or ~p[H][i-1][j] or vaccine(i-1,j) or quarantine(i,j) or spa_atoms['U'][i][j]
    # (~p[S3][i][j] and ~p[S2][i][j] and ~p[S1][i][j]) or ~p[H][i-1][j] or vaccine(i-1,j) or quarantine(i,j) or spa_atoms['U'][i][j]
    # Converting to CNF gives 3 clauses:
    # ~p[S3][i][j] or ~p[H][i-1][j]or vaccine(i-1,j) or quarantine(i,j) or spa_atoms['U'][i][j]
    # ~p[S2][i][j] or ~p[H][i-1][j] or vaccine(i-1,j) or quarantine(i,j) or spa_atoms['U'][i][j]
    # ~p[S1][i][j] or ~p[H][i-1][j] or vaccine(i-1,j) or quarantine(i,j) or spa_atoms['U'][i][j]
    rows = len(p_atoms['H'][0][0])
    columns = len(p_atoms['H'][0])
    steps = len(p_atoms['H'])
    clauses = []
    for step_indx in range(0, steps-1):
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                quar = a_atoms['Q'][step_indx][row_indx][col_indx]
                vax = a_atoms['V'][step_indx][row_indx][col_indx]
                # quar_list contains all quarantine actions atoms that impact tile i,j
                if row_indx != 0: # spread up can not happen for row 1
                    p_infected = p_atoms['H'][step_indx][row_indx - 1][col_indx]
                    a_spa = spa_atoms['U'][step_indx][row_indx][col_indx]
                    p_spreader = p_atoms['S'][step_indx][row_indx][col_indx]
                    quar_infected = a_atoms['Q'][step_indx][row_indx - 1][col_indx]
                    vax_infected = a_atoms['V'][step_indx][row_indx - 1][col_indx]
                    conjunction = [-p_spreader, -p_infected, quar, quar_infected, vax, vax_infected, a_spa]
                    clauses.append(conjunction)
                if row_indx != (rows - 1): # spread down
                    p_infected = p_atoms['H'][step_indx][row_indx + 1][col_indx]
                    a_spa = spa_atoms['D'][step_indx][row_indx][col_indx]
                    p_spreader = p_atoms['S'][step_indx][row_indx][col_indx]
                    quar_infected = a_atoms['Q'][step_indx][row_indx + 1][col_indx]
                    vax_infected = a_atoms['V'][step_indx][row_indx + 1][col_indx]
                    conjunction = [-p_spreader, -p_infected, quar, quar_infected, vax, vax_infected, a_spa]
                    clauses.append(conjunction)
                if col_indx != 0: # spread left
                    p_infected = p_atoms['H'][step_indx][row_indx][col_indx - 1]
                    a_spa = spa_atoms['L'][step_indx][row_indx][col_indx]
                    p_spreader = p_atoms['S'][step_indx][row_indx][col_indx]
                    quar_infected = a_atoms['Q'][step_indx][row_indx][col_indx - 1]
                    vax_infected = a_atoms['V'][step_indx][row_indx][col_indx - 1]
                    conjunction = [-p_spreader, -p_infected, quar, quar_infected, vax, vax_infected, a_spa]
                    clauses.append(conjunction)
                if col_indx != (columns - 1): # spread right
                    p_infected = p_atoms['H'][step_indx][row_indx][col_indx + 1]
                    a_spa = spa_atoms['R'][step_indx][row_indx][col_indx]
                    p_spreader = p_atoms['S'][step_indx][row_indx][col_indx]
                    quar_infected = a_atoms['Q'][step_indx][row_indx][col_indx + 1]
                    vax_infected = a_atoms['V'][step_indx][row_indx][col_indx + 1]
                    conjunction = [-p_spreader, -p_infected, quar, quar_infected, vax, vax_infected, a_spa]
                    clauses.append(conjunction)
    return clauses

def gen_action_interefernce_clauses(a_atoms, spa_atoms, noopa_atoms, agea_atoms):
    rows = len(noopa_atoms['H'][0][0])
    columns = len(noopa_atoms['H'][0])
    steps = len(noopa_atoms['H'])
    clauses = []
    # all agent actions interfere with each other (can only apply one of them at a tile at a step)
    for step_indx in range(0, steps-1):
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                a1 = a_atoms['V'][step_indx][row_indx][col_indx]
                a2 = a_atoms['Q'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
    # v and q actions on tile i,j prevent spreading from this tile
    for step_indx in range(0, steps-1):
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                a1 = spa_atoms['U'][step_indx][row_indx][col_indx]
                a2 = a_atoms['V'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a2 = a_atoms['Q'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a1 = spa_atoms['D'][step_indx][row_indx][col_indx]
                a2 = a_atoms['V'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a2 = a_atoms['Q'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a1 = spa_atoms['L'][step_indx][row_indx][col_indx]
                a2 = a_atoms['V'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a2 = a_atoms['Q'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a1 = spa_atoms['R'][step_indx][row_indx][col_indx]
                a2 = a_atoms['V'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a2 = a_atoms['Q'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
    # v and q actions on tile i,j prevent spreading to this tile
    for step_indx in range(0, steps-1):
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                if row_indx != (rows - 1):
                    a1 = spa_atoms['U'][step_indx][row_indx+1][col_indx]
                    a2 = a_atoms['V'][step_indx][row_indx][col_indx]
                    clauses.append([-a1, -a2])
                    a2 = a_atoms['Q'][step_indx][row_indx][col_indx]
                    clauses.append([-a1, -a2])
                if row_indx != 1:
                    a1 = spa_atoms['D'][step_indx][row_indx-1][col_indx]
                    a2 = a_atoms['V'][step_indx][row_indx][col_indx]
                    clauses.append([-a1, -a2])
                    a2 = a_atoms['Q'][step_indx][row_indx][col_indx]
                    clauses.append([-a1, -a2])
                if col_indx != (columns - 1):
                    a1 = spa_atoms['L'][step_indx][row_indx][col_indx+1]
                    a2 = a_atoms['V'][step_indx][row_indx][col_indx]
                    clauses.append([-a1, -a2])
                    a2 = a_atoms['Q'][step_indx][row_indx][col_indx]
                    clauses.append([-a1, -a2])
                if col_indx != 1:
                    a1 = spa_atoms['R'][step_indx][row_indx][col_indx-1]
                    a2 = a_atoms['V'][step_indx][row_indx][col_indx]
                    clauses.append([-a1, -a2])
                    a2 = a_atoms['Q'][step_indx][row_indx][col_indx]
                    clauses.append([-a1, -a2])
    # quaranteen to an S tile means it can not age
    for step_indx in range(0, steps-1):
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                a1 = a_atoms['Q'][step_indx][row_indx][col_indx]
                a2 = agea_atoms['S3'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a2 = agea_atoms['S2'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a2 = agea_atoms['S1'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])

    # vacination and quarantine means it can not be a noop
    for step_indx in range(0, steps-1):
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                a1 = a_atoms['Q'][step_indx][row_indx][col_indx]
                a2 = noopa_atoms['S3'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a2 = noopa_atoms['S2'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a2 = noopa_atoms['S1'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a1 = a_atoms['V'][step_indx][row_indx][col_indx]
                a2 = noopa_atoms['H'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])

    # spread to a tile can not happen with noop of that tile
    for step_indx in range(0, steps-1):
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                if row_indx != 0:
                    a1 = spa_atoms['D'][step_indx][row_indx-1][col_indx]
                    a2 = noopa_atoms['H'][step_indx][row_indx][col_indx]
                    clauses.append([-a1, -a2])
                if row_indx != (rows - 1):
                    a1 = spa_atoms['U'][step_indx][row_indx + 1][col_indx]
                    a2 = noopa_atoms['H'][step_indx][row_indx][col_indx]
                    clauses.append([-a1, -a2])
                if col_indx != 0:
                    a1 = spa_atoms['R'][step_indx][row_indx][col_indx - 1]
                    a2 = noopa_atoms['H'][step_indx][row_indx][col_indx]
                    clauses.append([-a1, -a2])
                if col_indx != (columns - 1):
                    a1 = spa_atoms['L'][step_indx][row_indx][col_indx + 1]
                    a2 = noopa_atoms['H'][step_indx][row_indx][col_indx]
                    clauses.append([-a1, -a2])
    # aging of a tile can not happen with noop of that tile
    for step_indx in range(0, steps-1):
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                a1 = agea_atoms['S3'][step_indx][row_indx][col_indx]
                a2 = noopa_atoms['S3'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a1 = agea_atoms['S2'][step_indx][row_indx][col_indx]
                a2 = noopa_atoms['S2'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a1 = agea_atoms['S1'][step_indx][row_indx][col_indx]
                a2 = noopa_atoms['S1'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a1 = agea_atoms['Q2'][step_indx][row_indx][col_indx]
                a2 = noopa_atoms['Q2'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
                a1 = agea_atoms['Q1'][step_indx][row_indx][col_indx]
                a2 = noopa_atoms['Q1'][step_indx][row_indx][col_indx]
                clauses.append([-a1, -a2])
    return clauses

def gen_fact_acheivement_clauses(p_atoms, a_atoms, spa_atoms, noopa_atoms, agea_atoms):
    # Add effect for vaccination is becoming in state 'I'
    # Add effect for quarantine is becoming in state 'Q2'
    # Add effect for spread action U(D) is changing the upper(lower) neighbour to S3
    # Add effect for spread action L(R) is changing the left(right) neighbour to S3
    # Add effect for noop sction

    rows = len(p_atoms['H'][0][0])
    columns = len(p_atoms['H'][0])
    steps = len(p_atoms['H'])
    action_acheivement_clauses = [] # a state implies actions which adds it

    for step_indx in range(1, steps):
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                # 'I' tiles
                # collect actions for which p is an add effect
                I_list = []
                # Vax actions can add an I
                I_list.append(a_atoms['V'][step_indx - 1][row_indx][col_indx])
                # Noop actions can add an I
                I_list.append(noopa_atoms['I'][step_indx - 1][row_indx][col_indx])

                # 'Q2' tiles
                Q2_list = []
                # Quarantine actions can add a Q2
                Q2_list.append(a_atoms['Q'][step_indx - 1][row_indx][col_indx])
                # Noop actions and aging can never cause Q2

                # 'U' tiles
                # Only noop actions can add an U
                U_list = []
                U_list.append(noopa_atoms['U'][step_indx - 1][row_indx][col_indx])

                # 'H' tiles
                H_list = []
                # aging from S1, Q1 will cause H
                H_list.append(agea_atoms['S1'][step_indx - 1][row_indx][col_indx])
                H_list.append(agea_atoms['Q1'][step_indx - 1][row_indx][col_indx])
                # noop can do
                H_list.append(noopa_atoms['H'][step_indx - 1][row_indx][col_indx])

                # 'S3' tiles
                # Only spread actions can add an S3
                S3_list = []
                if row_indx != 0:
                    S3_list.append(spa_atoms['D'][step_indx - 1][row_indx - 1][col_indx])
                if row_indx != (rows-1):
                    S3_list.append(spa_atoms['U'][step_indx - 1][row_indx + 1][col_indx])
                if col_indx != 0:
                    S3_list.append(spa_atoms['R'][step_indx - 1][row_indx][col_indx - 1])
                if col_indx != (columns - 1):
                    S3_list.append(spa_atoms['L'][step_indx - 1][row_indx][col_indx + 1])

                # 'S2' tiles
                # Only aging from S3 can cause S2
                S2_list = []
                S2_list.append(agea_atoms['S3'][step_indx - 1][row_indx][col_indx])

                # 'S1' tiles
                # Only aging from S2 can cause S1
                S1_list = []
                S1_list.append(agea_atoms['S2'][step_indx - 1][row_indx][col_indx])

                # 'Q1' tiles
                # Only aging from Q2 can cause Q1
                Q1_list = []
                Q1_list.append(agea_atoms['Q2'][step_indx - 1][row_indx][col_indx])

                p = p_atoms['U'][step_indx][row_indx][col_indx]
                action_acheivement_clauses.append([-p] + U_list)
                p = p_atoms['H'][step_indx][row_indx][col_indx]
                action_acheivement_clauses.append([-p] + H_list)
                p = p_atoms['S3'][step_indx][row_indx][col_indx]
                action_acheivement_clauses.append([-p] + S3_list)
                p = p_atoms['S2'][step_indx][row_indx][col_indx]
                action_acheivement_clauses.append([-p] + S2_list)
                p = p_atoms['S1'][step_indx][row_indx][col_indx]
                action_acheivement_clauses.append([-p] + S1_list)
                p = p_atoms['I'][step_indx][row_indx][col_indx]
                action_acheivement_clauses.append([-p] + I_list)
                p = p_atoms['Q2'][step_indx][row_indx][col_indx]
                action_acheivement_clauses.append([-p] + Q2_list)
                p = p_atoms['Q1'][step_indx][row_indx][col_indx]
                action_acheivement_clauses.append([-p] + Q1_list)

    return action_acheivement_clauses




def gen_precondition_clauses(p_atoms, a_atoms, sp_atoms, noopa_atoms, agea_atoms):
    # precondition for vaccination is being in state 'H'
    # precondition for quarantine is being in state 'S1' or S2 or S3
    # precondition for spread action U is being in state 'Sx' and having an upper neighbor in state 'H'
    # precondition for spread action D is being in state 'Sx' and having a lower neighbor in state 'H'
    # precondition for spread action L is being in state 'Sx' and having a left neighbor in state 'H'
    # precondition for spread action R is being in state 'Sx' and having a right neighbor in state 'H'
    # precondition for noop(p) is p
    # precondition for age tile (i,j) is being in state Sx(Qx)

    steps = len(p_atoms['H'])
    columns = len(p_atoms['H'][0])
    rows = len(p_atoms['H'][0][0])
    action_precond_clause = []
    for step_indx in range(0, steps-1):
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                p = p_atoms['H'][step_indx][row_indx][col_indx]
                a = a_atoms['V'][step_indx][row_indx][col_indx]
                action_precond_clause.append([-a, p])
                p = [p_atoms['S3'][step_indx][row_indx][col_indx], p_atoms['S2'][step_indx][row_indx][col_indx], p_atoms['S1'][step_indx][row_indx][col_indx]]
                a = a_atoms['Q'][step_indx][row_indx][col_indx]
                action_precond_clause.append([-a]+p)
    spread_clause = []
    for step_indx in range(0, steps-1):
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                # to spread- source must be sick
                p_source = [p_atoms['S3'][step_indx][row_indx][col_indx], p_atoms['S2'][step_indx][row_indx][col_indx], p_atoms['S1'][step_indx][row_indx][col_indx]]
                # spread up:
                if row_indx != 0: # can't spread up from row 1
                    a = -sp_atoms['U'][step_indx][row_indx][col_indx]
                    p_affected = p_atoms['H'][step_indx][row_indx - 1][col_indx]
                    spread_clause.append([a, p_affected])
                    spread_clause.append([a]+p_source)
                # spread down:
                if row_indx != (rows-1):  # can't spread down from last row
                    a = -sp_atoms['D'][step_indx][row_indx][col_indx]
                    p_affected = p_atoms['H'][step_indx][row_indx + 1][col_indx]
                    spread_clause.append([a, p_affected])
                    spread_clause.append([a] + p_source)
                # spread left:
                if col_indx != 0:  # can't spread left from column 1
                    a = -sp_atoms['L'][step_indx][row_indx][col_indx]
                    p_affected = p_atoms['H'][step_indx][row_indx][col_indx - 1]
                    spread_clause.append([a, p_affected])
                    spread_clause.append([a] + p_source)
                # spread right:
                if col_indx != (columns-1):  # can't spread right from last column
                    a = -sp_atoms['R'][step_indx][row_indx][col_indx]
                    p_affected = p_atoms['H'][step_indx][row_indx][col_indx + 1]
                    spread_clause.append([a, p_affected])
                    spread_clause.append([a] + p_source)
    noop_clause = []
    for step_indx in range(0, steps-1):
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                for st in ['U', 'H', 'S3', 'S2', 'S1','I', 'Q2', 'Q1']:
                    a = noopa_atoms[st][step_indx][row_indx][col_indx]
                    p = p_atoms[st][step_indx][row_indx][col_indx]
                    noop_clause.append([-a, p])
    aging_clause = []
    for step_indx in range(0, steps - 1):
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                for st in ['S3', 'S2', 'S1', 'Q2', 'Q1']:
                    a = agea_atoms[st][step_indx][row_indx][col_indx]
                    p = p_atoms[st][step_indx][row_indx][col_indx]
                    aging_clause.append([-a, p])

    return action_precond_clause + spread_clause + noop_clause + aging_clause

def gen_observation_clauses(atoms, observations):
    columns = len(observations[0])
    rows = len(observations[0][0])
    observation_clause = []
    step = 0
    for map in observations:
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                if map[row_indx][col_indx] != '?':
                    p = population_clause_add(map[row_indx][col_indx], atoms, step, row_indx, col_indx)
                    observation_clause.extend(p)
                    if step == 0:
                        if map[row_indx][col_indx] == 'S': # First time we know that S is actually S3
                            p = population_clause_add('S3', atoms, step, row_indx, col_indx)
                            observation_clause.extend(p)
                else:
                    if step == 0: # ? in the first step: exactly one of the three possible states must be
                        p = [atoms['U'][step][row_indx][col_indx], atoms['H'][step][row_indx][col_indx],
                             atoms['S3'][step][row_indx][col_indx]]
                        p_pairs = list(combinations(p,2))
                        observation_clause.append(p)
                        for pair in p_pairs:
                            observation_clause.append([-pair[0], -pair[1]])
                        # Can't start with any of these:'
                        p = [[-atoms['I'][step][row_indx][col_indx]], [-atoms['S2'][step][row_indx][col_indx]],
                             [-atoms['S1'][step][row_indx][col_indx]], [-atoms['Q2'][step][row_indx][col_indx]],
                             [-atoms['Q1'][step][row_indx][col_indx]]]
                        observation_clause.extend(p)
                    else: # ? not the first step: at least one possible state must be
                        p = [atoms['U'][step][row_indx][col_indx], atoms['H'][step][row_indx][col_indx],
                             atoms['S3'][step][row_indx][col_indx], atoms['S2'][step][row_indx][col_indx],
                             atoms['S1'][step][row_indx][col_indx], atoms['Q2'][step][row_indx][col_indx],
                             atoms['Q1'][step][row_indx][col_indx], atoms['I'][step][row_indx][col_indx]]
                        p_pairs = list(combinations(p, 2))
                        observation_clause.append(p)
                        for pair in p_pairs:
                            observation_clause.append([-pair[0], -pair[1]])

        step = step + 1
    return observation_clause


def population_clause_add(population_state, atoms, step, row_indx, col_indx):
    state_list = ['U', 'H', 'S3', 'S2', 'S1','I', 'Q2', 'Q1']
    no_S_list = ['U', 'H', 'I', 'Q2', 'Q1']
    no_Q_list = ['U', 'H', 'S3', 'S2', 'S1', 'I']
    observation_clause = []
    if population_state == 'S':
        if step == 0:
            observation_clause.append([atoms['S3'][step][row_indx][col_indx]])
        else:
            p = [atoms['S3'][step][row_indx][col_indx], atoms['S2'][step][row_indx][col_indx], atoms['S1'][step][row_indx][col_indx]]
            observation_clause.append(p)
        for st in no_S_list: # if state is S then all states other than S1, S2, S3 are FALSE
            observation_clause.append([-atoms[st][step][row_indx][col_indx]])
    elif population_state == 'Q':
        p = [atoms['Q2'][step][row_indx][col_indx], atoms['Q1'][step][row_indx][col_indx]]
        observation_clause.append(p)
        for st in no_Q_list:# if state is Q then all states other than Q1, Q2 are FALSE
            observation_clause.append([-atoms[st][step][row_indx][col_indx]])
    else: # State is not S and not Q then it is TRUE and all others are FALSE
        state_list.remove(population_state)
        observation_clause.append([atoms[population_state][step][row_indx][col_indx]])
        for st in state_list:
            observation_clause.append([-atoms[st][step][row_indx][col_indx]])
    return observation_clause

def gen_S_representation_clauses(p_atoms):
    # clauses to force the relation of S and S1,S2,S3
    S_clauses = []
    steps = len(p_atoms['H'])
    columns = len(p_atoms['H'][0])
    rows = len(p_atoms['H'][0][0])
    for step_indx in range(0, steps - 1):
        for row_indx in range(0, rows):
            for col_indx in range(0, columns):
                p = [[-p_atoms['S3'][step_indx][row_indx][col_indx], p_atoms['S'][step_indx][row_indx][col_indx]],
                     [-p_atoms['S2'][step_indx][row_indx][col_indx], p_atoms['S'][step_indx][row_indx][col_indx]],
                     [-p_atoms['S1'][step_indx][row_indx][col_indx], p_atoms['S'][step_indx][row_indx][col_indx]]]
                S_clauses.extend(p)
    return S_clauses

def enumerate_states(problem, start):
    steps = len(problem['observations'])
    columns = len(problem['observations'][0])
    rows = len(problem['observations'][0][0])
    U, last = build_enumeration_table(start, steps, rows, columns)
    H, last = build_enumeration_table(last, steps, rows, columns)
    S3, last = build_enumeration_table(last, steps, rows, columns)
    S2, last = build_enumeration_table(last, steps, rows, columns)
    S1, last = build_enumeration_table(last, steps, rows, columns)
    I, last = build_enumeration_table(last, steps, rows, columns)
    Q2, last = build_enumeration_table(last, steps, rows, columns)
    Q1, last = build_enumeration_table(last, steps, rows, columns)
    S, last = build_enumeration_table(last, steps, rows, columns)
    atoms = {
        'U': U,
        'H': H,
        'S3': S3,
        'S2': S2,
        'S1': S1,
        'I': I,
        'Q2': Q2,
        'Q1': Q1,
        'S': S # auxilery state to represent S3 or S2 or S
    }
    return atoms, last

def build_enumeration_table(start, steps, rows, columns):
    enum_table = ()
    k = start
    for step_indx in range(0, steps):
        mat = ()
        for row_indx in range(0, rows):
            mat_row = ()
            for col_indx in range(0, columns):
                mat_row = mat_row + (k,)
                k = k + 1
            mat = mat + (mat_row,)
        enum_table = enum_table + (mat,)
    return enum_table, k

def enumerate_spread_actions(problem, start):
    columns = len(problem['observations'][0])
    rows = len(problem['observations'][0][0])
    steps = len(problem['observations'])
    U, last = build_enumeration_table(start, steps, rows, columns)
    D, last = build_enumeration_table(last, steps, rows, columns)
    L, last = build_enumeration_table(last, steps, rows, columns)
    R, last = build_enumeration_table(last, steps, rows, columns)
    spread_actions = {
        'U': U,
        'D': D,
        'L': L,
        'R': R
    }
    return spread_actions, last

def enumerate_agent_actions(start, problem):
    columns = len(problem['observations'][0])
    rows = len(problem['observations'][0][0])
    steps = len(problem['observations'])
    Q, last = build_enumeration_table(start, steps-1, rows, columns)
    V, last = build_enumeration_table(last, steps-1, rows, columns)
    agent_actions = {
        'Q': Q,
        'V': V
    }
    return agent_actions, last