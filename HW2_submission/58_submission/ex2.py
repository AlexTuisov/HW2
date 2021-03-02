from itertools import chain, combinations, product

ids = ["206203226", "205906225"]

def all_repeat(str1, rno):
  chars = list(str1)
  results = []
  for c in product(chars, repeat = rno):
    results.append(c)
  return results

def powerset1(iterable, r):
    empty_list = []
    if (r == 0):
        return empty_list
    s = list(iterable)
    return list(chain.from_iterable(combinations(s, i) for i in range(0, r + 1)))[1:]

def find_height_neighbors(self, row_idx, col_idx):
    if (row_idx == 0):
        height_neighbors = [(row_idx+1, col_idx)]
    elif (row_idx == self.row_number-1):
        height_neighbors = [(row_idx-1, col_idx)]
    else:
        height_neighbors = [(row_idx+1, col_idx), (row_idx-1, col_idx)]
    return height_neighbors

def find_width_neighbors(self, row_idx, col_idx):
    if (col_idx == 0):
        width_neighbors = [(row_idx, col_idx+1)]
    elif (col_idx == self.col_number-1):
        width_neighbors = [(row_idx, col_idx-1)]
    else:
        width_neighbors = [(row_idx, col_idx+1), (row_idx, col_idx-1)]
    return width_neighbors


"""Search (Chapters 3-4)

The way to use this code is to subclass Problem to create a class of problems,
then create problem instances and solve them with calls to the various search
functions."""

from utils import (
    is_in, argmin, argmax, argmax_random_tie, probability, weighted_sampler,
    memoize, print_table, open_data, Stack, FIFOQueue, PriorityQueue, name,
    distance
)

infinity = float('inf')

# ______________________________________________________________________________


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

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        if isinstance(self.goal, list):
            return is_in(state, self.goal)
        else:
            return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1

    def value(self, state):
        """For optimization problems, each state has a value.  Hill-climbing
        and related algorithms try to maximize this value."""
        raise NotImplementedError
# ______________________________________________________________________________


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

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        """List the nodes reachable in one step from this node."""
        valid_children_list = []

        for action in problem.actions(self.state):
            x = self.child_node(problem, action)
            question_mark_count = 0
            count_equalities = 0
            if x.depth < len(problem.observation_list):
                for i in range(0, len(problem.observation_list[x.depth])):
                    for j in range(0, len(problem.observation_list[x.depth][0])):
                        if problem.observation_list[x.depth][i][j] == '?':
                            question_mark_count += 1

                for row in range(0, len(problem.observation_list[x.depth])):
                    for column in range(0, len(problem.observation_list[x.depth][0])):
                        if x.state[row][column][0] == problem.observation_list[x.depth][row][column]:
                            count_equalities += 1
                if count_equalities == ((len(problem.observation_list[x.depth])*len(problem.observation_list[x.depth][0]))-question_mark_count):
                    valid_children_list.append(x)

        return valid_children_list


    def child_node(self, problem, action):
        """[Figure 3.10]"""
        next = problem.result(self.state, action)


        return Node(next, self, action,
                    problem.path_cost(self.path_cost, self.state,
                                      action, next))

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node.state)
            node = node.parent
        return list(reversed(path_back))

    # We want for a queue of nodes in breadth_first_search or
    # astar_search to have no duplicated states, so we treat nodes
    # with the same state as equal. [Problem: this may not be what you
    # want in other contexts.]

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)

# ______________________________________________________________________________

def breadth_first_search(problem):
    """[Figure 3.11]"""
    node = Node(problem.initial)

    frontier = FIFOQueue()
    frontier.append(node)
    explored = set()
    child_path = []
    while frontier:
        node = frontier.pop()
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                if child.depth == len(problem.observation_list)-1:
                    child_path.append(child.path())
                frontier.append(child)

    return child_path


# ______________________________________________________________________________


