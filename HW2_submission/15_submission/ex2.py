ids = ['310246897','313769952']
import numpy as np
from utils import first, expr, Expr, subexpressions
from pysat.formula import IDPool, CNF
from pysat.solvers import Solver
from itertools import chain, combinations

VERBOSE = False

def solve_problem(input):
    pass
    # put your solution here, remember the format needed
    max_T = len(input['observations'])
    sol_dict = solve_problem_t(input,max_T)
    return sol_dict

def solve_problem_t(input,T):       

    n_police = input['police']
    n_medics = input['medics']
    observations = input['observations']
    queries = input['queries']
    H = len(observations[0])
    W = len(observations[0][0])

    vpool = IDPool()
    clauses = []
    tile = lambda code,r,c,t : '{0}{1}{2}_{3}'.format(code,r,c,t)
    CODES = ['U','H','S']
    ACTIONS = []
    if n_medics > 0:
        CODES.append('I')
        ACTIONS.append('medics')        
    if n_police > 0:
        CODES.append('Q')
        ACTIONS.append('police')

    # create list of predicates and associate an integer in pySat for each predicate
    for t in range(T):
        for code in CODES+ACTIONS:
            for r in range(H):
                for c in range(W):
                    vpool.id(tile(code,r,c,t))

    # clauses for the known tiles in the observation, both positive and negative
    for t in range(T):
        curr_observ = observations[t]
        for r in range(H):
            for c in range(W):
                curr_code = curr_observ[r][c]
                for code in CODES:
                    if (code == curr_code) & (curr_code != '?'):
                        clauses.append(tile(code,r,c,t))
                    elif (code != curr_code) & (curr_code != '?'):
                        clauses.append('~' + tile(code,r,c,t))

    # Uxy_t ==> Uxy_t-1 pre-condition
    for t in range(1,T):
        for r in range(H):
            for c in range(W):
                clauses.append(tile('U',r,c,t) + ' ==> ' + tile('U',r,c,t-1))

    # Uxy_t ==> Uxy_t+1 add effect (no del effect)
    for t in range(T-1):
        for r in range(H):
            for c in range(W):
                clauses.append(tile('U',r,c,t) + ' ==> ' + tile('U',r,c,t+1))

    # Ixy_t ==> Ixy_t-1 | (Hxy_t-1 & medicsxy_t-1)' - pre-condition of 'I'
    if n_medics > 0:
        for t in range(1,T):
            for r in range(H):
                for c in range(W):
                    #clauses.append(tile('I',r,c,t) + ' ==> (' + tile('I',r,c,t-1) + ' | ' + tile('H',r,c,t-1)+')')
                    clauses.append(tile('I',r,c,t) + ' ==> (' + tile('I',r,c,t-1) + \
                        ' | (' + tile('H',r,c,t-1) + ' & ' + tile('medics',r,c,t-1) + '))')

    # Ixy_t ==> Ixy_t+1 - add effect of 'I' (no del effect)
    if n_medics > 0:
        for t in range(T-1):
            for r in range(H):
                for c in range(W):
                    clauses.append(tile('I',r,c,t) + ' ==> ' + tile('I',r,c,t+1))

    # Qxy_t ==> Qxy_t-1 | (Sxy_t-1 & policexy_t-1)' - pre-condition of 'Q'
    if n_police > 0:
        for t in range(1,T):
            for r in range(H):
                for c in range(W):
                    clauses.append(tile('Q',r,c,t) + ' ==> (' + tile('Q',r,c,t-1) + \
                        ' | (' + tile('S',r,c,t-1) + ' & ' + tile('police',r,c,t-1) + '))')

    # add and del effects of Qxy_t
    if n_police > 0:
        for t in range(T-1):
            for r in range(H):
                for c in range(W):
                    if t<1: 
                        # Qxy_t ==> Qxy_t+1
                        clauses.append(tile('Q',r,c,t) +  ' ==> ' + tile('Q',r,c,t+1))
                    else:
                        # Qxy_t & ~Qxy_t-1 ==> Qxy_t+1
                        clauses.append('(' + tile('Q',r,c,t) + ' & ~' + tile('Q',r,c,t-1) + ')'\
                            + ' ==> ' + tile('Q',r,c,t+1))
                        # Qxy_t & Qxy_t-1 ==> Hxy_t+1
                        clauses.append('(' + tile('Q',r,c,t) +' & ' + tile('Q',r,c,t-1) + \
                            ') ==> ' + tile('H',r,c,t+1))
                        # Qxy_t & Qxy_t-1 ==> ~Qxy_t+1
                        clauses.append('(' + tile('Q',r,c,t) +' & ' + tile('Q',r,c,t-1) + \
                            ') ==> ~' + tile('Q',r,c,t+1))

    # precondition of S(x,y,t) is either S(x,y,t-1) or H(x,y,t-1) and at least one sick neighbor
    for t in range(1,T):
        for r in range(H):
            for c in range(W):
                #n_coords = get_neighbors(r,c,H,W)
                #curr_clause = tile('S',r,c,t) + ' ==> (' + tile('S',r,c,t-1) + ' | (' + tile('H',r,c,t-1) + ' & ('
                #for coord in n_coords:
                #    curr_clause+= tile('S',coord[0],coord[1],t-1) + ' | '
                #clauses.append(curr_clause[:-3] + ')))')
                clauses.append(tile('S',r,c,t) + ' ==> (' + tile('S',r,c,t-1) + ' | ' + tile('H',r,c,t-1) + ')')

    # add and del effects of Sxy_t
    for t in range(T-1):
        for r in range(H):
            for c in range(W):
                if n_police > 0:
                    # Sxy_t & policexy_t ==> Qxy_t+1 - add effect of 'S' if there's police
                    clauses.append(tile('S',r,c,t) + ' & ' + tile('police',r,c,t) + ' ==> ' + tile('Q',r,c,t+1))
                    # Sxy_t & policexy_t ==> ~Sxy_t+1 - del effect of 'S' if there's police
                    clauses.append(tile('S',r,c,t) + ' & ' + tile('police',r,c,t) + ' ==> ~' + tile('S',r,c,t+1))
                    if t<2:
                        # Sxy_t & ~policexy_t ==> Sxy_t+1
                        clauses.append('(' + tile('S',r,c,t) + ' & ' + tile('~police',r,c,t) + \
                            ') ==> ' + tile('S',r,c,t+1))
                    else:
                        # Sxy_t & ~policexy_t & ~Sxy_t-1 ==> Sxy_t+1
                        clauses.append('(' + tile('S',r,c,t) + ' & ~' + tile('police',r,c,t) + ' & ~' + tile('S',r,c,t-1) + ')'\
                            + ') ==> ' + tile('S',r,c,t+1))
                        # Sxy_t & ~policexy_t & Sxy_t-1 & ~Sxy_t-2 ==> Sxy_t+1
                        clauses.append('(' + tile('S',r,c,t) + ' & ~' + tile('police',r,c,t) + ' & ' + tile('S',r,c,t-1) + \
                            ' & ~' + tile('S',r,c,t-2) + ') ==> ' + tile('S',r,c,t+1))
                        # Sxy_t & ~policexy_t & Sxy_t-1 & Sxy_t-2 ==> Hxy_t+1
                        clauses.append('(' + tile('S',r,c,t) + ' & ~' + tile('police',r,c,t) + ' & ' + tile('S',r,c,t-1) + \
                            ' & ' + tile('S',r,c,t-2) + ') ==> ' + tile('H',r,c,t+1))
                        # Sxy_t & ~policexy_t & Sxy_t-1 & Sxy_t-2 ==> ~Sxy_t+1
                        clauses.append('(' + tile('S',r,c,t) + ' & ~' + tile('police',r,c,t) + ' & ' + tile('S',r,c,t-1) + \
                            ' & ' + tile('S',r,c,t-2) + ') ==> ~' + tile('S',r,c,t+1))
                else:
                    if t<2:
                        # Sxy_t ==> Sxy_t+1
                        clauses.append(tile('S',r,c,t) + ' ==> ' + tile('S',r,c,t+1))
                    else:
                        # Sxy_t & ~Sxy_t-1 ==> Sxy_t+1
                        clauses.append('(' + tile('S',r,c,t) + ' & ~' + tile('S',r,c,t-1) + ')'\
                            + ' ==> ' + tile('S',r,c,t+1))
                        # Sxy_t & Sxy_t-1 & ~Sxy_t-2 ==> Sxy_t+1
                        clauses.append('(' + tile('S',r,c,t) + ' & ' + tile('S',r,c,t-1) + \
                            ' & ~' + tile('S',r,c,t-2) + ') ==> ' + tile('S',r,c,t+1))
                        # Sxy_t & Sxy_t-1 & Sxy_t-2 ==> Hxy_t+1
                        clauses.append('(' + tile('S',r,c,t) + ' & ' + tile('S',r,c,t-1) + \
                            ' & ' + tile('S',r,c,t-2) + ' ) ==> ' + tile('H',r,c,t+1))
                        # Sxy_t & Sxy_t-1 & Sxy_t-2 ==> ~Sxy_t+1
                        clauses.append('(' + tile('S',r,c,t) + ' & ' + tile('S',r,c,t-1) + \
                            ' & ' + tile('S',r,c,t-2) + ' ) ==> ~' + tile('S',r,c,t+1))   

    # pre-conditions of 'H'
    for t in range(1,T):
        for r in range(H):
            for c in range(W):
                if t<3:
                    # Hxy_t ==> Hxy_t-1
                    clauses.append(tile('H',r,c,t) + ' ==> ' + tile('H',r,c,t-1))
                else:
                    # Hxy_t ==> Hxy_t-1 | (Sxy_t-1 & Sxy_t-2 & Sxy_t-3) | (Qxy_t-1, Qxy_t-2) 
                    curr_clause = tile('H',r,c,t) + ' ==> ' + tile('H',r,c,t-1) + ' | (' + \
                        tile('S',r,c,t-1) + ' & ' + tile('S',r,c,t-2) + ' & ' + tile('S',r,c,t-3) + ')'
                    if n_police > 0:
                        curr_clause+= ' | (' + tile('Q',r,c,t-1) + ' & ' + tile('Q',r,c,t-2) + ')'
                    clauses.append(curr_clause) 

    # add effect of 'H'
    for t in range(T-1):
        for r in range(H):
            for c in range(W):
                n_coords = get_neighbors(r,c,H,W)
                if n_medics > 0:
                    # Hxy_t & medicsxy_t ==> Ixy_t+1
                    clauses.append(tile('H',r,c,t) + ' & ' + tile('medics',r,c,t) + ' ==> ' + tile('I',r,c,t+1))
                    # Hxy_t & medicsxy_T ==> ~Hxy_t+1
                    clauses.append(tile('H',r,c,t) + ' & ' + tile('medics',r,c,t) + ' ==> ' + tile('~H',r,c,t+1))
                    # Hxy_t & ~medicsxy_t & (at least one sick neighbor) ==> Sxy_t+1
                    curr_clause = tile('H',r,c,t) + ' & ' + tile('~medics',r,c,t) + ' & ('
                    for coord in n_coords:
                        if n_police > 0: # if neighbors 'S' do not turn to 'Q' in the next turn
                            curr_clause += '(' + tile('S',coord[0],coord[1],t) + ' & ' + \
                                tile('~Q',coord[0],coord[1],t+1) + ') | '
                        else:
                            curr_clause += tile('S',coord[0],coord[1],t) + ' | '
                    curr_clause = curr_clause[:-3] + ') ==> ' + tile('S',r,c,t+1)
                    clauses.append(curr_clause)
                    # Hxy_t & ~medicsxy_t & (at least one sick neighbor) ==> ~Hxy_t+1
                    curr_clause = tile('H',r,c,t) + ' & ' + tile('~medics',r,c,t) + ' & ('
                    for coord in n_coords:
                        curr_clause += tile('S',coord[0],coord[1],t) + ' | '
                    curr_clause = curr_clause[:-3] + ') ==> ' + tile('~H',r,c,t+1)
                    clauses.append(curr_clause)
                    # Hxy_t & ~medicsxy_t & (no sick neighbors) ==> Hxy_t+1
                    curr_clause = []
                    curr_clause = tile('H',r,c,t) + ' & ' + tile('~medics',r,c,t) + ' & ('
                    for coord in n_coords:
                        curr_clause += tile('~S',coord[0],coord[1],t) + ' & '
                    curr_clause = curr_clause[:-3] + ') ==> ' + tile('H',r,c,t+1)
                    clauses.append(curr_clause)
                else:
                    # Hxy_t & (at least one sick neighbor) ==> Sxy_t+1
                    curr_clause = tile('H',r,c,t) + ' & ('
                    for coord in n_coords:
                        if n_police > 0:
                            curr_clause += '(' + tile('S',coord[0],coord[1],t) + ' & ' + \
                                tile('~Q',coord[0],coord[1],t+1) + ') | '
                        else:
                            curr_clause += tile('S',coord[0],coord[1],t) + ' | '
                    curr_clause = curr_clause[:-3] + ') ==> ' + tile('S',r,c,t+1)
                    clauses.append(curr_clause)
                    # Hxy_t & (at least one sick neighbor) ==> ~Hxy_t+1
                    curr_clause = tile('H',r,c,t) + ' & ('
                    for coord in n_coords:
                        curr_clause += tile('S',coord[0],coord[1],t) + ' | '
                    curr_clause = curr_clause[:-3] + ') ==> ' + tile('~H',r,c,t+1)
                    clauses.append(curr_clause)
                    # Hxy_t & (no sick neighbors) ==> Hxy_t+1
                    curr_clause = tile('H',r,c,t) + ' & ('
                    for coord in n_coords:
                        curr_clause += tile('~S',coord[0],coord[1],t) + ' & '
                    curr_clause = curr_clause[:-3] + ') ==> ' + tile('H',r,c,t+1)
                    clauses.append(curr_clause)

    ## Qxy_t ==> Qxy_t+1 - add effect of 'Q' 
    #if n_police > 0:
    #    for t in range(T-1):
    #        for r in range(H):
    #            for c in range(W):
    #                clauses.append(tile('Q',r,c,t) + ' ==> ' + tile('Q',r,c,t+1))

    ## Sxy_t ==> Sxy_t-1 - precondition of 'S' if there's no sick tiles
    #for t in range(1,T):
    #    for r in range(H):
    #        for c in range(W):
    #            if T<3:
    #                clauses.append(tile('S',r,c,t) + ' ==> ' + tile('S',r,c,t-1))

    ## action-add effect of 'H' - if tile 'H' in (x,y,t) and no sick neighbors, then 'H' in (x,y,t+1)
    #for t in range(1,T):
    #    for r in range(H):
    #        for c in range(W):
    #            n_coords = get_neighbors(r,c,H,W)
    #            curr_clause = tile('H',r,c,t) + ' <== (' + tile('H',r,c,t-1)
    #            for coord in n_coords:
    #                curr_clause+= ' & ' + tile('~S',coord[0],coord[1],t-1)
    #            clauses.append(curr_clause + ')')

    ## Hxy_t ==> Hxy_t-1 - precondition of 'H' if there's no sick tiles
    #for t in range(1,T):
    #    for r in range(H):
    #        for c in range(W):
    #            if T<3:
    #                clauses.append(tile('H',r,c,t) + ' ==> ' + tile('H',r,c,t-1))

    # Hxy_t & medicsxy_t ==> Ixy_t+1 - add effect of 'H' if there's no sick
    #for t in range(T-1):
    #    for r in range(H):
    #        for c in range(W):
    #            clauses.append(tile('H',r,c,t) + ' & ' + tile('medics',r,c,t) + ' ==> ' + tile('I',r,c,t+1))
    #            # Hxy_t & medicsxy_t ==> ~Hxy_t+1 - del effect of 'H'
    #            clauses.append(tile('H',r,c,t) + ' & ' + tile('medics',r,c,t) + ' ==> ~' + tile('H',r,c,t+1))


    # a single tile can only contain one code, i.e. or 'H' or 'S' or 'U' or 'I' or 'Q'
    #exclude_clause = lambda code_1,code_2,r,c,t : '~{0}{1}{2}_{3} | ~{4}{5}{6}_{7}'.format(code_1,r,c,t,code_2,r,c,t)
    for t in range(T):
        for r in range(H):
            for c in range(W):
                literal_list = []
                for code in CODES:
                    literal_list.append('~' + tile(code,r,c,t))
                powerset_res = lim_powerset(literal_list,2)
                for combo in powerset_res:
                    clauses.append(combo[0] + ' | ' + combo[1])
                    #CODES_reduced = []
                    #[CODES_reduced.append(code) if code != code_1 else '' for code in CODES]
                    #for code_2 in CODES_reduced:
                    #    clauses.append(exclude_clause(code_1,code_2,r,c,t))

    # medics is only valid for 'H' tiles
    if n_medics > 0:
        for code in CODES:
            for t in range(T):
                for r in range(H):
                    for c in range(W):
                        if code != 'H':
                            clauses.append(tile(code,r,c,t) + ' ==> ' + tile('~medics',r,c,t))

    if n_medics > 1:
        # medics has to be exactly n_medics times
        for t in range(T-1):
            tile_coords = []
            for r in range(H):
                for c in range(W):
                    tile_coords.append(tile('medics',r,c,t))
            positive_tiles = lim_powerset(tile_coords,n_medics)
            curr_clause = '(('
            for combo in positive_tiles:
                for predicate in combo:
                    curr_clause += predicate + ' & ' 
                for curr_tile in tile_coords:
                    if curr_tile not in combo:
                        curr_clause += '~' + curr_tile + ' & '
                curr_clause = curr_clause[:-3] + ') | ('
            clauses.append(curr_clause[:-3] + ')')
    elif n_medics == 1:
        for t in range(T-1):
            curr_clause = '('
            predicate_list = []
            for r in range(H):
                for c in range(W):
                    predicate_list.append(tile('~medics',r,c,t))
                    curr_clause += tile('medics',r,c,t) + ' | '
            clauses.append(curr_clause[:-3] + ')')
            powerset_res = lim_powerset(predicate_list,2)
            for combo in powerset_res:
                clauses.append(combo[0] + ' | ' + combo[1])
    
    # police is only valid for 'S' tiles
    if n_police > 0:
        for code in CODES:
            for t in range(T):
                for r in range(H):
                    for c in range(W):
                        if code != 'S':
                            clauses.append(tile(code,r,c,t) + ' ==> ' + tile('~police',r,c,t))

    # police has to be exactly n_police times
    if n_police > 1:
        for t in range(T-1):
            tile_coords = []
            for r in range(H):
                for c in range(W):
                    tile_coords.append(tile('police',r,c,t))
            positive_tiles = lim_powerset(tile_coords,n_police)
            curr_clause = '(('
            for combo in positive_tiles:
                for predicate in combo:
                    curr_clause += predicate + ' & ' 
                for curr_tile in tile_coords:
                    if curr_tile not in combo:
                        curr_clause += '~' + curr_tile + ' & '
                curr_clause = curr_clause[:-3] + ') | ('
            clauses.append(curr_clause[:-3] + ')')
    elif n_police == 1:
        for t in range(T-1):
            curr_clause = '('
            predicate_list = []
            for r in range(H):
                for c in range(W):
                    predicate_list.append(tile('~police',r,c,t))
                    curr_clause += tile('police',r,c,t) + ' | '
            clauses.append(curr_clause[:-3] + ')')
            powerset_res = lim_powerset(predicate_list,2)
            for combo in powerset_res:
                clauses.append(combo[0] + ' | ' + combo[1])

    clauses_in_cnf = all_clauses_in_cnf(clauses)
    clauses_in_pysat = all_clauses_in_pysat(clauses_in_cnf,vpool)
    s = Solver()
    s.append_formula(clauses_in_pysat)

    q_dict = dict()
    for q in queries:
        if VERBOSE:
            print('\n')
            print('Initial Observations')
            print_model(observations,T,H,W,n_police,n_medics)
            print('\n')
            print('Query')
            print(q)
            print('\n')
        res_list = []
        for code in CODES:
            clause_to_check = cnf_to_pysat(to_cnf(tile(code,q[0][0],q[0][1],q[1])),vpool)
            if s.solve(assumptions=clause_to_check):
                res_list.append(1)
                if VERBOSE:
                    print('Satisfiable for code=%s as follows:' % (code))
                    sat_observations = get_model(s.get_model(),vpool,T,H,W)
                    print_model(sat_observations,T,H,W,n_police,n_medics)
                    print('\n')
            else:
                res_list.append(0)
                if VERBOSE:
                    print('NOT Satisfiable for code=%s' % (code))
                    print('\n')
                    print(vpool.obj(s.get_core()[0]))
        if np.sum(res_list) == 1:
            if CODES[res_list.index(1)] == q[2]:
                q_dict[q] = 'T'
            else:
                q_dict[q] = 'F'
        else:
            q_dict[q] = '?'

    return q_dict




    ## medics has to be performed at least once
    #if n_medics > 0:
    #    for t in range(T):
    #        curr_clause = '('
    #        for r in range(H):
    #            for c in range(W):
    #                curr_clause+= tile('medics',r,c,t) + ' | '
    #        clauses.append(curr_clause[:-3] + ')')

    ## medics has to be performed at most n_medics times
    #if n_medics > 0:
    #    for t in range(T):
    #        tile_coords = []
    #        for r in range(H):
    #            for c in range(W):
    #                tile_coords.append(tile('medics',r,c,t))
    #        positive_tiles = lim_powerset(tile_coords,n_medics)
    #        for combo in positive_tiles:
    #            curr_clause = '('
    #            for predicate in combo:
    #                curr_clause += predicate + ' & ' 
    #            if n_medics < H*W:
    #                curr_clause = curr_clause[:-3] + ') ==> ('
    #                for r in range(H):
    #                    for c in range(W):
    #                        if tile('medics',r,c,t) not in combo:
    #                            curr_clause += '~' + tile('medics',r,c,t) + ' & '
    #            clauses.append(curr_clause[:-3] + ')')

