
from pysat.solvers import Glucose4

ids = ['322758483', '318724218']


def solve_problem(prob):
    problem = Problem(prob)
    return problem.solve_prob()


class Action:
    def __init__(self, index, pre, add, delt):
        self.index = index
        self.pre = pre
        self.add = add
        self.delt = delt
        self.actlist = [index, pre, add, delt]


class Problem:
    def __init__(self, input):

        self.obs = input["observations"]
        self.queries = input["queries"]

        self.prop_ind = 0
        self.action_ind = 0
        self.props_dict = {}
        self.actions = []

        self.options = ['S', 'H', 'U']
        self.ext_options = ['S', 'H', 'U', '?']
        self.obs_dict = {}

        self.no_turns = len(self.obs)
        self.len_rows = len(self.obs[0])
        self.len_cols = len(self.obs[0][0])

        self.as_strips()
        self.lights_set_Action()

    def knowledge_check(self, t, i, j, opt):
        return [self.props_dict[t, (i, j), opt], self.props_dict[t, (i, j), '?']]

    def as_strips(self):
        for time, obs in enumerate(self.obs):
            for i, row in enumerate(obs):
                for j, tile in enumerate(row):
                    self.obs_dict[(time, (i, j), '?')] = True if tile != '?' else False
                    self.prop_ind += 1
                    p_ind = self.prop_ind
                    self.props_dict[(time, (i, j), '?')] = p_ind

                    for opt in self.options:
                        if tile != opt and tile != '?':
                            self.obs_dict[(time, (i, j), opt)] = False
                        else:
                            self.obs_dict[(time, (i, j), opt)] = True
                        self.prop_ind += 1
                        p_ind = self.prop_ind
                        self.props_dict[(time, (i, j), opt)] = p_ind

    def get_neighs(self, i, j):
        neighs = []
        if i == 0:
            neighs.append((i + 1, j))
        elif i == self.len_rows - 1:
            neighs.append((i - 1, j))
        else:
            neighs.append((i - 1, j))
            neighs.append((i + 1, j))
        if j == 0:
            neighs.append((i, j + 1))
        elif j == self.len_cols - 1:
            neighs.append((i, j - 1))
        else:
            neighs.append((i, j + 1))
            neighs.append((i, j - 1))
        return neighs

    def in_bounds(self, x, y):
        if 0 <= x < self.len_rows and 0 <= y < self.len_cols:
            return True
        else:
            return False
    def neighbors_list(self, t, i, j, char):
        neighbor_props = []
        for x, y in self.get_neighs(i, j):
            if self.in_bounds(x, y):
                neighbor_props.append((t, (x, y), char))
        return neighbor_props

    def donot_remove_this(self, t, i, j, char):
        lst = []
        for letter in self.options:
            if letter != char:
                lst.append(self.props_dict[t, (i, j), letter])
        return lst

    def after_infected(self, t, i, j):
        add = []
        delt = []
        for sick_time in range(t + 1, t + 3):
            if sick_time < self.no_turns:
                add.extend(self.knowledge_check(sick_time, i, j, 'S'))
                delt.extend((self.donot_remove_this(sick_time, i, j, 'S')))
        if t + 3 < self.no_turns:
            add.extend(self.knowledge_check(t + 3, i, j, 'H'))
            delt.extend(self.donot_remove_this(t + 3, i, j, 'H'))

        return add, delt

    def lights_set_Action(self):
        for t in range(self.no_turns - 1):
            for i in range(self.len_rows):
                for j in range(self.len_cols):
                    self.countdown(t, i, j)
                    self.get_infected(t, i, j)
                    self.infect(t, i, j)
                    self.yuuu(t, i, j)
                    self.yuuunt(t, i, j)
                    self.is_healthy(t, i, j)
                    self.reverse_health(t, i, j)
                    self.who_r_u(t, i, j)

    def countdown(self, t, i, j):

        if 'Q' not in self.options and any(
                [time < self.no_turns and self.obs[time][i][j] == '?' for time in range(t + 1, t + 4)]):
            pre = self.knowledge_check(t, i, j, 'S')
            if t > 0:
                pre.extend(self.knowledge_check(t - 1, i, j, 'H'))

            add, delt = self.after_infected(t, i, j)
            self.action_ind += 1
            self.actions.append(Action(self.action_ind, pre, add, delt))

    def is_healthy(self, t, i, j):
        if (self.obs[t][i][j] == '?' or self.obs[t + 1][i][j] == '?') and t + 1 < self.no_turns:
            pre = self.knowledge_check(t, i, j, 'H')
            for neighbor in self.neighbors_list(t, i, j, 'S'):
                pre.append(-self.props_dict[neighbor])

            if 'I' not in self.options:
                add = self.knowledge_check(t + 1, i, j, 'H')
                delt = self.donot_remove_this(t + 1, i, j, 'H')

            else:
                lets = ['S', 'U']
                add = []
                if 'Q' in self.options:
                    lets.append('Q')
                delt = [self.props_dict[t + 1, (i, j), let] for let in lets]

            self.action_ind += 1
            self.actions.append(Action(self.action_ind, pre, add, delt))

    def reverse_health(self, t, i, j):
        if t + 1 < self.no_turns:
            if any([(self.in_bounds(x, y) and self.obs[t][x][y]) == '?' for x, y in self.get_neighs(i, j)]):
                pre = self.knowledge_check(t, i, j, 'H')
                pre.extend(self.knowledge_check(t + 1, i, j, 'H'))

                add = []
                dele = [self.props_dict[n] for n in self.neighbors_list(t, i, j, 'S')]

                self.action_ind += 1
                act = Action(self.action_ind, pre, add, dele)
                self.actions.append(act)

    def get_infected(self, t, i, j):
        for x, y in self.get_neighs(i, j):
            if self.in_bounds(x, y) and any(
                    [time < self.no_turns and self.obs[time][x][y] == '?' for time in range(t, t + 4)]):
                pre = self.knowledge_check(t, i, j, 'H')
                pre.extend(self.knowledge_check(t + 1, i, j, 'S'))
                for neighbor in self.neighbors_list(t, i, j, 'S'):
                    if neighbor[2] != (x, y):
                        pre.append(- self.props_dict[neighbor])
                pre.append(- self.props_dict[t, (x, y), '?'])

                add = self.knowledge_check(t, x, y, 'S')
                delt = self.donot_remove_this(t, x, y, 'S')


                a, d = self.after_infected(t, i, j)
                add.extend(a)
                delt.extend(d)

                self.action_ind += 1
                self.actions.append(Action(self.action_ind, pre, add, delt))

    def infect(self, t, i, j):
        pre = self.knowledge_check(t, i, j, 'S')

        for x, y in self.get_neighs(i, j):
            if self.in_bounds(x, y) and any(
                    [time < self.no_turns and self.obs[time][x][y] == '?' for time in range(t, t + 5)]):
                pre.extend(self.knowledge_check(t, x, y, 'H'))
                add = self.knowledge_check(t + 1, x, y, 'S')
                dele = self.donot_remove_this(t + 1, x, y, 'S')

                adder, deller = self.after_infected(t + 1, x, y)
                add.extend(adder)
                dele.extend(deller)

                self.action_ind += 1
                self.actions.append(Action(self.action_ind, pre, add, dele))

    def yuuu(self, t, i, j):
        if any([self.obs[time][i][j] == '?' for time in range(self.no_turns)]):
            pre = self.knowledge_check(t, i, j, 'U')
            add = []
            delt = []
            for t_U in range(self.no_turns):
                add.extend(self.knowledge_check(t_U, i, j, 'U'))
                delt.extend(self.donot_remove_this(t_U, i, j, 'U'))
            self.action_ind += 1
            act = Action(self.action_ind, pre, add, delt)
            self.actions.append(act)

    def yuuunt(self, t, i, j):
        if any([self.obs[time][i][j] == '?' for time in range(self.no_turns)]):
            for let in self.options:
                if let != 'U':
                    pre = self.knowledge_check(t, i, j, let)
                    add = []
                    delt = [self.props_dict[t_U, (i, j), 'U'] for t_U in range(self.no_turns)]
                    self.action_ind += 1
                    act = Action(self.action_ind, pre, add, delt)
                    self.actions.append(act)

    def who_r_u(self, t, i, j):
        if self.obs[t][i][j] == '?':
            for letter in self.options:
                pre = [-self.props_dict[t, (i, j), '?']]
                for let in self.options:
                    if let != letter:
                        pre.append(-self.props_dict[(t, (i, j), let)])
                add = self.knowledge_check(t, i, j, letter)
                delt = []
                self.action_ind += 1
                self.actions.append(Action(self.action_ind, pre, add, delt))

    def solve_prob(self):

        assignment_dict = {}  # Saves DPLL answer for each letter assignment
        results_dict = {}  # Saves final answer for each query
        flag = True
        for i in range(len(self.queries)):
            results_dict[self.queries[i]] = '?'  # Default value
            for letter in self.options:
                assignment_dict[letter] = juan_coin(self, self.queries[i], letter)

                #  if the letter is the query's input, and the result for said input is False:
                if letter == self.queries[i][2] and assignment_dict[letter] is False:
                    results_dict[self.queries[i]] = 'F'
                    break  # stop iterating over this entire query

                # if the letter is not the query's input, and the result for said input is True:
                elif assignment_dict[letter] and letter != self.queries[i][2]:
                    flag = False

            if flag and results_dict[self.queries[i]] != 'F':
                results_dict[self.queries[i]] = 'T'
            elif not flag and results_dict[self.queries[i]] != 'F':
                results_dict[self.queries[i]] = '?'

        return results_dict

    def is_negative(self, p):
        if p < 0:
            return -1
        else:
            return 1

    def actions_current_index(self, time):
        rounder = self.prop_ind + self.action_ind
        return time * rounder + self.prop_ind

    def props_current_index(self, time):
        rounder = self.prop_ind + self.action_ind
        return time * rounder


