from pysat.solvers import Solver
from itertools import combinations, product

ids = ['313136491', '205684269']

def solve_problem(input):
    map_vars, clauses = observations(input)
    queries = {}
    for q in input['queries']:
        if q in map_vars.keys():
            index = map_vars[q]
            temp_clauses = clauses + [[-index]]
            s = Solver(name='g4', bootstrap_with=temp_clauses)
            KBnega = s.solve()
            temp_clauses = clauses + [[index]]
            s = Solver(name='g4', bootstrap_with=temp_clauses)
            KBposa = s.solve()
            if (KBnega) and (KBposa):
                queries[q] = '?'
            elif not KBnega and KBposa:
                queries[q]='T'
            else:
                queries[q]='F'
        else :
            queries[q]='F'
    return queries    # put your solution here, remember the format needed


def observations (problem):
    tile_letters = ['H','S','U']
    operations = ['infectH', 'noopH','noopS','noopU']
    rows = len(problem['observations'][0])
    columns = len(problem['observations'][0][0])
    observations = problem['observations']
    turns = len(observations)
    map_states = {}
    map_actions = {}
    # reverse_map_vars={}
    clauses = []
    index=1
    police = problem['police']
    medics = problem['medics']
    m_operations = []
    p_operations = []
    if police and medics:
        final_achivements = add_achivements_final_turn_allteams
        create_action = create_action_caluses_allteams
        if police==1:
            quarantine_in_t = {'quarantine1':[]}
        else:
            p_operations = ['quarantine'+str(k) for k in range (1,police+1)]
            quarantine_in_t={x:[] for x in p_operations}
        if medics==1:
            vaccinate_in_t = {'vaccinate1':[]}
        else:
            m_operations = ['vaccinate'+str(l) for l in range (1,medics+1)]
            vaccinate_in_t = {x:[] for x in m_operations}
        operations+= []
    elif police:
        final_achivements = add_achivements_final_turn_police
        create_action = create_action_caluses_only_police
        if police==1:
            quarantine_in_t = {'quarantine1':[]}
        else:
            p_operations = ['quarantine'+str(k) for k in range (1,police+1)]
            quarantine_in_t={x:[] for x in p_operations}
    elif medics:
        final_achivements = add_achivements_final_turn_medics
        create_action = create_action_caluses_only_medic
        if medics==1:
            vaccinate_in_t = {'vaccinate1':[]}
        else:
            m_operations = ['vaccinate'+str(l) for l in range (1,medics+1)]
            vaccinate_in_t = {x:[] for x in m_operations}
    else:
        create_action = create_action_caluses_no_teams
        final_achivements = add_achivements_final_turn_noteams
    for t in range(turns):
        for i in range(rows):
            for j in range(columns):
                true_letter = observations[t][i][j]
                temp=[]
                if t<turns-1:  ## אפשר לוותר על זה ופשוט להריץ את הלולאה פעם אחת פחות
                    for op in operations:
                        cur = ((i,j), t, op)
                        map_actions[cur] = index
                        # reverse_map_vars[index] = cur
                        temp+=[index]
                        index += 1
                    quarantine_in_cell = []
                    vaccinate_in_cell = []
                    for p_op in p_operations:
                        cur = ((i,j), t, p_op)
                        map_actions[cur] = index
                        # reverse_map_vars[index] = cur
                        # temp+=[index]
                        quarantine_in_t[p_op] += [index]
                        quarantine_in_cell += [index]
                        index += 1
                    for m_op in m_operations:
                        cur = ((i,j), t, m_op)
                        map_actions[cur] = index
                        # reverse_map_vars[index] = cur
                        # temp+=[index]
                        vaccinate_in_t[m_op] += [index]
                        vaccinate_in_cell += [index]
                        index += 1
                    if police:
                        cur = ((i,j), t, 'quarantine')
                        map_actions[cur] = index
                        # reverse_map_vars[index] = cur
                        if police==1:
                            quarantine_in_t['quarantine1'] += [index]
                        else:
                            clauses+=atmost_k0(quarantine_in_cell,1)
                            clauses +=[[index]+[-i] for i in quarantine_in_cell]
                            clauses += [[-index]+[i for i in quarantine_in_cell]]
                        temp+=[index]
                        index += 1
                    if medics:
                        cur = ((i,j), t, 'vaccinate')
                        map_actions[cur] = index
                        # reverse_map_vars[index] = cur
                        if medics == 1:
                            vaccinate_in_t['vaccinate1'] += [index]
                        else:
                            clauses+=atmost_k0(vaccinate_in_cell,1)
                            clauses += [[index]+[-i] for i in vaccinate_in_cell]
                            clauses += [[-index]+[i for i in vaccinate_in_cell]]
                        temp+=[index]
                        index += 1
                    clauses+=(exactly_one_clauses(temp))
                temp=[]
                for letter in tile_letters:
                    cur = ((i, j), t, letter)
                    map_states[cur] = index
                    # reverse_map_vars[index] = cur  # מיותר
                    temp += [index]
                    index+=1
                    if t>=1:
                        clauses+= create_action(((i,j),t-1,letter),map_states,map_actions, rows,columns,q_ops,v_ops)
                if true_letter!='?':
                    cur = ((i, j), t, true_letter)
                    clauses.append([map_states[cur]])
                clauses+=(exactly_one_clauses(temp))
        if t==1:
            operations += ['StoH']
            if police:
                operations += ['QtoH']
        if t==0:
            if police:
                tile_letters+=['Q']
                operations += ['noopQ']
            if medics:
                tile_letters+=['I']
                operations += ['noopI']
        if t<turns-1:
            q_ops = []
            v_ops = []
            for k in range (1,police+1):
                cur = ('q'+str(k),t)
                map_actions[cur]=index
                # reverse_map_vars[index] = cur
                q_ops+=[index]
                clauses += atmost_k0(quarantine_in_t['quarantine'+str(k)],1)
                clauses +=[[index]+[-i] for i in quarantine_in_t['quarantine'+str(k)]]
                clauses += [[-index]+[i for i in quarantine_in_t['quarantine'+str(k)]]]
                index +=1
            for l in range (1,medics+1):
                cur = ('v'+str(l),t)
                map_actions[cur]=index
                # reverse_map_vars[index] = cur
                v_ops  += [index]
                clauses += atmost_k0(vaccinate_in_t['vaccinate'+str(l)],1)
                clauses +=[[index]+[-i] for i in vaccinate_in_t['vaccinate'+str(l)]]
                clauses += [[-index]+[i for i in vaccinate_in_t['vaccinate'+str(l)]]]
                index +=1
            if police>1:
                clauses += [[q_ops[g],-q_ops[g+1]] for g in range (police-1)]
                quarantine_in_t={x:[] for x in p_operations} ## איפוס
            elif police==1:
                quarantine_in_t = {'quarantine1':[]}
            if medics>1:
                clauses += [[v_ops[g],-v_ops[g+1]] for g in range (medics-1)]
                vaccinate_in_t = {x:[] for x in m_operations}
            elif medics==1:
                vaccinate_in_t = {'vaccinate1':[]}

    for i in range(rows):
        for j in range(columns):
            for letter in tile_letters:
                clauses+= final_achivements(((i,j),turns-1,letter),map_states,map_actions)
    # return map_vars,reverse_map_vars,clauses
    return map_states,clauses

