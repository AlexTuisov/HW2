from itertools import chain, combinations
from utils import (FIFOQueue)

infinity = float('inf')

ids = ["308387497", "311385041"]


class Problem(object):

    def __init__(self, initial, c=None):
        self.initial = initial
        self.c = c

    def actions(self, state):
        raise NotImplementedError

    def result(self, state, action):
        raise NotImplementedError


class MedicalProblem(Problem):

    def __init__(self, initial, c=None):
        self.police = initial["police"]
        self.medics = initial["medics"]
        self.initial = initial["observations"]
        self.update_board(self.initial, c)
        self.row = len(self.initial)
        self.col = len(self.initial[0])

        Problem.__init__(self, self.initial, c=None)

    def update_board(self, initial, c):
        obs1 = [list(x) for x in initial]
        list_obs = [[list(x) for x in obs1[i]] for i in range(len(obs1))]
        self.obs = tuple(list_obs)
        if c is not None:
            if len(c) > 0:
                iter = 0
                for j in range(len(list_obs[0])):
                    for k in range(len(list_obs[0][0])):
                        if list_obs[0][j][k] == "?":
                            list_obs[0][j][k] = c[iter]
                            iter += 1
        temp_tuple = [tuple(x) for x in list_obs]
        temp_tuple = tuple([tuple([tuple(x) for x in temp_tuple[i]]) for i in range(len(temp_tuple))])
        self.initial = temp_tuple[0]

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        sc = 0
        hc = 0
        actions = []
        actions_v = []
        actions_q = []
        for i in range(self.row):
            for j in range(self.col):
                if state[i][j] == "H":
                    actions_v.append(("vaccinate", (i, j)))
                    hc += 1
                elif state[i][j] == "S" or state[i][j] == "S1" or state[i][j] == "S2":
                    sc += 1
                    actions_q.append(("quarantine", (i, j)))
        if hc >= self.medics:
            all_comb_v = list(
                chain.from_iterable(combinations(actions_v, r) for r in range(self.medics, self.medics + 1)))
        else:
            all_comb_v = list(chain.from_iterable(combinations(actions_v, r) for r in range(self.medics + 1)))
        all_comb_q = list(chain.from_iterable(combinations(actions_q, r) for r in range(self.police + 1)))
        ifSbigger = list(chain.from_iterable(combinations(actions_q, r) for r in range(self.police, self.police + 1)))
        if len(all_comb_v) == 0 and len(all_comb_q) == 0: return []
        if len(all_comb_v) == 0 and len(all_comb_q) != 0: return all_comb_q
        if len(all_comb_v) != 0 and len(all_comb_q) == 0: return all_comb_v
        if sc <= self.police: return all_comb_q
        for i in range(len(all_comb_v)):
            for j in range(len(ifSbigger)):
                actions.append(all_comb_v[i] + ifSbigger[j])

        return actions

    def result(self, state, action):
        s = [list(i) for i in state]
        self.update_by_actions(s, action)
        self.update_by_former_state(state, s)
        return tuple(tuple(sub) for sub in s)

    def H_neighbors(self, state, s, i, j):
        try:
            if state[i][j + 1] == "H" and s[i][j + 1] != "I":
                s[i][j + 1] = "S"
        except IndexError:
            pass
        try:
            if state[i][j - 1] == "H" and j > 0 and s[i][j - 1] != "I":
                s[i][j - 1] = "S"
        except IndexError:
            pass
        try:
            if state[i + 1][j] == "H" and s[i + 1][j] != "I":
                s[i + 1][j] = "S"
        except IndexError:
            pass
        try:
            if state[i - 1][j] == "H" and i > 0 and s[i - 1][j] != "I":
                s[i - 1][j] = "S"
        except IndexError:
            pass

    def update_by_former_state(self, state, s):
        for i in range(self.row):
            for j in range(self.col):
                if state[i][j] == "Q1" or state[i][j] == "Q":
                    s[i][j] = "Q2"
                elif state[i][j] == "Q2":
                    s[i][j] = "H"
                elif ((state[i][j] == "S") or (state[i][j] == "S1") or (state[i][j] == "S2")) and s[i][j] != "Q1":
                    self.H_neighbors(state, s, i, j)
                    if state[i][j] == "S":
                        s[i][j] = "S1"
                    elif state[i][j] == "S1":
                        s[i][j] = "S2"
                    elif state[i][j] == "S2":
                        s[i][j] = "H"

    def update_by_actions(self, s, action):
        for a in action:
            act = a[0]
            i = a[1][0]
            j = a[1][1]
            if act == "vaccinate":

                s[i][j] = "I"
            elif act == "quarantine":

                s[i][j] = "Q1"


def check_equality(state, origin):
    for i in range(len(origin)):
        for j in range(len(origin[0])):
            if state[i][j] == "H" and origin[i][j] != "H" and origin[i][j] != "?":
                return False
            elif state[i][j] == "U" and origin[i][j] != "U" and origin[i][j] != "?":
                return False
            elif state[i][j] == "I" and origin[i][j] != "I" and origin[i][j] != "?":
                return False
            elif (state[i][j] == "Q" or state[i][j] == "Q1" or state[i][j] == "Q2") and origin[i][j] != "Q" and \
                    origin[i][j] != "?":
                return False
            elif (state[i][j] == "S" or state[i][j] == "S1" or state[i][j] == "S2") and origin[i][j] != "S" and \
                    origin[i][j] != "?":
                return False

    return True


