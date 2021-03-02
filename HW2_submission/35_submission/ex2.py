import copy
import itertools

from pysat.card import CardEnc
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

ids = ['319126397', '211990270']


def solve_problem(input):
    problem = Problem(input)
    solution_dict = problem.solve(solver_name="m22")  # m22 is PySAT's default solver, can check others as well
    return solution_dict


class Problem:
    def __init__(self, inputs):
        # unpack inputs
        self.police = inputs["police"]
        self.medics = inputs["medics"]
        self.observations = inputs["observations"]
        self.queries = inputs["queries"]

        # auxiliary variables
        self.t_max = len(self.observations) - 1
        self.num_observations = len(self.observations)
        self.rows = len(self.observations[0])
        self.cols = len(self.observations[0][0])
        self.num_tiles = self.rows * self.cols
        self.tiles = {(i, j) for j in range(self.cols) for i in range(self.rows)}

        # create predicates
        self.pool = IDPool()
        self.fill_predicates()
        self.obj2id = self.pool.obj2id

    def fill_predicates(self):
        for t in range(self.t_max + 1):
            for i in range(self.rows):
                for j in range(self.cols):
                    self.pool.id(f"U_{i}_{j}^{t}")
                    self.pool.id(f"I0_{i}_{j}^{t}")  # vaccinated now
                    self.pool.id(f"I_{i}_{j}^{t}")
                    self.pool.id(f"S0_{i}_{j}^{t}")  # current S
                    self.pool.id(f"S1_{i}_{j}^{t}")  # S minus 1 (prev)
                    self.pool.id(f"S2_{i}_{j}^{t}")  # S minus 2 (prev-prev)
                    self.pool.id(f"Q0_{i}_{j}^{t}")  # current Q
                    self.pool.id(f"Q1_{i}_{j}^{t}")  # Q minus 1 (prev)
                    self.pool.id(f"H_{i}_{j}^{t}")

    def U_tile_dynamics(self):
        clauses = []
        for i in range(self.rows):
            for j in range(self.cols):
                for t in range(self.t_max + 1):
                    # first
                    if t == 0:
                        clauses.append([-self.obj2id[f"U_{i}_{j}^{t}"], self.obj2id[f"U_{i}_{j}^{t + 1}"]])

                    # middle
                    if t > 0 and t != self.t_max:
                        clauses.append([-self.obj2id[f"U_{i}_{j}^{t}"], self.obj2id[f"U_{i}_{j}^{t + 1}"]])
                        clauses.append([-self.obj2id[f"U_{i}_{j}^{t}"], self.obj2id[f"U_{i}_{j}^{t - 1}"]])

                    # last
                    if t == self.t_max:
                        clauses.append([-self.obj2id[f"U_{i}_{j}^{t}"], self.obj2id[f"U_{i}_{j}^{t - 1}"]])

        return CNF(from_clauses=clauses)

    def I_tile_dynamics(self):
        clauses = []
        for i in range(self.rows):
            for j in range(self.cols):
                for t in range(self.t_max + 1):
                    # first
                    if t == 0:
                        continue

                    # middle
                    if t > 0 and t != self.t_max:
                        clauses.append([-self.obj2id[f"I_{i}_{j}^{t}"], self.obj2id[f"I_{i}_{j}^{t + 1}"]])
                        clauses.append([-self.obj2id[f"I0_{i}_{j}^{t}"], self.obj2id[f"I_{i}_{j}^{t + 1}"]])
                        clauses.append([-self.obj2id[f"I0_{i}_{j}^{t}"], self.obj2id[f"H_{i}_{j}^{t - 1}"]])
                        clauses.append([-self.obj2id[f"I_{i}_{j}^{t}"], self.obj2id[f"I_{i}_{j}^{t - 1}"], self.obj2id[f"I0_{i}_{j}^{t - 1}"]])

                    # last
                    if t == self.t_max:
                        clauses.append([-self.obj2id[f"I0_{i}_{j}^{t}"], self.obj2id[f"H_{i}_{j}^{t - 1}"]])
                        clauses.append([-self.obj2id[f"I_{i}_{j}^{t}"], self.obj2id[f"I_{i}_{j}^{t - 1}"], self.obj2id[f"I0_{i}_{j}^{t - 1}"]])

        return CNF(from_clauses=clauses)

    def S_tile_dynamics(self):
        clauses = []
        for i in range(self.rows):
            for j in range(self.cols):
                for t in range(self.t_max + 1):
                    neighbors = self.__get_neighbours_indices(i, j)

                    # Is sick
                    # Previous t
                    if 0 < t:
                        # S2_t => H_t-1
                        clauses.append([-self.obj2id[f"S0_{i}_{j}^{t}"], self.obj2id[f"H_{i}_{j}^{t - 1}"]])
                        # S1_t => S2_t-1
                        clauses.append([-self.obj2id[f"S1_{i}_{j}^{t}"], self.obj2id[f"S0_{i}_{j}^{t - 1}"]])
                        # S0_t => S1_t-1
                        clauses.append([-self.obj2id[f"S2_{i}_{j}^{t}"], self.obj2id[f"S1_{i}_{j}^{t - 1}"]])

                    # Next t
                    if t < self.num_observations - 1:
                        # S2_t => S1_t+1 v Q1_t+1
                        clauses.append([-self.obj2id[f"S0_{i}_{j}^{t}"], self.obj2id[f"S1_{i}_{j}^{t + 1}"], self.obj2id[f"Q0_{i}_{j}^{t + 1}"]])
                        # S1_t => S0_t+1 v Q1_t+1
                        clauses.append([-self.obj2id[f"S1_{i}_{j}^{t}"], self.obj2id[f"S2_{i}_{j}^{t + 1}"], self.obj2id[f"Q0_{i}_{j}^{t + 1}"]])
                        # S0_t => H_t+1 v Q1_t+1
                        clauses.append([-self.obj2id[f"S2_{i}_{j}^{t}"], self.obj2id[f"H_{i}_{j}^{t + 1}"], self.obj2id[f"Q0_{i}_{j}^{t + 1}"]])

                    # Infected By Someone
                    if 0 < t:
                        # S2_t => V (S2n_t-1 v S1n_t-1 v S0n_t-1) for n in neighbors
                        clause = [-self.obj2id[f"S0_{i}_{j}^{t}"]]
                        for (n_row, n_col) in neighbors:
                            clause.extend([self.obj2id[f"S0_{n_row}_{n_col}^{t - 1}"],
                                           self.obj2id[f"S1_{n_row}_{n_col}^{t - 1}"],
                                           self.obj2id[f"S2_{n_row}_{n_col}^{t - 1}"]])
                        clauses.append(clause)

                    # Infecting Others
                    if t < self.num_observations - 1:
                        for (n_row, n_col) in neighbors:
                            for sick_i in ["S0", "S1", "S2"]:
                                # Si_t /\ Hn_t /\ -Q1_t+1 /\ -In_recent_t+1 => S2n_t+1 (Sn, Hn stand for neighbor)
                                clauses.append([-self.obj2id[f"{sick_i}_{i}_{j}^{t}"],
                                                -self.obj2id[f"H_{n_row}_{n_col}^{t}"],
                                                self.obj2id[f"Q0_{i}_{j}^{t + 1}"],
                                                self.obj2id[f"I0_{n_row}_{n_col}^{t + 1}"],
                                                self.obj2id[f"S0_{n_row}_{n_col}^{t + 1}"]])

        return CNF(from_clauses=clauses)

    def Q_tile_dynamics(self):
        clauses = []
        for i in range(self.rows):
            for j in range(self.cols):
                for t in range(self.t_max + 1):
                    # first
                    if t == 0:
                        continue

                    # middle
                    if t > 0 and t != self.t_max:
                        clauses.append([-self.obj2id[f"Q0_{i}_{j}^{t}"], self.obj2id[f"Q1_{i}_{j}^{t + 1}"]])
                        clauses.append([-self.obj2id[f"Q1_{i}_{j}^{t}"], self.obj2id[f"H_{i}_{j}^{t + 1}"]])
                        clauses.append([-self.obj2id[f"Q1_{i}_{j}^{t}"], self.obj2id[f"Q0_{i}_{j}^{t - 1}"]])
                        clauses.append([-self.obj2id[f"Q0_{i}_{j}^{t}"], self.obj2id[f"S0_{i}_{j}^{t - 1}"],
                                        self.obj2id[f"S1_{i}_{j}^{t - 1}"], self.obj2id[f"S2_{i}_{j}^{t - 1}"]])

                    # last
                    if t == self.t_max:
                        clauses.append([-self.obj2id[f"Q1_{i}_{j}^{t}"], self.obj2id[f"Q0_{i}_{j}^{t - 1}"]])
                        clauses.append([-self.obj2id[f"Q0_{i}_{j}^{t}"], self.obj2id[f"S0_{i}_{j}^{t - 1}"],
                                        self.obj2id[f"S1_{i}_{j}^{t - 1}"], self.obj2id[f"S2_{i}_{j}^{t - 1}"]])

        return CNF(from_clauses=clauses)
    
    def H_tile_dynamics(self):
        clauses = []
        for i in range(self.rows):
            for j in range(self.cols):
                for t in range(self.t_max + 1):
                    if 0 < t:
                        # H_t => H_t-1 v Q0_t-1 v S0_t-1
                        clauses.append([-self.obj2id[f"H_{i}_{j}^{t}"],
                                        self.obj2id[f"H_{i}_{j}^{t - 1}"],
                                        self.obj2id[f"Q1_{i}_{j}^{t - 1}"],
                                        self.obj2id[f"S2_{i}_{j}^{t - 1}"],
                                        ])
                        
                    if t < self.num_observations - 1:
                        # H_t => H_t+1 \/ S2_t+1 \/ I_recent_t+1
                        clauses.append([-self.obj2id[f"H_{i}_{j}^{t}"],
                                        self.obj2id[f"S0_{i}_{j}^{t + 1}"],
                                        self.obj2id[f"I0_{i}_{j}^{t + 1}"],
                                        self.obj2id[f"H_{i}_{j}^{t + 1}"],
                                        ])

        return CNF(from_clauses=clauses)

    def unique_tile_dynamics(self):
        clauses = []
        for i in range(self.rows):
            for j in range(self.cols):
                for t in range(self.t_max + 1):  # including all
                    legal_states = [
                        self.pool.obj2id[f"U_{i}_{j}^{t}"],
                        self.pool.obj2id[f"I0_{i}_{j}^{t}"],
                        self.pool.obj2id[f"I_{i}_{j}^{t}"],
                        self.pool.obj2id[f"S0_{i}_{j}^{t}"],
                        self.pool.obj2id[f"S1_{i}_{j}^{t}"],
                        self.pool.obj2id[f"S2_{i}_{j}^{t}"],
                        self.pool.obj2id[f"Q0_{i}_{j}^{t}"],
                        self.pool.obj2id[f"Q1_{i}_{j}^{t}"],
                        self.pool.obj2id[f"H_{i}_{j}^{t}"],
                    ]
                    clauses.extend(CardEnc.equals(legal_states, 1, vpool=self.pool))
        return CNF(from_clauses=clauses)

    def first_turn_rules(self):
        clauses = []
        for i in range(self.rows):
            for j in range(self.cols):
                for t in range(min(2, self.num_observations)):
                    if t == 0:
                        # can't be Q0, Q1, S1, S2, I, I0 in the first turn
                        clauses.append([-self.obj2id[f"Q0_{i}_{j}^{t}"]])
                        clauses.append([-self.obj2id[f"Q1_{i}_{j}^{t}"]])
                        clauses.append([-self.obj2id[f"S1_{i}_{j}^{t}"]])
                        clauses.append([-self.obj2id[f"S2_{i}_{j}^{t}"]])
                        clauses.append([-self.obj2id[f"I_{i}_{j}^{t}"]])
                        clauses.append([-self.obj2id[f"I0_{i}_{j}^{t}"]])
                    if t == 1:
                        # can't be Q1, S2, I in the second turn
                        clauses.append([-self.obj2id[f"Q1_{i}_{j}^{t}"]])
                        clauses.append([-self.obj2id[f"S2_{i}_{j}^{t}"]])
                        clauses.append([-self.obj2id[f"I_{i}_{j}^{t}"]])
        return CNF(from_clauses=clauses)

    def hadar_dynamics(self):
        clauses = []

        for t in range(self.num_observations):
            clauses.extend(CardEnc.atmost(self.__get_I0_predicates(t), bound=self.medics, vpool=self.pool).clauses)

        if self.medics == 0:
            return clauses

        for t in range(self.num_observations - 1):
            for num_healthy in range(self.cols * self.rows):
                for healthy_tiles in itertools.combinations(self.tiles, num_healthy):
                    sick_tiles = [tile for tile in self.tiles if tile not in healthy_tiles]
                    clause = []

                    for i, j in healthy_tiles:
                        clause.append(-self.obj2id[f"H_{i}_{j}^{t}"])

                    for i, j in sick_tiles:
                        clause.append(self.obj2id[f"H_{i}_{j}^{t}"])

                    lits = [self.obj2id[f"I0_{i}_{j}^{t + 1}"] for i, j in healthy_tiles]
                    equals_clauses = CardEnc.equals(lits, bound=min(self.medics, num_healthy), vpool=self.pool).clauses
                    for sub_clause in equals_clauses:
                        temp_clause = copy.deepcopy(clause)
                        temp_clause += sub_clause
                        clauses.append(temp_clause)

        return CNF(from_clauses=clauses)

    def naveh_dynamics(self):
        clauses = []

        for t in range(1, self.num_observations):
            clauses.extend(CardEnc.atmost(self.__get_Q0_predicates(t),
                                          bound=self.police,
                                          vpool=self.pool).clauses)

        if self.police == 0:
            return clauses

        for t in range(self.num_observations - 1):
            for num_sick in range(self.cols * self.rows):
                for sick_tiles in itertools.combinations(self.tiles, num_sick):
                    healthy_tiles = [tile for tile in self.tiles if tile not in sick_tiles]
                    for sick_state_perm in itertools.combinations_with_replacement(self.possible_sick_states(t),
                                                                                   num_sick):
                        clause = []

                        for (i, j), state in zip(sick_tiles, sick_state_perm):
                            clause.append(-self.obj2id[f"{state}_{i}_{j}^{t}"])
                        for i, j in healthy_tiles:
                            for state in self.possible_sick_states(t):
                                clause.append(self.obj2id[f"{state}_{i}_{j}^{t}"])

                        equals_clauses = CardEnc.equals(lits=self.__get_Q0_predicates(t + 1),
                                                        bound=min(self.police, num_sick),
                                                        vpool=self.pool).clauses
                        for sub_clause in equals_clauses:
                            temp_clause = copy.deepcopy(clause)
                            temp_clause += sub_clause
                            clauses.append(temp_clause)

        return CNF(from_clauses=clauses)

    def world_dynamics(self):
        # single tile dynamics
        dynamics = CNF()
        dynamics.extend(self.U_tile_dynamics())
        dynamics.extend(self.I_tile_dynamics())
        dynamics.extend(self.S_tile_dynamics())
        dynamics.extend(self.Q_tile_dynamics())
        dynamics.extend(self.H_tile_dynamics())

        # exactly one state for each tile
        dynamics.extend(self.first_turn_rules())
        dynamics.extend(self.unique_tile_dynamics())

        # use all teams
        # dynamics.extend(self.use_all_medics_dynamics())
        dynamics.extend(self.hadar_dynamics())
        dynamics.extend(self.naveh_dynamics())

        return dynamics

    def observations_to_assumptions(self) -> list:
        obs = self.observations
        assumptions = []
        for t in range(self.num_observations):
            for i in range(self.rows):
                for j in range(self.cols):
                    if obs[t][i][j] == "H":
                        assumptions.append(self.obj2id[f"H_{i}_{j}^{t}"])
                    if obs[t][i][j] == "U":
                        assumptions.append(self.obj2id[f"U_{i}_{j}^{t}"])
                    if t == 0:
                        # assuming no Q and I in first turn
                        if obs[t][i][j] == "S":
                            assumptions.append(self.obj2id[f"S0_{i}_{j}^{t}"])
                    if t > 0:
                        # observed Q Q
                        if obs[t][i][j] == "Q" and obs[t - 1][i][j] == "Q":
                            assumptions.append(self.obj2id[f"Q1_{i}_{j}^{t}"])
                        # observed X Q
                        if obs[t][i][j] == "Q" and obs[t - 1][i][j] != "Q" and obs[t - 1][i][j] != "?":
                            assumptions.append(self.obj2id[f"Q0_{i}_{j}^{t}"])
                        # observed I I
                        if obs[t][i][j] == "I" and obs[t - 1][i][j] == "I":
                            assumptions.append(self.obj2id[f"I_{i}_{j}^{t}"])
                        # observed X I
                        if obs[t][i][j] == "I" and obs[t - 1][i][j] != "I" and obs[t - 1][i][j] != "?":
                            assumptions.append(self.obj2id[f"I0_{i}_{j}^{t}"])
                    if t == 1:
                        # second observation
                        # observed S S
                        if obs[t][i][j] == "S" and obs[t - 1][i][j] == "S":
                            assumptions.append(self.obj2id[f"S1_{i}_{j}^{t}"])
                        # observed X S
                        if obs[t][i][j] == "S" and obs[t - 1][i][j] != "S" and obs[t - 1][i][j] != "?":
                            assumptions.append(self.obj2id[f"S0_{i}_{j}^{t}"])

                    if t > 1:
                        # third observation and on
                        # observed S S S
                        if obs[t][i][j] == "S" and obs[t - 1][i][j] == "S" and obs[t - 2][i][j] == "S":
                            assumptions.append(self.obj2id[f"S2_{i}_{j}^{t}"])
                        # observed X S S
                        if obs[t][i][j] == "S" and obs[t - 1][i][j] == "S" and obs[t - 2][i][j] != "S" and obs[t - 2][i][j] != "?":
                            assumptions.append(self.obj2id[f"S1_{i}_{j}^{t}"])
                        # observed S X S
                        # observed X X S
                        # observed ? X S
                        if obs[t][i][j] == "S" and obs[t - 1][i][j] != "S" and obs[t - 1][i][j] != "?":
                            assumptions.append(self.obj2id[f"S0_{i}_{j}^{t}"])
        # assumptions = [[a] for a in assumptions]
        return assumptions

    def read_observations(self):
        clauses = []
        for t in range(self.num_observations):
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.observations[t][i][j] == "S":
                        clauses.append([self.obj2id[f"S0_{i}_{j}^{t}"],
                                        self.obj2id[f"S1_{i}_{j}^{t}"],
                                        self.obj2id[f"S2_{i}_{j}^{t}"]])
                        continue
                    if self.observations[t][i][j] == "Q":
                        clauses.append([self.obj2id[f"Q0_{i}_{j}^{t}"],
                                        self.obj2id[f"Q1_{i}_{j}^{t}"]])
                        continue
                    if self.observations[t][i][j] == "U":
                        clauses.append([self.obj2id[f"U_{i}_{j}^{t}"]])
                        continue
                    if self.observations[t][i][j] == "H":
                        clauses.append([self.obj2id[f"H_{i}_{j}^{t}"]])
                        continue
                    if self.observations[t][i][j] == "I":
                        clauses.append([self.obj2id[f"I0_{i}_{j}^{t}"],
                                        self.obj2id[f"I_{i}_{j}^{t}"]])
                        continue

        return CNF(from_clauses=clauses)

    def translate_query(self, query, state: bool):
        (i, j), t, s = query
        clauses = []
        if s == "U":
            clauses = [[self.pool.obj2id[f"U_{i}_{j}^{t}"]] if state else [-self.pool.obj2id[f"U_{i}_{j}^{t}"]]]
        if s == "H":
            clauses = [[self.pool.obj2id[f"H_{i}_{j}^{t}"]] if state else [-self.pool.obj2id[f"H_{i}_{j}^{t}"]]]
        if s == "I":
            if state:
                clauses = [[self.pool.obj2id[f"I_{i}_{j}^{t}"],
                            self.pool.obj2id[f"I0_{i}_{j}^{t}"]]]
            else:
                clauses = [[-self.pool.obj2id[f"I_{i}_{j}^{t}"]],
                           [-self.pool.obj2id[f"I0_{i}_{j}^{t}"]]]
        if s == "Q":
            if state:
                clauses = [[self.pool.obj2id[f"Q0_{i}_{j}^{t}"],
                            self.pool.obj2id[f"Q1_{i}_{j}^{t}"]]]
            else:
                clauses = [[-self.pool.obj2id[f"Q0_{i}_{j}^{t}"]],
                           [-self.pool.obj2id[f"Q1_{i}_{j}^{t}"]]]
        if s == "S":
            if state:
                clauses = [[self.pool.obj2id[f"S0_{i}_{j}^{t}"],
                            self.pool.obj2id[f"S1_{i}_{j}^{t}"],
                            self.pool.obj2id[f"S2_{i}_{j}^{t}"]]]
            else:
                clauses = [[-self.pool.obj2id[f"S0_{i}_{j}^{t}"]],
                           [-self.pool.obj2id[f"S1_{i}_{j}^{t}"]],
                           [-self.pool.obj2id[f"S2_{i}_{j}^{t}"]]]

        return CNF(from_clauses=clauses)

    def solve(self, solver_name="m22"):
        answers_dict = {}
        world_dynamics = self.world_dynamics()
        for q in self.queries:
            (i, j), t, s = q
            # create new solver and append world dynamics and query to it
            solver = Solver(name=solver_name)
            solver.append_formula(world_dynamics)
            solver.append_formula(self.read_observations())
            solver.append_formula(self.translate_query(q, state=True))

            assumptions = self.observations_to_assumptions()

            solution = solver.solve(assumptions=assumptions)

            if not solution:  # solution was false
                answers_dict[q] = 'F'
            else:  # solution was true
                other_states = ["Q", "U", "I", "H", "S"]
                other_states.remove(s)
                skip = False
                for other_state in other_states:
                    solver = Solver(name=solver_name)
                    solver.append_formula(world_dynamics)
                    solver.append_formula(self.read_observations())
                    q_new = (i, j), t, other_state
                    solver.append_formula(self.translate_query(q_new, state=True))
                    assumptions = self.observations_to_assumptions()

                    solution = solver.solve(assumptions=assumptions)
                    if solution:  # check for ambiguity
                        answers_dict[q] = '?'
                        skip = True
                        break

                if not skip:
                    answers_dict[q] = 'T'

        return answers_dict

    @staticmethod
    def possible_sick_states(t):
        if t == 0:
            return ["S0"]
        if t == 1:
            return ["S0", "S1"]
        return ["S0", "S1", "S2"]

    def __get_neighbours_indices(self, i, j):
        neighbours_indices = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
        if i == 0:
            neighbours_indices.remove((i - 1, j))
        if i == self.rows - 1:
            neighbours_indices.remove((i + 1, j))
        if j == 0:
            neighbours_indices.remove((i, j - 1))
        if j == self.cols - 1:
            neighbours_indices.remove((i, j + 1))
        return neighbours_indices

    def __get_I0_predicates(self, t):
        I0_predicates = []
        for i in range(self.rows):
            for j in range(self.cols):
                I0_predicates.append(self.obj2id[f"I0_{i}_{j}^{t}"])
        return I0_predicates

    def __get_Q0_predicates(self, t):
        Q0_predicates = []
        for i in range(self.rows):
            for j in range(self.cols):
                Q0_predicates.append(self.obj2id[f"Q0_{i}_{j}^{t}"])
        return Q0_predicates
