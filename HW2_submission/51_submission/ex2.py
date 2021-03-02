import copy
import time
from itertools import permutations
from itertools import chain, combinations
from utils import (
    is_in, argmin, argmax, argmax_random_tie, probability, weighted_sampler,
    memoize, print_table, open_data, Stack, FIFOQueue, PriorityQueue, name,
    distance
)

ids = ['205889892', '205907132']

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

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def our_powerset(self, s, num):
        return list(chain.from_iterable(combinations(s, r)  for r in range(num, num+1)))

    def our_powerset_old(self, s, num):
        return list(chain.from_iterable(combinations(s, r) for r in range(num+1)))[1:]

    def actions(self, state, Pteam, Mteam):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        # SAVE VARIABLES
        posH = []
        posS = []
        policeAct = []
        medicalAct = []
        num_rows = len(state)
        num_cols = len(state[0])

        for idx in range(num_rows):
            for idy in range(num_cols):
                if state[idx][idy] == 7:
                    posH.append([idx, idy])
                if state[idx][idy] in [0, 1, 2]:
                    posS.append([idx, idy])

        for ids in posS:
            policeAct.append(("quarantine", tuple(ids)))

        for idh in posH:
            medicalAct.append(("vaccinate", tuple(idh)))

        num_p_actions = min(Pteam, len(posS))
        num_m_actions = min(Mteam, len(posH))
        posSpow = self.our_powerset(policeAct, num_p_actions)
        posHpow = self.our_powerset(medicalAct, num_m_actions)

        actions = []
        if Pteam > 0 and Mteam > 0:
            if Pteam >= Mteam:
                for i in posSpow:
                    for j in posHpow:
                        actions.append(tuple(list(i) + list(j)))

            else:
                for i in posHpow:
                    for j in posSpow:
                        actions.append(tuple(list(j) + list(i)))
        else:
            if Pteam == 0:
                actions = (tuple(posHpow[i] for i in range(len(posHpow))))
            elif Mteam == 0:
                actions = tuple(posSpow[i] for i in range(len(posSpow)))
        actions = tuple(actions)

        return actions

    def check_neighbors(self, loc, state):
        # North, South, East, West
        neighbors = [-1, -1, -1, -1]
        if loc[0] > 0:
            neighbors[0] = state[loc[0] - 1][loc[1]]
        if loc[0] < (len(state) - 1):
            neighbors[1] = state[loc[0] + 1][loc[1]]
        if loc[1] > 0:
            neighbors[2] = state[loc[0]][loc[1] - 1]
        if loc[1] < (len(state[0]) - 1):
            neighbors[3] = state[loc[0]][loc[1] + 1]
        return neighbors


    def result(self, state, action, Pteam, Mteam):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        action = [action[i] for i in range(len(action))]
        new_state = [list(i) for i in state]
        num_rows = len(new_state)
        num_cols = len(new_state[0])
        if len(action) > 0:
            if Pteam + Mteam > 1:
                for single_action in action:
                    if single_action == ():
                        continue
                    idx = single_action[1][0]
                    idy = single_action[1][1]
                    if single_action[0] == "vaccinate":
                        # I=8
                        new_state[idx][idy] = 8
                    elif single_action[0] == "quarantine":
                        # Q=4,5,6
                        new_state[idx][idy] = 6
            elif Pteam + Mteam == 1:
                idx = action[0][1][0]
                idy = action[0][1][1]
                cur_command = action[0][0]
                if len(action[0]) > 0:
                    if cur_command == "vaccinate":
                        # I=8
                        new_state[idx][idy] = 8
                    elif cur_command == "quarantine":
                        new_state[idx][idy] = 6

        for i in range(num_rows):
            for j in range(num_cols):
                # H=7
                if new_state[i][j] == 7:
                    orientations = [i, j]
                    h_neighbors = self.check_neighbors(orientations, new_state)
                    if h_neighbors.count(0)+ h_neighbors.count(1)+h_neighbors.count(2) > 0:
                        new_state[i][j] = 3

        """ Find all S to be recovered and turn them into H
        Find all Q to be healthy and turn them into H
        Update the true value of remaining turns for Q, S """

        for i in range(num_rows):
            for j in range(num_cols):
                # S=0,1,2,3 ;  Q=4,5,6
                if new_state[i][j] == 0 or new_state[i][j] == 4:
                    # H=7
                    new_state[i][j] = 7
                elif new_state[i][j] in [1, 2, 3, 5, 6]:
                    new_state[i][j] -= 1

        new_state = tuple(tuple(i) for i in new_state)
        return new_state


    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)


class MedicalProblem(object):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        self.police = initial["police"]
        self.medical = initial["medics"]
        self.map_list = self.make_map(initial["observations"])
        self.num_turns = (len(self.map_list))
        self.queries = initial["queries"]

    def make_map(self, game_maps):
        x_dim = len(game_maps[0])
        y_dim = len(game_maps[0][0])
        final_map_list = []
        for cur_game in game_maps:
            cur_game = [list(cur_game[j]) for j in range(x_dim)]
            for i in range(x_dim):
                for j in range(y_dim):
                    cur_tile = cur_game[i][j]
                    if cur_tile == "U":
                        cur_game[i][j] = 9
                    elif cur_tile == "H":
                        cur_game[i][j] = 7
                    elif cur_tile == "S":
                        cur_game[i][j] = 2
                    elif cur_tile == 'I':
                        cur_game[i][j] = 8
                    elif cur_tile == 'Q':
                        cur_game[i][j] = 5

            final_map_list.append(tuple(tuple(i) for i in cur_game))
        return final_map_list


    def combinations(self, first_map):
        unknown_tiles = []
        for i in range(len(first_map)):
            for j in range(len(first_map[0])):
                if first_map[i][j] == "?":
                    unknown_tiles.append([i, j])
        num_unknown = len(unknown_tiles)
        combi_list = []
        combi_list.append([2, 7, 9]*num_unknown)
        combi_list = combi_list[0]
        perm = list(permutations(combi_list, num_unknown))
        perm = list(dict.fromkeys(perm))
        return unknown_tiles, perm


