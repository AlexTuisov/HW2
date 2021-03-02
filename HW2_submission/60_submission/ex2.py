from sympy import *
from itertools import combinations

ids = ['206312506', '206217366']


class SATMedicalSolver:
    def __init__(self, observations, medics, police):
        self.observations = observations
        self.initial_observations = observations.copy()
        self.medics = medics
        self.police = police
        self.rows = len(observations[0])
        self.cols = len(observations[0][0])
        self.duration = len(observations)  
        self.props = dict()
        self.actions = dict()
        self.possible_states = ("S", "H", "Q", "I", "U")


    def get_status_props(self, time, status_char, prefix:str, suffix:str):
        state = self.observations[time]
        props = dict()
        for i in range(len(state)):
            for j in range(len(state[0])):
                _key = prefix + str(i) + str(j) + suffix
                _symbol = symbols(_key)
                if state[i][j] == "?":
                    props[_key] = (_symbol,_symbol)
                else:
                    props[_key] = (_symbol,state[i][j] == status_char)
        return props


    def get_neighbors(self, row, col):
        indices = list()
        if col + 1 < self.rows:
            indices.append((row,col+1))
        if row + 1 < self.cols:
            indices.append((row+1,col))
        if row > 0:
            indices.append((row-1,col))
        if col > 0:
            indices.append((row,col-1))
        return indices


    def get_actions_props(self):
        """
        qa: Quarantine Action (requires a police team)
        ia: Immune Action (requires a medical team)
        ra: Recover Action (Sick for 3 days / Quarantine for 2 days)
        """
        actions = dict()
        actions_effect = list()
        q_actions = list()
        i_actions = list()

        # Each action will have 4 items: (symbol, pre, add, del)
        for k in range(self.duration-1):
            q_actions_k = list()
            i_actions_k = list()
            for i in range(self.rows):
                for j  in range(self.cols):
                    key = str(i) + str(j) + str(k)
                    next_key = str(i) + str(j) + str(k+1)

                    # quarantine action (symbol, pre, add, del)
                    qa_taken = self.observations[k][i][j]=='S' and self.observations[k+1][i][j]=='Q' and self.police > 0
                    actions['qa' + key] = (symbols('qa'+key), qa_taken)
                    q_actions_k.append(symbols('qa'+key))

                    # precondition constraint
                    actions_effect.append(actions['qa'+key][0] >> self.props['s'+key][0])
                    # add effect constraint
                    actions_effect.append(actions['qa'+key][0] >> self.props['q'+next_key][0])
                    # delete effect constraint
                    actions_effect.append(actions['qa'+key][0] >> ~self.props['s'+next_key][0])
                    # if in the next day s becomes q, we must have quarantined s
                    actions_effect.append((self.props['s'+key][0] & self.props['q'+next_key][0]) >> actions['qa'+key][0])

                    # immune action
                    ia_taken = self.observations[k][i][j]=='H' and self.observations[k+1][i][j]=='I' and self.medics > 0
                    actions['ia' + key] = (symbols('ia'+key), ia_taken)
                    i_actions_k.append(symbols('ia'+key))

                    # precondition constraint
                    actions_effect.append(actions['ia'+key][0] >> self.props['h'+key][0])
                    # add effect constraint
                    actions_effect.append(actions['ia'+key][0] >> self.props['i'+next_key][0])
                    # delete effect constraint
                    actions_effect.append(actions['ia'+key][0] >> ~self.props['h'+next_key][0])
                    # if in the next day h becomes i, we must have immuened h
                    actions_effect.append((self.props['h'+key][0] & self.props['i'+next_key][0]) >> actions['ia'+key][0])
                    ra_taken = symbols('ra'+key)
                    if k==0:
                        ra_taken = False
                    # recover action
                    actions['ra' + key] = (symbols('ra'+key), ra_taken)
            
            q_actions.append(q_actions_k)
            i_actions.append(i_actions_k)
        
        for k in range(self.duration-1):
            if self.police > 0:
                q_actions_disabled = And()
                for action in q_actions[k]:
                    q_actions_disabled = q_actions_disabled & ~action

                for action_comb in combinations(q_actions[k],self.police):
                    lhs = And(*action_comb)
                    rhs = q_actions_disabled.subs([(a,False) for a in action_comb])
                    actions_effect.append(lhs >> rhs)

            if self.medics > 0:
                i_actions_disabled = And()
                for action in i_actions[k]:
                    i_actions_disabled = i_actions_disabled & ~action

                for action_comb in combinations(i_actions[k],self.medics):
                    lhs = And(*action_comb)
                    rhs = i_actions_disabled.subs([(a,False) for a in action_comb])
                    actions_effect.append(lhs >> rhs)

        return actions, actions_effect


    def get_noops_props(self):
        noops = list()
        
        for k in range(self.duration-1):
            for i in range(self.rows):
                for j  in range(self.cols):
                    key = str(i) + str(j) + str(k)
                    next_key = str(i) + str(j) + str(k+1)
                    # Preserve immune
                    noops.append(self.props['i' + key][0] >> self.props['i' + next_key][0])

                    # Preserve unpopulated
                    noops.append(self.props['u' + key][0] >> self.props['u' + next_key][0])

                    # Impossible transitions
                    noops.append(self.props['h' + key][0] >> ~self.props['q' + next_key][0])
                    noops.append(self.props['h' + key][0] >> ~self.props['u' + next_key][0])

                    noops.append(self.props['s' + key][0] >> ~self.props['i' + next_key][0])
                    noops.append(self.props['s' + key][0] >> ~self.props['u' + next_key][0])
                    
                    noops.append(self.props['q' + key][0] >> ~self.props['i' + next_key][0])
                    noops.append(self.props['q' + key][0] >> ~self.props['u' + next_key][0])

                    noops.append((self.props['s'+key][0] & ~self.actions['ra'+key][0]) >> self.props['s' + next_key][0])
                    noops.append((self.props['q'+key][0] & ~self.actions['ra'+key][0]) >> self.props['q' + next_key][0])
                            
        return noops  


    def get_spread_props(self):
        props = list()
        for k in range(self.duration-1):
            for i in range(self.rows):
                for j  in range(self.cols):
                    key = str(i) + str(j) + str(k)
                    next_key = str(i) + str(j) + str(k+1)
                    neighbors = self.get_neighbors(i,j)
                    _danger = Or()
                    for neighbor in neighbors:
                        n_key = str(neighbor[0]) + str(neighbor[1]) + str(k)
                        _danger |= And(self.props['s'+n_key][0], Not(self.actions['qa'+n_key][0]))
                        in_danger = self.props['h'+key][0] & ~self.actions['ia'+key][0] & self.props['s'+n_key][0] & ~self.actions['qa'+n_key][0] 
                        props.append(in_danger >> self.props['s'+next_key][0])
                    
                    props.append((self.props['h'+key][0] & self.props['s'+next_key][0]) >> (_danger & ~self.actions['ia'+key][0]) )
                      
        return props  
    
    def get_sickness_expired_props(self):
        props = list()
        if self.duration > 3:
            for k in range(self.duration-3):
                for i in range(self.rows):
                    for j  in range(self.cols):
                        s1 = self.props['s'+str(i) + str(j) + str(k)]
                        s2 = self.props['s'+str(i) + str(j) + str(k+1)]
                        s3 = self.props['s'+str(i) + str(j) + str(k+2)]
                        recover = self.actions['ra'+str(i) + str(j) + str(k+2)]
                        
                        s4 = self.props['s'+str(i) + str(j) + str(k+3)]
                        h4 = self.props['h'+str(i) + str(j) + str(k+3)]
                        
                        props.append(Implies(s1[0] & s2[0] & s3[0], recover[0]))
                        props.append(recover[0] >> h4[0])
                        props.append(recover[0] >> ~s4[0])

                        if recover[1] != True:
                            ra_taken = (s1[1] == True) and (s2[1] == True) and (s3[1] == True)
                            self.actions['ra'+str(i) + str(j) + str(k+2)] = (recover[0], ra_taken)

        return props


    def get_quarantine_expired_props(self):
        props = list()
        if self.duration > 2:
            for k in range(self.duration-2):
                for i in range(self.rows):
                    for j  in range(self.cols):
                        q1 = self.props['q'+str(i) + str(j) + str(k)]
                        q2 = self.props['q'+str(i) + str(j) + str(k+1)]
                        recover = self.actions['ra'+str(i) + str(j) + str(k+1)]
                        
                        q3 = self.props['q'+str(i) + str(j) + str(k+2)]
                        h3 = self.props['h'+str(i) + str(j) + str(k+2)]

                        props.append(Implies(q1[0] & q2[0], recover[0]))
                        props.append(recover[0] >> h3[0])
                        props.append(recover[0] >> ~q3[0])

                        if recover[1] != True:
                            ra_taken = (q1[1] == True) and (q2[1] == True)
                            self.actions['ra'+str(i) + str(j) + str(k+1)] = (recover[0], ra_taken)
        else:
            # Can't be recovered at all
            for k in range(self.duration-1):
                for i in range(self.rows):
                    for j  in range(self.cols):
                        recover = self.actions['ra'+str(i)+str(j)+str(k)]
                        self.actions['ra'+str(i)+str(j)+str(k)] = (recover[0], False)
        return props


    def modify_observation(self, time, row, col, state):
        """
        time: the observation index in self.observations
        row: the row that needs to be modified
        col: the column that needs to be modified
        state: the new state in (row,col)
        """
        observation = list()
        for i in range(self.rows):
            observation_row = list()
            for j in range(self.cols):
                if i!=row or j!=col:
                    observation_row.append(self.observations[time][i][j])
                else:
                    observation_row.append(state)
            observation.append(tuple(observation_row))
        return tuple(observation)

    def satisfiable_state(self):
        for k in range(self.duration):
            for _state in self.possible_states:
                self.props.update(self.get_status_props(k, _state.upper(), _state.lower(), str(k)))

        # actions
        self.actions, actions_effect = self.get_actions_props()

        # noops
        noops = self.get_noops_props()

        # sickness spread h /\ has sick neighbor /\ not becoming immune -> s
        spread = self.get_spread_props()

        # sickness expired (only when duration > 3)
        sickness_expired_props = self.get_sickness_expired_props()

        # quarantine expired (only when duration > 2)
        quarantine_expired_props = self.get_quarantine_expired_props()

        t = And()
        for props_list in [actions_effect,noops,spread,sickness_expired_props,quarantine_expired_props]:
                t &= And(*props_list)
                
        t = t.subs(list(self.props.values()))
        t = t.subs(list(self.actions.values()))

        return satisfiable(t,algorithm="dpll") != False


    def test_unpopulated(self, time, row, col):
        for k in range(self.duration):
            if k != time and self.observations[k][row][col] not in ['U', '?']:
                return False
        return True


    def solve(self, queries):
        answers = dict()
        for query in queries:
            q_position = query[0]
            q_time = query[1]
            q_state = query[2]
            q_answer = '?'
            
            # reset any changes to the obsevations from previos queries
            self.observations = self.initial_observations.copy()
            self.observations[q_time] = self.modify_observation(q_time,q_position[0], q_position[1], q_state)
            q_state_proof = self.satisfiable_state()

            if q_state_proof == False:
                q_answer = 'F'
                answers[query] = q_answer
                continue 

            # From here it is true that: q_state_proof == True
            different_state_proof = False
            for _s in self.possible_states:
                if _s != q_state:
                    if _s == 'U':
                        # Easier test for unpopulated
                        if self.test_unpopulated(q_time,q_position[0], q_position[1]):
                            different_state_proof = True
                            break
                    else:
                        self.observations[q_time] = self.modify_observation(q_time,q_position[0], q_position[1], _s)
                        if self.satisfiable_state():
                            different_state_proof = True
                            break

            if different_state_proof == False:
                q_answer = 'T'
            answers[query] = q_answer 

        return answers


def solve_problem(input):
    solver = SATMedicalSolver(input['observations'], input['medics'], input['police'])
    return solver.solve(input['queries'])