class Node:
    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state.  Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node.  Other functions
    may add an f and h value; see best_first_graph_search and astar_search for
    an explanation of how the f and h values are handled. You will not need to
    subclass this class."""

    def __init__(self, state, parent=None, action=None):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def expand(self, problem, goal_dict):
        """List the nodes reachable in one step from this node."""
        result = []
        for action in problem.actions(self.state):
            child = self.child_node(problem, action)
            if child.depth < len(problem.obs):
                if check_equality(child.state, problem.obs[child.depth]):
                    result.append(child)
        return result

    def child_node(self, problem, action):
        next = problem.result(self.state, action)
        return Node(next, self, action)

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent

        return list(reversed(path_back))

    def path_state(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node.state)
            node = node.parent

        return list(reversed(path_back))


def bfs(problem, goal_dict, c, temp_dict):
    node = Node(problem.initial)
    frontier = FIFOQueue()
    frontier.append(node)
    explored = set()
    while frontier:
        node = frontier.pop()
        explored.add(node.state)
        for child in node.expand(problem, goal_dict):
            if child.state not in explored and child not in frontier:
                if child.depth == len(problem.obs) - 1:
                    # if c is not None:
                    k = child.path_state()
                    temp_dict[tuple(c)].append(k)

                frontier.append(child)

    return None


def count_questions(M):
    c = 0
    for i in range(len(M)):
        for j in range(len(M[0])):
            if M[i][j] == "?":
                c += 1

    return c


def solve_problem(input):
    queries = input["queries"]
    goal_dict = {}
    for q in queries:
        goal_dict[tuple(q)] = []

    n = count_questions(input["observations"][0])
    data = n * ["S", "H", "U"]
    c = comb(data, n)
    temp_dict = {}
    for i in c:
        temp_dict[tuple(i)] = []

    temp_dict[tuple()] = []
    for i in range(max(1, len(c))):
        if len(c) == 0:
            problem = MedicalProblem(Problem(input).initial)
            update_dict(problem, goal_dict, (), temp_dict)
        else:
            problem = MedicalProblem(Problem(input, c[i]).initial, c[i])
            update_dict(problem, goal_dict, c[i], temp_dict)
    update_goal_dict(queries, temp_dict, goal_dict)
    return goal_dict


def update_dict(problem, goal_dict, c, temp_dict):
    bfs(problem, goal_dict, c, temp_dict)


def update_goal_dict(queries, temp_dict, goal_dict):
    for q in queries:
        flag = True
        if flag:
            for i in temp_dict.keys():
                if flag:
                    for j in temp_dict[i]:
                        goal_dict[q].append(match(q, j))
                        if 0 in goal_dict[q] and 1 in goal_dict[q]:
                            goal_dict[q] = "?"
                            flag = False
                            break
        if flag:
            if 0 not in goal_dict[q] and 1 in goal_dict[q]:
                goal_dict[q] = "T"
            elif 1 not in goal_dict[q] and 0 in goal_dict[q]:
                goal_dict[q] = "F"
            elif 1 in goal_dict[q] and 0 in goal_dict[q]:
                goal_dict[q] = "?"
            else:
                goal_dict[q] = "F"


def match(q, l):
    if q[2] != "S" and q[2] != "Q":
        if l[q[1]][q[0][0]][q[0][1]] == q[2]:
            return 1
        else:
            return 0
    elif (q[2] == "S" and l[q[1]][q[0][0]][q[0][1]] == "S") or (q[2] == "S" and l[q[1]][q[0][0]][q[0][1]] == "S1") or \
            (q[2] == "S" and l[q[1]][q[0][0]][q[0][1]] == "S2"):
        return 1
    elif (q[2] == "Q" and l[q[1]][q[0][0]][q[0][1]] == "Q1") or (q[2] == "Q" and l[q[1]][q[0][0]][q[0][1]] == "Q2"):
        return 1
    return 0


def permutation(lst):
    # If lst is empty then there are no permutations
    if len(lst) == 0:
        return []
        # If there is only one element in lst then, only
    # one permuatation is possible
    if len(lst) == 1:
        return [lst]
        # Find the permutations for lst if there are
    # more than 1 characters
    l = []  # empty list that will store current permutation
    # Iterate the input(lst) and calculate the permutation
    for i in range(len(lst)):
        m = lst[i]
        # Extract lst[i] or m from the list.  remLst is
        # remaining list
        remLst = lst[:i] + lst[i + 1:]
        # Generating all permutations where m is first
        # element
        for p in permutation(remLst):
            l.append([m] + p)
    return l


def comb(data, n):
    l = []
    for i in permutation(data):
        if i[:n] not in l:
            l.append(i[:n])
    return l