def create_action_caluses_only_police(cur_cell_state,map_states,map_actions, rows,columns,q_ops,v_ops):
    clauses = []
    row = cur_cell_state[0][0]
    col = cur_cell_state[0][1]
    t = cur_cell_state[1]
    letter = cur_cell_state[2]
    if letter=='H':
        if t>2:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'StoH']] + [map_actions[(row,col),t-1,'noopH']]+[map_actions[(row,col),t-1,'QtoH']]] #achivements
        elif t>=1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopH']]]  #achivements
        sick_neighbors_pre_infect= []
        sick_neighbors_pre_noop = []
        if row-1>=0:
            sick_neighbors_pre_infect+=[[map_states[(row-1,col),t,'S'],-map_actions[((row-1,col),t,'quarantine')]]]
            sick_neighbors_pre_noop = [[-map_states[(row-1,col),t,'S'],map_actions[((row-1,col),t,'quarantine')]]]
        if row+1<rows:
            sick_neighbors_pre_infect+=[[map_states[(row+1,col),t,'S'],-map_actions[((row+1,col),t,'quarantine')]]]
            sick_neighbors_pre_noop += [[-map_states[(row+1,col),t,'S'],map_actions[((row+1,col),t,'quarantine')]]]
        if col-1>=0:
            sick_neighbors_pre_infect+=[[map_states[(row,col-1),t,'S'],-map_actions[((row,col-1),t,'quarantine')]]]
            sick_neighbors_pre_noop += [[-map_states[(row,col-1),t,'S'],map_actions[((row,col-1),t,'quarantine')]]]
        if col+1<columns:
            sick_neighbors_pre_infect+=[[map_states[(row,col+1),t,'S'],-map_actions[((row,col+1),t,'quarantine')]]]
            sick_neighbors_pre_noop += [[-map_states[(row,col+1),t,'S'],map_actions[((row,col+1),t,'quarantine')]]]
        if sick_neighbors_pre_infect:
            clauses+=infect_precondition(map_actions[((row,col),t,'infectH')],sick_neighbors_pre_infect)
            noop_pre = [[map_states[((row,col),t,'H')]]] +sick_neighbors_pre_noop
            clauses+= pre_clauses(map_actions[((row,col),t,'infectH')], [[map_states[((row,col),t,'H')]]])
        else:
            infect_pre =[[map_states[((row,col),t,'H')]]]+[sick_neighbors_pre_infect]
            clauses+=pre_clauses(map_actions[((row,col),t,'infectH')], infect_pre)
            noop_pre = [[map_states[((row,col),t,'H')]]]
        clauses+=pre_clauses(map_actions[((row,col),t,'noopH')], noop_pre)
        return clauses
    elif letter=='S':
        if t>=1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'infectH']] + [map_actions[(row,col),t-1,'noopS']]]#achivements
        if t>=2:
            noop_pre = [[map_states[((row,col),t,'S')]]]+ [[-map_states[((row,col),t-1,'S')],-map_states[((row,col),t-2,'S')]]]+[[x] for x in q_ops]
            stoh_pre = [[map_states[((row,col),t,'S')]],[map_states[((row,col),t-1,'S')]],[map_states[((row,col),t-2,'S')]]]
            clauses+=pre_clauses(map_actions[((row,col),t,'noopS')], noop_pre)
            clauses+=pre_clauses(map_actions[((row,col),t,'StoH')], stoh_pre)
            # clauses+= [[-map_vars[((row,col),t,'noopS')],-map_vars[((row,col),t,'StoH')]]] #inteference
        else:
            noop_pre = [[map_states[((row,col),t,'S')]]] +[[x] for x in q_ops]
            clauses += pre_clauses(map_actions[((row,col),t,'noopS')], noop_pre)
        quarantine_pre = [[map_states[((row,col),t,'S')]]]
        clauses += pre_clauses(map_actions[((row,col),t,'quarantine')], quarantine_pre)
        return clauses
    elif letter=='Q':
        if t==0:
            return []
        if t>1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopQ']] + [map_actions[(row,col),t-1,'quarantine']]] #achivements
        elif t==1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'quarantine']]]  #achivements
        if t>=2:
            noop_pre = [[map_states[((row,col),t,'Q')]],[-map_states[((row,col),t-1,'Q')]]]
            qtoh_pre = [[map_states[((row,col),t,'Q')]],[map_states[((row,col),t-1,'Q')]]]
            clauses+=pre_clauses(map_actions[((row,col),t,'QtoH')],qtoh_pre)
        else:
            noop_pre =  [[map_states[((row,col),t,'Q')]]]
        clauses+=pre_clauses(map_actions[((row,col),t,'noopQ')],noop_pre)
        return clauses
    else:
        if t>=1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopU']]] #achivements
        noop_pre = [[map_states[((row,col),t,'U')]]]
        clauses += pre_clauses(map_actions[((row,col),t,'noopU')], noop_pre)
        return clauses

