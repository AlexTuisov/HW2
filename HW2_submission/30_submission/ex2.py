from pysat.solvers import Solver, Glucose3
from sympy.logic.boolalg import to_cnf
from pysat.card import *
import itertools

ids = ['318539103', '302816863']
# state_list = ['S0', 'S1', 'S2', 'H', 'U', 'Q0', 'Q1', 'I', 'S','D','P']
state_list = ['S', 'H','U','I','Q','Q0','Q1','S0','S1','S2','D','P']
dict_full={}

def solve_problem(input):
    solver = Glucose3()
    cnf_ac=CNF()
    #this function create a map with all indexes and all states
    #and the usage is: map(turn,index x, index y,state)
    state_map,I,J,K=create_map(input,solver)
    # cnf = CardEnc.equals(lits=list(state_dict[i][j][k].values()), encoding=EncType.pairwise)
    # print(cnf.clauses)
    #cnf = make_clauses(state_map, solver, I, J, K)
    #decode(cnf, state_map, I, J, K, solver, cnf_ac)
    make_basic_iteration_rules(state_map, I, J, K, solver)
    #add observations
    observation(input['observations'],state_map,solver,I,J,K)
    #add basic rules
    #add equals
    out={}

    for query in input['queries'][0]:
        solver.append_formula(cnf_ac.clauses)
        #police_num = input['police']
        #medics_num = input['medics']
        ind = state_map[query[0][0]][query[0][1]][query[1]][query[2]][0]
        solutionH = solver.solve(assumptions=[ind])
        # print('SOLLUTION ',query[2],' IS ')
        # print(solutionH)
        # print(solver.get_core())
        #print('SOLLUTION ~', query[2], ' IS ')
        solutionS = solver.solve(assumptions=[-ind])
        if solver.get_model() != None:
            ans = list(solver.get_model())
            ans2 = [x for x in ans if x > 0]
            ans3 = [dict_full[x] for x in ans2]
            #print(ans3)
        # print(solutionS)
        # print(solver.get_core())
        if solutionH == True and solutionS == False:
            out[query] = 'T'
        elif solutionH == False and solutionS == True:
            out[query] = 'F'
        else:
            out[query] = '?'
    return out


def create_map(input,solver):
    #print("Im in create_map")
    index=1
    state_dict={}
    I=len(input['observations'][0])
    J=I
    K=len(input['observations'])
    for i in range(I):
        tempj = {}
        for j in range(J):
            tempk = {}
            for k in range(K):
                tempS = {}
                for s in state_list:
                    key = s
                    tup = (index,s+str(i)+str(j)+str(k))
                    dict_full[index] = s + str(i) + str(j) + str(k)
                    tempS[key] = tup
                    index = index+1
                tempk[k] = tempS
                tempS2 = dict(itertools.islice(tempS.items(), 3))
                list_for_eq = list(tempS2.values())
                cnf_equals = CardEnc.equals(lits=[x[0] for x in list_for_eq], bound=1, encoding=EncType.pairwise)
                for ind, c in enumerate(cnf_equals):
                    solver.add_clause(c)
            tempj[j] = tempk
        state_dict[i] = tempj
    return state_dict,I,J,K


def decode(cnf,map,I,J,K,solver,cnf_ac):
    exp = cnf.split('&')
    y = exp
    for clause in y:
        clause_out=[]
        clause = clause.replace(')', '')
        clause = clause.replace('(', '')
        clause = clause.replace(' ', '')
        clause = clause.split('|')
        clause_out = []
        for cl in clause:

            if(len(cl))==0:
                break
            if cl[0]=='~':
                clause_out.append(-search_in_map(map,cl[1:],I,J,K))

            else:
                clause_out.append(search_in_map(map,cl,I,J,K))
        if clause_out!=[]:
            cnf_ac.append(clause_out)


def observation(observations, state_map, solver, I, J, K):
    cnf=''
    for k in range(K):
        for i in range(I):
            for j in range(J):
                value = observations[k][i][j]
                if value =='H':
                    solver.add_clause([state_map[i][j][k]['H'][0]])
                    # cnf += '&' + str(state_map[i][j][k]['H'][0])
                if value == 'S':
                    # if k == 0:
                    #     solver.add_clause([state_map[i][j][k]['S2'][0]])
                    # if k == 1:
                    #     if observations[k-1][i][j]=='S':
                    #         solver.add_clause([state_map[i][j][k]['S1'][0]])
                    #     else:
                    #         solver.add_clause([state_map[i][j][k]['S2'][0]])
                    # if k >= 2:
                    #     if observations[k-1][i][j] == 'S':
                    #         if observations[k-2][i][j] == 'S':
                    #             solver.add_clause([state_map[i][j][k]['S0'][0]])
                    #         else:
                    #             solver.add_clause([state_map[i][j][k]['S1'][0]])
                    #     else:
                    #         solver.add_clause([state_map[i][j][k]['S2'][0]])
                    solver.add_clause([state_map[i][j][k]['S'][0]])
                if value =='Q':
                     solver.add_clause([state_map[i][j][k][f"Q{q_num}"][0] for q_num in range(2)])
                if value =='I':
                     solver.add_clause([state_map[i][j][k]['I'][0]])
                if value == 'U':
                     solver.add_clause([state_map[i][j][k]['U'][0]])


def find_all_neighbors(index, I, J):
    neighbors = []
    index_x = index[0]
    index_y = index[1]
    if index_x > 0:
        neighbors.append((index_x-1, index_y))
    if index_x < I-1:
        neighbors.append((index_x+1, index_y))
    if index_y > 0:
        neighbors.append((index_x, index_y-1))
    if index_y < J-1:
        neighbors.append((index_x, index_y+1))
    return neighbors


