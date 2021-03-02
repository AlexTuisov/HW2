try:
    import warnings
    warnings.filterwarnings('ignore')
except:
    pass

from sympy import *
from sympy.logic.inference import satisfiable
import itertools as it

ids = ['313410938', '342436953']

ACTIONS = {
    'Vaccinate': 'VAC',
    'Quarantine': 'QUA'
}

STATES = {
    'U': 'U',
    'H': 'H',
    'S': 'S',
    'I': 'I',
    'Q': 'Q'
}

UNKNOWN_STATE = '?'


def solve_problem(problem_input):
    problem_solver = ProblemSolver(problem_input)
    problem_solver.get_predictions_for_states()
    answer_dict = problem_solver.get_answers()
    return answer_dict


class LogicStatesHandler:
    def __init__(self, observations_number, rows_number, columns_number):
        self._map_all_logic_states = self.create_all_possible_states(observations_number, rows_number, columns_number)

    def get_list_defined_states(self):
        return ['H', 'S', 'U', 'I', 'Q']

    def get_map_all_logic_states(self):
        return self._map_all_logic_states

    def create_all_possible_states(self, observations_number, rows_number, columns_number):
        predictors = {}
        for index in range(observations_number):
            for row in range(rows_number):
                for column in range(columns_number):
                    for state in self.get_list_defined_states():
                        cell = Cell(index, row, column, state)
                        pred = self.get_observed_cell_state_symbol(cell, state)
                        predictors[pred] = self.get_observed_cell_state_symbol(cell, state)
        return predictors

    def get_cnf_mark_cell_as_target_states(self, cell, list_target_cell_states):
        if len(list_target_cell_states) < 1:
            return

        cnt_total = True
        for target_cell_state in list_target_cell_states:
            cnt_total = cnt_total & self.get_cnf_cell_state_by_target_state(cell, target_cell_state)

        return cnt_total

    def get_cnf_mark_cell_as_not_target_states(self, cell, list_target_cell_states):
        if len(list_target_cell_states) < 1:
            return

        cnt_total = True
        for target_cell_state in list_target_cell_states:
            cnt_total = cnt_total & ~self.get_cnf_cell_state_by_target_state(cell, target_cell_state)

        return cnt_total

    def get_cnf_mark_cell_as_complementary_target_states(self, cell, list_target_cell_states):
        list_complementary_states = self.get_complementary_list_of_states(list_target_cell_states)
        if len(list_complementary_states) < 1:
            return

        cnt_total = True
        for target_cell_state in list_complementary_states:
            cnt_total = cnt_total & self.get_cnf_cell_state_by_target_state(cell, target_cell_state)

        return cnt_total

    def get_cnf_mark_cell_as_not_complementary_target_states(self, cell, list_target_cell_states):
        list_complementary_states = self.get_complementary_list_of_states(list_target_cell_states)
        if len(list_complementary_states) < 1:
            return

        cnt_total = True
        for target_cell_state in list_complementary_states:
            cnt_total = cnt_total & ~self.get_cnf_cell_state_by_target_state(cell, target_cell_state)

        return cnt_total

    def get_cnf_mark_cell_as_possible_or_target_states(self, cell, list_target_cell_states):
        if len(list_target_cell_states) < 1:
            return

        cnt_total = False
        for target_cell_state in list_target_cell_states:
            cnt_total = cnt_total | self.get_cnf_cell_state_by_target_state(cell, target_cell_state)

        return cnt_total

    def get_cnf_cell_state_by_target_state(self, cell, cell_target_state):
        cell_state_key = self.get_observed_cell_state_symbol(cell, cell_target_state)
        cnf_state_cond = self._map_all_logic_states[cell_state_key]
        return cnf_state_cond

    def get_observed_cell_state_symbol(self, cell, state):
        pred = self.get_observed_cell_state_key(cell, state)
        return symbols(pred)

    def get_observed_cell_state_key(self, cell, state):
        return state + cell.get_cell_position_key()

    def get_complementary_list_of_states(self, list_of_states):
        result_list_states = []
        for current_state in self.get_list_defined_states():
            if current_state not in list_of_states:
                result_list_states.append(current_state)

        return result_list_states


class CellPosition:
    def __init__(self, tuple_position):
        self._row = tuple_position[0]
        self._column = tuple_position[1]

    def get_row(self):
        return self._row

    def get_column(self):
        return self._column


class Cell:
    def __init__(self, index, row, column, state_value):
        self._index = index
        self._row = row
        self._column = column
        self._state_value = state_value

    def get_index(self):
        return self._index

    def get_row(self):
        return self._row

    def get_column(self):
        return self._column

    def get_state_value(self):
        return self._state_value

    def get_cell_position_key(self):
        # return state + str(observation_index) + '(' + str(row) + str(column) + ')'
        return str(self.get_index()) + '(' + str(self.get_row()) + str(self.get_column()) + ')'


class UnknownUnpredictedCell:
    def __init__(self, cell, list_possible_states):
        self._cell = cell
        self._list_possible_states = list_possible_states

    # def __repr__(self):
    #     return self._get_print_str()
    #
    # def _get_print_str(self):
    #     print_str = f'UnknownUnpredictedCell[_cell={self._cell} '
    #     print_str += f' _list_possible_states = {self._list_possible_states}]'
    #     return print_str

    def get_cell(self):
        return self._cell

    def get_list_possible_states(self):
        return self._list_possible_states


class Observation:
    def __init__(self, object_observation, observation_index):
        self._observation = object_observation
        self._rows_number = len(self._observation)
        self._columns_number = 0
        self._index = observation_index
        self._applied_actions = self.get_init_value_applied_actions()
        # self._applied_actions_on_cells = self.get_init_value_applied_actions()
        self._excluded_applied_actions_cells = self.get_init_value_excluded_applied_actions_cells()
        if self._rows_number > 0:
            self._columns_number = len(self._observation[0])

    def get_rows_number(self):
        return self._rows_number

    def get_columns_number(self):
        return self._columns_number

    def get_object_observation(self):
        return self._observation

    def get_observation_index(self):
        return self._index

    def get_init_value_applied_actions(self):
        # applied_actions = {
        #     ACTIONS['Vaccinate']: 0,
        #     ACTIONS['Quarantine']: 0
        # }
        applied_actions = {
            ACTIONS['Vaccinate']: [],
            ACTIONS['Quarantine']: []
        }
        return applied_actions

    # def add_applied_action_vaccinate(self, cell: UnknownUnpredictedCell):
    def add_applied_action_vaccinate(self, cell):
        # self._applied_actions[ACTIONS['Vaccinate']] += 1
        # print(f' add_applied_action_vaccinate cell = { cell }')
        self._applied_actions[ACTIONS['Vaccinate']].append(cell)

    # def add_applied_action_quarantine(self, cell: UnknownUnpredictedCell):
    def add_applied_action_quarantine(self, cell):
        # self._applied_actions[ACTIONS['Quarantine']] += 1
        self._applied_actions[ACTIONS['Quarantine']].append(cell)

    # TODO: use it
    def get_number_of_applied_action_vaccinate(self):
        # return self._applied_actions[ACTIONS['Vaccinate']]
        return len(self._applied_actions[ACTIONS['Vaccinate']])

    def get_number_of_applied_action_quarantine(self):
        # return self._applied_actions[ACTIONS['Quarantine']]
        return len(self._applied_actions[ACTIONS['Quarantine']])

    def get_applied_action_vaccinate_cells(self):
        return self._applied_actions[ACTIONS['Vaccinate']]

    def get_applied_action_quarantine_cells(self):
        return self._applied_actions[ACTIONS['Quarantine']]

    def get_init_value_excluded_applied_actions_cells(self):
        excluded_applied_actions_cells = {
            ACTIONS['Vaccinate']: {},
            ACTIONS['Quarantine']: {}
        }
        return excluded_applied_actions_cells

    def add_excluded_applied_action_vaccinate(self, cell):
        self._excluded_applied_actions_cells[ACTIONS['Vaccinate']][cell.get_cell_position_key()] = cell

    def add_excluded_applied_action_quarantine(self, cell):
        self._excluded_applied_actions_cells[ACTIONS['Quarantine']][cell.get_cell_position_key()] = cell

    def is_excluded_applied_action_vaccinate_cell(self, cell):
        return cell.get_cell_position_key() in self._excluded_applied_actions_cells[ACTIONS['Vaccinate']]

    def is_excluded_applied_action_quarantine_cell(self, cell):
        return cell.get_cell_position_key() in self._excluded_applied_actions_cells[ACTIONS['Quarantine']]

    def is_valid_row(self, row):
        if row < 0 or row >= self.get_rows_number():
            return False
        return True

    def is_valid_column(self, column):
        if column < 0 or column >= self.get_columns_number():
            return False
        return True

    def get_cell(self, row, column):
        result_none = None

        if not self.is_valid_row(row):
            return result_none

        if not self.is_valid_column(column):
            return result_none

        cell_state_value = self._observation[row][column]
        cell = Cell(self.get_observation_index(), row, column, cell_state_value)
        return cell

    def get_cell_right_neighbor(self, cell):
        result_none = None
        right_row = cell.get_row()
        right_column = cell.get_column() + 1
        if self.is_valid_row(right_row) and self.is_valid_column(right_column):
            return self.get_cell(right_row, right_column)
        return result_none

    def get_cell_left_neighbor(self, cell):
        result_none = None
        left_row = cell.get_row()
        left_column = cell.get_column() - 1
        if self.is_valid_row(left_row) and self.is_valid_column(left_column):
            return self.get_cell(left_row, left_column)
        return result_none

    def get_cell_down_neighbor(self, cell):
        result_none = None
        down_row = cell.get_row() - 1
        down_column = cell.get_column()
        if self.is_valid_row(down_row) and self.is_valid_column(down_column):
            return self.get_cell(down_row, down_column)
        return result_none

    def get_cell_top_neighbor(self, cell):
        result_none = None
        top_row = cell.get_row() + 1
        top_column = cell.get_column()
        if self.is_valid_row(top_row) and self.is_valid_column(top_column):
            return self.get_cell(top_row, top_column)
        return result_none


class QueryObservation:
    def __init__(self, object_map_query):
        self._query = object_map_query
        self._query_cell = None
        self._query_row = None
        if self._query is not None and len(self._query) >= 3:
            self._query_cell = self._query[0]
            if self._query_cell is not None:
                self._query_row = self._query_cell[0]
                self._query_column = self._query_cell[1]

            self._query_index = self._query[1]
            self._query_predicted_state = self._query[2]

    def get_query(self):
        return self._query

    def get_query_row(self):
        return self._query_row

    def get_query_column(self):
        return self._query_column

    def get_query_index(self):
        return self._query_index

    def get_query_predicted_state(self):
        return self._query_predicted_state

    def get_query_cell(self):
        return Cell(self.get_query_index(), self.get_query_row(), self.get_query_column(),
                    self.get_query_predicted_state())


