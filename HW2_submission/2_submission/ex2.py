from itertools import permutations
from itertools import chain, combinations
from utils import FIFOQueue

infinity = float('inf')

ids = ["205542764", "312273063"]


def solve_problem(input):
    queries = input['queries']
    goal_dict = {}
    first_dict = {}
    questions_idx = []
    board = input['observations'][0]
    for i in range(len(board)):  # rows
        for j in range(len(board[0])):  # cols
            if board[i][j][0] == '?':
                questions_idx.append((i, j))
    options = ['U', 'H', 'S'] * len(questions_idx)
    changing = changing_val_in_idx(options, len(questions_idx))
    new_states = []
    for change in changing:
        temp_state = [list(x) for x in board]
        j = 0
        for i in range(len(questions_idx)):
            temp_state[questions_idx[i][0]][questions_idx[i][1]] = change[j]
            j += 1
        new_states.append(temp_state)
        # new_states holds all the possible new boards after assignments
    temp_tuple = tuple([tuple([tuple(x) for x in new_states[i]]) for i in range(len(new_states))])
    for i in range(len(temp_tuple)):
        first_dict[(temp_tuple[i])] = []
    for state in new_states:
        problem = MedicalProblem(Problem(input).initial, state)
        # print("rrrr", problem.initial)
        breadth_first_search(problem, len(input['observations']), state, first_dict)
    # checking according to queries
    for q in queries:
        goal_dict[tuple(q)] = []
    for q in queries:
        idx = q[0]
        turn = q[1]
        letter = q[2]
        true_flag = False
        false_flag = False
        no_question_flag = True
        if no_question_flag:
            for d in first_dict.keys():
                    if no_question_flag:
                            for val in first_dict[d]:
                                if check_query(idx, turn, letter, val) == 0:
                                    false_flag = True
                                else:
                                    true_flag = True
                                goal_dict[q].append(check_query(idx, turn, letter, val))
                                if 0 in goal_dict[q] and 1 in goal_dict[q]:
                                    goal_dict[q] = "?"
                                    no_question_flag = False
                                    break
        if no_question_flag:
            if true_flag:
                goal_dict[q] = 'T'
            elif false_flag:
                goal_dict[q] = 'F'
    return goal_dict


def check_query(idx, turn, letter, paths):
    if paths[turn][idx[0]][idx[1]][0] == letter:
        return 1
    return 0


def changing_val_in_idx(options, l):
    new_options = []
    for p in permutations(options):
        if p[:l] not in new_options:
            new_options.append(p[:l])
    return new_options


def possible_assignment(check_board, input_board):
    # print("input_board:",input_board)
    # print(len(check_board))
    # print(len(input_board))
    for i in range(len(input_board)):  # rows
        for j in range(len(input_board[0])):  # cols
            if input_board[i][j][0] != "?":
                if input_board[i][j] == "H" and check_board[i][j][0] != "H":
                    return False
                elif input_board[i][j] == "U" and check_board[i][j][0] != "U":
                    return False
                elif input_board[i][j] == "I" and check_board[i][j][0] != "I":
                    return False
                elif input_board[i][j] == "Q" and check_board[i][j][0] != "Q":
                    return False
    return True


class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        # self.state = tuple([tuple(x) for x in state])
        self.state=state
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

    def expand(self, problem, num_observe, obs):
        ok_array = []

        for action in problem.actions(self.state):
            child = self.child_node(problem, action)
            if child.depth <= num_observe - 1:
                if possible_assignment(child.state, obs[child.depth]):
                    ok_array.append(child)
        return ok_array

    def child_node(self, problem, action):
        """[Figure 3.10]"""
        # print(problem,"kk")
        next = problem.result(self.state, action)
        return Node(next, self, action)

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)

    def find_dynasty(self):
        # returning the list of dynasty till the root
        node = self
        dynasty = []
        while node:
            dynasty.append(node.state)
            node = node.parent
        # dynasty=dynasty[::-1]
        return list(reversed(dynasty))


def breadth_first_search(problem, num_observe, board, dict_bfs):
    node = Node(problem.initial)
    frontier = FIFOQueue()
    frontier.append(node)
    explored = set()
    tmp_board = tuple([tuple(x) for x in board])
    while frontier:
        node = frontier.pop()
        explored.add(node.state)
        for child in node.expand(problem, num_observe, problem.obs_tup):
            if child.state not in explored and child not in frontier:
                if child.depth == num_observe - 1:
                    path = child.find_dynasty()
                    dict_bfs[tmp_board].append(path)
                frontier.append(child)
    return None