class MedicalProblem(Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial, first_map_permutation=None):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        self.police = int(initial.get("police"))
        self.medics = int(initial.get("medics"))
        self.observation_list = initial.get("observations")
        self.row_number = len(self.observation_list[0])
        self.col_number = len(self.observation_list[0][0])

        for i in range(0, self.row_number):
            first_map_permutation[i] = list(first_map_permutation[i])
            for j in range (0, self.col_number):
                if first_map_permutation[i][j] == 'S':
                    first_map_permutation[i][j] = ('S', 3)
                if first_map_permutation[i][j] == 'H' or first_map_permutation[i][j] == 'U':
                    first_map_permutation[i][j] = (first_map_permutation[i][j], None)

        for i in range(0, self.row_number):
            first_map_permutation[i] = tuple(first_map_permutation[i])
        self.first_map = tuple(first_map_permutation)
        initial1 = self.first_map
        Problem.__init__(self, initial1)


    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        vaccinate_actions = []
        quarantine_actions = []

        for i in range(0, self.row_number):
            for j in range(0, self.col_number):
                if state[i][j][0] == 'H':
                    vaccinate_actions.append(('vaccinate', (i, j)))
                if state[i][j][0] == 'S':
                    quarantine_actions.append(('quarantine', (i, j)))
        vaccinate_actions_pre = powerset1(vaccinate_actions, self.medics)
        quarantine_actions_pre = powerset1(quarantine_actions, self.police)
        vaccinate_actions_tup = vaccinate_actions_pre
        quarantine_actions_tup = quarantine_actions_pre

        if ((len(vaccinate_actions_tup) == 0) and (len(quarantine_actions_tup) != 0)):
            possible_actions = quarantine_actions_tup
        elif ((len(quarantine_actions_tup) == 0) and (len(vaccinate_actions_tup) != 0)):
            possible_actions = vaccinate_actions_tup
        elif ((len(quarantine_actions_tup) == 0) and (len(vaccinate_actions_tup) == 0)):
            possible_actions = [()]
        else:
            possible_actions = tuple()
            for action_p in quarantine_actions_tup:
                for action_m in vaccinate_actions_tup:
                    action_m += (action_p, )
                    possible_actions += (action_m, )
            possible_actions += vaccinate_actions_tup + quarantine_actions_tup

        return tuple(possible_actions)


    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        state1 = list(state)

        for i in range(0, self.row_number):
            state1[i] = list(state1[i])
            for j in range(0, self.col_number):
                state1[i][j] = list(state1[i][j])

        if(len(action) != 0):
            for act in action:
                if len(action) != 1:
                    for act_i in act:
                        if act_i[0] == "quarantine":
                            i = act_i[1][0]
                            j = act_i[1][1]
                            state1[i][j][0] = "Q"
                            state1[i][j][1] = 3
                        elif act_i[0] == "vaccinate":
                            i = act_i[1][0]
                            j = act_i[1][1]
                            state1[i][j][0] = "I"
                            state1[i][j][1] = None
                else:
                    if act[0] == "quarantine":
                        i = act[1][0]
                        j = act[1][1]
                        state1[i][j][0] = "Q"
                        state1[i][j][1] = 3
                    elif act[0] == "vaccinate":
                        i = act[1][0]
                        j = act[1][1]
                        state1[i][j][0] = "I"
                        state1[i][j][1] = None

        for i in range(0, self.row_number):
            for j in range(0, self.col_number):

                flag = False
                if(state1[i][j][0] == 'H'):
                    neighbors = find_height_neighbors(self, i, j) + find_width_neighbors(self, i, j)
                    for n in range(0, len(neighbors)):
                        neighbor_row = neighbors[n][0]
                        neighbor_col = neighbors[n][1]
                        if ((state1[neighbor_row][neighbor_col][0] == 'S') and (state1[neighbor_row][neighbor_col][1] != 4) and (flag == False)):
                            state1[i][j][0] = 'S'
                            state1[i][j][1] = 4
                            flag = True

        for i in range(0, self.row_number):
            for j in range(0, self.col_number):
                if(state1[i][j][1] != None):
                    if(state1[i][j][1] == 1):
                        state1[i][j][0] = 'H'
                        state1[i][j][1] = None
                    else:
                        state1[i][j][1] -= 1


        for i in range(0, self.row_number):
            for j in range(0, self.col_number):
                state1[i][j] = tuple(state1[i][j])
            state1[i] = tuple(state1[i])


        return tuple(state1)

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        for i in range(0, self.row_number):
            for j in range(0, self.col_number):
                if(state[i][j] == 'S'):
                    return False
        return True