def can_be_identical(template, cur_state):
    for i in range(len(template)):
        for j in range(len(template[0])):
            temp_tile = template[i][j]
            state_tile = cur_state[i][j]
            if state_tile in [0, 1, 2]:
                if temp_tile != 2 and temp_tile != '?':
                    return False
            elif state_tile in [4, 5]:
                if temp_tile != 5 and temp_tile != '?':
                    return False
            elif temp_tile != state_tile and temp_tile != '?':
                return False
    return True


def answer_queries_init(game):
    sol = {}
    single_template = game.map_list[0]
    for key in game.queries:
        idx = key[0][0]
        idy = key[0][1]
        val = single_template[idx][idy]
        if val == "?":
            if key[2] == 'Q' or key[2] == 'I':
                sol[key] = 'F'
            else:
                sol[key] = '?'
        else:
            if val == 7:
                val = 'H'
            elif val == 2:
                val = 'S'
            elif val == 9:
                val = 'U'
            if key[2] == val:
                sol[key] = 'T'
            else:
                sol[key] = 'F'
    return sol


def answer_queries_false(queries):
    sol = {}
    for key in queries:
        sol[key] = 'F'
    return sol


def answer_queries(leaf_node, queries):
    """
    :param leaf_node: curr state
    :param game: MedicalProblem object
    :return list of legnth # num queries with values True / False:
    """

    dup = copy.deepcopy(leaf_node)
    answer_list = [False]*len(queries)
    not_root = True
    while dup.depth >= 0 and not_root:
        query_count = 0
        for i in queries:
            if dup.depth == i[1]:
                idx = i[0][0]
                idy = i[0][1]
                query_val = i[2]
                state_val = dup.state[idx][idy]
                if query_val == 'U':
                    if state_val == 9:
                        answer_list[query_count] = True
                elif query_val == 'I' and dup.depth != 0:
                    if state_val == 8:
                        answer_list[query_count] = True
                elif query_val == 'H':
                    if state_val == 7:
                        answer_list[query_count] = True
                elif query_val == 'Q' and dup.depth != 0:
                    if state_val == 5 or state_val == 4:
                        answer_list[query_count] = True
                elif query_val == 'S':
                    if state_val == 2 or state_val == 1 or state_val == 0:
                        answer_list[query_count] = True
            query_count += 1

        if dup.depth > 0:
            x = dup.parent
            dup = x
        else:
            not_root = False

    return answer_list


def fill_q_mark(init_map, coordinations, cur_per):
    new_root = [list(i) for i in init_map]
    for i in range(len(coordinations)):
        idx = coordinations[i][0]
        idy = coordinations[i][1]
        new_root[idx][idy] = cur_per[i]
    new_state = tuple(tuple(i) for i in new_root)
    return new_state


def breadth_first_search(problem):
    """[Figure 3.11]"""
    node_count = 0
    leaf_counter = 0
    game = MedicalProblem(problem)
    Pteam, Mteam = game.police, game.medical
    if len(game.map_list) == 1:
        return answer_queries_init(game)

    grey = FIFOQueue()
    leafs_queries = []
    coordination, permutation = game.combinations(game.map_list[0])
    for i in permutation:
        root_state = fill_q_mark(game.map_list[0], coordination, i)
        grey.append(Node(root_state))
        node_count += 1

    while grey:
        node_to_explore = grey.pop()
        if len(game.map_list) - 1 > node_to_explore.depth:
            actions = node_to_explore.actions(node_to_explore.state, Pteam, Mteam)
            for action in actions:
                cur_map = node_to_explore.result(node_to_explore.state, action, Pteam, Mteam)
                turn = node_to_explore.depth
                child_template = game.map_list[turn+1]
                if can_be_identical(child_template, cur_map):
                    new_node = Node(cur_map, node_to_explore, action)
                    node_count += 1
                    if new_node not in grey:
                        grey.append(new_node)

        else:
            leaf_counter += 1
            leafs_queries.append(answer_queries(node_to_explore, game.queries))

    if len(leafs_queries) == 0:
        return answer_queries_false(game.queries)
    else:
        sol = {}
        for j in range(len(leafs_queries[0])):
            Found_True = False
            Found_False = False
            for i in range(len(leafs_queries)):
                if leafs_queries[i][j]:
                    Found_True = True
                else:
                    Found_False = True
            if Found_True and Found_False:
                sol[game.queries[j]] = '?'
            elif Found_True:
                sol[game.queries[j]] = 'T'
            elif Found_False:
                sol[game.queries[j]] = 'F'
            else:
                sol[game.queries[j]] = 'error'
                break
    return sol


def solve_problem(input):
    return breadth_first_search(input)
