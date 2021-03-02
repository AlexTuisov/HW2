import itertools
import random
import math
from itertools import chain
from itertools import combinations_with_replacement, combinations, \
    permutations

ids = ['205737372', '308513704']

from utils import (
    is_in, argmin, argmax, argmax_random_tie, probability,
    weighted_sampler,
    memoize, print_table, open_data, Stack, FIFOQueue, PriorityQueue, name,
    distance
)

infinity = float('inf')


# ______________________________________________________________________________


class Problem(object):
    def __init__(self, initial, goal=None):
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        raise NotImplementedError

    def result(self, state, action):
        raise NotImplementedError

    def goal_test(self, state):
        if isinstance(self.goal, list):
            return is_in(state, self.goal)
        else:
            return state == self.goal

    def path_cost(self, c, state1, action, state2):
        return c + 1

    def value(self, state):
        raise NotImplementedError


# ______________________________________________________________________________


class Node:

    def __init__(self, state, parent=None, action=None, path_cost=0):
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

    def expand(self, problem, observation):  # עבור כל פעולה פותח ילד
        action = problem.actions(self.state)
        empty_tuple = ()
        if action == empty_tuple:
            return [self.child_node(problem, action, observation)]
        else:
            return [self.child_node(problem, a, observation) for a in
                    action]

    def check_if_match(self, board1, board2):
        columns = len(board1[0])
        rows = len(board1)
        for i in range(rows):
            for j in range(columns):
                if board1[i][j] != board2[i][j]:
                    if (board1[i][j] == "?") or (board2[i][j] == "?"):
                        continue
                    else:
                        return False
        return True

    def child_node(self, problem, action,
                   observation):  # בדיקה של האם מתאים ללוח שקיבלתי מהם!!! רק אותו להכניס
        """[Figure 3.10]"""
        next = problem.result(self.state, action)
        if self.depth + 1 >= len(observation):
            return
        if self.check_if_match(next[0], observation[self.depth + 1]):
            return Node(next, self, action,
                        problem.path_cost(self.path_cost, self.state,
                                          action, next))
        else:
            return

    # if self.check_if_match(next[0], observation[self.depth]):

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


def breadth_first_search(problem, observation):
    """[Figure 3.11]"""
    node = Node(problem.initial)
    if len(observation) == 1:
        return node
    frontier = FIFOQueue()
    frontier.append(node)
    explored = set()
    all_games = []
    while frontier:
        node = frontier.pop()
        explored.add(node.state)
        new_check = []
        check = node.expand(problem, observation)
        for i in range(len(check)):
            if check[i] is not None:
                new_check.append(check[i])
        if len(new_check) > 0:
            for child in new_check:
                if child.state not in explored and child not in frontier:
                    if len(
                            observation) - 1 == child.depth:  # במקום זה בודקים אם הגענו לעומק האחרון
                        current_child = []
                        temp_ch = child
                        for ch in range(len(
                                observation)):  # if there is a problem check here
                            current_child.append(temp_ch)
                            temp_ch = child.parent
                        all_games.append(current_child)

                frontier.append(child)

    return all_games