def solve_problem(input):
    #pass
    observations_list = input.get("observations")
    queries_list = input.get("queries")
    row_number = len(observations_list[0])
    col_number = len(observations_list[0][0])
    first_map = list(observations_list[0])
    question_mark_count = 0
    question_mark_list = []
    for i in range(0, row_number):
        first_map[i] = list(first_map[i])
        for j in range(0, col_number):
            if first_map[i][j] == '?':
                question_mark_count += 1
                question_mark_list.append((i, j))

    permutation_list = all_repeat('HSU', question_mark_count)

    optional_first_map = []
    for p1 in range(0, len(permutation_list)):
        first_map = list(observations_list[0])
        temp = [list(i) for i in first_map]
        for p2 in range(0, len(permutation_list[p1])):
            for i in range(0, len(question_mark_list)):
                temp[question_mark_list[i][0]][question_mark_list[i][1]] = permutation_list[p1][p2]
                optional_first_map.append(temp)


    result_list = []

    if (len(optional_first_map) == 0):
        p = MedicalProblem(input, first_map)
        result_list.append(breadth_first_search(p))

    else:
        for i in range(0, len(optional_first_map)):
            p = MedicalProblem(input, optional_first_map[i])
            result_list.append(breadth_first_search(p))



    answers_dict = {}
    ans_list = []
    for q in range(0, len(queries_list)):
        temp_list = []
        for r in range(0, len(result_list)):
            if len(result_list[r]) == 0:
                temp_list.append('F')
            else:
                map_row_index = queries_list[q][0][0]
                map_col_index = queries_list[q][0][1]
                time_index = queries_list[q][1]
                path_in_per = []
                for p in range(0, len(result_list[r])):
                    if time_index <= len(result_list[r][p])-1:
                        if result_list[r][p][time_index][map_row_index][map_col_index][0] == queries_list[q][2]:
                            path_in_per.append('T')
                        else:
                            path_in_per.append('F')
                    else:
                        path_in_per.append('F')
                for i in range(0, len(path_in_per)):
                    first_value = path_in_per[0]
                    flag = True
                    for j in range(1, len(path_in_per)):
                        if path_in_per[i] != first_value:
                            per_true = '?'
                            flag = False

                    if first_value == 'F' and flag == True:
                        per_true = 'F'

                    elif first_value == 'T' and flag == True:
                        per_true = 'T'
                temp_list.append(per_true)

        ans_list.append(temp_list)


    count_true_q = []
    count_false_q = []
    count_question_q = []

    for q in range(0, len(queries_list)):
        count_true = 0
        count_false = 0
        count_question = 0
        for a in range(0, len(ans_list[q])):
            if ans_list[q][a] == 'T':
                count_true += 1
            if ans_list[q][a] == 'F':
                count_false += 1
            if ans_list[q][a] == '?':
                count_question += 1
        count_true_q.append(count_true)
        count_false_q.append(count_false)
        count_question_q.append(count_question)


    for q in range(0, len(queries_list)):
        for a in range(0, len(ans_list[q])):
            if (count_true_q[q] == 0 and count_question_q[q] >= 1) or count_true_q[q] > 1:
                answers_dict[queries_list[q]] = '?'
            elif count_false_q[q] == len(ans_list[q]):
                answers_dict[queries_list[q]] = 'F'
            elif count_true_q[q] == 1:
                answers_dict[queries_list[q]] = 'T'

    return answers_dict