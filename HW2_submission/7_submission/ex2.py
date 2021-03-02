ids = ['313354235', '318358090']
import itertools
from itertools import combinations
from utils import (
    is_in, argmin, argmax, argmax_random_tie, probability, weighted_sampler,
    memoize, print_table, open_data, Stack, FIFOQueue, PriorityQueue, name,
    distance
)


class Problem(object):

    """The abstract class for a formal problem.  You should subclass
    this and implement the methods actions and result, and possibly
    __init__, goal_test, and path_cost. Then you will create instances
    of your subclass and solve them with the various search functions."""

    def __init__(self, initial, goal=None):
        """The constructor specifies the initial state, and possibly a goal
        state, if there is a unique goal.  Your subclass's constructor can add
        other arguments."""
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        raise NotImplementedError

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        raise NotImplementedError


class Node:

    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state.  Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node.  Other functions
    may add an f and h value; see best_first_graph_search and astar_search for
    an explanation of how the f and h values are handled. You will not need to
    subclass this class."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def expand(self, problem):
        """List the nodes reachable in one step from this node."""
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        """[Figure 3.10]"""
        next = problem.result(self.state, action)
        return Node(next, self, action)

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

def checks_if_kid_is_valid(child, obs_t):
    # print("in checks if kis is valid")
    # print("compared to: ", obs_t)
    for i in range(len(child)):
        for j in range(len(child[0])):
            if obs_t[i][j] != '?' and obs_t[i][j] not in child[i][j]:
                    # print("not supposed to be here!!")
                    # print("child in i, j: ", child[i][j], i, j)
                    return 0
    return 1

def create_valid_kids_list(children_list, problem):
    valid_kids_list = []
    child_depth = children_list[0].depth
    obs_t = problem.observations[child_depth]
    # print("obs_t:", obs_t)
    for child in children_list:
        # print("child.state:", child.state)
        if checks_if_kid_is_valid(child.state, obs_t):
            # print("I checked if kid is valid")
            valid_kids_list.append(child)
    # print("valid_kids_list:", valid_kids_list)
    return valid_kids_list

def breadth_first_search(problem):
    """[Figure 3.11]"""
    node = Node(problem.initial)
    # if problem.goal_test(node.state):
    #     return node
    frontier = FIFOQueue()
    frontier.append(node)
    explored = set()
    while frontier:
        node = frontier.pop()
        # print("here")
        explored.add(node.state)
        # print("explored:", explored)
        children_list = node.expand(problem)
        # print("children list:", children_list, "of node:", node.state)
        valid_kids_list = create_valid_kids_list(children_list, problem)
        # print("valid kids:", valid_kids_list)
        final_children = []
        for child in valid_kids_list:
            if child.state not in explored and child not in frontier:
                if child.depth == len(problem.observations) - 1:
                    final_children.append(child)
                    # return child
                else:
                    frontier.append(child)
    return final_children
    # return None