class MedicalProblem(Problem):

    def initiate_days_matrix(self, state, turn_num):
        for i in range(self.col):
            for j in range(self.row):
                if state[j][i] == "S":
                    turn_num[j][i] = 3
                elif state[j][i] == "Q":
                    turn_num[j][i] = 2
        return turn_num

    def __init__(self, initial):
        self.police = initial["police"]
        self.medical = initial["medics"]
        initial1 = [list(x) for x in initial["map"]]
        self.col = len(initial1[0])
        self.row = len(initial1[:])
        self.initial = initial["map"]
        turn_num = [([0] * self.col) for i in range(self.row)]
        turn_num = self.initiate_days_matrix(self.initial,
                                             turn_num)  # updating the days
        self.initial = tuple((initial["map"]))
        turn_num = tuple(tuple(sub) for sub in turn_num)
        self.initial = tuple((self.initial, turn_num))
        Problem.__init__(self, self.initial)

    def actions(self, state):
        states = [list(i) for i in state[0]]  # לשלוח פעולות רלוונטיות
        action_vac = []
        action_qur = []
        empty_tuple = ()
        s_amount = 0
        h_amount = 0
        if self.police == 0 and self.medical == 0:
            return empty_tuple
        for i in range(self.col):  # איך מאחדים לפי כמה משטרה ורםואה יש
            for j in range(self.row):
                if states[j][i] == "S":
                    action_qur.append(("quarantine", (j, i)))
                    s_amount += 1
                elif states[j][i] == "H":
                    action_vac.append(("vaccinate", (j, i)))
                    h_amount += 1

        if s_amount <= self.police:
            all_comb_qur = list(combinations(action_qur, s_amount))
        else:
            all_comb_qur = list(combinations(action_qur, self.police))

        if h_amount <= self.medical:
            all_comb_vac = list(combinations(action_vac, h_amount))
        else:
            all_comb_vac = list(combinations(action_vac, self.medical))

        if len(all_comb_vac) == 0 and len(all_comb_qur) == 0: return []
        if len(all_comb_vac) == 0 and len(
            all_comb_qur) != 0: return all_comb_vac
        if len(all_comb_vac) != 0 and len(
            all_comb_qur) == 0: return all_comb_qur
        all_mixed_comb = []
        for i in all_comb_vac:
            for j in all_comb_qur:
                all_mixed_comb.append(i + j)

        return all_mixed_comb

    def spread_right(self, state, i, j, temp_turn_num):
        if j == self.col - 1:
            return state
        if state[i][j + 1] == "H" and temp_turn_num[i][j] != 4:
            state[i][j + 1] = "S"
            temp_turn_num[i][j + 1] = 4
        return state

    def spread_left(self, state, i, j, temp_turn_num):
        if j == 0:
            return state
        if state[i][j - 1] == "H" and temp_turn_num[i][j] != 4:
            state[i][j - 1] = "S"
            temp_turn_num[i][j - 1] = 4
        return state

    def spread_up(self, state, i, j, temp_turn_num):
        if i == 0:
            return state
        if state[i - 1][j] == "H" and temp_turn_num[i][j] != 4:
            state[i - 1][j] = "S"
            temp_turn_num[i - 1][j] = 4
        return state

    def spread_down(self, state, i, j, temp_turn_num):
        if i == self.row - 1:
            return state
        if state[i + 1][j] == "H" and temp_turn_num[i][j] != 4:
            state[i + 1][j] = "S"
            temp_turn_num[i + 1][j] = 4
        return state

    def spreading(self, state, temp_turn_num,
                  idx_check):  # spreading S to all sides
        for i in range(self.row):
            for j in range(self.col):
                if 'S' == state[i][j]:  # and (i,j) not in idx_check:
                    state = self.spread_right(state, i, j, temp_turn_num)
                    state = self.spread_left(state, i, j, temp_turn_num)
                    state = self.spread_up(state, i, j, temp_turn_num)
                    state = self.spread_down(state, i, j, temp_turn_num)
                # if state[i][j] == 'S' or state[i][j] == 'Q':
                #     temp_turn_num[i][j] = temp_turn_num[i][j] - 1
        return state, temp_turn_num

    def take_day_off(self, board_to_work, temp_turn_num):
        for i in range(self.row):
            for j in range(self.col):
                if board_to_work[i][j] == 'S' or board_to_work[i][
                    j] == 'Q':
                    temp_turn_num[i][j] = temp_turn_num[i][j] - 1
        return board_to_work, temp_turn_num

    def healed_or_free(self, state,
                       temp_turn_num):  # updating the S and Q to H (days=0)
        for i in range(self.row):
            for j in range(self.col):
                if (state[i][j] == 'S' or state[i][j] == 'Q') and \
                        temp_turn_num[i][j] == 0:
                    state[i][j] = 'H'
        return state, temp_turn_num

    def result(self, state, action):
        board_to_work = [list(i) for i in state[0]]
        temp_turn_num = [list(i) for i in state[1]]
        idx_check = []
        for i in range(len(action)):  # updeting the incoming action
            row_to_change = action[i][1][0]
            col_to_change = action[i][1][1]
            idx_check.append(tuple((row_to_change, col_to_change)))
            if action[i][0] == "vaccinate":
                board_to_work[row_to_change][col_to_change] = 'I'
                temp_turn_num[row_to_change][col_to_change] = int(0)
            if action[i][0] == "quarantine":
                board_to_work[row_to_change][col_to_change] = 'Q'
                temp_turn_num[row_to_change][col_to_change] = int(3)

        board_to_work, temp_turn_num = self.spreading(board_to_work,
                                                      temp_turn_num,
                                                      idx_check)  # יש פה בעיה , מתעדכן לא טוב
        board_to_work, temp_turn_num = self.take_day_off(board_to_work,
                                                         temp_turn_num)
        board_to_work, temp_turn_num = self.healed_or_free(board_to_work,
                                                           temp_turn_num)

        temp_turn_num = tuple(tuple(sub) for sub in temp_turn_num)
        board_to_work = tuple(tuple(sub) for sub in board_to_work)
        board_to_work = tuple((board_to_work, temp_turn_num))
        return board_to_work

    def goal_test(self, state):
        state = [list(i) for i in state[0]]
        for i in state:
            for j in i:
                if 'S' in j:
                    return False

        return True


