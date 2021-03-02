from pysat.solvers import Glucose4

# from itertools import combinations, product

ids = ['308292051']

class Problem:

    def __init__(self, input):
        self.police = input['police']
        self.medics = input['medics']
        self.maps = input.get("observations")
        self.queries = list(input.get("queries"))
        self.results = {}
        self.num_observations = len(self.maps)
        self.rows = len(self.maps[0])
        self.cols = len(self.maps[0][0])
        # self.rows, self.cols = 1, 3
        self.kb = []
        self.query_kb = []
        self.clauses_S = []

    def arrange_problem(self):
        for i in self.queries:
            # If there's only one observation then any '?' tile state is unknown
            if self.num_observations == 1:
                self.results[i] = '?'
                continue
            self.kb = []
            self.query_kb = []
            self.build_kb(i)
            input_clause = self.query_to_cnf(i)

            g = Glucose4()
            f = Glucose4()

            f_clauses, extra_f = [], []
            for kb_clause in self.query_kb:
                g.add_clause(kb_clause)
                f_clauses.append(kb_clause)

                if (abs(input_clause) // 10) % 10 == self.tile_state('S'):
                    for index, k in enumerate(kb_clause):
                        if abs(k) % 10 == 0:
                            g.add_clause([-1 * abs(k)])
                            break

                if (abs(input_clause) // 10) % 10 == self.tile_state('H'):
                    for index, k in enumerate(kb_clause):
                        if abs(k) % 10 == 0:
                            extra_f.append([-1*abs(k)])
                            break

            for kb_clause in self.kb:
                g.add_clause(kb_clause)
                f_clauses.append(kb_clause)

            for clause in f_clauses:
                for index, l in enumerate(clause):
                    if abs(l) % 10000 == input_clause:
                        clause[index] = -1*l
                        f.add_clause(clause)
                        break

            for kb_clause in extra_f:
                f.add_clause(kb_clause)

            asked_query = g.solve()
            if asked_query:
                self.results[i] = 'T'
            elif not asked_query:
                self.results[i] = 'F'
            """opposite_query = f.solve()
            if asked_query != opposite_query:
                if asked_query:
                    self.results[i] = 'T'
                elif not asked_query:
                    self.results[i] = 'F'
            else:
                self.results[i] = '?'"""

        return self.results


    def formalize_state_clause(self, index, state, time):
        return index * 100 + self.tile_state(state) * 10 + time+1

    @staticmethod
    def tile_state(x):
        return {
            'H': 0,
            'S': 1,
            'U': 2,
            '?': 3,
        }.get(x, 9)

    def build_kb(self, i):
        for time, j in enumerate(self.maps):
            for row, k in enumerate(j):
                for col, l in enumerate(k):
                    loc = (row+1)*10 + col+1
                    query_translated_loc = (i[0][0] + 1)*10 + i[0][1] + 1
                    if loc == query_translated_loc and time == i[1]:
                        clause = self.formalize_state_clause(loc, i[2], time)
                    else:
                        clause = self.formalize_state_clause(loc, l, time)
                    self.kb.append([clause])
                    self.add_negators(clause)

    def query_to_cnf(self, query):
        location = (query[0][0]+1) * 10 + query[0][1] + 1
        time = query[1]
        state = query[2]

        input_clause = self.formalize_state_clause(location, state, time)
        input_last_turn = self.formalize_state_clause(location, state, time - 1)
        adjacent_tiles = self.existing_adj_tiles(location)
        adjacent_sick_conds = self.clausify_possible_sick_neighbors(adjacent_tiles, time)

        if query[2] == 'H':

            u_clause = self.add_u_clauses(input_clause)
            neighbors_clause = [input_clause, -input_last_turn]
            main_clause = [-input_clause, input_last_turn]
            curr_tile_last_turns = [self.formalize_state_clause(location, 'S', time - i) for i in range(1, 4)]

            if time >= 3:
                for i in curr_tile_last_turns:
                    self.query_kb.append(main_clause + [i])
            else:
                self.query_kb.append(main_clause)

            for i in adjacent_sick_conds:
                if time >= 3:
                    for j in curr_tile_last_turns:
                        self.query_kb.append([-input_clause, -i, j])
                else:
                    self.query_kb.append([-input_clause, -i])
                neighbors_clause.append(i)

            adjacency_list = []
            [adjacency_list.append([i+2]) for i in adjacent_sick_conds]

            k = 0
            for i in adjacency_list:
                adj_of_adj = self.existing_adj_tiles(i[0]//100)
                for j in self.clausify_possible_sick_neighbors(adj_of_adj, i[0] % 10 - 1):
                    if not j // 100 == input_clause // 100:
                        adjacency_list[k].append(j)
                k += 1

            for i in adjacency_list:
                temp_clause = [-input_clause, -i[0]]
                # Go into for-loop only if adjacent tile has neighbors
                if len(i) > 1:
                    k = 0
                    for j in i:
                        if k == 0:
                            k += 1
                            continue
                        temp_clause.append(j)
                        k += 1

                if time >= 3:
                    for j in curr_tile_last_turns:
                        self.query_kb.append(temp_clause + [j])
                else:
                    self.query_kb.append(temp_clause)

            self.clauses_S = []
            self.recursive_listing(adjacency_list, neighbors_clause + u_clause)
            for i in self.clauses_S:
                self.query_kb.append(i)

        if query[2] == 'S':

            u_clause = self.add_u_clauses(input_clause)
            self.query_kb.append([input_clause, -input_last_turn] + u_clause)
            main_clause = [-input_clause, input_last_turn]
            for i in adjacent_sick_conds:
                self.query_kb.append([input_clause, -i] + u_clause)
                main_clause.append(i)

            self.query_kb.append(main_clause)   # may be redundant

            clauses_for_neighbors = [input_clause]
            for i in adjacent_tiles:
                if [self.formalize_state_clause(i, 'H', time)] in self.kb:
                    clause_curr = self.formalize_state_clause(i, 'H', time)
                    clause_future = self.formalize_state_clause(i, 'S', time+1)
                    clauses_for_neighbors.append(-clause_curr)
                    clauses_for_neighbors.append(-clause_future)

                    self.query_kb.append(main_clause + [clause_curr])
                    self.query_kb.append(main_clause + [clause_future])

                adj_of_adj = self.existing_adj_tiles(i)
                for j in self.clausify_possible_sick_neighbors(adj_of_adj, time+1):
                    if not j // 100 == input_clause // 100:
                        clauses_for_neighbors.append(j)
            self.query_kb.append(clauses_for_neighbors + u_clause)

            if time >= 3:
                # Create clauses to check if sick in consecutive last 3 turns
                curr_tile_last_turns = [self.formalize_state_clause(location, state, time - i) for i in range(1, 4)]
                main_clause = [-input_clause]
                [main_clause.append(-i) for i in curr_tile_last_turns]
                self.query_kb.append(main_clause)

        if query[2] == 'U':
            main_clause = [input_clause]
            for i in range(len(self.maps)):
                if not i == time:
                    not_h = self.formalize_state_clause(location, 'H', i)
                    not_s = self.formalize_state_clause(location, 'S', i)
                    self.query_kb.append([-input_clause, -not_h])
                    self.query_kb.append([-input_clause, -not_s])
                    main_clause += [not_h, not_s]
                else:
                    continue
            self.query_kb.append(main_clause)

        return input_clause


    def add_negators(self, tile):
        """Add negators for each tile - if tile is S then add [-S,-H], [-S,-?],..."""
        tile_options_num = 4
        location = tile // 100
        state = tile // 10 % 10
        time = tile % 10
        for i in range(tile_options_num-1):
            if i == state:
                continue
            else:
                self.kb.append([-(100*location+i*10+time), -(100*location+state*10+time)])
        return

    def existing_adj_tiles(self, location):
        adjacent_tiles = []
        row, col = location // 10, location % 10
        
        if row - 1 > 0:
            adjacent_tiles.append(location - 10)
        if row + 1 <= self.rows:
            adjacent_tiles.append(location + 10)
        if col - 1 > 0:
            adjacent_tiles.append(location - 1)
        if col + 1 <= self.cols:
            adjacent_tiles.append(location + 1)
        return adjacent_tiles

    def clausify_possible_sick_neighbors(self, adjacent_tiles, time):
        statements = []
        for i in adjacent_tiles:
            statements.append(self.formalize_state_clause(i, 'S', time - 1))
        return statements

    def recursive_listing(self, input1, clause):
        if len(input1) > 1:
            for i in range(len(input1[0])):
                clause.append(input1[0][i])
                self.recursive_listing(input1[1:], clause)
                clause.pop()

        if len(input1) == 1:
            for i in range(len(input1[0])):
                clause.append(input1[0][i])
                self.clauses_S.append(clause[:])
                clause.pop()
            return

    def add_u_clauses(self, input_clause):
        time, location, u_clause = input_clause % 10, input_clause // 100, []
        for i in range(1, self.num_observations+1):
            if not i == time:
                not_u = self.formalize_state_clause(location, 'U', i-1)
                self.query_kb.append([-input_clause, -not_u])
                u_clause += [not_u]
            else:
                continue
        return u_clause

def solve_problem(input_problem):
    problem_obj = Problem(input_problem)
    return problem_obj.arrange_problem()
