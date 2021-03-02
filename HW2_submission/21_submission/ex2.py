from pysat.formula import CNF
from pysat.formula import IDPool
from itertools import combinations, combinations_with_replacement, permutations
from itertools import product
import numpy as np
from pysat.solvers import Glucose3, Minisat22
import re
from pysat.card import *
#### INIT ####
vpool = IDPool(start_from=1)
literals = lambda state, t, i, j: vpool.id('{0}@{1}@({2},{3})'.format(state, t ,i, j))


class Problem:
    def __init__(self, problem):
        self.medics = problem['medics']
        self.police = problem['police']
        self.observations = problem['observations']
        self.rows = len(self.observations[0])
        self.cols = len(self.observations[0][0])
        self.times = len(self.observations)
        self.states = ["U", "H", "S"]
        if self.medics:
            self.states.append("I")
        if self.police:
            self.states.append("Q")
        self.queries = problem['queries']
        self.KB = CNF()
        
    def oprint(self):
        for b in (self.observations):
            for l in b:
                print(l)
            print('')
######################################### Utils ##################################################################
def prity_clauses(clauses):
    for cla in clauses:
        print([('- ' if k < 0 else '') + vpool.obj(abs(k)) for k in cla])
        
def extract_literal_from_model(lit, model):
    if lit in model:
        print(lit)
    elif -lit in model:
        print(-lit)
    else:
        assert 0
        
def extract_id(literal):
    cells = vpool.obj(literal).split('@')
    state = cells[0]
    time = cells[1]
    tmp = re.findall(r'\d+', cells[2])
    row = tmp[0]
    col = tmp[1]
    return state, int(time), int(row), int(col)

def draw_sol_from_model(model):
    builder = np.asarray(P.observations)
    board=np.zeros_like(builder, dtype=str)
    for lit in model:
        state, time, row, col = extract_id(abs(lit))
        valid = lit > 0 and row != 999 and state in P.states
        if valid:
            #print(vpool.obj(lit))
            #print(time, row, col)
            #print(board[time][row][col])
            assert board[time][row][col] == ''
            board[time][row][col] = state
    print(board)
def draw_sol_from_clauses(clauses):
    model = [cla[0] for cla in clauses]
    draw_sol_from_model(model)
    
def find_neighbors (state_i, state_j):
    #return all neigbours even if they out of grid - init_padding_litirals() will defined them
    diretions = [(0,1), (0,-1), (1,0), (-1,0)]
    neighbors = []
    for dir in diretions:
        neighbor = (state_i + dir[0], state_j + dir[1])
        neighbors.append(neighbor)
    return(neighbors)

def call_function(func, arg_type='all'):
    #print(func.__name__, "run type: ", arg_type)
    for t in range(P.times -1):
        if arg_type == 'all':
            for i in range(P.rows):
                for j in range(P.cols):
                    func(t, i, j)
        elif arg_type == 't_only':
            func(t)
def parse_querie(q):
    return q[2], q[1], q[0][0], q[0][1]
######################################### Functions ##################################################################
def add_initial_state_to_KB(true_state, t, i, j):
    '''set state to ture and other states of same cell to false'''
    for state in P.states:
        if state == true_state:
            P.KB.append([literals(state, t, i, j)])
        else:
            P.KB.append([-literals(state, t, i, j)])
            
def add_qureire_to_solver(true_state, t, i, j, solver):
    '''set state to ture and other states of same cell to false'''
    for state in P.states:
        if state == true_state:
            solver.add_clause([literals(state, t, i, j)])
        else:
            solver.add_clause([-literals(state, t, i, j)])
            
def init_padding_litirals():
    '''padding the grid with literals that are not belogns to states to handle edge issues'''
    for t in range(P.times):
        for i in range(P.rows):
            add_initial_state_to_KB('neg_only', t, i, -1)
            add_initial_state_to_KB('neg_only', t, i, P.cols)
        for j in range(P.cols):
            add_initial_state_to_KB('neg_only', t, -1, j)
            add_initial_state_to_KB('neg_only', t, P.rows, j)
                
