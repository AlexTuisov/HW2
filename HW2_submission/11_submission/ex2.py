ids = ['316219997', '316278670']
import utils
from itertools import chain, combinations




class Node:

    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def expand(self, problem,num_obs):
        childs_list=[]
        for act in problem.actions(self.state):
            child=self.child_node(problem,act)
            if child.depth<num_obs:
                if is_possible(child.state,problem.observ_list[child.depth]):
                    childs_list.append(child)
        return childs_list

    def child_node(self, problem, action):
        """[Figure 3.10]"""
        next = problem.result(self.state, action)
        return Node(next, self, action)

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node.state)
            node = node.parent
        return list(reversed(path_back))


class Problem(object):
    def __init__(self, initial, permutations=None):
        self.initial = initial
        self.permutations = permutations

    def actions(self, state):
        raise NotImplementedError

    def result(self, state, action):
        raise NotImplementedError


class MedicalProblem(Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial,permutation=None):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        self.medics = initial["medics"]
        self.police = initial["police"]
        self.initial = initial['observations']
        self.obser_num = len(initial['observations'])
        self.row = len(initial['observations'][0])
        self.col = len(initial['observations'][0][0])
        self.init_matrix(self.initial,permutation)
        Problem.__init__(self, self.initial,permutation)

    def init_matrix(self,initial,perm):

        observ = [list(x) for x in initial]
        observations_list = [[list(x) for x in observ[i]] for i in range(len(observ))]
        self.observ_list = tuple(observations_list)
        if perm != ():
            if len(perm)>0:
                index=0
                for i in range(len(observations_list[0])):
                    for j in range(len(observations_list[0][0])):
                        if observations_list[0][i][j]=='?':
                            observations_list[0][i][j]=(perm[index],1)
                            index+=1
                        else:
                            observations_list[0][i][j]=(observations_list[0][i][j],1)

        else:
            for k in range(len(observations_list[0])):
                for l in range(len(observations_list[0][0])):
                    observations_list[0][k][l] = (observations_list[0][k][l], 1)

        temp = [tuple(x) for x in observations_list]
        temp = tuple([tuple([tuple(x) for x in temp[i]]) for i in range(len(temp))])
        self.initial = temp[0]


    def actions(self,state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        sick = []
        health = []
        num_s = 0
        num_h = 0
        for i in range(self.row):
            for j in range(self.col):
                if state[i][j][0] == 'S':
                    sick.append(("quarantine", (i, j)))
                    num_s += 1
                elif state[i][j][0] == 'H':
                    health.append(("vaccinate", (i, j)))
                    num_h += 1

        res = []
        if num_h < self.medics:
            health_pow = list(chain.from_iterable(combinations(health, r) for r in range(num_h, num_h + 1)))[:]
        else:
            health_pow = list(chain.from_iterable(combinations(health, r) for r in range(self.medics, self.medics + 1)))[:]
        if num_s < self.police:
            sick_pow = list(chain.from_iterable(combinations(sick, r) for r in range(num_s, num_s + 1)))[:]
        else:
            sick_pow = list(chain.from_iterable(combinations(sick, r) for r in range(self.police, self.police + 1)))[:]
        if len(health_pow) == 0:
            sick_pow.append(())
            return tuple(sick_pow)
        if len(sick_pow) == 0:
            health_pow.append(())
            return tuple(health_pow)
        for i in range(len(health_pow)):
            for j in range(len(sick_pow)):
                res.append(health_pow[i] + sick_pow[j])
        return tuple(res)

    def healthy(self,i, j, state,state_after_act):
        if (i - 1) >= 0:
            if state[i - 1][j][0] == 'S':
                if state_after_act[i-1][j]!=0:
                    if state_after_act[i - 1][j][0] != 'Q':
                        return ('S', 1)
                else:
                    return ('S', 1)
        if (i + 1) < self.row:
            if state[i + 1][j][0] == 'S':
                if state_after_act[i+1][j]!=0:
                    if state_after_act[i +1][j][0] != 'Q':
                        return ('S', 1)
                else:
                    return ('S', 1)
        if (j - 1) >= 0:
            if state[i][j - 1][0] == 'S':
                if state_after_act[i][j-1]!=0:
                    if state_after_act[i][j-1][0] != 'Q':
                        return ('S', 1)
                else:
                    return ('S', 1)
        if (j + 1) < self.col:
            if state[i][j + 1][0] == 'S':
                if state_after_act[i][j+1]!=0:
                    if state_after_act[i][j +1][0] != 'Q':
                        return ('S', 1)
                else:
                    return ('S', 1)
        return ('H', 1)


    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        state_after_act = [[0 for i in range(self.col)] for j in range(self.row)]
        for k in action:
            x = k[1][0]
            y = k[1][1]
            if k[0] == "vaccinate":
                state_after_act[x][y] = ('I', 1)
            else:
                state_after_act[x][y] = ('Q', 1)

        for i in range(self.row):
            for j in range(self.col):
                if state_after_act[i][j] == 0:
                    if state[i][j][0] == 'U' or state[i][j][0] == 'I':
                        state_after_act[i][j] = state[i][j]

                    elif state[i][j][0] == 'S':
                        if state[i][j][1] == 3:
                            state_after_act[i][j] = ('H', 1)
                        else:
                            if state[i][j][1] == 1:
                                state_after_act[i][j] = ('S', 2)
                            elif state[i][j][1] == 2:
                                state_after_act[i][j] = ('S', 3)

                    elif state[i][j][0] == 'Q':
                        if state[i][j][1] == 2:
                            state_after_act[i][j] = ('H', 1)
                        else:
                            state_after_act[i][j] = ('Q', 2)

                    elif state[i][j][0] == 'H':
                        state_after_act[i][j] = self.healthy(i, j, state,state_after_act)
            state_after_act[i] = tuple(state_after_act[i])
        return tuple(state_after_act)


def solve_problem(input):
    queries=input['queries']
    num_question_mark=count_question_mark(input['observations'][0])
    possible_states=num_question_mark*['S','H','U']
    if num_question_mark==1:
        permutation=possible_states
    else:
        permutation = list(set(list(chain.from_iterable(combinations(possible_states, r) for r in range(num_question_mark, num_question_mark+1)))[:]))
    result_dict={}
    for query in queries:
        result_dict[tuple(query)]=[]
    help_dict={}
    for perm in permutation:
        help_dict[tuple(perm)]=[]
    if len(permutation)==0:
        problem=MedicalProblem(Problem(input).initial)
        BFS(problem,(),help_dict,problem.obser_num)
    else:
        for p in range(len(permutation)):
            problem = MedicalProblem(Problem(input,permutation[p]).initial,permutation[p])
            BFS(problem, permutation[p], help_dict,problem.obser_num)

    check_query(queries,result_dict,help_dict)
    return result_dict


def count_question_mark(observation):
    counter = 0
    for i in range(len(observation)):
        for j in range(len(observation[0])):
            if observation[i][j] == '?':
                counter += 1
    return counter


def BFS(problem,permutation,help_dict,num_observ):
    node = Node(problem.initial)
    frontier = utils.FIFOQueue()
    frontier.append(node)
    explored = set()
    while frontier:
        node = frontier.pop()
        explored.add(node.state)
        for child in node.expand(problem,num_observ):
            if child.state not in explored and child not in frontier:
                if child.depth == len(problem.observ_list)-1:
                    c=child.path()
                    help_dict[tuple(permutation)].append(c)
                frontier.append(child)
    return None


def is_possible(possible_state,true_state):
    for i in range(len(possible_state)):
        for j in range(len(possible_state[0])):
            if possible_state[i][j][0]!=true_state[i][j] and true_state[i][j]!='?':
                return False
    return True


def equal(query,state):

    if state[query[1]][query[0][0]][query[0][1]][0]==query[2]:
        return 1
    else:
        return 0


def check_query(queries,result_dict,help_dict):
    for query in queries:
        b=True
        if b:
            for i in help_dict.keys():
                if b:
                    for j in help_dict[i]:

                        result_dict[query].append(equal(query,j))

                        if 0 in result_dict[query] and 1 in result_dict[query]:
                            result_dict[query]="?"
                            b=False
                            break
        if b:
            if 0 not in result_dict[query]:
                result_dict[query]='T'
            else:
                result_dict[query]='F'