def search_in_map(map,str,I,J,K):
    for k in range(K):
        for i in range(I):
            for j in range(J):
                for s in state_list:
                    if map[i][j][k][s][1] == str:
                        return map[i][j][k][s][0]

                    # D--> im sick and no q next turn
                    # P-->one of my neighbours is D
                    # St&~Qa>>D
                    # P<<Dl|Dr


def make_basic_iteration_rules(state_map, I, J, K, solver):
    for k in range(K):
        if k == K-1:
            continue
        for i in range(I):
            for j in range(J):
                if k == 0:
                     first_s = ['S1','S0','I','Q0','Q1']
                     for s in first_s:
                         solver.add_clause([-state_map[i][j][k][s][0]])
                solver.add_clause([-state_map[i][j][k]['S0'][0], state_map[i][j][k+1]['H'][0]])
                # Q2t+1 --> S0t or S1t or S2t

                solver.add_clause([-state_map[i][j][k]['S1'][0], state_map[i][j][k + 1]['S0'][0]])
                solver.add_clause([-state_map[i][j][k]['S2'][0], state_map[i][j][k + 1]['S1'][0]])
                solver.add_clause([-state_map[i][j][k]['Q0'][0], state_map[i][j][k + 1]['H'][0]])
                solver.add_clause([-state_map[i][j][k]['Q1'][0], state_map[i][j][k + 1]['Q0'][0]])
                solver.add_clause([-state_map[i][j][k]['U'][0], state_map[i][j][k + 1]['U'][0]])
                solver.add_clause([-state_map[i][j][k]['I'][0], state_map[i][j][k + 1]['I'][0]])

                # ### S -> S1 or S-> S2 or S->S0   --> ~S

                solver.add_clause([-state_map[i][j][k]['S'][0], state_map[i][j][k]["S0"][0], state_map[i][j][k]["S1"][0], state_map[i][j][k]["S2"][0]])
                solver.add_clause([state_map[i][j][k]['S'][0],-state_map[i][j][k]["S0"][0]])
                solver.add_clause([state_map[i][j][k]['S'][0], -state_map[i][j][k]["S1"][0]])
                solver.add_clause([state_map[i][j][k]['S'][0], -state_map[i][j][k]["S2"][0]])

                # ## D RULES ### D->S&~Q  ~D|(S&~Q) ====> ~D|S & ~D|~Q second rule:  S&~Q-->D ==> ~S|Q|D
                d_to_s = [[-state_map[i][j][k]['D'][0], state_map[i][j][k]['S'][0]], [-state_map[i][j][k]['D'][0], -state_map[i][j][k + 1]['Q1'][0]]]
                d_to_s_cont = [[-state_map[i][j][k]['S'][0],state_map[i][j][k]['D'][0],state_map[i][j][k + 1]['Q1'][0], state_map[i][j][k]['D'][0]]]
                d_to_s += d_to_s_cont
                for clause in d_to_s:
                     solver.add_clause(clause)

                # ### P RULES ###    P -> one of my neighbors is D    P-> Dl | Dr
                neighbors = find_all_neighbors((i, j), I, J)
                n = []
                for neighbor in neighbors:
                    n.append(state_map[neighbor[0]][neighbor[1]][k]['D'][0])
                n.insert(0, -state_map[i][j][k]['P'][0])
                n = [n]
                cont_p_clauses = [[state_map[i][j][k]['P'][0],-state_map[neighbor[0]][neighbor[1]][k]['D'][0]] for neighbor in neighbors]
                n += cont_p_clauses
                for clause in n:
                    solver.add_clause(clause)
                solver.add_clause([-state_map[i][j][k]['H'][0], state_map[i][j][k]['P'][0], state_map[i][j][k+1]['H'][0]])

                # Ht & sick neighbor --> (S2t+1 | It+1) or (Q2 & Ht+1)
                solver.add_clause([-state_map[i][j][k]['H'][0], -state_map[i][j][k]['P'][0], state_map[i][j][k+1]['S2'][0]])

                # Ht & no sick neighbor --> (Ht+1 or It+1)
                solver.add_clause([-state_map[i][j][k]['H'][0], state_map[i][j][k]['P'][0], state_map[i][j][k + 1]['H'][0]])

# Ht+1 ->(no sick neighbors & Ht) or S0t or Q0t => (~Ht+1 or no sick neighbor or S0t or Q0t)&(~Ht+1 or Ht or S0t or Q0t)
                solver.add_clause([-state_map[i][j][k+1]['H'][0],-state_map[i][j][k]['P'][0], state_map[i][j][k]['S0'][0],state_map[i][j][k]['Q0'][0]])
                solver.add_clause([-state_map[i][j][k + 1]['H'][0], state_map[i][j][k]['H'][0], state_map[i][j][k]['S0'][0],state_map[i][j][k]['Q0'][0]])
                solver.add_clause([-state_map[i][j][k]['H'][0], -state_map[i][j][k+1]['U'][0]])
                solver.add_clause([-state_map[i][j][k]['S'][0], -state_map[i][j][k+1]['U'][0]])
                solver.add_clause([-state_map[i][j][k]['Q1'][0], -state_map[i][j][k+1]['U'][0]])
                solver.add_clause([-state_map[i][j][k]['Q0'][0], -state_map[i][j][k+1]['U'][0]])
                solver.add_clause([-state_map[i][j][k]['I'][0], -state_map[i][j][k + 1]['U'][0]])
                solver.add_clause([-state_map[i][j][k]['S1'][0], -state_map[i][j][k + 1]['H'][0]])
                solver.add_clause([-state_map[i][j][k]['S2'][0], -state_map[i][j][k + 1]['H'][0]])