def create_action_caluses_only_medic(cur_cell_state,map_states,map_actions, rows,columns,q_ops,v_ops):
    clauses = []
    row = cur_cell_state[0][0]
    col = cur_cell_state[0][1]
    t = cur_cell_state[1]
    letter = cur_cell_state[2]
    if letter=='H':
        if t>2:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'StoH']] + [map_actions[(row,col),t-1,'noopH']]] #achivements
        elif t>=1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopH']]]  #achivements
        sick_neighbors_index = []
        if row-1>=0:
            sick_neighbors_index+=[map_states[(row-1,col),t,'S']]
        if row+1<rows:
            sick_neighbors_index+=[map_states[(row+1,col),t,'S']]
        if col-1>=0:
            sick_neighbors_index+=[map_states[(row,col-1),t,'S']]
        if col+1<columns:
            sick_neighbors_index+=[map_states[(row,col+1),t,'S']]
        if sick_neighbors_index:
            infect_pre =[[map_states[((row,col),t,'H')]]]+[sick_neighbors_index]
            noop_pre = [[map_states[((row,col),t,'H')]]] + [[-x] for x in sick_neighbors_index] + [[x] for x in v_ops]
        else:
            infect_pre =[[map_states[((row,col),t,'H')]]]+[sick_neighbors_index]
            noop_pre = [[map_states[((row,col),t,'H')]]] + [[x] for x in v_ops]
        clauses+=pre_clauses(map_actions[((row,col),t,'infectH')], infect_pre)
        clauses+=pre_clauses(map_actions[((row,col),t,'noopH')], noop_pre)
        vaccinate_pre = [[map_states[((row,col),t,'H')]]]
        clauses += pre_clauses(map_actions[((row,col),t,'vaccinate')], vaccinate_pre)
        return clauses
    elif letter=='S':
        if t>=1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'infectH']] + [map_actions[(row,col),t-1,'noopS']]]#achivements
        if t>=2:
            noop_pre = [[map_states[((row,col),t,'S')]]]+ [[-map_states[((row,col),t-1,'S')],-map_states[((row,col),t-2,'S')]]]
            stoh_pre = [[map_states[((row,col),t,'S')]],[map_states[((row,col),t-1,'S')]],[map_states[((row,col),t-2,'S')]]]
            clauses+=pre_clauses(map_actions[((row,col),t,'noopS')], noop_pre)
            clauses+=pre_clauses(map_actions[((row,col),t,'StoH')], stoh_pre)
            clauses+= [[-map_actions[((row,col),t,'noopS')],-map_actions[((row,col),t,'StoH')]]] #inteference
            return clauses
        else:
            noop_pre = [[map_states[((row,col),t,'S')]]]
            clauses += pre_clauses(map_actions[((row,col),t,'noopS')], noop_pre)
        return clauses
    elif letter =='I':
        if t==0:
            return []
        if t>1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopI']] + [map_actions[(row,col),t-1,'vaccinate']]] #achivements
        elif t==1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'vaccinate']]]  #achivements
        noop_pre = [[map_states[((row,col),t,'I')]]]
        clauses+=pre_clauses(map_actions[((row,col),t,'noopI')],noop_pre)
        return clauses
    else:
        if t>=1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopU']]] #achivements
        noop_pre = [[map_states[((row,col),t,'U')]]]
        clauses += pre_clauses(map_actions[((row,col),t,'noopU')], noop_pre)
        return clauses

