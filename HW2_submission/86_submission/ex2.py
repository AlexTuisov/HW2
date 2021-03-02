import numpy as np
from pysat.solvers import Glucose4
from itertools import product

ids = ['207829581', '322277179']
directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]


def get_directions(i, j):
    ret = []
    for direction in directions:
        x = i + direction[0]
        y = j + direction[1]
        ret.append((x, y))
    return ret


class Action:
    def __init__(self, pre, add, dele, index):
        self.index = index
        self.pre = pre
        self.add = add
        self.dele = dele


class BigProblem:
    def __init__(self, prob):
        self.medical_teams = prob["medics"]
        self.police_teams = prob["police"]
        self.observations = prob["observations"]
        self.game_length = len(prob["observations"])
        self.queries = prob["queries"]
        self.time = len(self.observations)
        self.rows = len(self.observations[0])
        self.cols = len(self.observations[0][0])
        self.letters = ['S', 'H', 'U']
        if self.medical_teams > 0:
            self.letters.append('I')
        if self.police_teams > 0:
            self.letters.append('Q')
        self.initial_state = {}
        self.prop_index = 0  # index for the propositions, in order to use PySAT
        self.action_index = 0  # index for the actions, in order to use PySAT
        self.proposition_to_number = {}
        self.locs = []
        self.init_locs()

        self.actions = []

        for time, obs in enumerate(self.observations):
            for i, row in enumerate(obs):
                for j, letter_in_matrix in enumerate(row):
                    self.initial_state[('known', time, (i, j), '_')] = True if letter_in_matrix != '?' else False
                    self.prop_index += 1
                    self.proposition_to_number[('known', time, (i, j), '_')] = self.prop_index

                    for let in self.letters:
                        if letter_in_matrix == let or letter_in_matrix == '?':
                            self.initial_state[('letter', time, (i, j),  let)] = True
                        else:
                            self.initial_state[('letter', time, (i, j), let)] = False
                        self.prop_index += 1
                        self.proposition_to_number[('letter', time, (i, j), let)] = self.prop_index
        self.do_funcs()


    def init_locs(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.locs.append((i, j))

    def definetly_True(self, t, i, j, x):
        return [self.proposition_to_number['letter', t, (i, j), x], self.proposition_to_number['known', t, (i, j), '_']]

    def in_board(self, x, y):
        return 0 <= x < self.rows and 0 <= y < self.cols

    def is_near(self, state, known, t, i, j, char):
        for x, y in get_directions(i, j):
            if self.in_board(x, y) and self.definetly_True(state, known, t, x, y, char):
                return True
        return False

    # Returns Keys of the neighbors
    def neighbors(self, t, i, j, char):
        neighbor_props = []
        for x, y in get_directions(i, j):
            if self.in_board(x, y):
                neighbor_props.append(('letter', t, (x, y), char))
        return neighbor_props

    def all_letters_but(self, t, i, j, char):
        lst = []
        for letter in self.letters:
            if letter != char:
                lst.append(self.proposition_to_number['letter', t, (i, j), letter])
        return lst

    def how_many_x_in_board(self, t, x):
        count_x = 0
        for i in range(self.rows):
            for j in range(self.cols):
                if self.observations[t][i][j] == x:
                    count_x += 1
        return count_x

    #(no Q)
    def after_infected(self, t, i, j):
        add = []
        dele = []
        for sick_time in range(t + 1, t + 3):
            if sick_time < self.time:
                add.extend(self.definetly_True(sick_time, i, j, 'S'))
                dele.extend((self.all_letters_but(sick_time, i, j, 'S')))
        if t + 3 < self.time:
            add.extend(self.definetly_True(t + 3, i, j, 'H'))
            dele.extend(self.all_letters_but(t + 3, i, j, 'H'))

        return add, dele

    def after_quarantine(self, t, i, j):
        add = []
        dele = []
        if t + 1 < self.time:
            add = self.definetly_True(t + 1, i, j, 'Q')
            dele = self.all_letters_but(t + 1, i, j, 'Q')
            if t + 2 < self.time:
                add.extend(self.definetly_True(t + 2, i, j, 'H'))
                dele.extend(self.all_letters_but(t + 2, i, j, 'H'))
        return add, dele

    def do_funcs(self):
        for t in range(self.time - 1):
            for i in range(self.rows):
                for j in range(self.cols):
                    self.sick_timer(t, i, j)
                    self.stay_healthy(t, i, j)
                    self.stayed_healthy(t, i, j)
                    self.who_infected_me(t, i, j)
                    self.infect(t, i, j)
                    self.i_am_u(t, i, j)
                    self.i_am_not_u(t, i, j)
                    self.do_i_know_you_kind_sir(t, i, j)
                    self.Q_timer(t, i, j)
                    self.no_I_Q_in_0(t, i, j)
                    self.steve_immune_per_round(t, i, j)
                    self.not_this_then_not_that(t, i, j)

    # If a node got sick in time t it is sick in the next 3 turns then healthy (if there is Q, then he is not healthy)
    def sick_timer(self, t, i, j):
        if any([time < self.time and self.observations[time][i][j] == '?' for time in range(t + 1, t + 4)]):
            pre = self.definetly_True(t, i, j, 'S')
            add = []
            if t > 0:
                pre.extend(self.definetly_True(t - 1, i, j, 'H'))
            if 'Q' not in self.letters:
                add, dele = self.after_infected(t, i, j)
            else:
                dele = [self.proposition_to_number['letter', time, (i, j), 'H'] for time in range(t + 1, t + 3) if time < self.time]
                if 'I' in self.letters:
                    dele.extend([self.proposition_to_number['letter', time, (i, j), 'I'] for time in range(t + 1, t + 4) if time < self.time])
            self.action_index += 1
            self.actions.append(Action(pre, add, dele, self.action_index))

    def Q_timer(self, t, i, j):
        if 'Q' in self.letters and t > 0 and any([time < self.time and self.observations[time][i][j] == '?' for time in range(t + 1, t + 3)]):
            pre = self.definetly_True(t - 1, i, j, 'S') + self.definetly_True(t, i, j, 'Q')
            add, dele = self.after_quarantine(t, i, j)

            self.action_index += 1
            self.actions.append(Action(pre, add, dele, self.action_index))


    # A healthy node will stay healthy if there are no sick nodes nearby.
    def stay_healthy(self, t, i, j):
        if (self.observations[t + 1][i][j] == '?') and t + 1 < self.time:
            pre = self.definetly_True(t, i, j, 'H')
            for neighbor in self.neighbors(t, i, j, 'S'):
                pre.append(-self.proposition_to_number[neighbor])

            if 'I' not in self.letters:
                add = self.definetly_True(t + 1, i, j, 'H')
                dele = self.all_letters_but(t + 1, i, j, 'H')

            else:
                lets = ['S', 'U']
                add = []
                if 'Q' in self.letters:
                    lets.append('Q')
                dele = [self.proposition_to_number['letter', t + 1, (i, j), let] for let in lets]

            self.action_index += 1
            self.actions.append(Action(pre, add, dele, self.action_index))


    def stayed_healthy(self, t, i, j):
        if t + 1 < self.time:
            if any([(self.in_board(x, y) and self.observations[t][x][y]) == '?' for x, y in get_directions(i, j)]):
                pre = self.definetly_True(t, i, j, 'H')
                pre.extend(self.definetly_True(t + 1, i, j, 'H'))

                add = []
                dele = [self.proposition_to_number[n] for n in self.neighbors(t, i, j, 'S')]

                self.action_index += 1
                act = Action(pre, add, dele, self.action_index)
                self.actions.append(act)


    # if a Healthy node got sick, and only one of his neighbors can be sick, it must be sick.
    def who_infected_me(self, t, i, j):
        for x, y in get_directions(i, j):
            if self.in_board(x, y) and any([time < self.time and self.observations[time][x][y] == '?' for time in range(t, t + 4)]):
                pre = self.definetly_True(t, i, j, 'H')
                pre.extend(self.definetly_True(t + 1, i, j, 'S'))
                for neighbor in self.neighbors(t, i, j, 'S'):
                    if neighbor[2] != (x, y):
                        pre.append(- self.proposition_to_number[neighbor])
                pre.append(- self.proposition_to_number['known', t, (x, y), '_'])

                add = self.definetly_True(t, x, y, 'S')
                dele = self.all_letters_but(t, x, y, 'S')

                if 'Q' not in self.letters:
                    a, d = self.after_infected(t, i, j)
                    add.extend(a)
                    dele.extend(d)

                self.action_index += 1
                self.actions.append(Action(pre, add, dele, self.action_index))

    # if sick is near H, H will turn to S
    def infect(self, t, i, j):
        pre = self.definetly_True(t, i, j, 'S')

        for x, y in get_directions(i, j):
            if self.in_board(x, y) and any([time < self.time and self.observations[time][x][y] == '?' for time in range(t, t + 5)]):
                pre.extend(self.definetly_True(t, x, y, 'H'))
                add = self.definetly_True(t + 1, x, y, 'S')
                dele = self.all_letters_but(t + 1, x, y, 'S')
                if 'Q' not in self.letters:
                    a, d = self.after_infected(t + 1, x, y)
                    add.extend(a)
                    dele.extend(d)

                self.action_index += 1
                self.actions.append(Action(pre, add, dele, self.action_index))

    def i_am_u(self, t, i, j):
        if any([self.observations[time][i][j] == '?' for time in range(self.time)]):
            pre = self.definetly_True(t, i, j, 'U')
            add = []
            dele = []
            for t_i in range(self.time):
                add.extend(self.definetly_True(t_i, i, j, 'U'))
                dele.extend(self.all_letters_but(t_i, i, j, 'U'))
            self.action_index += 1
            act = Action(pre, add, dele, self.action_index)
            self.actions.append(act)

    def i_am_not_u(self, t, i, j):
        if any([self.observations[time][i][j] == '?' for time in range(self.time)]):
            for let in self.letters:
                if let != 'U':
                    pre = self.definetly_True(t, i, j, let)
                    add = []
                    dele = [self.proposition_to_number['letter', t_i, (i, j), 'U'] for t_i in range(self.time)]
                    self.action_index += 1
                    act = Action(pre, add, dele, self.action_index)
                    self.actions.append(act)

    def do_i_know_you_kind_sir(self, t, i, j):
        if self.observations[t][i][j] == '?':
            for letter in self.letters:
                pre = [-self.proposition_to_number['known', t, (i, j), '_']]
                for let in self.letters:
                    if let != letter:
                        pre.append(-self.proposition_to_number[('letter', t, (i, j), let)])
                add = self.definetly_True(t, i, j, letter)
                dele = []
                self.action_index += 1
                self.actions.append(Action(pre, add, dele, self.action_index))


    #false on all Q in time 0
    def no_I_Q_in_0(self, t, i, j):
        if self.observations[t][i][j] == '?' and t == 0:
            pre = [-self.proposition_to_number['known', t, (i, j), '_']]
            add = []
            dele = []
            if 'Q' in self.letters:
                dele.append(self.proposition_to_number['letter', t, (i, j), 'Q'])
            if 'I' in self.letters:
                dele.append(self.proposition_to_number['letter', t, (i, j), 'I'])
            self.action_index += 1
            self.actions.append(Action(pre, add, dele, self.action_index))



    def steve_immune_per_round(self, t, i, j):

        if t + 1 < self.time and 'I' in self.letters and self.observations[t + 1][i][j] == '?':
            new_immune = self.how_many_x_in_board(t + 1, 'I') - self.how_many_x_in_board(t, 'I')
            missing_immune = self.medical_teams - new_immune

            # If all actions happened, nobody else is I
            if missing_immune == 0:  # TODO cant solve if there were not enough H in last turn
                pre = [-self.proposition_to_number['known', t + 1, (i, j), '_']]
                add = []
                dele = [self.proposition_to_number['letter', t + 1, (i, j), 'I']]

                self.action_index += 1
                self.actions.append(Action(pre, add, dele, self.action_index))
            # If not all actions happened
            elif missing_immune > 0:
                for comb in product(*[self.locs] * missing_immune):
                    pre = []
                    for loc in self.locs:
                        if loc in comb:
                            pre.extend(self.definetly_True(t, loc[0], loc[1], 'H'))
                        else:
                            pre.append([-self.proposition_to_number['letter', t, (loc[0], loc[1]), 'H']])

                    add = []
                    dele = []
                    for node in comb:
                        add.extend(self.definetly_True(t + 1, node[0], node[1], 'I'))
                        dele.extend(self.all_letters_but(t + 1, node[0], node[1], 'I'))

                    self.action_index += 1
                    self.actions.append(Action(pre, add, dele, self.action_index))


    def not_this_then_not_that(self, t, i, j):
        if t + 1 < self.time:
            if self.observations[t + 1][i][j] == '?':
                # I wasn't healthy so I can't
                if 'I' in self.letters:
                    pre = [-self.proposition_to_number['known', t + 1, (i, j), '_'],
                           -self.proposition_to_number['letter', t, (i, j), 'H']]
                    add = []
                    dele = [self.proposition_to_number['letter', t + 1, (i, j), 'I']]
                    self.action_index += 1
                    act = Action(pre, add, dele, self.action_index)
                    self.actions.append(act)
                    # wasn't sick, can't be in quarantine
                if 'Q' in self.letters:
                    pre = [-self.proposition_to_number['known', t + 1, (i, j), '_'],
                           -self.proposition_to_number['letter', t, (i, j), 'S']]
                    add = []
                    dele = [self.proposition_to_number['letter', t + 1, (i, j), 'Q']]
                    self.action_index += 1
                    act = Action(pre, add, dele, self.action_index)
                    self.actions.append(act)



    def solve(self):
        answers = {}
        aba_halach = {}
        for Query in self.queries:
            #
            # for letter in self.letters:
            #     aba_halach[letter] = single_problem(self, letter, Query)

            bool = False
            for letter in self.letters:
                if letter != Query[2]:
                    bool = bool or single_problem(self, letter, Query)

            if single_problem(self, Query[2], Query):
                if bool:
                    answers[Query] = '?'
                else:
                    answers[Query] = 'T'
            else:
                answers[Query] = 'F'
        return answers


def Santa_clauses(problem, g):
    if december is 25:
        while kids is exists:
            if not matanot.empty:
                matanot.give_to_yeled
            else:
                cry_without_pants



def fix_sign(p, prop_at_time):
    if p >= 0:
        return p + prop_at_time
    else:
        return p - prop_at_time


def return_interfeering(actions):
    # Paralel
    interfering = []
    for act in actions:
        for act_2 in actions:
            if act != act_2:
                interfere = False
                for d in act.dele:
                    if d in (act_2.pre + act_2.add):
                        interfere = True
                for d in act_2.dele:
                    if d in (act.pre + act.add):
                        interfere = True
                if interfere:
                    interfering.append((act.index, act_2.index))
    return interfering

def single_problem(problem, letter, query):

    round = problem.prop_index + problem.action_index
    actions_at_time = lambda time: time * round + problem.prop_index
    prop_at_time = lambda time: time * round

    #interfering = return_interfeering(problem.actions)
    g = Glucose4()
    # Initial state clauses
    for key in problem.initial_state.keys():
        sign = 1 if problem.initial_state[key] else -1
        g.add_clause([sign * problem.proposition_to_number[key]])

    for t in range(30):
        #Linear

        # Goal State
        know_assumption = prop_at_time(t) + problem.proposition_to_number['known', query[1], query[0], '_']
        letter_assumption = prop_at_time(t) + problem.proposition_to_number['letter', query[1], query[0], letter]

        for act in problem.actions:
            # Action precondition clauses
            for p in act.pre:
                g.add_clause([-(act.index + actions_at_time(t)), fix_sign(p, prop_at_time(t))])

            # Action effect clauses
            for p in act.add:
                g.add_clause([-(act.index + actions_at_time(t)), (p + prop_at_time(t+1))])
            for p in act.dele:
                g.add_clause([-(act.index + actions_at_time(t)), -(p + prop_at_time(t+1))])

            for p in range(1, problem.prop_index + 1):
                # Positive Frame axiom clauses
                if p not in act.dele:
                    g.add_clause([-(act.index + actions_at_time(t)), -(p + prop_at_time(t)), p + prop_at_time(t + 1)])

                # Negative Frame axiom clauses
                if p not in act.add:
                    g.add_clause([-(act.index + actions_at_time(t)), p + prop_at_time(t), -(p + prop_at_time(t + 1))])

            # Linearity constraints clauses
            for act_tag in problem.actions:
                if act_tag.index != act.index:
                    g.add_clause([-(act.index + actions_at_time(t)), -(act_tag.index + actions_at_time(t))])

            g.add_clause([act.index + actions_at_time(t) for act in problem.actions])

        if g.solve(assumptions=[know_assumption, letter_assumption]):
            return True
    return False


def solve_problem(prob):
    problem = BigProblem(prob)
    return problem.solve()

