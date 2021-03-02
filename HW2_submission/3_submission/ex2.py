from pysat.solvers import Glucose3
from pysat.card import CardEnc, EncType
from itertools import combinations
from sympy import to_cnf


ids = ['211451364', '211622352']


def solve_problem(input):
    org_in = input.copy()
    org_in["queries"] = org_in["queries"]
    ans = {}
    for query in org_in["queries"]:
        input["queries"] = (query, True)
        prob = Problem(input)
        is_possible_true = prob.solve()
        if not is_possible_true:
            ans[query] = "F"
            input = org_in.copy()
            continue
        input["queries"] = (query, False)
        prob = Problem(input)
        is_possible_false = prob.solve()
        if is_possible_false:
            ans[query] = "?"
            input = org_in.copy()
            continue
        ans[query] = "T"
        input = org_in.copy()
    return ans


def at_most(lits: list, k):
    k_groups = list(combinations(lits, k+1))
    atmost_k = []
    for group in k_groups:
        p = []
        for lit in group:
            p.append(-lit)
        atmost_k.append(p)
    return atmost_k


def at_least(lits: list, bound):
    lits_to_str_dict = {}
    str_to_lits_dict = {}
    for idx, lit in enumerate(lits):
        lits_to_str_dict[lit] = "A" * (idx + 1)
        str_to_lits_dict["A" * (idx + 1)] = lit
    lits = list(str_to_lits_dict.keys())
    k_groups = list(combinations(lits, bound))
    not_cnf_strings = []
    for group in k_groups:
        group = [str(item) for item in group]
        cur_str = "( " + " & ".join(group) + " )"
        not_cnf_strings.append(cur_str)
    not_cnf_strings = " | ".join(not_cnf_strings)
    cnf_string = to_cnf(not_cnf_strings)
    cnf_string = str(cnf_string)
    cnf_string = cnf_string.split("&")
    clauses = []
    for clause in cnf_string:
        clause = clause.replace("(", "").replace(")", "").split("|")
        clause = [lit.strip() for lit in clause if lit != ""]
        clause = [str_to_lits_dict[lit] for lit in clause]
        clauses.append(clause)
    return clauses