def infected_pre_cond(t, i, j):
    '''infected implies pre cond - cell H and at least one neighbor is sick'''
    assert t != P.times
    # infect_t-> H_t
    P.KB.append([-literals('infect', t, i, j), literals('H', t, i, j)]) 
    #infect_t -> (s1|s2|s3|s4)
    n_formula = [literals('S', t, n_i, n_j) for n_i, n_j in find_neighbors(i, j)] 
    n_formula.append(-literals('infect', t, i, j))
    P.KB.append(n_formula)


def infected_affect(t, i, j):
    '''infected affects: H0 -> S1'''
    assert t != P.times
    #add affect is S(t+1)
    P.KB.append([-literals('infect', t, i, j), literals('S', t +1, i, j)])
    #delete affect is 
    P.KB.append([-literals('infect', t, i, j), -literals('U', t +1, i, j)])
    P.KB.append([-literals('infect', t, i, j), -literals('H', t +1, i, j)])
    if P.medics:
        P.KB.append([-literals('infect', t, i, j), -literals('I', t +1, i, j)])
    if P.police:
        P.KB.append([-literals('infect', t, i, j), -literals('Q', t +1, i, j)])
        
def healing_strict_pre_cond(t, i, j):
    '''
    healing implies its pre cond - St and St-1 and St-2.
    note! this is "strict" pre cond as if we can heal we must heal 
    meaning also pre cond implies healing'''
    assert t != P.times
    if t < 2: # to soon to heal
        P.KB.append([-literals('heal', t, i, j)])
        return
    pre_imp_heal = []
    #(s-2 | ~heal) & (s-1 | ~heal) & (s0 | ~heal)
    for tt in range(t-2, t+1):
        P.KB.append([literals('S', tt, i, j), -literals('heal', t, i, j)])
        pre_imp_heal.append(-literals('S', tt, i, j))
    # if pre cond exist we must heal
    # (heal | ~s-2 | ~s-1 | ~s0)
    pre_imp_heal.append(literals('heal', t, i, j))
    P.KB.append(pre_imp_heal)
    
def healing_affect(t, i, j):
    '''healing affects'''
    assert t != P.times
    #add affect is H(t+1)
    P.KB.append([-literals('heal', t, i, j), literals('H', t +1, i, j)])
    #delete affect is 
    P.KB.append([-literals('heal', t, i, j), -literals('U', t +1, i, j)])
    P.KB.append([-literals('heal', t, i, j), -literals('S', t +1, i, j)])
    if P.medics:
        P.KB.append([-literals('heal', t, i, j), -literals('I', t +1, i, j)])
    if P.police:
        P.KB.append([-literals('heal', t, i, j), -literals('Q', t +1, i, j)])
        
def vaccinate_pre_cond(t, i, j):
    '''vaccinate implies its pre cond - cell is H'''
    assert t != P.times
    if not P.medics:
        return
    P.KB.append([-literals('vaccinate', t, i, j), literals('H', t, i, j)])

def vaccinate_affect(t, i, j):
    '''vaccinate affects'''
    assert t != P.times
    if not P.medics:
        return
    #add affect is I(t+1)
    P.KB.append([-literals('vaccinate', t, i, j), literals('I', t +1, i, j)])
    #delete affect is 
    P.KB.append([-literals('vaccinate', t, i, j), -literals('U', t +1, i, j)])
    P.KB.append([-literals('vaccinate', t, i, j), -literals('S', t +1, i, j)])
    P.KB.append([-literals('vaccinate', t, i, j), -literals('H', t +1, i, j)])
    if P.police:
        P.KB.append([-literals('vaccinate', t, i, j), -literals('Q', t +1, i, j)])
        
def vaccinate_limit(t):
    '''limit the number of vaccinate to medics teams'''
    assert t != P.times
    if not P.medics:
        return
    # we can only vaccinate at most medics(int) celss
    all_possible_vaccinate_actions = [literals('vaccinate', t, i, j) for i in range(P.rows) for j in range(P.cols)]
    P.KB.extend(CardEnc.atmost(lits=all_possible_vaccinate_actions, bound=P.medics, encoding=EncType.pairwise))
    
