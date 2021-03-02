ids = ["328711569", "312581655"]
from itertools import combinations, product


# function receives state and code=area status (S,H,Q,U or I)
# function returns all indexes where appears area with given code.
def find_areas_in_state(state, code):
    qur_map = state[0]
    q_status_areas = ()
    for i in range(len(qur_map)):
        for j in range(len(qur_map[0])):
            if qur_map[i][j] == code:
                q_status_areas = q_status_areas + ((i, j),)
    return q_status_areas


# function receives indexes of some areas and a team
# returns tuple of tuples. Each tuple=(team,area index)
def add_team_to_area(areas, team):
    areas = list(areas)
    for i in range(len(areas)):
        action = (team, areas[i])
        areas[i] = action
    return tuple(areas)


def actions(state, police, medics):
    s_areas = add_team_to_area(find_areas_in_state(state, "S"), "quarantine")
    h_areas = add_team_to_area(find_areas_in_state(state, "H"), "vaccinate")
    s_combinations = tuple(combinations(s_areas, min(police, len(s_areas))))
    h_combinations = tuple(combinations(h_areas, min(medics, len(h_areas))))
    all_actions = tuple(product(h_combinations, s_combinations))
    return all_actions


#  function receives map, areas and code in {U,I,Q,S,H}
# function changes received areas status to code and returns modified map
# status_map is not updated here!
def change_area_status(map, areas, code):
    aux_map = list(map)
    for i in range(len(areas)):
        index = areas[i][1]
        if code == 'I':
            assert aux_map[index[0]][index[1]] == 'H'
        elif code == 'Q':
            assert aux_map[index[0]][index[1]] == 'S'
        else:
            raise NotImplementedError
        aux_map[index[0]][index[1]] = code
    return aux_map


# function receives state and indexes of areas with status S.
# function finds all healthy neighbours of sick areas, and updates them all to be sick
# status_map is not updated here!
def update_H_areas_acc_to_neighbors(state, sick_areas):
    qur_map = list(list(sub) for sub in state[0])
    for area in sick_areas:
        neighbors_list = []
        i = area[0]
        j = area[1]
        if i > 0:
            neighbors_list.append([i - 1, j])
        if i < len(qur_map) - 1:
            neighbors_list.append([i + 1, j])

        if j > 0:
            neighbors_list.append([i, j - 1])
        if j < len(qur_map[0]) - 1:
            neighbors_list.append([i, j + 1])

        for neighbor in neighbors_list:
            if qur_map[neighbor[0]][neighbor[1]] == 'H':
                qur_map[neighbor[0]][neighbor[1]] = 'S'
    return qur_map, state[1]


# function updates map and  status map. returns state after updates.
def update_state(state, state_after_infection_spread):
    qur_map = state[0]
    status_map = list(list(sub) for sub in state[1])
    map_after_infection_spread = state_after_infection_spread[0]
    for i in range(len(map_after_infection_spread)):
        for j in range(len(map_after_infection_spread[0])):
            if map_after_infection_spread[i][j] == qur_map[i][j]:
                if map_after_infection_spread[i][j] == 'U' or map_after_infection_spread[i][j] == 'I' \
                        or map_after_infection_spread[i][j] == 'H':
                    continue
                if map_after_infection_spread[i][j] == 'Q' and status_map[i][j] < 2:
                    status_map[i][j] += 1
                elif map_after_infection_spread[i][j] == 'S' and status_map[i][j] < 3:
                    status_map[i][j] += 1
                else:
                    status_map[i][j] = -1
                    map_after_infection_spread[i][j] = "H"
                continue
            if (qur_map[i][j] == "H" and map_after_infection_spread[i][j] == "S") or (
                    qur_map[i][j] == "S" and map_after_infection_spread[i][j] == "Q"):
                status_map[i][j] = 1

    updated_status_map = tuple(tuple(sub) for sub in status_map)
    updated_map = tuple(tuple(sub) for sub in map_after_infection_spread)
    return updated_map, updated_status_map


def result(state, action):
    qur_map = list(list(sub) for sub in state[0])
    areas_to_be_vaccinated = list(action[0])
    areas_to_be_quarantined = list(action[1])
    quarantined_areas_map = change_area_status(qur_map, areas_to_be_quarantined, "Q")
    quarantined_and_vaccinated_map = change_area_status(quarantined_areas_map, areas_to_be_vaccinated, "I")
    map_after_action = tuple(tuple(sub) for sub in quarantined_and_vaccinated_map)
    sick_areas = find_areas_in_state((map_after_action, state[1]), 'S')
    state_after_infection_spread = update_H_areas_acc_to_neighbors((map_after_action, state[1]), sick_areas)
    state_after_sickness_expires = update_state(state, state_after_infection_spread)
    return state_after_sickness_expires


class Node:
    def __init__(self, state, depth, parent=None):
        self.depth = depth
        self.state = state
        self.parent = parent
        self.children_list = []
        self.isLegal = True

    def update_isLegal(self, max_d):
        if len(self.children_list) == 0:
            self.isLegal = self.depth == max_d
        else:
            self.isLegal = any([n.update_isLegal(max_d) for n in self.children_list])
        return self.isLegal

    def trim_illegal(self):
        self.children_list = [n.trim_illegal() for n in self.children_list if n.isLegal]
        return self


