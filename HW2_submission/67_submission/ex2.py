import itertools
from utils import (FIFOQueue)
ids = ['316406685', '205783244']


class Problem(object):

    def __init__(self, initial):
        self.initial = initial

    def actions(self, state):
        raise NotImplementedError

    def result(self, state, action):
        raise NotImplementedError


def is_valid_state(state1, state2):
    N_row = len(state1)
    N_cols = len(state1[0])
    for i in range(N_row):
        for j in range(N_cols):
            if state2[i][j] != '?' and state1[i][j] != state2[i][j]:
                return False
    return True


class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem, observations):
        valid_res = []
        for action in problem.actions(self.state):
            current_child = self.child_node(problem, action)
            if current_child.depth < len(observations) and is_valid_state(current_child.state[0], observations[current_child.depth]):
                valid_res.append(current_child)
        return valid_res

    def child_node(self, problem, action):
        next = problem.result(self.state, action)
        return Node(next, self, action)

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node.state[0])
            node = node.parent
        return list(reversed(path_back))

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)


def edit_init_state(state_map, i, j, letter):
    state_row_to_add = list(state_map[i])
    state_row_to_add[j] = letter
    state_map_to_return = state_map[:i] + (tuple(state_row_to_add), ) + state_map[i+1:]
    return state_map_to_return


class MedicalProblem(Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, init_map, N_cops, N_medics):
        self.Nrow = len(init_map)
        self.Ncol = len(init_map[0])
        init_state = (
            init_map,
            tuple((tuple(0 for j in range(self.Ncol)) for i in range(self.Nrow)))
        )
        self.Ncops = N_cops
        self.Nmedics = N_medics
        self.initial = init_map
        Problem.__init__(self, init_state)

    def actions(self, state):
        V = "vaccinate"
        Q = "quarantine"
        map_state = state[0]
        N_cops = self.Ncops
        N_medics = self.Nmedics
        S_indexes = []
        H_indexes = []
        for i in range(self.Nrow):
            for j in range(self.Ncol):
                if map_state[i][j] == 'S':
                    S_indexes.append((Q, (i, j)))
                elif map_state[i][j] == 'H':
                    H_indexes.append((V, (i, j)))

        final_sick = tuple(itertools.combinations(S_indexes, min(N_cops, len(S_indexes))))
        final_health = tuple(itertools.combinations(H_indexes, min(N_medics, len(H_indexes))))

        final_actions = []
        if min(N_cops, len(S_indexes)) == 0 and min(N_medics, len(H_indexes)) == 0:
            final_actions.append((),)
            return tuple(final_actions)

        if self.Ncops == 0:
            return tuple(final_health)
        elif self.Nmedics == 0:
            return tuple(final_sick)

        for sick_comb in final_sick:
            for health_comb in final_health:
                final_actions.append((sick_comb + health_comb))
        return tuple(final_actions)

    def result(self, state, action):
        state_map = state[0]
        state_map = [list(x) for x in state_map]
        counter_map = state[1]
        counter_map = [list(x) for x in counter_map]
        has_changed = list((list(0 for _ in range(self.Ncol)) for __ in range(self.Nrow)))

        #change according to actions
        for act in action:
            if len(act) < 1:
                continue
            act_index = act[1]
            act_index_row = act_index[0]
            act_index_col = act_index[1]
            act_type = act[0]
            if act_type == 'quarantine':
                state_map[act_index_row][act_index_col] = 'Q'
                counter_map[act_index_row][act_index_col] = 0
                has_changed[act_index_row][act_index_col] = 1
            elif act_type == 'vaccinate':
                state_map[act_index_row][act_index_col] = 'I'
                counter_map[act_index_row][act_index_col] = 0
                has_changed[act_index_row][act_index_col] = 1

        #H become S
        original_state_map = tuple(tuple(k) for k in state_map)
        for i in range(self.Nrow):
            for j in range(self.Ncol):
                if original_state_map[i][j] == 'H':
                    if (i != 0) and (original_state_map[i - 1][j] == 'S'):
                        state_map[i][j] = 'S'
                        counter_map[i][j] = 0
                        has_changed[i][j] = 1
                    elif (i != (self.Nrow - 1)) and (original_state_map[i + 1][j] == 'S'):
                        state_map[i][j] = 'S'
                        counter_map[i][j] = 0
                        has_changed[i][j] = 1
                    elif (j != 0) and (original_state_map[i][j - 1] == 'S'):
                        state_map[i][j] = 'S'
                        counter_map[i][j] = 0
                        has_changed[i][j] = 1
                    elif (j != (self.Ncol - 1)) and (original_state_map[i][j + 1] == 'S'):
                        state_map[i][j] = 'S'
                        counter_map[i][j] = 0
                        has_changed[i][j] = 1
                elif (original_state_map[i][j] == 'S') and (counter_map[i][j] == 2):
                    state_map[i][j] = 'H'
                    counter_map[i][j] = 0
                    has_changed[i][j] = 1
                elif (original_state_map[i][j] == 'Q') and (counter_map[i][j] == 1):
                    state_map[i][j] = 'H'
                    counter_map[i][j] = 0
                    has_changed[i][j] = 1
                if has_changed[i][j] != 1:
                    counter_map[i][j] += 1

        state_map = tuple(tuple(k) for k in state_map)
        counter_map = tuple(tuple(i) for i in counter_map)
        return tuple((state_map, counter_map))


def breadth_first_search(problem, max_depth, results_dict, init_state, observations):
    node = Node(problem.initial)
    frontier = FIFOQueue()
    frontier.append(node)
    explored = set()
    while frontier:
        node = frontier.pop()
        explored.add(node.state)
        for child in node.expand(problem, observations):
            if child.state not in explored and child not in frontier:
                if child.depth == max_depth - 1:
                    path = child.path()
                    results_dict[init_state].append(path)
                frontier.append(child)
    return None


def solve_problem(input):
    N_cops = input['police']
    N_medics = input['medics']
    observations = input['observations']
    init_state = observations[0]
    queries = input['queries']
    N_rows = len(observations[0])
    N_cols = len(observations[0][0])
    N_obs = len(observations)

    question_mark_list = []
    for i in range(N_rows):
        for j in range(N_cols):
            if init_state[i][j] == '?':
                question_mark_list.append((i, j))

    permutations = itertools.product(['H', 'S', 'U'], repeat=len(question_mark_list))

    possible_init_state = []
    init_option = init_state
    for per in permutations:
        for k, letter in enumerate(per):
            i, j = question_mark_list[k]
            init_option = edit_init_state(init_option, i, j, letter)
        possible_init_state.append(init_option)

    results_dict = {}

    for init_option in possible_init_state:
        results_dict[init_option] = []
        med_prob = MedicalProblem(Problem(init_option).initial, N_cops, N_medics)
        breadth_first_search(med_prob, N_obs, results_dict, init_option, observations)

    dict_to_return = {}
    for query in queries:
        i = query[0][0]
        j = query[0][1]
        t = query[1]
        state = query[2]
        answer_list = []
        for values in results_dict.values():
            if len(values) == 0:
                continue
            for path in values:
                if path[t][i][j] == state:
                    answer_list.append(True)
                else:
                    answer_list.append(False)

        if len(set(answer_list)) == 2:
            dict_to_return[query] = '?'
        else:
            if list(set(answer_list))[0]:
                dict_to_return[query] = 'T'
            else:
                dict_to_return[query] = 'F'
    return dict_to_return