def quarantie_pre_cond(t, i, j):
    '''quarantie implies its pre cond - cell is S (S0 | ~qur) '''
    assert t != P.times
    if not P.police:
        return
    P.KB.append([-literals('quarantie', t, i, j), literals('S', t, i, j)])
    
def quarantie_affect(t, i, j):
    '''quarantie affects'''
    assert t != P.times
    if not P.police:
        return
    #add affect is Q(t+1)
    P.KB.append([-literals('quarantie', t, i, j), literals('Q', t +1, i, j)])
    #delete affect is 
    P.KB.append([-literals('quarantie', t, i, j), -literals('U', t +1, i, j)])
    P.KB.append([-literals('quarantie', t, i, j), -literals('S', t +1, i, j)])
    P.KB.append([-literals('quarantie', t, i, j), -literals('H', t +1, i, j)])
    if P.medics:
        P.KB.append([-literals('quarantie', t, i, j), -literals('I', t +1, i, j)])
        
def quarantie_limit(t):
    '''limit the number of quarantie to police teams'''
    assert t != P.times
    if not P.police:
        return
    # we can only quarantie at most police(int) cells
    all_possible_quarantie_actions = [literals('quarantie', t, i, j) for i in range(P.rows) for j in range(P.cols)]
    P.KB.extend(CardEnc.atmost(lits=all_possible_quarantie_actions, bound=P.police, encoding=EncType.pairwise))

def freedom_strict_pre_cond(t, i, j):
    '''
    freedom(getting out of quarantie) implies its pre cond - Qt and Qt-1.
    note! this is "strict" pre cond as if we can getting out of quarantie  we must out of quarantie
    meaning also pre cond implies freedom'''
    assert t != P.times
    if not P.police:
        return
    if t < 1: # to soon to freedom
        P.KB.append([-literals('free', t, i, j)])
        return
    pre_imp_free = []
   #(s-1 | ~free & (s0 | ~free)
    for tt in range(t-1, t+1):
        P.KB.append([literals('Q', tt, i, j), -literals('free', t, i, j)])
        pre_imp_free.append(-literals('Q', tt, i, j))
    # if pre cond exist we must heal
    # (free | ~s-1 | ~s0)
    pre_imp_free.append(literals('free', t, i, j))
    P.KB.append(pre_imp_free)

def freedom_affect(t, i, j):
    '''freedom affects'''
    assert t != P.times
    if not P.police:
        return
    #add affect is H(t+1)
    P.KB.append([-literals('free', t, i, j), literals('H', t +1, i, j)])
    #delete affect is 
    P.KB.append([-literals('free', t, i, j), -literals('U', t +1, i, j)])
    P.KB.append([-literals('free', t, i, j), -literals('S', t +1, i, j)])
    P.KB.append([-literals('free', t, i, j), -literals('Q', t +1, i, j)])
    if P.medics:
        P.KB.append([-literals('free', t, i, j), -literals('I', t +1, i, j)])

def handle_actions_priorities(t, i, j):
    ''' 
    H cell with sick neighbors must be infected unless his vaccinated
    without medics:
    (infect | ~h0 | ~n_s_left) & (infect | ~h0 | ~n_s_right) & (infect | ~h0 | ~n_s_up) & (infect | ~h0 | ~n_s_down)
    with medics:
    (infect |vaccinate| ~h0 | ~n_s_left) & (infect|vaccinate| ~h0 | ~n_s_right) &'''
    assert t != P.times
    for n_i, n_j in find_neighbors(i, j):   
        cond = [literals('infect', t, i, j), -literals('H', t, i, j), -literals('S', t, n_i, n_j)]
        if P.medics:
            cond.append(literals('vaccinate', t, i, j))
        P.KB.append(cond)
    '''S cell can be qurdenate unless is healing (~heal | ~qur)'''  
    if P.police:
        P.KB.append([-literals('quarantie', t, i, j), -literals('heal', t, i, j)])
        