def juan_coin(problem, query, letter):
    g = Glucose4()
    b = 20
    
    # Initial state clauses
    for key in problem.obs_dict.keys():
        sign = 1 if problem.obs_dict[key] else -1
        g.add_clause([sign * problem.props_dict[key]])

    for t in range(b):

        # Goal State Clauses
        know_assumption = problem.props_current_index(t) + problem.props_dict[query[1], query[0], '?']
        letter_assumption = problem.props_current_index(t) + problem.props_dict[query[1], query[0], letter]

        for act in problem.actions:
            # Action prec
            for pre_prop in act.pre:
                pre_prefix = problem.is_negative(pre_prop)
                g.add_clause([-(act.index + problem.actions_current_index(t)), pre_prop + pre_prefix * problem.props_current_index(t)])

            # Action effect
            for p in act.add:
                g.add_clause([-(act.index + problem.actions_current_index(t)), (p + problem.props_current_index(t + 1))])

            for p in act.delt:
                g.add_clause([-(act.index + problem.actions_current_index(t)), -(p + problem.props_current_index(t + 1))])

            # Positive and Negative Frame axiom clauses
            for p in range(1, problem.prop_ind + 1):

                if p not in act.delt:
                    g.add_clause([-(act.index + problem.actions_current_index(t)), -(p + problem.props_current_index(t)),
                                  p + problem.props_current_index(t + 1)])

                if p not in act.add:
                    g.add_clause([-(act.index + problem.actions_current_index(t)), p + problem.props_current_index(t),
                                  -(p + problem.props_current_index(t + 1))])

            # Linearity
            for act_tag in problem.actions:
                if act_tag.index != act.index:
                    g.add_clause([-(act.index + problem.actions_current_index(t)), -(act_tag.index + problem.actions_current_index(t))])

            g.add_clause([act.index + problem.actions_current_index(t) for act in problem.actions])

        if g.solve(assumptions=[know_assumption, letter_assumption]):
            return True
    return False