class Problem:

    def __init__(self, problem: dict):
        self.num_turns = len(problem["observations"])
        self.bottom = len(problem["observations"][0]) - 1
        self.right = len(problem["observations"][0][0]) - 1
        self.map = problem["observations"]
        self.num_police = problem["police"]
        self.num_medics = problem["medics"]
        # self.board = self.normalize_board(input(["observations"]))
        self.literal_meanings = {}
        self.rev_literal_meanings = {}
        self.solver = Glucose3()
        self.init_literal_meaning()
        self.queries = problem["queries"]
        self.add_known_clauses()
        self.add_num_ops_constraints()
        self.add_turn_constraints()
        self.add_using_all_constraints(use_police=True)
        self.add_using_all_constraints(use_police=False)

    def init_literal_meaning(self):
        counter = 1
        states = ["S2", "S1", "S0", "Q1", "Q0", "U", "I0", "I1", "H"]
        for turn, turn_state in enumerate(self.map):
            self.literal_meanings[turn] = {}
            for i, row in enumerate(turn_state):
                for j, item in enumerate(row):
                    for num in range(len(states)):
                        self.rev_literal_meanings[counter + num] = (turn, (i, j), states[num])
                    self.literal_meanings[turn][(i, j)] = {
                        state: counter + num for num, state in enumerate(states)
                    }
                    cnf = CardEnc.equals(lits=list(self.literal_meanings[turn][(i, j)].values()), bound=1,
                                         encoding=EncType.pairwise)
                    for clause in cnf.clauses:
                        self.solver.add_clause(clause)
                    counter += len(states)
                    self.literal_meanings[turn][(i, j)]["D"] = counter
                    self.rev_literal_meanings[counter] = (turn, (i, j), "D")
                    counter += 1
                    self.literal_meanings[turn][(i, j)]["P"] = counter
                    self.rev_literal_meanings[counter] = (turn, (i, j), "P")
                    counter += 1
                    self.literal_meanings[turn][(i, j)]["Sick"] = counter
                    self.rev_literal_meanings[counter] = (turn, (i, j), "Sick")
                    counter += 1
                    not_s = ["Q1", "Q0", "U", "I0", "I1", "H", "Sick"]
                    literals = [self.literal_meanings[turn][(i, j)][state] for state in not_s]
                    cnf = CardEnc.equals(lits=literals, bound=1,
                                         encoding=EncType.pairwise)
                    for clause in cnf.clauses:
                        self.solver.add_clause(clause)

    def add_known_clauses(self):
        for turn, turn_state in enumerate(self.map):
            for i, row in enumerate(turn_state):
                for j, item in enumerate(row):
                    if item == "H":
                        self.solver.add_clause([self.literal_meanings[turn][(i, j)]["H"]])
                    if item == "S":
                        self.solver.add_clause([self.literal_meanings[turn][(i, j)]["Sick"]])
                    if item == "Q":
                        self.solver.add_clause([self.literal_meanings[turn][(i, j)][f"Q{sick_num}"]
                                                for sick_num in range(2)])
                    if item == "I":
                        for cur_turn in range(turn, len(self.map)):
                            self.solver.add_clause([self.literal_meanings[turn][(i, j)][f"I{sick_num}"]
                                                    for sick_num in range(2)])
                    if item == "U":
                        for cur_turn in range(len(self.map)):
                            self.solver.add_clause([self.literal_meanings[cur_turn][(i, j)]["U"]])
        (q_loc, q_turn, q_state), q_val = self.queries
        q_literals = [self.literal_meanings[q_turn][q_loc][k] for k in self.literal_meanings[q_turn][q_loc].keys()
                      if q_state in k]
        if q_val:
            self.solver.add_clause(q_literals)
        else:
            for lit in q_literals:
                self.solver.add_clause([-lit])

    def add_num_ops_constraints(self):
        for turn, turn_states in self.literal_meanings.items():
            now_q = []
            now_i = []
            for item in turn_states.values():
                now_q.append(item["Q1"])
                now_i.append(item["I1"])
            if self.num_police > 0:
                cnf_q = at_most(lits=now_q, k=self.num_police)
                for clause in cnf_q:
                    self.solver.add_clause(clause)
            else:
                cnf_q = [[-item] for item in now_q]
                for clause in cnf_q:
                    self.solver.add_clause(clause)
            if self.num_medics > 0:
                cnf_i = at_most(lits=now_i, k=self.num_medics)
                for clause in cnf_i:
                    self.solver.add_clause(clause)
            else:
                cnf_i = [[-item] for item in now_i]
                for clause in cnf_i:
                    self.solver.add_clause(clause)
                    
    def get_neighbors(self, i, j):
        neighbors = []

        if i != 0:
            neighbors.append((i-1, j))
        if i != self.bottom:
            neighbors.append((i+1, j))
        if j != 0:
            neighbors.append((i, j-1))
        if j != self.right:
            neighbors.append((i, j+1))
        return neighbors
    
    def add_turn_constraints(self):
        for turn, turn_state in self.literal_meanings.items():
            if turn == len(self.literal_meanings) - 1:
                continue
            for loc, item in turn_state.items():
                self.solver.add_clause([-item["I1"], self.literal_meanings[turn + 1][loc]["I0"]])
                self.solver.add_clause([-item["I0"], self.literal_meanings[turn + 1][loc]["I0"]])
                self.solver.add_clause([-item["U"], self.literal_meanings[turn + 1][loc]["U"]])
                self.solver.add_clause([-item["Q1"], self.literal_meanings[turn + 1][loc]["Q0"]])
                self.solver.add_clause([-item["Q0"], self.literal_meanings[turn + 1][loc]["H"]])
                self.solver.add_clause([-item["S0"], self.literal_meanings[turn + 1][loc]["H"],
                                        self.literal_meanings[turn + 1][loc]["Q1"]])
                self.solver.add_clause([-item["S1"], self.literal_meanings[turn + 1][loc]["S0"],
                                        self.literal_meanings[turn + 1][loc]["Q1"]])
                self.solver.add_clause([-item["S2"], self.literal_meanings[turn + 1][loc]["S1"],
                                        self.literal_meanings[turn + 1][loc]["Q1"]])
                if turn == 0:
                    imp_on_first = ["S1", "S0", "Q1", "Q0", "I0", "I1"]
                    for state in imp_on_first:
                        self.solver.add_clause([-item[state]])
                i, j = loc

                sick_clauses = [[-item["Sick"]] + [item[f"S{sick_idx}"] for sick_idx in range(3)]]
                sick_clauses_cont = [[item["Sick"], -item[f"S{sick_idx}"]] for sick_idx in range(3)]
                sick_clauses = sick_clauses + sick_clauses_cont
                for clause in sick_clauses:
                    self.solver.add_clause(clause)

                # + [item[f"S{sick_idx}"] for sick_idx in range(3)],
                d_clauses = [[-item["D"], item["Sick"]],
                             [-item["D"], -self.literal_meanings[turn + 1][loc]["Q1"]]]
                d_clauses_cont = [[item["D"], self.literal_meanings[turn + 1][loc]["Q1"], -item["Sick"]]]
                d_clauses = d_clauses + d_clauses_cont
                for clause in d_clauses:
                    self.solver.add_clause(clause)
                neighbors = self.get_neighbors(i, j)
                neg_p_clauses = [[-item["P"]] + [self.literal_meanings[turn][cur_loc]["D"] for cur_loc in neighbors]]
                pos_p_clauses = [[item["P"], -self.literal_meanings[turn][cur_loc]["D"]] for cur_loc in neighbors]
                p_clauses = neg_p_clauses + pos_p_clauses
                for p_clause in p_clauses:
                    self.solver.add_clause(p_clause)
                p_clauses = [[-item["H"], -item["P"], self.literal_meanings[turn + 1][loc]["S2"],
                              self.literal_meanings[turn + 1][loc]["I1"]],
                             [-item["H"], item["P"], self.literal_meanings[turn + 1][loc]["H"],
                              self.literal_meanings[turn + 1][loc]["I1"]]
                             ]
                for p_clause in p_clauses:
                    self.solver.add_clause(p_clause)

    def add_using_all_constraints(self, use_police):
        if use_police:
            max_teams = self.num_police
            cur_state = "Sick"
            out_state = "Q1"
        else:
            max_teams = self.num_medics
            cur_state = "H"
            out_state = "I1"
        tiles_options = (self.literal_meanings[0].keys())
        for turn in range(self.num_turns - 1):
            all_rel_next = [item[out_state] for item in self.literal_meanings[turn + 1].values()]

            for k in range(1, max_teams + 1):
                at_least_k = at_least(all_rel_next, bound=k)

                subsets = list(combinations(tiles_options, k))
                for sub in subsets:
                    left_side = [-item[cur_state] for loc, item in self.literal_meanings[turn].items() if loc in sub]
                    clauses = [left_side + c_i for c_i in at_least_k]
                    for clause in clauses:
                        self.solver.add_clause(clause)

    def solve(self):
        is_solvable = self.solver.solve()
        # return is_solvable
        # model = self.solver.get_model()
        # if model is None:
        #     return is_solvable
        # states = [0] * self.num_turns
        # for t in range(len(states)):
        #     states[t] = {}
        # for lit in model:
        #     turn, loc, name = self.rev_literal_meanings[abs(lit)]
        #     if lit > 0 and loc not in states[turn]:
        #         states[turn][loc] = name
        return is_solvable