def no_action(t, i, j):
    '''
    if no actions is taken than state(t) == state(t+1)
    here we generate the no_action literal: if no action is taken no_actions is true else no_actions is false
    '''
    assert t != P.times
    #(~infect | ~noA) & (~heal | ~noA) & (infect | heal | noA) - consider if t<2 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    P.KB.append([-literals('infect', t, i, j) , -literals('no_action', t, i, j)])
    P.KB.append([-literals('heal', t, i, j) , -literals('no_action', t, i, j)])
    or_cond = [ literals('heal', t, i, j) , literals('infect', t, i, j), literals('no_action', t, i, j)]
    if P.medics:
        P.KB.append([-literals('vaccinate', t, i, j) , -literals('no_action', t, i, j)])
        or_cond.append(literals('vaccinate', t, i, j))
    if P.police:
        P.KB.append([-literals('quarantie', t, i, j) , -literals('no_action', t, i, j)])
        or_cond.append(literals('quarantie', t, i, j))
        P.KB.append([-literals('free', t, i, j) , -literals('no_action', t, i, j)])
        or_cond.append(literals('free', t, i, j))
    P.KB.append(or_cond)

def no_action_positive_frame(t, i, j):
    '''no actions take state(t)==state(t+1)'''
    assert t != P.times
    for state in P.states:
        P.KB.append([-literals('no_action', t, i, j), -literals(state, t, i, j), literals(state, t +1, i, j)])
                
def no_action_negative_frame(t, i, j):
    '''no actions take state(t)==state(t+1)'''
    assert t != P.times
    for state in P.states:
        P.KB.append([-literals('no_action', t, i, j), literals(state, t, i, j), -literals(state, t +1, i, j)])
        
######################################### Main ######################################################################
ids = ['301412110']

def solve_problem(input):
    global P
    P = Problem(input)
    #P.oprint()
    ### initial state clauses ###
    for t in range(P.times):
        for i in range(P.rows):
            for j in range(P.cols):
                if P.observations[t][i][j] != '?':
                    state = P.observations[t][i][j]
                    add_initial_state_to_KB(state, t, i, j)

    init_padding_litirals()
    
    # infaction spread
    call_function(infected_pre_cond)
    call_function(infected_affect)

    # healing from sickness
    call_function(healing_strict_pre_cond)
    call_function(healing_affect)

    #make vacsine
    call_function(vaccinate_pre_cond)
    call_function(vaccinate_affect)
    call_function(vaccinate_limit, 't_only')
    
    # make quarantie
    call_function(quarantie_pre_cond)
    call_function(quarantie_affect)
    call_function(quarantie_limit, 't_only')
    
    #getting out of quarantie
    call_function(freedom_strict_pre_cond)
    call_function(freedom_affect)
    
    # handle conflicts of pre cond
    call_function(handle_actions_priorities)

    # if cell(t) is not healing and not infectead and not quarantie it remain the same
    call_function(no_action)
    call_function(no_action_positive_frame)
    call_function(no_action_negative_frame)
    
    ret_dic = dict()
    for queire in P.queries:
        states_status = []
        q_state, t, i, j = parse_querie(queire)
        states = [state for state in P.states if state != q_state ]
        states.insert(0, q_state)
        for state in states:
            # lets solve!
            g = Glucose3()
            g.append_formula(P.KB.clauses)
            add_qureire_to_solver(state, t, i, j, g)    
            solve = g.solve()
            #print("qur: ", queire)
            #print(state, t, i, j)
            #print(solve)
            #if solve : 
            #    model = g.get_model()
            #    print(model)
            #    prity_clauses([model])
            #    print("sol: ")
            #    draw_sol_from_model(model)
            states_status.append(solve)
            g.delete()
            if not solve and state == q_state:
                ret_dic[queire] = 'F'
                break
        if len(states_status) > 1:
            ret_dic[queire] = '?'  if any(states_status[1:]) else 'T'
    return ret_dic