def create_action_caluses_allteams(cur_cell_state,map_states,map_actions, rows,columns,q_ops,v_ops):
    clauses = []
    row = cur_cell_state[0][0]
    col = cur_cell_state[0][1]
    t = cur_cell_state[1]
    letter = cur_cell_state[2]
    if letter=='H':
        if t>2:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'StoH']] + [map_actions[(row,col),t-1,'noopH']]+[map_actions[(row,col),t-1,'QtoH']]] #achivements
        elif t>=1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopH']]]  #achivements
        sick_neighbors_pre_infect= []
        sick_neighbors_pre_noop = []
        if row-1>=0:
            sick_neighbors_pre_infect+=[[map_states[(row-1,col),t,'S'],-map_actions[((row-1,col),t,'quarantine')]]]
            sick_neighbors_pre_noop = [[-map_states[(row-1,col),t,'S'],map_actions[((row-1,col),t,'quarantine')]]]
        if row+1<rows:
            sick_neighbors_pre_infect+=[[map_states[(row+1,col),t,'S'],-map_actions[((row+1,col),t,'quarantine')]]]
            sick_neighbors_pre_noop += [[-map_states[(row+1,col),t,'S'],map_actions[((row+1,col),t,'quarantine')]]]
        if col-1>=0:
            sick_neighbors_pre_infect+=[[map_states[(row,col-1),t,'S'],-map_actions[((row,col-1),t,'quarantine')]]]
            sick_neighbors_pre_noop += [[-map_states[(row,col-1),t,'S'],map_actions[((row,col-1),t,'quarantine')]]]
        if col+1<columns:
            sick_neighbors_pre_infect+=[[map_states[(row,col+1),t,'S'],-map_actions[((row,col+1),t,'quarantine')]]]
            sick_neighbors_pre_noop += [[-map_states[(row,col+1),t,'S'],map_actions[((row,col+1),t,'quarantine')]]]
        if sick_neighbors_pre_infect:
            clauses+=infect_precondition(map_actions[((row,col),t,'infectH')],sick_neighbors_pre_infect)
            noop_pre = [[map_states[((row,col),t,'H')]]] +sick_neighbors_pre_noop +  [[x] for x in v_ops]
            clauses+= pre_clauses(map_actions[((row,col),t,'infectH')], [[map_states[((row,col),t,'H')]]])
        else:
            infect_pre =[[map_states[((row,col),t,'H')]]]+[sick_neighbors_pre_infect]
            clauses+=pre_clauses(map_actions[((row,col),t,'infectH')], infect_pre)
            noop_pre = [[map_states[((row,col),t,'H')]]] + [[x] for x in v_ops]
        clauses+=pre_clauses(map_actions[((row,col),t,'noopH')], noop_pre)
        vaccinate_pre = [[map_states[((row,col),t,'H')]]]
        clauses += pre_clauses(map_actions[((row,col),t,'vaccinate')], vaccinate_pre)
        return clauses
    elif letter=='S':
        if t>=1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'infectH']] + [map_actions[(row,col),t-1,'noopS']]]#achivements
        if t>=2:
            noop_pre = [[map_states[((row,col),t,'S')]]]+ [[-map_states[((row,col),t-1,'S')],-map_states[((row,col),t-2,'S')]]]+[[x] for x in q_ops]
            stoh_pre = [[map_states[((row,col),t,'S')]],[map_states[((row,col),t-1,'S')]],[map_states[((row,col),t-2,'S')]]]
            clauses+=pre_clauses(map_actions[((row,col),t,'noopS')], noop_pre)
            clauses+=pre_clauses(map_actions[((row,col),t,'StoH')], stoh_pre)
        else:
            noop_pre = [[map_states[((row,col),t,'S')]]] +[[x] for x in q_ops]
            clauses += pre_clauses(map_actions[((row,col),t,'noopS')], noop_pre)
        quarantine_pre = [[map_states[((row,col),t,'S')]]]
        clauses += pre_clauses(map_actions[((row,col),t,'quarantine')], quarantine_pre)
        return clauses
    elif letter=='Q':
        if t==0:
            return []
        if t>1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopQ']] + [map_actions[(row,col),t-1,'quarantine']]] #achivements
        elif t==1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'quarantine']]]  #achivements
        if t>=2:
            noop_pre = [[map_states[((row,col),t,'Q')]],[-map_states[((row,col),t-1,'Q')]]]
            qtoh_pre = [[map_states[((row,col),t,'Q')]],[map_states[((row,col),t-1,'Q')]]]
            clauses+=pre_clauses(map_actions[((row,col),t,'QtoH')],qtoh_pre)
        else:
            noop_pre =  [[map_states[((row,col),t,'Q')]]]
        clauses+=pre_clauses(map_actions[((row,col),t,'noopQ')],noop_pre)
        return clauses
    elif letter =='I':
        if t==0:
            return []
        if t>1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopI']] + [map_actions[(row,col),t-1,'vaccinate']]] #achivements
        elif t==1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'vaccinate']]]  #achivements
        noop_pre = [[map_states[((row,col),t,'I')]]]
        clauses+=pre_clauses(map_actions[((row,col),t,'noopI')],noop_pre)
        return clauses
    else:
        if t>=1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopU']]] #achivements
        noop_pre = [[map_states[((row,col),t,'U')]]]
        clauses += pre_clauses(map_actions[((row,col),t,'noopU')], noop_pre)
        return clauses