class MedicalProblem(Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial, permutation):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        self.police = initial["police"]
        self.medics = initial["medics"]
        self.observations = initial["observations"]
        self.obs0 = self.observations[0]
        self.queries = initial["queries"]
        self.permutation = permutation
        self.rows = len(self.permutation)
        self.cols = len(self.permutation[0])
        Problem.__init__(self, self.permutation)

    def better_powerset(self, l_action_units, n):
        c = []
        for i in range(n+1):
            c.extend(combinations(l_action_units, i))
        return tuple(c)

    def count_str(self, combo, str):
        k = len(combo)
        count = 0
        for i in range(k):
            if combo[i][0] == str:
                count += 1
        return count

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        action_units = []
        count_s = 0
        count_h = 0
        possibility = ["quarantine", "vaccinate"]
        for i in range(self.rows):
            for j in range(self.cols):
                if 'S' in state[i][j]:
                    action_units.append((possibility[0], (i, j)))
                    count_s += 1
                elif state[i][j] == 'H':
                    count_h += 1
                    action_units.append((possibility[1], (i, j)))
        combo_actions = self.better_powerset(action_units, self.police + self.medics)
        possible_actions = []
        final_possible_actions = []
        for combo in combo_actions:
            count_quarantine = self.count_str(combo, "quarantine")
            count_vaccinate = self.count_str(combo, "vaccinate")
            if (count_quarantine <= self.police) and (count_vaccinate <= self.medics):
                # possible_actions.append(combo)
                # return tuple(possible_actions)
                if count_s >= self.police:
                    if (count_quarantine == self.police):
                        possible_actions.append(combo)
                elif (count_s < self.police):
                    if (count_quarantine == count_s):
                        possible_actions.append(combo)

        if count_h != 0:
            for pa in possible_actions:
                count_vaccinate = self.count_str(pa, "vaccinate")
                if count_h >= self.medics:
                    if count_vaccinate == self.medics:
                        final_possible_actions.append(pa)
                elif count_h < self.medics:
                    if count_vaccinate == count_h:
                        final_possible_actions.append(pa)
            # print("final_possible_actions:", final_possible_actions)
            return tuple(final_possible_actions)
        else:
            # print("possible_actions:", possible_actions)
            return tuple(possible_actions)

    def result(self, state, action):

        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        list_state = [list(tup) for tup in state]
        dict_action = {"vaccinate": "I", "quarantine": "Q"}
        change_dict = {"X": "S", "U": "U", "I": "I", "H": "H", "S": "S1", "S1": "S2", "S2": "H", "Q": "Q1",
                       "Q1": "H"}
        coordinates = []
        for action_unit in action:
            coordinates.append(action_unit[1])
            list_state[action_unit[1][0]][action_unit[1][1]] = dict_action[action_unit[0]]
        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) not in coordinates:
                    if list_state[i][j] == 'H':
                        if j + 1 < self.cols:
                            if 'S' in list_state[i][j+1]:
                                list_state[i][j] = 'X'
                        if j - 1 >= 0:
                            if 'S' in list_state[i][j - 1]:
                                list_state[i][j] = 'X'
                        if i + 1 < self.rows:
                            if 'S' in list_state[i+1][j]:
                                list_state[i][j] = 'X'
                        if i - 1 >= 0:
                            if 'S' in list_state[i-1][j]:
                                list_state[i][j] = 'X'
        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) not in coordinates:
                    list_state[i][j] = change_dict[list_state[i][j]]
        new_state = [tuple(x) for x in list_state]
        return tuple(new_state)

def create_permutations(observation0):
    letters = ['H', 'S', 'U']
    count_qu_mark = 0
    for i in range(len(observation0)):
        for j in range(len(observation0[0])):
            if observation0[i][j] == '?':
                count_qu_mark += 1
    if count_qu_mark == 0:
        # print("count qu mark == 0")
        # print("obs 0:", observation0)
        return [observation0]
    perms = []
    for p in itertools.product(letters, repeat = count_qu_mark):
        perms.append(p)
    final_perms = []
    for per in perms:
        per_idx = 0
        matrix_perm = [list(li) for li in observation0]
        for i in range(len(observation0)):
            for j in range(len(observation0[0])):
                if observation0[i][j] == '?':
                    matrix_perm[i][j] = per[per_idx]
                    per_idx += 1
        final_perms.append(matrix_perm)
    return final_perms

def checks_if_query_T_F(path, query):
    matrix = path[query[1]].state
    # print("the matrix is:", matrix)
    # print("path len:", len(path))
    # print("turn in query:", query[1])
    # print("(i,j) = ", query[0][0], query[0][1])
    return query[2] in matrix[query[0][0]][query[0][1]]

def solve_problem(input):
    possible_paths = []
    query_dict = {}
    permutations = create_permutations(input["observations"][0])
    for perm_not_tup in permutations:
        perm = tuple([tuple(x) for x in perm_not_tup])
        # print("current permutation: ", perm)
        problem = MedicalProblem(input, perm)
        # possible_bfs_kid = breadth_first_search(problem)
        possible_bfs_kids = breadth_first_search(problem)
        # print("possible_bfs_kids:", possible_bfs_kids)
        for kid in possible_bfs_kids:
            # if kid != None:
            possible_paths.append(kid.path())
            # print("possible_path:",possible_bfs_kid.path())
    queries_tup = tuple([tuple(x) for x in problem.queries])
    # print("querie tup:", queries_tup)
    # print("final possible paths: ", possible_paths)
    for q in queries_tup:
        l_queries = []
        for idx, path in enumerate(possible_paths):
            # print("path is:", path)
            # print("idx in possible paths: ", idx)
            l_queries.append(checks_if_query_T_F(path, q))
        query_dict[q] = l_queries
        # query_dict[q] = [checks_if_query_T_F(path, q) for path in possible_paths]
        # print("query:",q, "possible answeres:", query_dict[q])
    for k in query_dict.keys():
        if 1 in query_dict[k] and 0 in query_dict[k]:
            query_dict[k] = '?'
        elif 1 not in query_dict[k]:
            query_dict[k] = 'F'
        elif 0 not in query_dict[k]:
            query_dict[k] = 'T'

    return query_dict