class ProblemSolver:
    def __init__(self, data):
        self.police = data["police"]
        self.medics = data["medics"]
        self.observations = tuple(sub for sub in data["observations"])
        self.queries = tuple(sub for sub in data["queries"])
        # root node has no status map
        self.root_node = Node((self.observations[0], None), depth=-1)
        self.create_root_children()

    def trim_map_if_U(self, undefined_areas):
        U_areas = list()
        new_undefined = list(undefined_areas)
        for area in undefined_areas:
            for ob in self.observations:
                i = area[0]
                j = area[1]
                if ob[i][j] == 'U':
                    U_areas.append(area)
                    new_undefined.remove(area)
                    break
        return U_areas, new_undefined

    # return all possible maps using 0 observation and possible assignments to '?' areas.
    def generate_init_maps(self):
        init = list(self.observations[0])
        possible_codes = ('H', 'S', 'U')
        undefined_areas = []
        for i in range(len(init)):
            for j in range(len(init[i])):
                if init[i][j] == '?':
                    undefined_areas.append([i, j])

        U_areas, undefined_areas = self.trim_map_if_U(undefined_areas)
        num_of_undefined_areas = len(undefined_areas)

        code_assignments = tuple((product(possible_codes, repeat=num_of_undefined_areas)))
        undefined_areas = tuple(undefined_areas for a in range(len(code_assignments)))
        all_possible_assignments = []
        for codes_assignment_set, areas_set in zip(code_assignments, undefined_areas):
            code_to_area = []
            for assignment, area in zip(codes_assignment_set, areas_set):
                code_to_area.append((assignment, area))
            all_possible_assignments.append(code_to_area)
        possible_init_states = []
        for code_to_area in all_possible_assignments:
            init_copy = list(list(area) for area in init)
            for assignment in code_to_area:
                code = assignment[0]
                i = assignment[1][0]
                j = assignment[1][1]
                init_copy[i][j] = code
            for u_area in U_areas:
                init_copy[u_area[0]][u_area[1]] = 'U'
            possible_init_states.append(tuple(tuple(area) for area in init_copy))
        assert len(possible_init_states) <= len(possible_codes) ** num_of_undefined_areas
        return tuple(sub for sub in possible_init_states)

    def generate_all_init_states(self):
        all_init_states = []
        init_maps = self.generate_init_maps()
        for init_map in init_maps:
            status_map = self.init_state_status_map(init_map)
            all_init_states.append((init_map, status_map))
        return tuple(all_init_states)

    def init_state_status_map(self, init_map):
        status_map = [[0 for i in range(len(init_map[0]))] for i in range(len(init_map))]
        for i in range(len(init_map)):
            for j in range(len(init_map[0])):
                if init_map[i][j] == "S" or init_map[i][j] == "Q":
                    status_map[i][j] = 1
                else:
                    status_map[i][j] = -1
        return tuple(tuple(sub) for sub in status_map)

    def create_root_children(self):
        possible_init_states = self.generate_all_init_states()
        for state in possible_init_states:
            child = Node(state, 0, self.root_node)
            self.root_node.children_list.append(child)

    def generate_all_possible_states_after_1_step(self, state):
        all_actions = actions(state, self.police, self.medics)
        all_possible_states = []
        for action in all_actions:
            next_state = result(state, action)
            all_possible_states.append(next_state)
        return tuple(sub for sub in all_possible_states)

    def expand(self, node: Node):
        state = node.state
        states = self.generate_all_possible_states_after_1_step(state)
        observation = self.observations[node.depth + 1]
        for state in states:
            if self.state_fits_observation(state, observation):
                child_node = Node(state, node.depth + 1, parent=node)
                node.children_list.append(child_node)
        return node.children_list

    def generate_tree(self):
        nodes = self.root_node.children_list
        t = len(self.observations)
        for i in range(0, t - 1):
            next_nodes = []
            for node in nodes:
                children = self.expand(node)
                next_nodes.extend(children)
            nodes = next_nodes
        self.root_node.update_isLegal(len(self.observations) - 1)
        self.root_node.trim_illegal()

    def get_solution(self):
        sol_dict = {}
        self.generate_tree()
        nodes_in_same_t = self.root_node.children_list
        t = len(self.observations)
        for i in range(0, t):
            states_in_t = []
            nodes_t1 = []
            for node in nodes_in_same_t:
                states_in_t.append(node.state)
                nodes_t1.extend(node.children_list)
            queries = self.get_queries(i)
            for query in queries:
                sol_dict[query] = self.query_related_to_obs_t_is_sufficient(query, states_in_t)
            nodes_in_same_t = nodes_t1
        return sol_dict

    def get_queries(self, observation_number):
        queries_set = []
        for query in self.queries:
            if query[1] == observation_number:
                queries_set.append(query)
        return tuple(sub for sub in queries_set)

    def state_fits_observation(self, state, observation):
        curr_map = state[0]
        for i in range(len(curr_map)):
            for j in range(len(curr_map[i])):
                if observation[i][j] != '?' and curr_map[i][j] != observation[i][j]:
                    return False
        return True

    def query_related_to_obs_t_is_sufficient(self, query, states_t):
        if len(states_t) == 0:
            return 'F'
        i = query[0][0]
        j = query[0][1]
        flag = states_t[0][0][i][j] == query[2]
        for state in states_t[1:]:
            t_map = state[0]
            if (t_map[i][j] == query[2]) != flag:
                return '?'
        return 'T' if flag else 'F'


def solve_problem(input):
    problem = ProblemSolver(input)
    return problem.get_solution()