def create_action_caluses_no_teams(cur_cell_state,map_states,map_actions, rows,columns,notrelvant1, notrelvant2):
    clauses = []
    row = cur_cell_state[0][0]
    col = cur_cell_state[0][1]
    t = cur_cell_state[1]
    letter = cur_cell_state[2]
    if letter=='H':
        if t>2:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'StoH']] + [map_actions[(row,col),t-1,'noopH']]] #achivements
        elif t>=1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopH']]]  #achivements
        sick_neighbors_index = []
        if row-1>=0:
            sick_neighbors_index+=[map_states[(row-1,col),t,'S']]
        if row+1<rows:
            sick_neighbors_index+=[map_states[(row+1,col),t,'S']]
        if col-1>=0:
            sick_neighbors_index+=[map_states[(row,col-1),t,'S']]
        if col+1<columns:
            sick_neighbors_index+=[map_states[(row,col+1),t,'S']]
        if sick_neighbors_index:
            infect_pre =[[map_states[((row,col),t,'H')]]]+[sick_neighbors_index]
            noop_pre = [[map_states[((row,col),t,'H')]]] + [[-x] for x in sick_neighbors_index]
        else:
            infect_pre =[[map_states[((row,col),t,'H')]]]+[sick_neighbors_index]
            noop_pre = [[map_states[((row,col),t,'H')]]]
        clauses+=pre_clauses(map_actions[((row,col),t,'infectH')], infect_pre)
        clauses+=pre_clauses(map_actions[((row,col),t,'noopH')], noop_pre)
        clauses+= [[-map_actions[((row,col),t,'noopH')],-map_actions[((row,col),t,'infectH')]]] #inteference
        return clauses
    elif letter=='S':
        if t>=1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'infectH']] + [map_actions[(row,col),t-1,'noopS']]]#achivements
        if t>=2:
            noop_pre = [[map_states[((row,col),t,'S')]]]+ [[-map_states[((row,col),t-1,'S')],-map_states[((row,col),t-2,'S')]]]
            stoh_pre = [[map_states[((row,col),t,'S')]],[map_states[((row,col),t-1,'S')]],[map_states[((row,col),t-2,'S')]]]
            clauses+=pre_clauses(map_actions[((row,col),t,'noopS')], noop_pre)
            clauses+=pre_clauses(map_actions[((row,col),t,'StoH')], stoh_pre)
            clauses+= [[-map_actions[((row,col),t,'noopS')],-map_actions[((row,col),t,'StoH')]]] #inteference
            return clauses
        else:
            noop_pre = [[map_states[((row,col),t,'S')]]]
            clauses += pre_clauses(map_actions[((row,col),t,'noopS')], noop_pre)
            return clauses
    else:
        if t>=1:
            clauses += [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopU']]] #achivements
        noop_pre = [[map_states[((row,col),t,'U')]]]
        clauses += pre_clauses(map_actions[((row,col),t,'noopU')], noop_pre)
        return clauses

def add_achivements_final_turn_noteams (cur_cell_state,map_states,map_actions):
    row = cur_cell_state[0][0]
    col = cur_cell_state[0][1]
    t = cur_cell_state[1]
    letter = cur_cell_state[2]
    if letter=='H':
        if t>2:
            return [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'StoH']] + [map_actions[(row,col),t-1,'noopH']]] #achivements
        else:
            return [[-map_states[cur_cell_state]] + [map_actions[(row,col),t-1,'noopH']]] #achivements
    elif letter=='S':
        return  [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'infectH']] + [map_actions[(row,col),t-1,'noopS']]]#achivements
    else:
        return  [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopU']]] #achivements

def add_achivements_final_turn_police (cur_cell_state,map_states,map_actions):
    row = cur_cell_state[0][0]
    col = cur_cell_state[0][1]
    t = cur_cell_state[1]
    letter = cur_cell_state[2]
    if letter=='H':
        if t>2:
            return [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'StoH']] + [map_actions[(row,col),t-1,'noopH']]+[map_actions[(row,col),t-1,'QtoH']]] #achivements
        elif t>=1:
            return [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopH']]]  #achivements
    elif letter=='S':
        if t>=1:
            return [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'infectH']] + [map_actions[(row,col),t-1,'noopS']]]#achivements
    elif letter=='Q':
        if t>1:
            return  [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopQ']] + [map_actions[(row,col),t-1,'quarantine']]] #achivements
        elif t==1:
            return [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'quarantine']]]  #achivements
    else:
        return  [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopU']]] #achivements

def add_achivements_final_turn_medics (cur_cell_state,map_states,map_actions):
    row = cur_cell_state[0][0]
    col = cur_cell_state[0][1]
    t = cur_cell_state[1]
    letter = cur_cell_state[2]
    if letter=='H':
        if t>2:
            return [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'StoH']] + [map_actions[(row,col),t-1,'noopH']]] #achivements
        elif t>=1:
            return [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopH']]]  #achivements
    elif letter=='S':
        if t>=1:
            return [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'infectH']] + [map_actions[(row,col),t-1,'noopS']]]#achivements
    elif letter=='I':
        if t>1:
            return  [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopI']] + [map_actions[(row,col),t-1,'vaccinate']]] #achivements
        elif t==1:
            return [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'vaccinate']]]  #achivements
    else:
        return  [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopU']]] #achivements

def add_achivements_final_turn_allteams (cur_cell_state,map_states,map_actions):
    row = cur_cell_state[0][0]
    col = cur_cell_state[0][1]
    t = cur_cell_state[1]
    letter = cur_cell_state[2]
    if letter=='H':
        if t>2:
            return [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'StoH']] + [map_actions[(row,col),t-1,'noopH']]+[map_actions[(row,col),t-1,'QtoH']]] #achivements
        elif t>=1:
            return [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopH']]]  #achivements
    elif letter=='S':
        if t>=1:
            return [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'infectH']] + [map_actions[(row,col),t-1,'noopS']]]#achivements
    elif letter=='I':
        if t>1:
            return  [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopI']] + [map_actions[(row,col),t-1,'vaccinate']]] #achivements
        elif t==1:
            return [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'vaccinate']]]  #achivements
    elif letter=='Q':
        if t>1:
            return  [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopQ']] + [map_actions[(row,col),t-1,'quarantine']]] #achivements
        elif t==1:
            return [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'quarantine']]]  #achivements
    else:
        return  [[-map_states[cur_cell_state]]+[map_actions[(row,col),t-1,'noopU']]] #achivements

def infect_precondition (action, pre):
    clauses = []
    for x in product(*pre):
        clauses +=[[-action]+list(x)]
    return clauses

def pre_clauses (action, preconditions):
    clauses = []
    for p in preconditions:
        clauses.append([-action]+p)
    return clauses

def atmost_k0 (vars,k):
    clauses = []
    for i in combinations(vars,k+1):
        clauses+=[[-j for j in i]]
    return clauses

def exactly_one_clauses (vars):
    clauses = []
    all_pos=[]
    for i in range(len(vars)):
        for j in range (i+1,len(vars)):
            clauses+=[[-vars[i],-vars[j]]]
        all_pos+=[vars[i]]
    clauses+=[all_pos]
    return clauses