class LogicStatePredictions:
    def __init__(self):
        self._possible_states = True
        self._impossible_states = True

    def get_possible_states(self):
        return self._possible_states

    def get_impossible_states(self):
        return self._impossible_states

    def update_possible_states_add_and_cnf(self, cnf_and):
        # TODO: check if  need to convert to_cnf
        # cnf_and = to_cnf(cnf_and)
        self._possible_states = self._possible_states & cnf_and


class ProblemSolver:
    def __init__(self, input):
        # self._observations = input['observations']
        self._observations = []
        for observation_index in range(len(input['observations'])):
            input_observation = input['observations'][observation_index]
            observation = Observation(input_observation, observation_index)
            self._observations.insert(observation_index, observation)

        self._queries = input["queries"]
        self._police_number = input["police"]
        self._medics_number = input["medics"]

        # self._applied_actions = {}
        # per observation

        # self._logic_state_predictions = {
        #     'possible_states': True,
        #     'impossible_states': True,
        # }

        self._logic_state_predictions = LogicStatePredictions()

        self._observations_number = len(self._observations)
        self._observation_rows_number = 0
        self._observation_columns_number = 0
        if self._observations_number > 0:
            first_observation = self.get_observation_by_index(0)
            self._observation_rows_number = first_observation.get_rows_number()
            self._observation_columns_number = first_observation.get_columns_number()

        # self._map_all_logic_states = self.create_all_possible_states()
        self._logic_states_handler = LogicStatesHandler(self.get_observations_number(),
                                                        self.get_observation_rows_number(),
                                                        self.get_observation_columns_number())
        self._initial_state_logic = self.get_initial_state()
        # new logic for the case of no police or medics
        self.exclude_predicted_logic_for_agent_actions_when_no_police_or_medics()
        # TODO: use it
        self._map_unknown_cells = {}
        self._map_predicted_cells = {}

    def get_logic_state_predictions(self):
        return self._logic_state_predictions

    def get_observations(self):
        return self._observations

    def get_observation_by_index(self, observation_index):
        result_none = None
        if not self.is_valid_observation_index(observation_index):
            return result_none

        # current_observation_object = self._observations[observation_index]
        # current_observation = Observation(current_observation_object, observation_index)
        # return current_observation
        return self._observations[observation_index]

    def is_valid_observation_index(self, index):
        # if index >= 0 and index < self.get_observations_number():
        if 0 <= index < self.get_observations_number():
            return True
        return False

    def get_map_all_logic_states(self):
        # return self._map_all_logic_states
        return self._logic_states_handler.get_map_all_logic_states()

    def get_observation_rows_number(self):
        return self._observation_rows_number

    def get_observation_columns_number(self):
        return self._observation_columns_number

    def get_observations_number(self):
        return self._observations_number

    def get_list_defined_states(self):
        # return ['H', 'S', 'U', 'I', 'Q']
        return self._logic_states_handler.get_list_defined_states()

    def get_cell_by_index(self, cell, target_index):
        row = cell.get_row()
        column = cell.get_column()

        target_observation = self.get_observation_by_index(target_index)

        target_cell = None
        if target_observation is not None:
            target_cell = target_observation.get_cell(row, column)

        return target_cell

    def get_map_unknown_cells(self):
        return self._map_unknown_cells

    def get_map_unknown_cells_in_observation(self, observation_index):
        # TODO: complete
        map_cells = {}
        for current_unknown_cell_key in self.get_map_unknown_cells().keys():
            # current_unknown_unpredicted_cell: UnknownUnpredictedCell = self.get_map_unknown_cells()[
            current_unknown_unpredicted_cell = self.get_map_unknown_cells()[current_unknown_cell_key]
            # current_unknown_cell: Cell = current_unknown_unpredicted_cell.get_cell()
            current_unknown_cell = current_unknown_unpredicted_cell.get_cell()
            # current_unknown_cell_list_states = current_unknown_unpredicted_cell.get_list_possible_states()
            if current_unknown_cell.get_index() != observation_index:
                continue
            map_cells[current_unknown_cell_key] = current_unknown_unpredicted_cell
        return map_cells

    def get_list_unknown_cells_in_observation(self, observation_index):
        list_observation_cells = []
        for current_unknown_cell_key in self.get_map_unknown_cells().keys():
            # current_unknown_unpredicted_cell: UnknownUnpredictedCell = self.get_map_unknown_cells()[
            current_unknown_unpredicted_cell = self.get_map_unknown_cells()[current_unknown_cell_key]
            # current_unknown_cell: Cell = current_unknown_unpredicted_cell.get_cell()
            current_unknown_cell = current_unknown_unpredicted_cell.get_cell()
            # current_unknown_cell_list_states = current_unknown_unpredicted_cell.get_list_possible_states()
            if current_unknown_cell.get_index() != observation_index:
                continue
            list_observation_cells.append(current_unknown_unpredicted_cell)
        return list_observation_cells

    def add_cell_to_map_unknown_cells(self, unpredicted_cell):
        self._map_unknown_cells[unpredicted_cell.get_cell().get_cell_position_key()] = unpredicted_cell

    def get_map_predicted_cells(self):
        return self._map_predicted_cells

    def add_cell_to_map_predicted_cells(self, cell):
        self._map_predicted_cells[cell.get_cell_position_key()] = cell

    # def create_all_possible_states(self):
    #     predictors = {}
    #     for index in range(self.get_observations_number()):
    #         for row in range(self.get_observation_rows_number()):
    #             for column in range(self.get_observation_columns_number()):
    #                 for state in self.get_list_defined_states():
    #                     pred = self.get_observed_cell_state_symbol(row, column, index, state)
    #                     predictors[pred] = self.get_observed_cell_state_symbol(row, column, index, state)
    #     return predictors

    # def get_observed_cell_state_key(self, row, column, observation_index, state):
    #     return state + str(observation_index) + '(' + str(row) + str(column) + ')'

    # def get_observed_cell_state_symbol(self, row, column, observation_index, state):
    #     pred = self.get_observed_cell_state_key(row, column, observation_index, state)
    #     return symbols(pred)

    def get_initial_state(self):
        # , input, map_all_logic_states
        initial_state = True
        # observation_index = -1
        # for object_observation in self.get_observations():
        for observation in self.get_observations():
            # observation_index += 1
            # observation = Observation(object_observation, observation_index)
            observation_index = observation.get_observation_index()
            for row in range(self.get_observation_rows_number()):
                for column in range(self.get_observation_columns_number()):
                    cell = observation.get_cell(row, column)
                    if cell is None:
                        continue

                    val = cell.get_state_value()
                    if val != UNKNOWN_STATE:
                        current_cell_logic_cnf = self.get_cell_current_state_logic_cnf(val, row, column,
                                                                                       observation_index)
                        initial_state = initial_state & current_cell_logic_cnf

        return to_cnf(initial_state)

        # loop_through_observation_cells(input, get_cell_logic_initial_state, initial_state)

    def exclude_predicted_logic_for_agent_actions_when_no_police_or_medics(self):
        # new logic for the case of no police or medics
        logic_state = True
        if self._medics_number > 0 and self._police_number > 0:
            return

        for observation in self.get_observations():
            observation_index = observation.get_observation_index()
            for row in range(self.get_observation_rows_number()):
                for column in range(self.get_observation_columns_number()):
                    cell = observation.get_cell(row, column)
                    if cell is None:
                        continue

                    val = cell.get_state_value()
                    if val != UNKNOWN_STATE:
                        continue

                    # current cell is ?
                    if self._medics_number == 0:
                        # cell can not be I
                        self.update_cnf_possible_states_mark_cell_unknown_state_as_not_target_states(observation, cell,
                                                                                                     [STATES['I']])

                    if self._police_number == 0:
                        # cell can not be Q
                        self.update_cnf_possible_states_mark_cell_unknown_state_as_not_target_states(observation, cell,
                                                                                                     [STATES['Q']])

        # result_cnf = to_cnf(logic_state)
        # self.update_current_logic_state_add_and_cnf_to_possible_states(result_cnf)

    # def get_observation_cell_value(self, index, row, column):
    #    return self._observations[index][row][column]

    def get_cell_current_state_logic_cnf(self, current_cell_state, row, column, index):
        cond = true
        for possible_value in self.get_list_defined_states():
            if possible_value == current_cell_state:
                cell_possible = Cell(index, row, column, current_cell_state)
                # cell_state_key = self._logic_states_handler.get_observed_cell_state_key(cell_possible,
                #                                                                         current_cell_state)
                cell_state_key = self._logic_states_handler.get_observed_cell_state_symbol(cell_possible,
                                                                                           current_cell_state)
                # print(f' self.get_map_all_logic_states() = {self.get_map_all_logic_states()}')

                cond = cond & self.get_map_all_logic_states()[cell_state_key]
            else:
                cell_impossible = Cell(index, row, column, possible_value)
                # cell_state_key = self._logic_states_handler.get_observed_cell_state_key(cell_impossible, possible_value)
                cell_state_key = self._logic_states_handler.get_observed_cell_state_symbol(cell_impossible,
                                                                                           possible_value)
                cond = cond & ~self.get_map_all_logic_states()[cell_state_key]
        return to_cnf(cond)

    def get_answers(self):
        answer_dict = {}
        query_index = 0
        for object_map_query in self._queries:
            query_answer_result = self.get_query_answer(object_map_query, query_index)
            # query = QueryObservation(object_map_query, query_index)
            # answer_dict[str(object_map_query)] = query_answer_result
            # answer_dict[object_map_query] = query_answer_result
            result_query = object_map_query
            if type(result_query) is not tuple:
                result_query = tuple(result_query)

            answer_dict[result_query] = query_answer_result
            query_index += 1

        return answer_dict

    def get_query_answer(self, object_map_query, query_index):

        # print(f'query_index={query_index} start')
        # print(f'initial_state_logic={self._initial_state_logic}')

        query = QueryObservation(object_map_query)

        # query_cell_state_key = self.get_observed_cell_state_key(query.get_query_row(), query.get_query_column(), query.get_query_index(),
        #                                                         query.get_query_predicted_state())
        # query_cell_state_key_symbol = self._map_all_logic_states[query_cell_state_key]

        query_cell_state_key = self._logic_states_handler.get_observed_cell_state_symbol(query.get_query_cell(),
                                                                                         query.get_query_predicted_state())
        query_cell_state_key_symbol = self.get_map_all_logic_states()[query_cell_state_key]

        # do not override existing observations
        # logic_states_predictions = self.get_predictions_for_states(input, query, map_all_logic_states)

        # new logic
        # ref to previous self.get_predictions_for_states()
        # logic_states_predictions = self.get_predictions_for_states()

        logic_states_predictions = self.get_logic_state_predictions()

        # answer_dict[str(query)] = answer_to_query(query, input["observations"], pred, initial,
        #                                     police_num, med_num, actions_pred, col_len, row_len)
        # query_pred = state_verse(query[2], place[0], place[1], query[1], pred)
        # query_pred = get_cell_current_state_logic_cnf(query_predicted_state, query_row, query_column, query_index,
        #                                              map_all_logic_states)
        # query_pred = get_observed_cell_state_key(query_row,query_column, query_index, query_predicted_state)
        query_pred = to_cnf(query_cell_state_key_symbol)

        # print(f'query_pred={query_pred}')

        # logic_state_predictions = {
        #     'possible_states': True,
        #     'impossible_states': True,
        # }

        # cnf_predicted_possible_states = logic_states_predictions['possible_states']
        # cnf_predicted_impossible_states = logic_states_predictions['impossible_states']

        cnf_predicted_possible_states = logic_states_predictions.get_possible_states()
        cnf_predicted_impossible_states = logic_states_predictions.get_impossible_states()

        # print(f'cnf_predicted_possible_states={cnf_predicted_possible_states}')
        # print(f'cnf_predicted_impossible_states={cnf_predicted_impossible_states}')
        cnf_predicted_states = cnf_predicted_possible_states & cnf_predicted_impossible_states

        # print(f'cnf_predicted_states={cnf_predicted_states}')
        # TODO: check if query_pred is not in initial_state_logic & cnf_predicted_states
        # in this case return '?'
        # TODO: add represantation of cnf_predicted_states as dictionary
        # in order to check if query_pred is in (otherwise return '?')
        # print(
        #     f'map_all_logic_states.get(query_cell_state_key_symbol)={self.get_map_all_logic_states().get(str(query_cell_state_key_symbol))}')
        # print(f'cnf_predicted_states[query_cell_state_key_symbol]={cnf_predicted_states.get(str(query_cell_state_key_symbol))}')

        # result_satisfiable = satisfiable(to_cnf(initial_state_logic & cnf_predicted_states & query_pred))
        # remove & query_pred
        result_satisfiable = satisfiable(to_cnf(self._initial_state_logic & cnf_predicted_states))
        # print(f'str(query)={str(query)}')
        # print(f'result_satisfiable={result_satisfiable}')
        # print(f'query_cell_state_key={query_cell_state_key}')
        # print(f'query_cell_state_key_symbol={query_cell_state_key_symbol}')
        # print(f'query_cell_state_key_symbol in result_satisfiable={query_cell_state_key_symbol in result_satisfiable}')

        # print(f' get_map_predicted_cells = {self.get_map_predicted_cells()}')
        # print(f' get_map_unknown_cells = {self.get_map_unknown_cells()}')

        # TODO: add debug if needed
        # print(f'logic_states_predictions["DEBUG"]={logic_states_predictions["DEBUG"]}')
        # print(f'logic_states_predictions["DEBUG"]=TODO')

        # print(f'query_cell_state_key_symbol in cnf_predicted_states={query_cell_state_key_symbol in cnf_predicted_states}')
        # just for ref
        # answer_dict[str(query)] = answer_to_query(query, input["observations"], pred, initial,
        #                                           police_num, med_num, actions_pred, col_len, row_len)

        # answer_dict[str(query)] = 'T' | 'F' | '?'
        result_status = ''
        if result_satisfiable is True:
            result_status = 'T'
        elif result_satisfiable is False:
            result_status = 'F'
        elif result_satisfiable is None:
            # todo update to '?' after the tests
            # return 'N'
            result_status = '?'

        elif query_cell_state_key_symbol not in result_satisfiable:
            # return '?'
            result_status = '?'

        elif result_satisfiable is not None and self.check_result_satisfiable_for_question_mark(result_satisfiable,
                                                                                                query):
            result_status = '?'

        elif result_satisfiable and result_satisfiable[query_cell_state_key_symbol] is True:
            result_status = 'T'

        elif result_satisfiable[query_cell_state_key_symbol] is False:
            result_status = 'F'

        else:
            # TODO: update to '?' after the tests
            result_status = '?'

        # answer_dict[str(query)] = result_status
        # print(f'result_status={result_status}')
        # print(f'query_number={query_number} complete')

        # return answer_dict
        return result_status

    # important
    def check_result_satisfiable_for_question_mark_previous_logic_important(self, result_satisfiable, query):
        # returns True if query result_satisfiable should be '?'
        # prev args: , query_row, query_column, query_index,
        #                                                    map_all_logic_states)

        # find single True or False
        number_of_true = 0
        number_of_false = 0
        for possible_state_check in self.get_list_defined_states():
            check_cell_state_key = self._logic_states_handler.get_observed_cell_state_symbol(query.get_query_cell(),
                                                                                             possible_state_check)
            check_cell_key_logic = self.get_map_all_logic_states()[check_cell_state_key]
            # new logic
            if result_satisfiable is None or check_cell_key_logic not in result_satisfiable:
                return True

            cell_result_value = result_satisfiable[check_cell_key_logic]
            if cell_result_value is True:
                number_of_true += 1
                if number_of_true > 1:
                    return True

            elif cell_result_value is False:
                number_of_false += 1
            else:
                # unknown state
                return True

        if number_of_true > 1:
            return True

        # TODO: check this logic
        if number_of_false == 5:
            return True

        return False

    # new logic
    def check_result_satisfiable_for_question_mark(self, result_satisfiable, query):
        # new logic
        # returns True if query result_satisfiable should be '?'
        # prev args: , query_row, query_column, query_index,
        #                                                    map_all_logic_states)

        if result_satisfiable is None:
            # should be ? - no information
            return True

        # find single True or False
        number_of_true = 0
        number_of_false = 0
        list_possible_states = []
        for possible_state_check in self.get_list_defined_states():
            check_cell_state_key = self._logic_states_handler.get_observed_cell_state_symbol(query.get_query_cell(),
                                                                                             possible_state_check)
            check_cell_key_logic = self.get_map_all_logic_states()[check_cell_state_key]

            if check_cell_key_logic not in result_satisfiable:
                # should be ? - no information
                return True

            cell_result_value = result_satisfiable[check_cell_key_logic]
            if cell_result_value is True:
                number_of_true += 1
                list_possible_states.append(possible_state_check)
                # if number_of_true > 1:
                #     return True

            elif cell_result_value is False:
                number_of_false += 1
            else:
                # unknown state
                return True

        # if number_of_true > 1:
        #     return True
        if query.get_query_predicted_state() in list_possible_states and len(list_possible_states) > 1:
            # not a single possible  state
            # state could not be definitely defined
            # should be ?
            return True

        # return  False
        # TODO: check this logic
        if number_of_false == 5:
            return True

        return False

    # detect possible states by observations transitions
    def get_predictions_for_states(self):
        for observation_index in range(self.get_observations_number()):
            current_observation = self.get_observation_by_index(observation_index)
            row = 0
            while row < self.get_observation_rows_number():
                column = 0
                while column < self.get_observation_columns_number():
                    current_cell = current_observation.get_cell(row, column)
                    prev_observation = self.get_observation_by_index(observation_index - 1)
                    next_observation = self.get_observation_by_index(observation_index + 1)

                    prev_cell = None
                    if prev_observation is not None:
                        prev_cell = prev_observation.get_cell(row, column)

                    next_cell = None
                    if next_observation is not None:
                        next_cell = next_observation.get_cell(row, column)

                    # current_logic_state = process_cell_state_transition(row, column, index, current_cell, next_cell,
                    #                                                     prev_cell, current_observation, observations,
                    #                                                     current_logic_state, map_all_logic_states)

                    self.process_cell_state_transition(current_cell, next_cell, prev_cell, current_observation)

                    column += 1
                row += 1
            observation_index += 1

        # process current observation
        # TODO: process available agent actions
        self.process_agent_actions_by_medics_and_police()
        self.process_unknown_unpredicted_cells()

        # cell_state_key = get_observed_cell_key(row, column, turn)
        # predictors[pred] = symbols(pred)
        #    turn += 1
        # return logic_state_predictions
        # current_logic_state["logic_state_predictions"]["DEBUG"] = current_logic_state["DEBUG"]
        # return current_logic_state["logic_state_predictions"]
        return self._logic_state_predictions

    def get_init_value_available_actions(self, police_number, medics_number):
        available_actions = {
            ACTIONS['Vaccinate']: medics_number,
            ACTIONS['Quarantine']: police_number
        }
        return available_actions

    # def process_cell_state_transition(self, row, column, index, current_cell_state, next_cell_state, prev_cell,
    #                                  current_observation, observations, current_logic_state, map_all_logic_states):
    def process_cell_state_transition(self, current_cell, next_cell, prev_cell, current_observation):
        # list_neighbors = self.get_cell_list_neighbors_in_observation(current_observation, current_cell)

        if current_cell is not None and current_cell.get_state_value() == STATES['H']:
            # Transition from 'H' to 'H'
            if next_cell is not None and next_cell.get_state_value() == STATES['H']:
                # neighbors can be 'H' | 'U' | 'I' (t>0)
                self.update_cnf_possible_states_mark_cell_unknown_neighbors_as_not_sick(current_observation,
                                                                                        current_cell)

            # Transition from 'H' to 'I'
            if next_cell is not None and next_cell.get_state_value() == STATES['I']:
                # TODO: verify the availalbe limit
                self.update_cnf_possible_states_mark_cell_unknown_neighbors_as_not_sick(current_observation,
                                                                                        current_cell)
                current_observation.add_applied_action_vaccinate(current_cell)

            # Transition from 'H' to 'S'
            if next_cell is not None and next_cell.get_state_value() == STATES['S']:
                self.update_cnf_possible_states_mark_cell_single_unknown_neighbor_as_sick(current_observation,
                                                                                          current_cell)

            if prev_cell is not None and prev_cell.get_state_value() == STATES['H']:
                prev_observation = self.get_observation_by_index(current_cell.get_index() - 1)
                prev_cell_ref = self.get_cell_by_index(current_cell, current_cell.get_index() - 1)
                self.update_cnf_possible_states_mark_cell_unknown_neighbors_as_not_sick(prev_observation,
                                                                                        prev_cell_ref)

            # TODO: check
            # prev state S handled by current S and next H
            # prev state Q handled by current Q and next H

        if current_cell is not None and current_cell.get_state_value() == STATES['S']:
            # update next observations as sick
            # TODO: add this logic if needed
            # if index == 0:
            #
            #     cnf_next_sq = get_cnf_logic_next_observations_of_cell_as_sick_or_quarantine(row, column, index,
            #                                                                                 current_observation,
            #                                                                                 observations,
            #                                                                                 map_all_logic_states)
            #
            #     current_logic_state = update_current_logic_state_add_and_cnf_to_possible_states(current_logic_state,
            #                                                                                     cnf_next_sq )
            #
            #     current_logic_state["DEBUG"].append(
            #         f'[index={index} row={row} column={column}] -> [current_cell_state == S && index == 0] ')

            # transition from S to H
            if next_cell is not None and next_cell.get_state_value() == STATES['H']:
                self.update_cnf_possible_states_mark_cell_unknown_2_previous_indices_as_sick(current_observation,
                                                                                             current_cell)
                prev_cell = self.get_cell_by_index(current_cell, current_cell.get_index() - 1)
                prev_m2_cell = self.get_cell_by_index(current_cell, current_cell.get_index() - 2)
                current_observation.add_excluded_applied_action_quarantine(prev_cell)
                current_observation.add_excluded_applied_action_quarantine(prev_m2_cell)

            if next_cell is not None and next_cell.get_state_value() == STATES['S']:
                current_observation.add_excluded_applied_action_quarantine(current_cell)

            if next_cell is not None and next_cell.get_state_value() == STATES['Q']:
                current_observation.add_applied_action_quarantine(current_cell)

            # TODO: come  back to this case
            # if prev_cell.get_state_value() == 'H':
            #     previous_observation = get_previous_observation(observations, index)
            #     # TODO: update to new function
            #     # cnf_possible_sick_neighbors_prev = get_cnf_logic_cell_neighbors_possibly_sick_in_observation(row, column,
            #     #                                                                                              index - 1,
            #     #                                                                                              previous_observation,
            #     #                                                                                              observations,
            #     #                                                                                              map_all_logic_states)
            #     #
            #
            #     # current_observation -> previous_observation
            #     cnf_possible_sick_neighbors_prev = get_cnf_logic_cell_check_sick_neighbors_observation(row, column,
            #                                                                                            index - 1,
            #                                                                                            previous_observation,
            #                                                                                            observations,
            #                                                                                            map_all_logic_states)
            #     current_logic_state = update_current_logic_state_add_and_cnf_to_possible_states(current_logic_state,
            #                                                                                     cnf_possible_sick_neighbors_prev)
            #
            #     current_logic_state["DEBUG"].append(
            #         f'[index={index} row={row} column={column}] -> [current_cell_state == S && prev_cell == H] ')

        if current_cell is not None and current_cell.get_state_value() == STATES['Q']:

            if next_cell is not None and next_cell.get_state_value() == STATES['H']:
                self.update_cnf_possible_states_mark_cell_previous_unknown_state_as_quarantine(current_observation,
                                                                                               current_cell)
                self.update_cnf_possible_states_mark_cell_previous_index_2_unknown_state_as_sick(current_observation,
                                                                                                 current_cell)
                prev_index_2_cell = self.get_cell_by_index(current_cell, current_cell.get_index() - 2)
                current_observation.add_applied_action_quarantine(prev_index_2_cell)

            if next_cell is not None and next_cell.get_state_value() == STATES['Q']:
                self.update_cnf_possible_states_mark_cell_previous_unknown_state_as_sick(current_observation,
                                                                                         current_cell)
                next_index_p2 = next_cell.get_index() + 1
                next_cell_index_p2 = self.get_cell_by_index(current_cell, next_index_p2)
                if next_cell_index_p2 is not None:
                    next_observation = self.get_observation_by_index(next_index_p2)
                    self.update_cnf_possible_states_mark_cell_and_future_next_unknown_state_as_healthy(next_observation,
                                                                                                       next_cell_index_p2)

                prev_cell = self.get_cell_by_index(current_cell, current_cell.get_index() - 1)
                current_observation.add_applied_action_quarantine(prev_cell)

        if current_cell is not None and current_cell.get_state_value() == STATES['I']:
            # if next_cell.get_state_value() == UNKNOWN_STATE:
            self.update_cnf_possible_states_mark_cell_and_future_unknown_states_as_immune(current_observation,
                                                                                          current_cell)

        if current_cell is not None and current_cell.get_state_value() == STATES['U']:
            self.update_cnf_possible_states_mark_cell_and_all_unknown_states_as_unpopulated(current_observation,
                                                                                            current_cell)

        # update_cnf_possible_states_mark_cell_and_all_unknown_states_as_unpopulated
        if current_cell is not None and current_cell.get_state_value() == UNKNOWN_STATE:
            self.handle_logic_for_current_unknown_cell(current_observation, current_cell)

        #     cnf_general_u = get_cnf_logic_for_unknown_cell_healthy_in_observation(row, column, index,
        #                                                                           current_observation,
        #                                                                           observations,
        #                                                                           list_neighbors_positions,
        #                                                                           map_all_logic_states)
        #     current_logic_state = update_current_logic_state_add_and_cnf_to_possible_states(current_logic_state,
        #                                                                                     cnf_general_u)
        #

        # return current_logic_state

    # def get_cell_neighbors_positions_in_observation(self, cell):
    def get_cell_list_neighbors_in_observation(self, observation, cell):
        # prev args: (row, column, current_observation)
        neighbors_list = []
        # if current_observation is None:
        #    return neighbors_list

        # right = get_cell_right_neighbor_observation(row, column, current_observation)

        right = observation.get_cell_right_neighbor(cell)
        left = observation.get_cell_left_neighbor(cell)
        top = observation.get_cell_top_neighbor(cell)
        down = observation.get_cell_down_neighbor(cell)

        if right is not None:
            neighbors_list.append(right)

        if left is not None:
            neighbors_list.append(left)

        if top is not None:
            neighbors_list.append(top)

        if down is not None:
            neighbors_list.append(down)

        return neighbors_list

    # def get_cnf_logic_cell_neighbors_healthy_in_observation(self, row, column, index, current_observation, observations,
    #                                                         list_neighbors_positions, map_all_logic_states):
    def update_cnf_possible_states_mark_cell_unknown_neighbors_as_not_sick(self, observation, cell):
        # neighbors can be 'H' | 'U' | 'I' (t>0)
        cnf_predicted = True

        list_neighbors = self.get_cell_list_neighbors_in_observation(observation, cell)

        for current_neighbor in list_neighbors:
            if current_neighbor is not None and current_neighbor.get_state_value() == UNKNOWN_STATE:
                # cnf_not_s = ~get_cnf_mark_cell_as_sick_in_observation(n_row, n_column, index, map_all_logic_states)
                cnf_not_s = self._logic_states_handler.get_cnf_mark_cell_as_not_target_states(current_neighbor,
                                                                                              [STATES['S']])

                # TODO: move this index 0 logic to '?'
                # cnf_index_0 = True
                # if index == 0:
                #     cnf_index_0 = get_cnf_mark_cell_by_states_operation_and_not_in_observation(row, column,
                #                                                                                index,
                #                                                                                map_all_logic_states,
                #                                                                                ['I', 'Q'])
                # cnf_predicted = cnf_predicted & cnf_not_s & cnf_index_0
                cnf_predicted = cnf_predicted & cnf_not_s

                # if self._medics_number == 0:
                #     cnf_not_i = self._logic_states_handler.get_cnf_mark_cell_as_not_target_states(current_neighbor,
                #                                                                                   [STATES['I']])
                #     cnf_predicted = cnf_predicted & cnf_not_i

        result_cnf = to_cnf(cnf_predicted)
        self.update_current_logic_state_add_and_cnf_to_possible_states(result_cnf)

    def update_cnf_possible_states_mark_cell_single_unknown_neighbor_as_sick(self, observation, cell):
        cnf_predicted = True

        list_neighbors = self.get_cell_list_neighbors_in_observation(observation, cell)
        map_neighbors_states = {}
        for current_neighbor in list_neighbors:
            if current_neighbor is None:
                continue
            current_neighbor_state = current_neighbor.get_state_value()
            if current_neighbor_state not in map_neighbors_states:
                map_neighbors_states[current_neighbor_state] = []

            map_neighbors_states[current_neighbor_state].append(current_neighbor)

        if STATES['S'] in map_neighbors_states and len(map_neighbors_states[STATES['S']]) > 0:
            return

        if UNKNOWN_STATE in map_neighbors_states and len(map_neighbors_states[UNKNOWN_STATE]) == 1:
            # single_unknown_sick_neighbor
            single_unknown_sick_neighbor = map_neighbors_states[UNKNOWN_STATE][0]
            target_states_s = [STATES['S']]
            cnf_s = self._logic_states_handler.get_cnf_mark_cell_as_target_states(single_unknown_sick_neighbor,
                                                                                  target_states_s)
            cnf_not_all_complementary_s = self._logic_states_handler.get_cnf_mark_cell_as_not_complementary_target_states(
                single_unknown_sick_neighbor, target_states_s)
            cnf_predicted = cnf_predicted & cnf_s & cnf_not_all_complementary_s

        result_cnf = to_cnf(cnf_predicted)
        self.update_current_logic_state_add_and_cnf_to_possible_states(result_cnf)

    def update_cnf_possible_states_mark_cell_unknown_2_previous_indices_as_sick(self, observation, cell):
        cnf_predicted = True

        current_observation_index = observation.get_observation_index()

        prev_cell = self.get_cell_by_index(cell, current_observation_index - 1)
        prev_prev_cell = self.get_cell_by_index(cell, current_observation_index - 2)

        if prev_cell is not None and prev_cell.get_state_value() == UNKNOWN_STATE:
            target_states_s = [STATES['S']]
            cnf_s = self._logic_states_handler.get_cnf_mark_cell_as_target_states(prev_cell, target_states_s)
            cnf_not_all_complementary_s = self._logic_states_handler.get_cnf_mark_cell_as_not_complementary_target_states(
                prev_cell, target_states_s)
            cnf_predicted = cnf_predicted & cnf_s & cnf_not_all_complementary_s

        if prev_prev_cell is not None and prev_prev_cell.get_state_value() == UNKNOWN_STATE:
            target_states_s = [STATES['S']]
            cnf_s = self._logic_states_handler.get_cnf_mark_cell_as_target_states(prev_prev_cell, target_states_s)
            cnf_not_all_complementary_s = self._logic_states_handler.get_cnf_mark_cell_as_not_complementary_target_states(
                prev_prev_cell, target_states_s)
            cnf_predicted = cnf_predicted & cnf_s & cnf_not_all_complementary_s

        result_cnf = to_cnf(cnf_predicted)
        self.update_current_logic_state_add_and_cnf_to_possible_states(result_cnf)

    def update_cnf_possible_states_mark_cell_previous_unknown_state_as_quarantine(self, observation, cell):
        cnf_predicted = True

        current_observation_index = observation.get_observation_index()

        prev_cell = self.get_cell_by_index(cell, current_observation_index - 1)

        if prev_cell is not None and prev_cell.get_state_value() == UNKNOWN_STATE:
            target_states_q = [STATES['Q']]
            cnf_q = self._logic_states_handler.get_cnf_mark_cell_as_target_states(prev_cell, target_states_q)
            cnf_not_all_complementary_q = self._logic_states_handler.get_cnf_mark_cell_as_not_complementary_target_states(
                prev_cell, target_states_q)
            cnf_predicted = cnf_predicted & cnf_q & cnf_not_all_complementary_q

        result_cnf = to_cnf(cnf_predicted)
        self.update_current_logic_state_add_and_cnf_to_possible_states(result_cnf)

    def update_cnf_possible_states_mark_cell_previous_index_2_unknown_state_as_sick(self, observation, cell):
        cnf_predicted = True

        current_observation_index = observation.get_observation_index()

        prev_index_2_cell = self.get_cell_by_index(cell, current_observation_index - 2)

        if prev_index_2_cell is not None and prev_index_2_cell.get_state_value() == UNKNOWN_STATE:
            target_states_s = [STATES['S']]
            cnf_s = self._logic_states_handler.get_cnf_mark_cell_as_target_states(prev_index_2_cell, target_states_s)
            cnf_not_all_complementary_s = self._logic_states_handler.get_cnf_mark_cell_as_not_complementary_target_states(
                prev_index_2_cell, target_states_s)
            cnf_predicted = cnf_predicted & cnf_s & cnf_not_all_complementary_s

        result_cnf = to_cnf(cnf_predicted)
        self.update_current_logic_state_add_and_cnf_to_possible_states(result_cnf)

    def update_cnf_possible_states_mark_cell_previous_unknown_state_as_sick(self, observation, cell):
        cnf_predicted = True

        current_observation_index = observation.get_observation_index()

        prev_cell = self.get_cell_by_index(cell, current_observation_index - 1)

        if prev_cell is not None and prev_cell.get_state_value() == UNKNOWN_STATE:
            target_states_s = [STATES['S']]
            cnf_s = self._logic_states_handler.get_cnf_mark_cell_as_target_states(prev_cell, target_states_s)
            cnf_not_all_complementary_s = self._logic_states_handler.get_cnf_mark_cell_as_not_complementary_target_states(
                prev_cell, target_states_s)
            cnf_predicted = cnf_predicted & cnf_s & cnf_not_all_complementary_s

        result_cnf = to_cnf(cnf_predicted)
        self.update_current_logic_state_add_and_cnf_to_possible_states(result_cnf)

    def update_cnf_possible_states_mark_cell_and_future_unknown_states_as_immune(self, observation, cell):
        cnf_predicted = True

        target_cell = cell
        while target_cell is not None and target_cell.get_index() < self.get_observations_number():
            if target_cell is not None and target_cell.get_state_value() == UNKNOWN_STATE:
                target_states_i = [STATES['I']]
                cnf_i = self._logic_states_handler.get_cnf_mark_cell_as_target_states(target_cell, target_states_i)
                cnf_not_all_complementary_i = self._logic_states_handler.get_cnf_mark_cell_as_not_complementary_target_states(
                    target_cell, target_states_i)
                cnf_predicted = cnf_predicted & cnf_i & cnf_not_all_complementary_i
            target_cell = self.get_cell_by_index(target_cell, target_cell.get_index() + 1)

        result_cnf = to_cnf(cnf_predicted)
        self.update_current_logic_state_add_and_cnf_to_possible_states(result_cnf)

    def update_cnf_possible_states_mark_cell_and_all_unknown_states_as_unpopulated(self, observation, cell):
        cnf_predicted = True

        target_cell = self.get_cell_by_index(cell, 0)
        while target_cell is not None and target_cell.get_index() < self.get_observations_number():
            if target_cell is not None and target_cell.get_state_value() == UNKNOWN_STATE:
                target_states_u = [STATES['U']]
                cnf_u = self._logic_states_handler.get_cnf_mark_cell_as_target_states(target_cell, target_states_u)
                cnf_not_all_complementary_u = self._logic_states_handler.get_cnf_mark_cell_as_not_complementary_target_states(
                    target_cell, target_states_u)
                cnf_predicted = cnf_predicted & cnf_u & cnf_not_all_complementary_u
            target_cell = self.get_cell_by_index(target_cell, target_cell.get_index() + 1)

        result_cnf = to_cnf(cnf_predicted)
        self.update_current_logic_state_add_and_cnf_to_possible_states(result_cnf)

    def update_cnf_possible_states_mark_cell_and_future_next_unknown_state_as_healthy(self, observation, cell):
        cnf_predicted = True

        next_cell = self.get_cell_by_index(cell, cell.get_index() + 1)
        if next_cell is not None and next_cell.get_state_value() == UNKNOWN_STATE:
            target_states_h = [STATES['H']]
            cnf_h = self._logic_states_handler.get_cnf_mark_cell_as_target_states(next_cell, target_states_h)
            cnf_not_all_complementary_h = self._logic_states_handler.get_cnf_mark_cell_as_not_complementary_target_states(
                next_cell, target_states_h)
            cnf_predicted = cnf_predicted & cnf_h & cnf_not_all_complementary_h

        result_cnf = to_cnf(cnf_predicted)
        self.update_current_logic_state_add_and_cnf_to_possible_states(result_cnf)

    # def update_cnf_possible_states_mark_cell_unknown_state_as_healthy(self, observation, cell):
    def update_cnf_possible_states_mark_cell_unknown_state_as_target_states(self, observation, cell,
                                                                            list_target_states):
        cnf_predicted = True

        if cell is None:
            return

        if cell.get_state_value() != UNKNOWN_STATE:
            return

        cnf_targets = self._logic_states_handler.get_cnf_mark_cell_as_target_states(cell, list_target_states)
        cnf_not_all_complementary_targets = self._logic_states_handler.get_cnf_mark_cell_as_not_complementary_target_states(
            cell, list_target_states)
        cnf_predicted = cnf_predicted & cnf_targets & cnf_not_all_complementary_targets

        result_cnf = to_cnf(cnf_predicted)
        self.update_current_logic_state_add_and_cnf_to_possible_states(result_cnf)

    def update_cnf_possible_states_mark_cell_unknown_state_as_not_target_states(self, observation, cell,
                                                                                list_not_target_states):
        cnf_predicted = True

        if cell is None:
            return

        if cell.get_state_value() != UNKNOWN_STATE:
            return

        cnf_not_targets = self._logic_states_handler.get_cnf_mark_cell_as_not_target_states(cell,
                                                                                            list_not_target_states)
        # cnf_not_all_complementary_targets = self._logic_states_handler.get_cnf_mark_cell_as_not_complementary_target_states(
        #     cell, list_target_states)
        # cnf_predicted = cnf_predicted & cnf_targets & cnf_not_all_complementary_targets
        cnf_predicted = cnf_predicted & cnf_not_targets

        result_cnf = to_cnf(cnf_predicted)
        self.update_current_logic_state_add_and_cnf_to_possible_states(result_cnf)

    def update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(self, observation, cell,
                                                                                        list_target_states):
        cnf_predicted = True

        if cell is not None and cell.get_state_value() == UNKNOWN_STATE:
            cnf_targets = self._logic_states_handler.get_cnf_mark_cell_as_possible_or_target_states(cell,
                                                                                                    list_target_states)
            cnf_not_all_complementary_targets = self._logic_states_handler.get_cnf_mark_cell_as_not_complementary_target_states(
                cell, list_target_states)
            cnf_predicted = cnf_predicted & cnf_targets & cnf_not_all_complementary_targets

        result_cnf = to_cnf(cnf_predicted)
        self.update_current_logic_state_add_and_cnf_to_possible_states(result_cnf)

    def update_cnf_possible_states_mark_cell_unknown_state_as_by_previous_quarantine(self, observation, cell):
        # cnf_predicted = True

        if cell is None or cell.get_state_value() != UNKNOWN_STATE:
            return

        prev_minus2_cell = self.get_cell_by_index(cell, cell.get_index() - 2)

        if prev_minus2_cell is None:
            return

        # Q, S, ?
        if prev_minus2_cell.get_state_value() == STATES['Q']:
            target_states_h = [STATES['H']]
            self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell, target_states_h)
            # all current NBS are H
            self.update_cnf_possible_states_mark_cell_unknown_neighbors_as_not_sick(observation, cell)
            return

        # S, ?
        if prev_minus2_cell.get_state_value() != STATES['Q']:

            if prev_minus2_cell.get_state_value() == STATES['S']:
                target_states_q = [STATES['Q']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_q)

            if prev_minus2_cell.get_state_value() == UNKNOWN_STATE:
                # S | Q
                prev_minus3_cell = self.get_cell_by_index(cell, cell.get_index() - 3)

                if prev_minus3_cell is None:
                    # -> prev_minus2_cell is index 0
                    # -> prev_minus2_cell is S and current is Q
                    prev_minus2_observation = self.get_observation_by_index(prev_minus2_cell.get_index())
                    target_states_s = [STATES['S']]
                    self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(prev_minus2_observation,
                                                                                             prev_minus2_cell,
                                                                                             target_states_s)
                    target_states_q = [STATES['Q']]
                    self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation,
                                                                                             cell,
                                                                                             target_states_q)

                    return
                else:
                    # current is Q or H
                    target_states_or_qh = [STATES['Q'], STATES['H']]
                    self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation,
                                                                                                         cell,
                                                                                                         target_states_or_qh)
                    self.add_cell_to_map_unknown_cells(UnknownUnpredictedCell(cell, target_states_or_qh))

    def update_cnf_possible_states_mark_cell_unknown_state_as_sick_by_previous_sick_neighbors(self, observation, cell):
        # cnf_predicted = True
        # check previous neighbors
        # if found certain SICK then current unknown cell = S
        cnf_predicted = True

        if cell is None or cell.get_state_value() != UNKNOWN_STATE:
            return

        previous_index = cell.get_index() - 1
        previous_observation = self.get_observation_by_index(previous_index)
        previous_cell = self.get_cell_by_index(cell, previous_index)
        list_previous_neighbors = self.get_cell_list_neighbors_in_observation(previous_observation, previous_cell)

        map_previous_neighbors_states = {}
        for previous_neighbor in list_previous_neighbors:
            if previous_neighbor is None:
                continue
            previous_neighbor_state = previous_neighbor.get_state_value()
            if previous_neighbor_state not in map_previous_neighbors_states:
                map_previous_neighbors_states[previous_neighbor_state] = []

            map_previous_neighbors_states[previous_neighbor_state].append(previous_neighbor)

        if STATES['S'] in map_previous_neighbors_states and len(map_previous_neighbors_states[STATES['S']]) > 0:
            target_states_s = [STATES['S']]
            self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation,
                                                                                     cell,
                                                                                     target_states_s)
            return

        # else - if not S and not ? then H OR I
        if self._medics_number == 0:
            target_states_h = [STATES['H']]
            self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation,
                                                                                     cell,
                                                                                     target_states_h)
            return

        target_states_or_hi = [STATES['H'], STATES['I']]
        self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation, cell,
                                                                                             target_states_or_hi)
        self.add_cell_to_map_unknown_cells(UnknownUnpredictedCell(cell, target_states_or_hi))

    def update_cnf_possible_states_mark_cell_unknown_state_as_sick_by_possible_previous_sick_neighbors(self,
                                                                                                       observation,
                                                                                                       cell):
        # cnf_predicted = True
        # check previous neighbors
        # if found certain SICK then current unknown cell = S
        cnf_predicted = True

        if cell is None or cell.get_state_value() != UNKNOWN_STATE:
            return

        previous_index = cell.get_index() - 1
        previous_observation = self.get_observation_by_index(previous_index)
        previous_cell = self.get_cell_by_index(cell, previous_index)
        list_previous_neighbors = self.get_cell_list_neighbors_in_observation(previous_observation, previous_cell)

        map_previous_neighbors_states = {}
        for previous_neighbor in list_previous_neighbors:
            if previous_neighbor is None:
                continue
            previous_neighbor_state = previous_neighbor.get_state_value()
            if previous_neighbor_state not in map_previous_neighbors_states:
                map_previous_neighbors_states[previous_neighbor_state] = []

            map_previous_neighbors_states[previous_neighbor_state].append(previous_neighbor)

        if STATES['S'] in map_previous_neighbors_states and len(map_previous_neighbors_states[STATES['S']]) > 0:
            target_states_s = [STATES['S']]
            self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation,
                                                                                     cell,
                                                                                     target_states_s)
            return

        target_states_or_hs = [STATES['H'], STATES['S']]
        self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation, cell,
                                                                                             target_states_or_hs)
        self.add_cell_to_map_unknown_cells(UnknownUnpredictedCell(cell, target_states_or_hs))

    def update_cnf_possible_states_mark_cell_unknown_state_as_healthy_or_quarantine_by_previous_minus2_states(self,
                                                                                                              observation,
                                                                                                              cell):
        # check previous-minus2 (from current[current-2])
        # if Q then current ? = H
        # if S then current ? = Q
        # if ? then current ? = H or Q

        if cell is None or cell.get_state_value() != UNKNOWN_STATE:
            return

        previous_minus2_cell = self.get_cell_by_index(cell, cell.get_index() - 2)

        if previous_minus2_cell is None:
            return

        if previous_minus2_cell.get_state_value() == STATES['Q']:
            target_states_h = [STATES['H']]
            self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation,
                                                                                     cell,
                                                                                     target_states_h)
            return

        if previous_minus2_cell.get_state_value() == STATES['S']:
            target_states_q = [STATES['Q']]
            self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation,
                                                                                     cell,
                                                                                     target_states_q)
            return

        # else - if ? then current ? = H or Q
        target_states_or_hq = [STATES['H'], STATES['Q']]
        self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation, cell,
                                                                                             target_states_or_hq)

    def update_cnf_possible_states_mark_cell_unknown_state_as_sick_or_quarantine_by_next_plus2_states(self, observation,
                                                                                                      cell):
        # if current + 2 is Q then current ? = S
        # if current + 2 is H then current ? = Q
        # else - S OR Q
        if cell is None or cell.get_state_value() != UNKNOWN_STATE:
            return

        next_plus2_cell = self.get_cell_by_index(cell, cell.get_index() + 2)

        if next_plus2_cell is None:
            return

        if next_plus2_cell.get_state_value() == STATES['Q']:
            target_states_s = [STATES['S']]
            self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation,
                                                                                     cell,
                                                                                     target_states_s)
            observation.add_applied_action_quarantine(cell)
            return

        if next_plus2_cell.get_state_value() == STATES['H']:
            target_states_q = [STATES['Q']]
            self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation,
                                                                                     cell,
                                                                                     target_states_q)

            previous_index = cell.get_index() - 1
            previous_observation = self.get_observation_by_index(previous_index)
            previous_cell = self.get_cell_by_index(cell, previous_index)
            previous_observation.add_applied_action_quarantine(previous_cell)
            return

        # else - if ? then current ? = H or Q
        target_states_or_hq = [STATES['H'], STATES['Q']]
        self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation, cell,
                                                                                             target_states_or_hq)
        self.add_cell_to_map_unknown_cells(UnknownUnpredictedCell(cell, target_states_or_hq))

    def update_cnf_possible_states_mark_cell_current_healthy_neighbors_as_next_sick_if_unknown(self, observation,
                                                                                               cell):
        # mark current healthy neighbors as sick if next unknown
        list_current_neighbors = self.get_cell_list_neighbors_in_observation(observation, cell)

        map_current_neighbors_states = {}
        for current_neighbor in list_current_neighbors:
            if current_neighbor is None:
                continue
            current_neighbor_state = current_neighbor.get_state_value()
            if current_neighbor_state not in map_current_neighbors_states:
                map_current_neighbors_states[current_neighbor_state] = []

            map_current_neighbors_states[current_neighbor_state].append(current_neighbor)

        if STATES['H'] in map_current_neighbors_states and len(map_current_neighbors_states[STATES['H']]) > 0:
            for current_healthy_neighbor in map_current_neighbors_states[STATES['H']]:
                next_healthy_neighbor = self.get_cell_by_index(current_healthy_neighbor,
                                                               current_healthy_neighbor.get_index() + 1)
                if next_healthy_neighbor is None:
                    continue
                if next_healthy_neighbor.get_state_value() == UNKNOWN_STATE:
                    target_states_s = [STATES['S']]
                    observation_next_healthy_neighbor = self.get_observation_by_index(next_healthy_neighbor.get_index())
                    self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(
                        observation_next_healthy_neighbor,
                        next_healthy_neighbor,
                        target_states_s)

    def update_cnf_possible_states_mark_cell_as_sick_or_healthy_by_previous_minus3(self, observation,
                                                                                   cell):
        previous_minus3_index = cell.get_index() - 3
        previous_minus3_cell = self.get_cell_by_index(cell, previous_minus3_index)

        previous_minus2_index = cell.get_index() - 2
        previous_minus2_cell = self.get_cell_by_index(cell, previous_minus2_index)

        previous_minus2_observation = self.get_observation_by_index(previous_minus2_index)

        if previous_minus2_cell is None:
            # should not happen
            return

        if previous_minus3_cell is None:
            # previous minus 2 is  index == 0
            # previous minus 2 should be marked as S if ?

            if previous_minus2_cell.get_state_value() == UNKNOWN_STATE:
                target_states_s = [STATES['S']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_s)
                previous_minus2_observation = self.get_observation_by_index(previous_minus2_index)
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(previous_minus2_observation,
                                                                                         previous_minus2_cell,
                                                                                         target_states_s)

        else:
            # previous_minus3_cell exists
            if previous_minus3_cell.get_state_value() == STATES['S']:
                # mark previous minus2 as sick
                target_states_s = [STATES['S']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(previous_minus2_observation,
                                                                                         previous_minus2_cell,
                                                                                         target_states_s)
                target_states_h = [STATES['H']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_h)

            elif previous_minus3_cell.get_state_value() == STATES['H']:
                target_states_s = [STATES['S']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_s)
                if previous_minus2_cell.get_state_value() == UNKNOWN_STATE:
                    target_states_s = [STATES['S']]
                    self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(
                        previous_minus2_observation, previous_minus2_cell,
                        target_states_s)

    def update_cnf_possible_states_mark_cell_as_sick_or_healthy_by_previous_minus2(self, observation,
                                                                                   cell):

        previous_minus2_index = cell.get_index() - 2
        previous_minus2_cell = self.get_cell_by_index(cell, previous_minus2_index)

        previous_minus2_observation = self.get_observation_by_index(previous_minus2_index)

        # (previous minus1 cell is S - info in caller function)

        if previous_minus2_cell is None:
            # previous cell is index == 0
            # (previous minus1 cell is S - info in caller function)
            # current cell is S
            target_states_s = [STATES['S']]
            self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                     target_states_s)
            return

        if previous_minus2_cell.get_state_value() == STATES['S']:
            # current is H
            # (previous minus1 cell is S - info in caller function)
            target_states_h = [STATES['H']]
            self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                     target_states_h)
            return

        if previous_minus2_cell.get_state_value() == STATES['H']:
            # current is S
            # (previous minus1 cell is S - info in caller function)
            target_states_s = [STATES['S']]
            self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                     target_states_s)
            return

        # else previous_minus2_cell is ?
        # current is H | S
        target_states_or_hs = [STATES['H'], STATES['S']]
        self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation, cell,
                                                                                             target_states_or_hs)
        self.add_cell_to_map_unknown_cells(UnknownUnpredictedCell(cell, target_states_or_hs))

    def update_cnf_possible_states_mark_cell_state_by_previous_minus3(self, observation, cell):

        if cell is None or cell.get_state_value() != UNKNOWN_STATE:
            return

        previous_index = cell.get_index() - 1
        previous_cell = self.get_cell_by_index(cell, previous_index)

        previous_minus2_index = cell.get_index() - 2
        previous_minus2_cell = self.get_cell_by_index(cell, previous_minus2_index)

        previous_minus3_index = cell.get_index() - 3
        previous_minus3_cell = self.get_cell_by_index(cell, previous_minus3_index)

        previous_minus2_observation = self.get_observation_by_index(previous_minus2_index)

        # we know for sure that previous cell is S !!!

        if previous_minus2_cell is None:
            if self._police_number == 0:
                target_states_s = [STATES['S']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_s)
            else:
                target_states_or_sq = [STATES['S'], STATES['Q']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation, cell,
                                                                                                     target_states_or_sq)
                self.add_cell_to_map_unknown_cells(UnknownUnpredictedCell(cell, target_states_or_sq))

            return

        if previous_minus3_cell is None:

            if previous_minus2_cell.get_state_value() == STATES['S']:

                if self._police_number == 0:
                    target_states_s = [STATES['S']]
                    self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                             target_states_s)
                else:
                    target_states_or_sq = [STATES['S'], STATES['Q']]
                    self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation,
                                                                                                         cell,
                                                                                                         target_states_or_sq)
                    self.add_cell_to_map_unknown_cells(UnknownUnpredictedCell(cell, target_states_or_sq))

            elif previous_minus2_cell.get_state_value() == STATES['H']:

                if self._police_number == 0:
                    target_states_s = [STATES['S']]
                    self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                             target_states_s)
                    self.update_cnf_possible_states_mark_cell_single_unknown_neighbor_as_sick(
                        previous_minus2_observation, previous_minus2_cell)

                else:
                    target_states_or_sq = [STATES['S'], STATES['Q']]
                    self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation,
                                                                                                         cell,
                                                                                                         target_states_or_sq)
                    self.add_cell_to_map_unknown_cells(UnknownUnpredictedCell(cell, target_states_or_sq))

            else:

                if self._police_number == 0:
                    target_states_s = [STATES['S']]
                    self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                             target_states_s)

                else:
                    target_states_or_sq = [STATES['S'], STATES['Q']]
                    self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation,
                                                                                                         cell,
                                                                                                         target_states_or_sq)
                    self.add_cell_to_map_unknown_cells(UnknownUnpredictedCell(cell, target_states_or_sq))

        else:
            # previous_minus3_cell exists
            if previous_minus3_cell.get_state_value() == STATES['S']:

                if previous_minus2_cell.get_state_value() == STATES['S']:
                    # prev is Sick
                    # current is H (after S,S,S)
                    target_states_h = [STATES['H']]
                    self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                             target_states_h)

            elif previous_minus3_cell.get_state_value() == STATES['H']:

                if previous_minus2_cell.get_state_value() == STATES['S']:
                    target_states_s = [STATES['S']]
                    self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                             target_states_s)

    # def update_current_logic_state_add_and_cnf_to_possible_states(current_logic_state, cnf_and):
    def update_current_logic_state_add_and_cnf_to_possible_states(self, cnf_and):
        self._logic_state_predictions.update_possible_states_add_and_cnf(cnf_and)

    #### Danger Zone #####
    # def get_cnf_logic_for_unknown_cell_healthy_in_observation(row, column, index, current_observation, observations,
    #                                                           list_neighbors_positions, map_all_logic_states):
    def handle_logic_for_current_unknown_cell(self, observation, cell):
        # current state of the cell is '?' (Unknown)
        # cnf_predicted = True

        current_cell_index = cell.get_index()

        # TODO: handle neighbors (neighbor_state_next)
        previous_observation = self.get_observation_by_index(cell.get_index() - 1)
        next_observation = self.get_observation_by_index(cell.get_index() + 1)

        prev_cell = self.get_cell_by_index(cell, cell.get_index() - 1)
        next_cell = self.get_cell_by_index(cell, cell.get_index() + 1)

        if current_cell_index == 0:
            # TODO: handle all special cases for index == 0
            if next_cell is not None and next_cell.get_state_value() == STATES['H']:
                # current cell is H
                # current unknown NBS are NOT S
                target_states_h = [STATES['H']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_h)
                self.update_cnf_possible_states_mark_cell_unknown_neighbors_as_not_sick(observation, cell)

            elif next_cell is not None and next_cell.get_state_value() == STATES['Q']:
                # current cell is S
                target_states_s = [STATES['S']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_s)
                # mark current healthy neighbors as sick if next unknown
                self.update_cnf_possible_states_mark_cell_current_healthy_neighbors_as_next_sick_if_unknown(observation,
                                                                                                            cell)

            elif next_cell is not None and next_cell.get_state_value() == STATES['S']:
                # TODO: add more logic if needed
                target_states_hs = [STATES['H'], STATES['S']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation, cell,
                                                                                                     target_states_hs)

            elif next_cell is not None and next_cell.get_state_value() == STATES['I']:
                # current cell is H
                # current unknown NBS are NOT S
                target_states_h = [STATES['H']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_h)
                self.update_cnf_possible_states_mark_cell_unknown_neighbors_as_not_sick(observation, cell)

            elif next_cell is not None and next_cell.get_state_value() == STATES['U']:
                # current cell is U
                target_states_u = [STATES['U']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_u)

            else:

                target_states_hsu = [STATES['H'], STATES['S'], STATES['U']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation, cell,
                                                                                                     target_states_hsu)

        if (next_cell is not None and next_cell.get_state_value() == STATES['U']) or (
                prev_cell is not None and prev_cell.get_state_value() == STATES['U']):
            self.update_cnf_possible_states_mark_cell_and_all_unknown_states_as_unpopulated(observation, cell)

        if next_cell is not None and next_cell.get_state_value() == STATES['I']:

            if current_cell_index == 0:
                # update current as H
                # self.update_cnf_possible_states_mark_cell_unknown_state_as_healthy(observation, cell)
                target_states_h = [STATES['H']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_h)
                self.update_cnf_possible_states_mark_cell_and_future_unknown_states_as_immune(next_observation,
                                                                                              next_cell)
                self.update_cnf_possible_states_mark_cell_unknown_neighbors_as_not_sick(observation, cell)

            if prev_cell is not None and prev_cell.get_state_value() == STATES['I']:
                target_states_i = [STATES['I']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_i)
                # added logic
                self.update_cnf_possible_states_mark_cell_and_future_unknown_states_as_immune(observation, cell)

            elif prev_cell is not None and prev_cell.get_state_value() == STATES['H']:
                # TODO: find the VAC action and decide by the VAC
                target_states_hi = [STATES['H'], STATES['I']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_hi)
                self.update_cnf_possible_states_mark_cell_and_future_unknown_states_as_immune(next_observation,
                                                                                              next_cell)

                self.update_cnf_possible_states_mark_cell_unknown_neighbors_as_not_sick(previous_observation, prev_cell)
                self.add_cell_to_map_unknown_cells(UnknownUnpredictedCell(cell, target_states_hi))

            elif prev_cell is not None and prev_cell.get_state_value() == STATES['Q']:
                target_states_h = [STATES['H']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_h)

                self.update_cnf_possible_states_mark_cell_unknown_neighbors_as_not_sick(observation, cell)
                observation.add_applied_action_vaccinate(cell)

            elif prev_cell is not None and prev_cell.get_state_value() == STATES['S']:
                target_states_h = [STATES['H']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_h)

                self.update_cnf_possible_states_mark_cell_unknown_neighbors_as_not_sick(observation, cell)
                observation.add_applied_action_vaccinate(cell)

                target_states_s = [STATES['S']]

                previous_index_minus2 = cell.get_index() - 2
                previous_index_minus3 = cell.get_index() - 3
                previous_cell_minus2 = self.get_cell_by_index(cell, previous_index_minus2)
                previous_cell_minus3 = self.get_cell_by_index(cell, previous_index_minus3)
                previous_observation_minus2 = self.get_observation_by_index(previous_index_minus2)
                previous_observation_minus3 = self.get_observation_by_index(previous_index_minus3)
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(previous_observation_minus2,
                                                                                         previous_cell_minus2,
                                                                                         target_states_s)

                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(previous_observation_minus3,
                                                                                         previous_cell_minus3,
                                                                                         target_states_s)

            # else:
            # else - not both are i (prev or next)
            else:

                target_states_hi = [STATES['H'], STATES['I']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_hi)
                self.update_cnf_possible_states_mark_cell_and_future_unknown_states_as_immune(next_observation,
                                                                                              next_cell)
                # print(f'UNKNOWN TODO cell={cell}')
                # self._map_unknown_cells[cell.get_cell_position_key()] = cell
                self.add_cell_to_map_unknown_cells(UnknownUnpredictedCell(cell, target_states_hi))
                # prev logic (I OR H) (AND NOT: U Q S)

        if prev_cell is not None and prev_cell.get_state_value() == STATES['I']:
            self.update_cnf_possible_states_mark_cell_and_future_unknown_states_as_immune(previous_observation,
                                                                                          prev_cell)

            # if next_cell is not None and next_cell.get_state_value() == STATES['I']:
            #     # else:
            #     # next cell I and not index 0

        if next_cell is not None and next_cell.get_state_value() == STATES['H']:
            if current_cell_index == 0:
                # self.update_cnf_possible_states_mark_cell_unknown_state_as_healthy(observation, cell)
                target_states_h = [STATES['H']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_h)
                # all current NBS are H
                self.update_cnf_possible_states_mark_cell_unknown_neighbors_as_not_sick(observation, cell)

            elif prev_cell is not None and prev_cell.get_state_value() == STATES['H']:
                target_states_h = [STATES['H']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_h)
                # all current NBS are H
                self.update_cnf_possible_states_mark_cell_unknown_neighbors_as_not_sick(observation, cell)
                self.update_cnf_possible_states_mark_cell_unknown_neighbors_as_not_sick(previous_observation, prev_cell)

            elif prev_cell is not None and prev_cell.get_state_value() == STATES['Q']:
                # prev logic in or H | Q (and not S,U,I)
                self.update_cnf_possible_states_mark_cell_unknown_state_as_by_previous_quarantine(observation, cell)

            elif prev_cell is not None and prev_cell.get_state_value() == STATES['S']:
                self.update_cnf_possible_states_mark_cell_as_sick_or_healthy_by_previous_minus3(observation, cell)

            else:
                # prev can be ?
                # prev logic : CELL IN ( H| Q| S)

                if self._police_number == 0:
                    target_states_or_hs = [STATES['H'], STATES['S']]
                    self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation,
                                                                                                         cell,
                                                                                                         target_states_or_hs)
                else:
                    target_states_or_hqs = [STATES['H'], STATES['Q'], STATES['S']]
                    self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation,
                                                                                                         cell,
                                                                                                         target_states_or_hqs)
                    self.add_cell_to_map_unknown_cells(UnknownUnpredictedCell(cell, target_states_or_hqs))

        if prev_cell is not None and prev_cell.get_state_value() == STATES['H']:
            # prev logic: get_cnf_logic_check_current_cell_by_possible_sick_neighbors_in_observation
            # get_cnf_logic_check_current_cell_by_possible_sick_neighbors_in_observation
            self.update_cnf_possible_states_mark_cell_unknown_state_as_sick_by_previous_sick_neighbors(observation,
                                                                                                       cell)

        if prev_cell is not None and prev_cell.get_state_value() == STATES['Q']:
            # prev logic: H OR Q (and not: U I S)
            self.update_cnf_possible_states_mark_cell_unknown_state_as_healthy_or_quarantine_by_previous_minus2_states(
                observation, cell)

        if next_cell is not None and next_cell.get_state_value() == STATES['Q']:

            if prev_cell is not None and prev_cell.get_state_value() == STATES['S']:
                # prev logic: ( S OR Q ) (AND NOT: I, U, H)
                self.update_cnf_possible_states_mark_cell_unknown_state_as_sick_or_quarantine_by_next_plus2_states(
                    observation, cell)

            elif prev_cell is not None and prev_cell.get_state_value() == STATES['H']:
                target_states_s = [STATES['S']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_s)

                self.update_cnf_possible_states_mark_cell_single_unknown_neighbor_as_sick(previous_observation,
                                                                                          prev_cell)
                observation.add_applied_action_quarantine(cell)

            else:
                # unknown cell ?
                target_states_or_hs = [STATES['H'], STATES['S']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation,
                                                                                                     cell,
                                                                                                     target_states_or_hs)
                self.add_cell_to_map_unknown_cells(UnknownUnpredictedCell(cell, target_states_or_hs))

        if next_cell is not None and next_cell.get_state_value() == STATES['S']:
            # prev logic: (S OR H) (AND NOT U I Q)
            if prev_cell is not None and prev_cell.get_state_value() == STATES['S']:
                # target_states_s = [STATES['S']]
                # self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                #                                                                          target_states_s)

                # H OR S
                self.update_cnf_possible_states_mark_cell_as_sick_or_healthy_by_previous_minus2(observation, cell)

            elif prev_cell is not None and prev_cell.get_state_value() == STATES['H']:
                # H OR S
                # self.update_cnf_possible_states_mark_cell_unknown_state_as_sick_by_previous_sick_neighbors()
                self.update_cnf_possible_states_mark_cell_unknown_state_as_sick_by_possible_previous_sick_neighbors(
                    observation, cell)

            elif prev_cell is not None and prev_cell.get_state_value() == STATES['Q']:
                target_states_h = [STATES['H']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_target_states(observation, cell,
                                                                                         target_states_h)

                self.update_cnf_possible_states_mark_cell_single_unknown_neighbor_as_sick(observation, cell)

            else:
                # previous cell is unknown ?
                # current unknown is H OR S
                target_states_or_hs = [STATES['H'], STATES['S']]
                self.update_cnf_possible_states_mark_cell_unknown_state_as_possible_or_target_states(observation, cell,
                                                                                                     target_states_or_hs)
                self.add_cell_to_map_unknown_cells(UnknownUnpredictedCell(cell, target_states_or_hs))

        if prev_cell is not None and prev_cell.get_state_value() == STATES['S']:
            # if next_cell is None:
            self.update_cnf_possible_states_mark_cell_state_by_previous_minus3(observation, cell)

        #
        # if prev_cell is not None and prev_cell.get_state_value() == STATES['S']:
        #     # prev logic ( S OR H OR Q) (AND NOT: U I)
        #
        #
        # # TODO: check if need to handle neighbors
        # # taking  _state and not position!
        # right_neighbor_prev_state = get_cell_right_neighbor_observation_state(row, column, previous_observation)
        # left_neighbor_prev_state = get_cell_left_neighbor_observation_state(row, column, previous_observation)
        # down_neighbor_prev_state = get_cell_down_neighbor_observation_state(row, column, previous_observation)
        # top_neighbor_prev_state = get_cell_top_neighbor_observation_state(row, column, previous_observation)
        #
        # right_neighbor_current_state = get_cell_right_neighbor_observation_state(row, column, current_observation)
        # left_neighbor_current_state = get_cell_left_neighbor_observation_state(row, column, current_observation)
        # down_neighbor_current_state = get_cell_down_neighbor_observation_state(row, column, current_observation)
        # top_neighbor_current_state = get_cell_top_neighbor_observation_state(row, column, current_observation)
        #
        # right_neighbor_next_state = get_cell_right_neighbor_observation_state(row, column, next_observation)
        # left_neighbor_next_state = get_cell_left_neighbor_observation_state(row, column, next_observation)
        # down_neighbor_next_state = get_cell_down_neighbor_observation_state(row, column, next_observation)
        # top_neighbor_next_state = get_cell_top_neighbor_observation_state(row, column, next_observation)
        #
        # if index > 0:
        #     # check previous neighbors
        #     is_all_prev_neighbor_healthy = True
        #     check_prev_neighbors = [right_neighbor_prev_state, left_neighbor_prev_state, down_neighbor_prev_state,
        #                             top_neighbor_prev_state]
        #     for check_prev_neighbor in check_prev_neighbors:
        #         if check_prev_neighbor is not None and check_prev_neighbor != 'H':
        #             is_all_prev_neighbor_healthy = False
        #             break
        #
        #     if is_all_prev_neighbor_healthy is True and cell_state_prev == 'H':
        #         cnf_predicted = cnf_predicted & get_cnf_mark_cell_by_states_operation_or_in_observation(row, column,
        #                                                                                                 index,
        #                                                                                                 map_all_logic_states,
        #                                                                                                 ['H'])
        #         cnf_predicted = cnf_predicted & get_cnf_mark_cell_by_states_operation_and_not_in_observation(row,
        #                                                                                                      column,
        #                                                                                                      index,
        #                                                                                                      map_all_logic_states,
        #                                                                                                      ['U', 'I',
        #                                                                                                       'Q',
        #                                                                                                       'S'])
        # return to_cnf(cnf_predicted)

    def process_agent_actions_by_medics_and_police(self):
        # print(f'TODO: process_agent_actions_by_medics_and_police')
        # print(f' TODO: process taken actions')
        self.process_agent_actions_by_medics()
        self.process_agent_actions_by_police()

    def process_agent_actions_by_medics(self):
        if self._medics_number == 0:
            return

        for observation in self.get_observations():
            observation_index = observation.get_observation_index()

            # print(f' [process_agent_actions_by_medics] observation_index = {observation_index}')
            # print(
            #     f' [process_agent_actions_by_medics] get_number_of_applied_action_vaccinate={observation.get_number_of_applied_action_vaccinate()}')
            # print(
            #     f' [process_agent_actions_by_medics] get_applied_action_vaccinate_cells = {observation.get_applied_action_vaccinate_cells()}')

            # candidates - H or ?
            map_possible_candidates_cells = {
                STATES['H']: [],
                UNKNOWN_STATE: []
            }
            total_action_vac_candidates = 0

            for row in range(self.get_observation_rows_number()):
                for column in range(self.get_observation_columns_number()):
                    cell = observation.get_cell(row, column)
                    if cell is None:
                        continue

                    val = cell.get_state_value()
                    if val != UNKNOWN_STATE and val != STATES['H']:
                        continue

                    map_possible_candidates_cells[val].append(cell)
                    total_action_vac_candidates += 1

            # print(f' [process_agent_actions_by_medics] observation_index = {observation_index}')
            # print(f' [process_agent_actions_by_medics] map_possible_candidates_cells = {map_possible_candidates_cells}')
            # print(f' [process_agent_actions_by_medics] total_action_vac_candidates = {total_action_vac_candidates}')
            # print(f' [process_agent_actions_by_medics] get_map_unknown_cells = {self.get_map_unknown_cells()}')

            if observation.get_number_of_applied_action_vaccinate() == self._medics_number:
                next_observation = self.get_observation_by_index(observation.get_observation_index() + 1)
                list_next_observation_unknown_unpredicted_cells = self.get_list_unknown_cells_in_observation(
                    next_observation.get_observation_index())
                if len(list_next_observation_unknown_unpredicted_cells) == 0:
                    continue

                for next_observation_unknown_unpredicted_cell in list_next_observation_unknown_unpredicted_cells:
                    next_observation_unknown_cell = next_observation_unknown_unpredicted_cell.get_cell()
                    is_found_in_applied_vac = False
                    # current unknown cell is in next observation
                    for applied_vac_cell in observation.get_applied_action_vaccinate_cells():
                        # current_applied_cell: Cell = applied_vac_cell
                        current_applied_cell = applied_vac_cell
                        if current_applied_cell.get_row() != next_observation_unknown_cell.get_row() and current_applied_cell.get_column() != next_observation_unknown_cell.get_column():
                            continue
                        is_found_in_applied_vac = True

                    if not is_found_in_applied_vac:
                        next_observation_of_unknown_cell = self.get_observation_by_index(
                            next_observation_unknown_cell.get_index())
                        target_not_states_i = [STATES['I']]
                        self.update_cnf_possible_states_mark_cell_unknown_state_as_not_target_states(
                            next_observation_of_unknown_cell, next_observation_unknown_cell,
                            target_not_states_i)

    def process_agent_actions_by_police(self):
        if self._police_number == 0:
            return

        for observation in self.get_observations():
            observation_index = observation.get_observation_index()

            # print(f' [process_agent_actions_by_medics] observation_index = {observation_index}')
            # print(
            #     f' [process_agent_actions_by_medics] get_number_of_applied_action_vaccinate={observation.get_number_of_applied_action_vaccinate()}')
            # print(
            #     f' [process_agent_actions_by_medics] get_applied_action_vaccinate_cells = {observation.get_applied_action_vaccinate_cells()}')

            # candidates - S or ?
            map_possible_candidates_cells = {
                STATES['S']: [],
                UNKNOWN_STATE: []
            }
            total_action_qua_candidates = 0

            for row in range(self.get_observation_rows_number()):
                for column in range(self.get_observation_columns_number()):
                    cell = observation.get_cell(row, column)
                    if cell is None:
                        continue

                    val = cell.get_state_value()
                    if val != UNKNOWN_STATE and val != STATES['S']:
                        continue

                    map_possible_candidates_cells[val].append(cell)
                    total_action_qua_candidates += 1

            # print(f' [process_agent_actions_by_police] observation_index = {observation_index}')
            # print(f' [process_agent_actions_by_police] map_possible_candidates_cells = {map_possible_candidates_cells}')
            # print(f' [process_agent_actions_by_police] total_action_qua_candidates = {total_action_qua_candidates}')
            # print(f' [process_agent_actions_by_police] get_map_unknown_cells = {self.get_map_unknown_cells()}')

            if observation.get_number_of_applied_action_quarantine() == self._police_number:
                next_observation = self.get_observation_by_index(observation.get_observation_index() + 1)
                list_next_observation_unknown_unpredicted_cells = self.get_list_unknown_cells_in_observation(
                    next_observation.get_observation_index())
                if len(list_next_observation_unknown_unpredicted_cells) == 0:
                    continue

                for next_observation_unknown_unpredicted_cell in list_next_observation_unknown_unpredicted_cells:
                    next_observation_unknown_cell = next_observation_unknown_unpredicted_cell.get_cell()
                    is_found_in_applied_qua = False
                    # current unknown cell is in next observation
                    for applied_qua_cell in observation.get_applied_action_quarantine_cells():
                        # current_applied_cell: Cell = applied_qua_cell
                        current_applied_cell = applied_qua_cell
                        if current_applied_cell.get_row() != next_observation_unknown_cell.get_row() and current_applied_cell.get_column() != next_observation_unknown_cell.get_column():
                            continue
                        is_found_in_applied_qua = True

                    if not is_found_in_applied_qua:
                        next_observation_of_unknown_cell = self.get_observation_by_index(
                            next_observation_unknown_cell.get_index())
                        target_not_states_q = [STATES['Q']]
                        self.update_cnf_possible_states_mark_cell_unknown_state_as_not_target_states(
                            next_observation_of_unknown_cell, next_observation_unknown_cell,
                            target_not_states_q)

    def process_unknown_unpredicted_cells(self):
        # print(f'TODO: process_unknown_unpredicted_cells')
        # print(f'TODO: map_unknown_cells={self.get_map_unknown_cells()}')
        pass