class Problem(object):
    def __init__(self, initial):
        self.initial = initial

    def actions(self, state):
        raise NotImplementedError

    def result(self, state, action):
        raise NotImplementedError


class MedicalProblem(Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial, board):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        self.police = initial["police"]
        self.medics = initial["medics"]
        self.initial = initial["observations"]
        self.rows = len(self.initial[0])
        self.cols = len(self.initial[0][0])
        self.obs_tup = tuple(initial["observations"])
        state1 = [[(0, 0) for i in range(self.cols)] for j in range(self.rows)]
        for i in range(self.rows):
            for j in range(self.cols):
                if board[i][j] == 'S':
                    state1[i][j] = (board[i][j], 3)
                elif board[i][j] == 'Q':
                    state1[i][j] = (board[i][j], 2)
                else:
                    state1[i][j] = (board[i][j], 0)
        state1 = tuple(tuple(sub) for sub in state1)
        self.state1 = state1
        self.initial = state1

        Problem.__init__(self, self.initial)

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        possible_actions = []
        v_actions = []
        q_actions = []
        s_counter = 0
        h_counter = 0
        for i in range(self.rows):
            for j in range(self.cols):
                if state[i][j][0] == "H":
                    v_actions.append(("vaccinate", (i, j)))
                    h_counter += 1
                elif state[i][j][0] == "S":
                    s_counter += 1
                    q_actions.append(("quarantine", (i, j)))
        if h_counter >= self.medics:
            v_combs = list(
                chain.from_iterable(combinations(v_actions, r) for r in range(self.medics, self.medics + 1)))
        else:
            v_combs = list(chain.from_iterable(combinations(v_actions, r) for r in range(self.medics + 1)))
        q_combs = list(chain.from_iterable(combinations(q_actions, r) for r in range(self.police + 1)))
        max_s = list(chain.from_iterable(combinations(q_actions, r) for r in range(self.police, self.police + 1)))
        if len(v_combs) == 0 and len(q_combs) == 0:
            return []
        if len(v_combs) == 0 and len(q_combs) != 0:
            return q_combs
        if len(v_combs) != 0 and len(q_combs) == 0:
            return v_combs
        if s_counter <= self.police:
            return q_combs
        for i in range(len(v_combs)):
            for j in range(len(max_s)):
                possible_actions.append(v_combs[i] + max_s[j])
        return possible_actions

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        state_l = [[(0, 0) for i in range(self.cols)] for j in
                   range(self.rows)]
        for i in range(self.rows):
            for j in range(self.cols):
                state_l[i][j] = state[i][j]
        for act in action:
            if act[0] == "vaccinate":
                state_l[act[1][0]][act[1][1]] = ("I", 0)
            if act[0] == "quarantine":
                state_l[act[1][0]][act[1][1]] = ("Q", 3)
        for i in range(self.rows):
            for j in range(self.cols):
                if state_l[i][j][0] == "H":
                    if self.check_s_neighbors(state_l, i, j):
                        state_l[i][j] = ("H", 4)
                elif state_l[i][j][0] == "S":
                    state_l[i][j] = ("S", (state_l[i][j][1]) - 1)
                elif state_l[i][j][0] == "Q":
                    state_l[i][j] = ("Q", (state_l[i][j][1]) - 1)
        for i in range(self.rows):
            for j in range(self.cols):
                if (state_l[i][j][0] == "S" or state_l[i][j][0] == "Q") and (state_l[i][j][1] == 0):
                    state_l[i][j] = ("H", 0)
                if state_l[i][j] == ("H", 4):
                    state_l[i][j] = ("S", 3)
        new_state = tuple(tuple(sub) for sub in state_l)
        return new_state

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        # for i in range(self.rows):
        win = True
        for i in range(self.rows):
            for j in range(self.cols):
                if state[i][j][0] == "S":
                    win = False
                    break
        return win

    def check_s_neighbors(self, state, irow, jcol):
        locations = [False] * 4
        sick_neighbor = False
        if irow == 0:
            locations[0] = True
        if irow == self.rows - 1:
            locations[1] = True
        if jcol == 0:
            locations[2] = True
        if jcol == self.cols - 1:
            locations[3] = True
        if not locations[0]:
            if state[irow - 1][jcol][0] == 'S':
                sick_neighbor = True
        if not locations[1]:
            if state[irow + 1][jcol][0] == 'S':
                sick_neighbor = True
        if not locations[2]:
            if state[irow][jcol - 1][0] == 'S':
                sick_neighbor = True
        if not locations[3]:
            if state[irow][jcol + 1][0] == 'S':
                sick_neighbor = True
        return sick_neighbor