########################## Helper functions ###############################

def all_clauses_in_pysat(clauses,vpool):
    clauses_in_pysat = []
    [clauses_in_pysat.append(cnf_to_pysat(clause,vpool)) for clause in clauses]
    return clauses_in_pysat

def all_clauses_in_cnf(clauses):
    clauses_in_cnf = list()
    for clause in clauses:
        cnf_clause = to_cnf(clause)
        if len(conjuncts(cnf_clause)) == 1:
            clauses_in_cnf.append(cnf_clause)
        else:
            for sub_clause in conjuncts(cnf_clause):
                clauses_in_cnf.append(sub_clause)
    return clauses_in_cnf

def lim_powerset(iterable, max_r):
    """powerset([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    all_combos = list(chain.from_iterable(combinations(s, r) for r in range(max_r+1)))[1:]
    length_r_combos = []
    [length_r_combos.append(combo) if (len(combo)==max_r) else '' for combo in all_combos]
    return length_r_combos

def clauses_relating_to(clauses,p):
    [print(clause) for clause in clauses if p in clause]

def from_pysat_to_logic(sol,vpool):
    res_list = []
    for lit in sol:
        loc = abs(lit)
        if lit > 0:
            res_list.append(vpool.obj(loc))
        else:
            res_list.append('~' + vpool.obj(loc))
    return res_list

def get_model(sol, vpool, T, H, W):
    model = dict()
    observations = []
    for id in sol:
        if id>0:
            #model.append(vpool.obj(id))
            p = vpool.obj(id)
            model[p[1]+p[2]+'_'+p[4]] = p[0]
    
    for t in range(T):
        curr_map = []
        for r in range(H):
            curr_row = []
            for c in range(W):
                curr_tile = str(r)+str(c)+'_'+str(t)
                if curr_tile not in model.keys():
                    #curr_map += '? '
                    curr_row.append('?')
                else:
                    #curr_map += model[curr_tile] + ' '
                    curr_row.append(model[curr_tile])
            curr_map.append(curr_row)
        observations.append(curr_map)

    return observations

def print_model(observations, T, H, W, n_police, n_medics):
    for r in range(H):
        row_str = str()
        for t in range(T):
            for c in range(W):
                row_str += observations[t][r][c] + ' '
            row_str += '   '
        print(row_str)  
    print('medics: ' + str(n_medics) + ', police: ' + str(n_police))

def get_neighbors(r, c, H, W):
    if r >= 1 and r < H-1 and c >= 1 and c < W-1:
        return([[r-1,c],[r+1,c],[r,c-1],[r,c+1]])
    if r==0 and c>=1 and c < W-1:
        return([[r+1,c],[r,c-1],[r,c+1]])
    if r==H-1 and c>=1 and c < W-1:
        return([[r-1,c],[r,c-1],[r,c+1]])
    if r >= 1 and r < H-1 and c==0:
        return([[r-1,c],[r+1,c],[r,c+1]])
    if r >= 1 and r < H-1 and c==W-1:
        return([[r-1,c],[r+1,c],[r,c-1]])
    if r==0 and c==0:
        return([[r+1,c],[r,c+1]])
    if r==H-1 and c==0:
        return([[r-1,c],[r,c+1]])
    if r==0 and c==W-1:
        return([[r+1,c],[r,c-1]])
    if r==H-1 and c==W-1:
        return([[r-1,c],[r,c-1]])

def cnf_to_pysat(clause, vpool):
    pysat_clause = list()
    # single literal
    if len(clause.args) == 0:
        pysat_clause.append(vpool.id(str(clause.op)))
    elif len(clause.args)==1 and clause.op == '~':
        pysat_clause.append(-vpool.id(str(clause.args[0])))
    else:
        for literal in clause.args:
            if len(literal.args) == 0:
                pysat_clause.append(vpool.id(str(literal.op)))
            elif len(literal.args)==1 and literal.op == '~':
                pysat_clause.append(-vpool.id(str(literal.args[0])))
    return pysat_clause

def to_cnf(s):
    """
    [Page 253]
    Convert a propositional logical sentence to conjunctive normal form.
    That is, to the form ((A | ~B | ...) & (B | C | ...) & ...)
    >>> to_cnf('~(B | C)')
    (~B & ~C)
    """
    s = expr(s)
    if isinstance(s, str):
        s = expr(s)
    s = eliminate_implications(s)  # Steps 1, 2 from p. 253
    s = move_not_inwards(s)  # Step 3
    return distribute_and_over_or(s)  # Step 4

def eliminate_implications(s):
    """Change implications into equivalent form with only &, |, and ~ as logical operators."""
    s = expr(s)
    if not s.args or is_symbol(s.op):
        return s  # Atoms are unchanged.
    args = list(map(eliminate_implications, s.args))
    a, b = args[0], args[-1]
    if s.op == '==>':
        return b | ~a
    elif s.op == '<==':
        return a | ~b
    elif s.op == '<=>':
        return (a | ~b) & (b | ~a)
    elif s.op == '^':
        assert len(args) == 2  # TODO: relax this restriction
        return (a & ~b) | (~a & b)
    else:
        assert s.op in ('&', '|', '~')
        return Expr(s.op, *args)

def move_not_inwards(s):
    """Rewrite sentence s by moving negation sign inward.
    >>> move_not_inwards(~(A | B))
    (~A & ~B)
    """
    s = expr(s)
    if s.op == '~':
        def NOT(b):
            return move_not_inwards(~b)

        a = s.args[0]
        if a.op == '~':
            return move_not_inwards(a.args[0])  # ~~A ==> A
        if a.op == '&':
            return associate('|', list(map(NOT, a.args)))
        if a.op == '|':
            return associate('&', list(map(NOT, a.args)))
        return s
    elif is_symbol(s.op) or not s.args:
        return s
    else:
        return Expr(s.op, *list(map(move_not_inwards, s.args)))

def distribute_and_over_or(s):
    """Given a sentence s consisting of conjunctions and disjunctions
    of literals, return an equivalent sentence in CNF.
    >>> distribute_and_over_or((A & B) | C)
    ((A | C) & (B | C))
    """
    s = expr(s)
    if s.op == '|':
        s = associate('|', s.args)
        if s.op != '|':
            return distribute_and_over_or(s)
        if len(s.args) == 0:
            return False
        if len(s.args) == 1:
            return distribute_and_over_or(s.args[0])
        conj = first(arg for arg in s.args if arg.op == '&')
        if not conj:
            return s
        others = [a for a in s.args if a is not conj]
        rest = associate('|', others)
        return associate('&', [distribute_and_over_or(c | rest)
                               for c in conj.args])
    elif s.op == '&':
        return associate('&', list(map(distribute_and_over_or, s.args)))
    else:
        return s

def is_symbol(s):
    """A string s is a symbol if it starts with an alphabetic char.
    >>> is_symbol('R2D2')
    True
    """
    return isinstance(s, str) and s[:1].isalpha()

def associate(op, args):
    """Given an associative op, return an expression with the same
    meaning as Expr(op, *args), but flattened -- that is, with nested
    instances of the same op promoted to the top level.
    >>> associate('&', [(A&B),(B|C),(B&C)])
    (A & B & (B | C) & B & C)
    >>> associate('|', [A|(B|(C|(A&B)))])
    (A | B | C | (A & B))
    """
    args = dissociate(op, args)
    if len(args) == 0:
        return _op_identity[op]
    elif len(args) == 1:
        return args[0]
    else:
        return Expr(op, *args)

_op_identity = {'&': True, '|': False, '+': 0, '*': 1}

def conjuncts(s):
    """Return a list of the conjuncts in the sentence s.
    >>> conjuncts(A & B)
    [A, B]
    >>> conjuncts(A | B)
    [(A | B)]
    """
    return dissociate('&', [s])

def dissociate(op, args):
    """Given an associative op, return a flattened list result such
    that Expr(op, *result) means the same as Expr(op, *args).
    >>> dissociate('&', [A & B])
    [A, B]
    """
    result = []

    def collect(subargs):
        for arg in subargs:
            if arg.op == op:
                collect(arg.args)
            else:
                result.append(arg)

    collect(args)
    return result