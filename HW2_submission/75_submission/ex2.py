from itertools import combinations
from itertools import permutations
import copy

ids = ['208660621', '316368679']

# Class (Struct) Node in a tree of states
class Node:
    def __init__(self,state,stage,parent=None):
        self.state=state
        self.stage=stage
        self.parent=parent
        self.children=[]

# Class Problem tp solve Problem
class Problem:

    def listify(self,tuple_matrix):
        # 2D tuple to 2D list
        return [list(i) for i in tuple_matrix]

    def tuplify(self,list_matrix):
        # 2D list to 2D tuple
        return tuple([tuple(i) for i in list_matrix])

    def check_neighbors(self,arr, location, criteria, cols=1, non_binary=False):
        """
        checks whether any of the neigbors are sick,
         if non_binary = False : if yes return true
         if non_binary = True : returns total number of sick neighbors
        """
        if non_binary == True:
            total = 0
        neighbors_sick = False
        try:
            if arr[location[0] + 1][location[1]] in criteria: #bottom neighbor
                neighbors_sick = True
                if non_binary:
                    total += 1
        except IndexError:
            neighbors_sick = False
        if not neighbors_sick:
            try:
                if location[0] and arr[location[0] - 1][location[1]] in criteria: #top neighbor
                    neighbors_sick = True
                    if non_binary:
                        total += 1
            except IndexError:
                neighbors_sick = False
        if not neighbors_sick:
            try:
                if (location[1] + 1) % cols and arr[location[0]][location[1] + 1] in criteria: #right neighbor
                    neighbors_sick = True
                    if non_binary:
                        total += 1
            except IndexError:
                neighbors_sick = False
        if not neighbors_sick:
            try:
                if (location[1]) and arr[location[0]][location[1] - 1] in criteria: #left neighbor
                    neighbors_sick = True
                    if non_binary:
                        total += 1
            except IndexError:
                neighbors_sick = False
        if non_binary:
            return total
        return neighbors_sick

    def update_action(self, result, action):
        '''
        Update according to action, vaccinate vaccinates while quarantine goes to lockdown(quarantine)
        '''
        action_name = action[0]
        row = action[1][0]
        col = action[1][1]
        if action_name == "vaccinate":
            result[row][col] = ("I", 0)
        elif action_name == "quarantine":
            result[row][col] = ("Q", -1)
        else:
            return

    def __init__(self, input):
        """Initialize the world of our problem, including states observations and queries"""
        self.medics=input['medics']
        self.police=input['police']
        self.observed_states={i:input['observations'][i] for i in range(len(input['observations']))}
        self.queries=[i for i in input['queries']]  # list of given queries
        self.queries=sorted(self.queries,key=lambda x:x[1]) # sort queries according to stages
        self.answers={tuple(i):"?" for i in self.queries} # dictionary of query:answer
        self.num_queries=len(self.queries)
        self.last_stage=max([i[1] for i in self.queries]) # last stage asked about
        self.number_observations = len(self.observed_states)
        self.rows=len(self.observed_states[0])
        self.cols=len(self.observed_states[0][0])
        self.transformations={("Q",-1):("Q",0),("Q",0):("Q",1),("Q",1):("H",0),("H",0):("H",0),("U",0):("U",0), \
                              ("S",-1):("S",0),("S",0):("S",1),("S",1):("S",2),("S",2):("H",0),("I",0):("I",0),\
                              ("?",0):("?",0)}
        self.sick = [("S", 0), ("S", 1), ("S", 2)]
        self.propagated={i:[] for i in range(self.last_stage+1)}  #  all possible boards- compatible with given observations

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file
        returns a tuple of actions in the format (("vaccinate",(R,C),("quarantine",(R,C))
        """
        state=self.listify(state)
        all_H=[]
        all_S=[]
        for i in range(self.rows):
            for j in range(self.cols):
                if state[i][j][0]=="H":
                    all_H.append(("vaccinate",(i,j)))
                if state[i][j][0]=="S":
                    all_S.append(("quarantine",(i,j)))
        r=min(self.medics,len(all_H))
        actions_H = tuple([tuple(i) for i in combinations(all_H,r)])
        r=min(self.police,len(all_S))
        actions_S = tuple([tuple(i) for i in combinations(all_S,r)])
        all_actions=[]
        for quarantine in actions_S:
            for vaccinate in actions_H:
                all_actions.append((quarantine+vaccinate))
        return all_actions


    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        result=self.listify(state)
        # change according to actions
        if action:
            for act in action:
                self.update_action(result,act)
        # change according to sick infecting healthy

        for i in range(self.rows):
            for j in range(self.cols):
                if result[i][j]==("H",0):
                    if self.check_neighbors(result,(i,j),self.sick,self.cols):
                        result[i][j]=("S",-1)

        # update according to time dynamics
        for i in range(self.rows):
            for j in range(self.cols):
                result[i][j]=self.transformations[result[i][j]]
        result=self.tuplify(result)
        return result

    def is_compatible(self,state,stage):
        """
        checks if a state is compatible with observation at this stage
        :return: T/F
        """
        compatible=True
        if stage>=len(self.observed_states):
            return compatible
        for row in range(self.rows):
            for col in range(self.cols):
                if self.observed_states[stage][row][col]!='?':
                    if state[row][col][0]!=self.observed_states[stage][row][col]:
                        compatible=False
                        return compatible
        return compatible

    def initialize_stage_zero(self):
        """
        initialize all ?'s at stage 0 to any possible sign : U/H/S
        :return: all possible assignments for the 0 stage board
        """
        initial = self.listify(self.observed_states[0])
        initial = [[(i,0) for i in j] for j in initial]
        initial = Node(self.tuplify(initial), stage=0)
        possibilities = [('S', 0), ('H', 0), ('U', 0)]
        possible_assignments = []
        question_marks = []
        # find all locations of ? in board
        for row in range(self.rows):
            for col in range(self.cols):
                if initial.state[row][col][0] == '?':
                    question_marks.append((row, col))

        # generates all possible assignments per question mark, and their combinations
        all_combinations = set([tuple(i) for i in permutations \
            (possibilities * len(question_marks), len(question_marks))])
        for combo in all_combinations:
            poss_state = copy.deepcopy(initial.state)
            poss_state=self.listify(poss_state)
            for q in range(len(question_marks)):
                poss_state[question_marks[q][0]][question_marks[q][1]] = combo[q]
            poss_state=self.tuplify(poss_state) #generates all possible states
            possible_assignments.append(Node(poss_state,0))
        return possible_assignments

    def node_propagate(self,node,stage):
        """
        recursive function to propagate all children of state, and add to propagated dictionary if possible
        :param node: node to check if possible
        :param stage: stage of node.state
        :return: True if node is possible: it is compatible + at least one of its children possible
        """
        possible=False
        if stage==self.last_stage:
            return True
        all_actions=self.actions(node.state)
        for action in all_actions:
            result=self.result(node.state,action)
            if self.is_compatible(result,stage+1): #node is compatible
                child=Node(result,stage=stage+1,parent=node)
                if self.node_propagate(child,stage+1): # at least one child is possible
                    node.children.append(child)
                    self.propagated[stage+1].append(child.state)
                    possible=True
        return possible

    # def insert_to_propagated(self,node,stage):
    #     if stage>self.last_stage:
    #         return
    #     for i in node.children:


    def propagate(self):
        """
        fill the propagated dictionary with all possible states at each stage
        :return:
        """
        all_assignments=self.initialize_stage_zero()
        n=len(all_assignments)
        for i in reversed(range(n)):
            if not self.node_propagate(all_assignments[i],0):
                all_assignments.pop(i)
        for assign in all_assignments:
            self.propagated[0].append(assign.state)

    def answer(self):
        """
        main function, to answer all queries.
        :return: answers dictionary
        """
        self.propagate()
        for query in self.queries:
            row,col,stage,claim=query[0][0],query[0][1],query[1],query[2]
            f,t=True,True
            first_result=self.propagated[stage][0][row][col][0]
            if first_result!=claim:
                for state in self.propagated[stage]:
                    if state[row][col][0]==claim:
                        f=False
                        break
                if f:
                    self.answers[query]='F'
            else:
                for state in self.propagated[stage]:
                    if state[row][col][0]!=claim:
                        t=False
                        break
                if t:
                    self.answers[query] = 'T'
        return self.answers


def solve_problem(input):
    problem=Problem(input)
    return problem.answer()