def find_any_sign_idx(state, columns, rows, sign):
    state = [list(i) for i in state]
    quest_index = []
    for i in range(rows):
        for j in range(columns):
            if state[i][j] == sign:
                quest_index.append((i, j))
    return quest_index


def find_question_mark(state, col, row):
    quest_index = []
    for i in range(row):
        for j in range(col):
            if state[i][j] == '?':
                quest_index.append((i, j))
    return quest_index


def all_possible_boards(comb, list_of_q_mark, current_board):
    for i in range(len(list_of_q_mark)):
        x = list_of_q_mark[i][0]
        y = list_of_q_mark[i][1]
        current_board[x][y] = comb[i]
    current_board = tuple(tuple(sub) for sub in current_board)
    return current_board


def query_check(games, queries):
    final_answers = {}
    for query in queries:
        x = query[0][0]
        y = query[0][1]
        turn = query[1]
        sign = query[2]
        apperance_count = 0
        mother_board = []
        also_other = 0  # 1
        for i in range(len(games)):
            mother_board = games[i]
            mother_board = mother_board[len(mother_board) - turn - 1]
            if mother_board.state[0][x][y] == sign:
                apperance_count += 1
            else:
                also_other = 1

        if apperance_count > 0 and also_other == 1:
            final_answers[query] = '?'
        elif apperance_count > 0 and also_other == 0:
            final_answers[query] = 'T'
        else:
            final_answers[query] = 'F'
    return final_answers


def solve_problem(input):
    police = input["police"]
    medical = input["medics"]
    queries = input["queries"]
    moves = [list(x) for x in input["observations"]]  # הלוחות שמקבלים כקלט
    board_moves = []
    for move in moves:
        board_moves.append([list(x) for x in move])
    col = len(board_moves[0][0])
    row = len(board_moves[0][:])
    options = ['H', 'S', 'U']
    list_of_q_mark = find_question_mark(board_moves[0], col, row)
    all_possible_letters = list(
        itertools.product(options, repeat=len(list_of_q_mark)))
    updated_board = []
    for i in all_possible_letters:
        updated_board.append(
            all_possible_boards(i, list_of_q_mark, board_moves[0]))
    games = []
    observations_as_tuple = []
    observations = tuple(input["observations"])
    updated_board = tuple(tuple(sub) for sub in updated_board)
    updated_board = tuple(updated_board)
    board_moves = tuple(tuple(sub) for sub in board_moves)

    for board in updated_board:
        problems = {"police": police,
                    "medics": medical,
                    "map": (board)}
        x = MedicalProblem(problems)
        final = breadth_first_search(x, observations)
        for i in range(len(final)):
            games.append(final[i])

    return query_check(games, queries)
