from sympy.logic import to_cnf
import numpy as np
from pysat.formula import IDPool
from pysat.solvers import Glucose3


ids = ['315227686', '035904275']
vpool = IDPool()
var = lambda i: vpool.id('var{0}'.format(i))
dirs = {'right': (0, 1), 'left': (0, -1), 'up': (1, 0), 'down': (-1, 0)}
is_legal = lambda i, j, n, m: (i < n) and (i >= 0) and (j < m) and (j >= 0)  # check if the given location is legal


def symb(letter, i, j, num_round):
    if letter[0] == 'F' or letter[0] == 'G':
        # will be 2 letters with index
        return f'{letter}' + '0' * 8 + str(num_round)
    num_round += 4  # TODO change to 4
    i = str(int(i / 10)) + str(i % 10)
    j = str(int(j / 10)) + str(j % 10)
    return f'{letter}{(i, j)}00' if letter == 'U' else f'{letter}{(i, j)}{str(int(num_round / 10)) + str(num_round % 10)}'


def pysat_to_cnf(formula):
    # Assume word is exactly 8 letters
    letters = ['S', 'Q', 'H', 'U', 'I', '?', 'P', 'M']
    bin_to_symb = lambda x: (str(bin(x))[2:]).replace('0', 'A').replace('1', 'B')
    set_of_words = set()
    for i in range(len(formula)):
        if formula[i] in letters:
            if formula[i] == 'P' or formula[i] == 'M':
                set_of_words.add(formula[i:i + 14])
            else:
                set_of_words.add(formula[i:i + 13])
    words = list(set_of_words)
    doc = {words[i]: bin_to_symb(i + 1) for i in range(len(words))}
    for key in doc:
        formula = formula.replace(key, doc[key])
    cnf_formula = to_cnf(formula, force=True)
    # formula = str(simplify_logic(cnf_formula, form='cnf', deep=True, force=True))
    formula = str(cnf_formula)
    for i in range(len(words) - 1, -1, -1):
        formula = formula.replace(bin_to_symb(i + 1), words[i])
    return formula


def string_to_nums(clause):
    splitted_clauses = clause[1:-1].split(' | ') if clause[0] == '(' else clause.split(' | ')
    return [-var(sym[1:]) if sym[0] == '~' else var(sym) for sym in splitted_clauses if sym != '']


class MedicalProblem:

    def iter_over_map(self):
        r, n, m = self.observations.shape
        for num_round in range(r):
            locs = np.where(self.observations[num_round] != 'X')
            for location in zip(locs[0], locs[1]):
                yield num_round, location

    def __init__(self, input):
        pol, med, queries = input['police'], input['medics'], input['queries']
        self.pol = pol
        self.med = med
        self.queries = queries
        self.observations = np.array(input['observations'])
        self.change_map()
        self.KB = KB()

        self.teams('P')
        self.teams('M')
        all_functions = [self.healthy_people, self.obs_facts, self.quarantined_people,
                         self.immune_people, self.teams_actions, self.sick_people]

        for func in all_functions:
            func()

    def change_map(self):
        r, n, m = self.observations.shape
        for num_round in range(r):
            locs = np.where(self.observations[num_round] == 'U')
            for i, j in zip(locs[0], locs[1]):
                self.observations[:, i, j] = 'U'

            locs = np.where(self.observations[num_round] == 'I')
            for i, j in zip(locs[0], locs[1]):
                self.observations[num_round:, i, j] = 'I'

    def obs_facts(self):
        r, n, m = self.observations.shape
        letters = ['S', 'Q', 'H', 'U', 'I']
        nall = lambda letter, i, j, nr: ' & '.join([f'~{symb(item, i, j, nr)}' for item in letters if item != letter])

        def given_letters():
            for num_round in range(r):
                for i in range(n):
                    for j in range(m):
                        self.KB.tell(symb(self.observations[num_round, i, j], i, j, num_round), False)

        def unique():
            for num_round in range(r):
                for i in range(n):
                    for j in range(m):
                        if self.observations[num_round, i, j] != "?":
                            let = self.observations[num_round, i, j]
                            # uunique_sentence = f'(({symb(let, i, j, num_round)}) >> ({nall(let, i, j, num_round)}))'
                            # self.KB.tell(uunique_sentence)
                            uunique_sentence = " & ".join(
                                [f'(~{symb(let, i, j, num_round)} | ~{symb(letter, i, j, num_round)})' for letter in
                                 letters if letter != let])
                            self.KB.tell(uunique_sentence, False)
                        else:
                            self.KB.tell(
                                f'(~{symb("Q", i, j, num_round)} | ~{symb("U", i, j, num_round)}) & (~{symb("Q", i, j, num_round)} | ~{symb("I", i, j, num_round)}) & (~{symb("Q", i, j, num_round)} | ~{symb("H", i, j, num_round)}) & (~{symb("Q", i, j, num_round)} | ~{symb("S", i, j, num_round)}) & (~{symb("U", i, j, num_round)} | ~{symb("I", i, j, num_round)}) & (~{symb("U", i, j, num_round)} | ~{symb("H", i, j, num_round)}) & (~{symb("U", i, j, num_round)} | ~{symb("S", i, j, num_round)}) & (~{symb("I", i, j, num_round)} | ~{symb("H", i, j, num_round)}) & (~{symb("I", i, j, num_round)} | ~{symb("S", i, j, num_round)}) & (~{symb("H", i, j, num_round)} | ~{symb("S", i, j, num_round)})',
                                False)
                            # for let in letters:
                            #     uunique_sentence = f'(({symb(let, i, j, num_round)}) >> ({nall(let, i, j, num_round)}))'
                            #     self.KB.tell(uunique_sentence)

        def unknown():
            r, n, m = self.observations.shape
            for num_round in range(r):
                locs = np.where(self.observations[num_round] == '?')
                for location in zip(locs[0], locs[1]):
                    i, j = location
                    if self.observations[num_round, i, j] != '?':
                        continue
                    if num_round == 0:
                        # sen = f'(({symb("?", i, j, num_round)}) >> ({symb("H", i, j, num_round)} | {symb("S", i, j, num_round)} | {symb("U", i, j, num_round)}))'
                        self.KB.tell(
                            f'{symb("H", i, j, num_round)} | {symb("U", i, j, num_round)} | {symb("S", i, j, num_round)} | ~{symb("?", i, j, num_round)}',
                            False)
                    else:
                        # sen = f'(({symb("?", i, j, num_round)}) >> ({symb("H", i, j, num_round)} | {symb("S", i, j, num_round)} | {symb("U", i, j, num_round)} | {symb("I", i, j, num_round)} | {symb("Q", i, j, num_round)}))'
                        self.KB.tell(
                            f'{symb("I", i, j, num_round)} | {symb("S", i, j, num_round)} | {symb("H", i, j, num_round)} | {symb("U", i, j, num_round)} | {symb("Q", i, j, num_round)} | ~{symb("?", i, j, num_round)}',
                            False)

        given_letters()
        unique()
        unknown()

    def sick_people(self):
        r, n, m = self.observations.shape
        for num_round in range(r):
            # locs = np.where(self.observations[num_round] != 'X')
            locs = np.where((self.observations[num_round] == 'S') | (self.observations[num_round] == '?'))
            for location in zip(locs[0], locs[1]):
                i, j = location
                # disease spread
                all_police_round_t = "(" + " | ".join(
                    [f'{symb("P" + str(pp), *location, num_round)}' for pp in range(self.pol)]) + ")"
                for direction in dirs:
                    neighbor_location = tuple(np.array(location) + np.array(dirs[direction]))
                    x, y = neighbor_location
                    if is_legal(*neighbor_location, n, m):
                        if num_round + 1 < r:
                            if self.observations[num_round + 1, x, y] == 'S':
                                continue
                            elif self.observations[num_round + 1, x, y] == '?':
                                if self.pol > 0:
                                    # spread_disease = f'({symb("S", *location, num_round)} & ~{all_police_round_t} & {symb("H", *neighbor_location, num_round)} & ~{symb("I", *neighbor_location, num_round + 1)}) >> ({symb("S", *neighbor_location, num_round + 1)})'
                                    spread_disease = f'{symb("I", *neighbor_location, num_round + 1)} | {symb("S", *neighbor_location, num_round + 1)} | {all_police_round_t} | ~{symb("H", *neighbor_location, num_round)} | ~{symb("S", *location, num_round)}'

                                else:
                                    # spread_disease = f'({symb("S", *location, num_round)} & {symb("H", *neighbor_location, num_round)} & ~{symb("I", *neighbor_location, num_round + 1)}) >> ({symb("S", *neighbor_location, num_round + 1)})'
                                    spread_disease = f'{symb("I", *neighbor_location, num_round + 1)} | {symb("S", *neighbor_location, num_round + 1)} | ~{symb("S", *location, num_round)} | ~{symb("I", *neighbor_location, num_round)}'
                                self.KB.tell(spread_disease, False)
                            else:
                                if self.pol > 0:
                                    spread_disease = f'~({symb("S", *location, num_round)} & ~{all_police_round_t} & {symb("H", *neighbor_location, num_round)} & ~{symb("I", *neighbor_location, num_round + 1)})'
                                else:
                                    spread_disease = f'~({symb("S", *location, num_round)} & {symb("H", *neighbor_location, num_round)} & ~{symb("I", *neighbor_location, num_round + 1)})'
                                self.KB.tell(spread_disease)

                # sick now, was healthy -> one of my neighbors was sick who was not policed
                all_police_round_t_1 = lambda location_pol: "(" + " | ".join(
                    [f'{symb("P" + str(pp), *location_pol, num_round - 1)}' for pp in range(self.pol)]) + ")"
                locs = lambda loc, direction: tuple(np.array(loc) + np.array(dirs[direction]))
                police_dirs = {direction: all_police_round_t_1(locs((i, j), direction)) for direction in dirs}
                if self.pol > 0:
                    contagious_neighbor = "(" + " | ".join(
                        [f'({symb("S", *locs((i, j), direction), num_round - 1)} & ~{police_dirs[direction]})' for
                         direction in dirs if is_legal(*locs((i, j), direction), n, m) and self.pol > 0]) + ")"
                    # sick who is policed will be Q for 2 turns and then H
                    # sick_policed = f'(({symb("S", i, j, num_round)} & {all_police_round_t}) >> ({symb("Q", i, j, num_round + 1)} & {symb("Q", i, j, num_round + 2)} & {symb("H", i, j, num_round + 3)}))'
                    # self.KB.tell(sick_policed)
                    sick_policed = f'({symb("H", i, j, num_round + 3)} | ~{all_police_round_t} | ~{symb("S", i, j, num_round)}) & ({symb("Q", i, j, num_round + 1)} | ~{all_police_round_t} | ~{symb("S", i, j, num_round)}) & ({symb("Q", i, j, num_round + 2)} | ~{all_police_round_t} | ~{symb("S", i, j, num_round)})'
                    self.KB.tell(sick_policed, False)
                    #  sick who is not policed (or there is no police) will be S or H
                    # sick_will_be_S_or_H = f'(({symb("S", i, j, num_round)} & ~{all_police_round_t}) >> ({symb("S", i, j, num_round + 1)} | {symb("H", i, j, num_round + 1)}))'
                    sick_will_be_S_or_H = f'{symb("S", i, j, num_round + 1)} | {symb("H", i, j, num_round + 1)} | {all_police_round_t} | ~{symb("S", i, j, num_round)}'
                    S_was_H = f'(({symb("S", *location, num_round)} & {symb("H", *location, num_round - 1)}) >> {contagious_neighbor})'
                    self.KB.tell(S_was_H)
                else:
                    contagious_neighbor = "(" + " | ".join(
                        [f'({symb("S", *locs((i, j), direction), num_round - 1)})' for direction in dirs if
                         is_legal(*locs((i, j), direction), n, m) and self.pol == 0]) + ")"
                    # sick_will_be_S_or_H = f'(({symb("S", i, j, num_round)}) >> ({symb("S", i, j, num_round + 1)} | {symb("H", i, j, num_round + 1)}))'
                    sick_will_be_S_or_H = f'{symb("S", i, j, num_round + 1)} | {symb("H", i, j, num_round + 1)} | ~{symb("S", i, j, num_round)}'
                    # S_was_H = f'(({symb("S", *location, num_round)} & {symb("H", *location, num_round - 1)}) >> {contagious_neighbor})'
                    S_was_H = f'{contagious_neighbor[1:-1]} | ~{symb("H", *location, num_round - 1)} | ~{symb("S", *location, num_round)}'
                    self.KB.tell(S_was_H, False)
                self.KB.tell(sick_will_be_S_or_H, False)

                if num_round <= 2:
                    if self.pol > 0:
                        # stay_s_less_3_rounds = f'(({symb("S", i, j, num_round)} & ~{all_police_round_t}) >> ({symb("S", i, j, num_round + 1)}))'
                        stay_s_less_3_rounds = f'{symb("S", i, j, num_round + 1)} | {all_police_round_t} | ~{symb("S", i, j, num_round)}'
                    else:
                        # stay_s_less_3_rounds = f'(({symb("S", i, j, num_round - 1)}) >> ({symb("S", i, j, num_round)}))'
                        stay_s_less_3_rounds = f'{symb("S", i, j, num_round)} | ~{symb("S", i, j, num_round - 1)}'
                    self.KB.tell(stay_s_less_3_rounds, False)
                else:
                    # need to check if 3 rounds before was sick
                    all_police_round_t_1 = " | ".join(
                        [f'{symb("P" + str(pp), *location, num_round - 1)}' for pp in range(self.pol)])
                    if self.pol > 0:
                        # was_sick_3_rounds_now_H = f'((({symb("S", i, j, num_round - 3)} & {symb("S", i, j, num_round - 2)} & {symb("S", i, j, num_round - 1)}) & ~{all_police_round_t_1}) >> ({symb("H", i, j, num_round)}))'
                        was_sick_3_rounds_now_H = f'{symb("H", i, j, num_round)} | {all_police_round_t_1} | ~{symb("S", i, j, num_round - 3)} | ~{symb("S", i, j, num_round - 1)} | ~{symb("S", i, j, num_round - 2)}'
                        # wasnt_sick_3_rounds_now_S = f'(((~{symb("S", i, j, num_round - 3)} | ~{symb("S", i, j, num_round - 2)}) & {symb("S", i, j, num_round - 1)} & ~{all_police_round_t_1}) >> ({symb("S", i, j, num_round)}))'
                        wasnt_sick_3_rounds_now_S = f'({symb("S", i, j, num_round - 2)} | {symb("S", i, j, num_round)} | {all_police_round_t_1} | ~{symb("S", i, j, num_round - 1)}) & ({symb("S", i, j, num_round)} | {all_police_round_t_1} | {symb("S", i, j, num_round - 3)} | ~{symb("S", i, j, num_round - 1)})'

                    else:
                        # was_sick_3_rounds_now_H = f'(({symb("S", i, j, num_round - 3)} & {symb("S", i, j, num_round - 2)} & {symb("S", i, j, num_round - 1)}) >> ({symb("H", i, j, num_round)}))'
                        was_sick_3_rounds_now_H = f'{symb("H", i, j, num_round)} | ~{symb("S", i, j, num_round - 1)} | ~{symb("S", i, j, num_round - 2)} | ~{symb("S", i, j, num_round - 3)}'
                        # wasnt_sick_3_rounds_now_S = f'(((~{symb("S", i, j, num_round - 3)} | ~{symb("S", i, j, num_round - 2)}) & {symb("S", i, j, num_round - 1)}) >> ({symb("S", i, j, num_round)}))'
                        wasnt_sick_3_rounds_now_S = f'({symb("S", i, j, num_round - 2)} | {symb("S", i, j, num_round)} | ~{symb("S", i, j, num_round - 1)}) & ({symb("S", i, j, num_round - 3)} | {symb("S", i, j, num_round)} | ~{symb("S", i, j, num_round - 1)})'

                    self.KB.tell(was_sick_3_rounds_now_H, False)
                    self.KB.tell(wasnt_sick_3_rounds_now_S, False)

    def healthy_people(self):
        r, n, m = self.observations.shape
        for num_round in range(r):
            # locs = np.where(self.observations[num_round] != 'X')
            locs = np.where((self.observations[num_round] == "H") | (self.observations[num_round] == '?'))
            for location in zip(locs[0], locs[1]):
                i, j = location
                # H was one of this thing: S for 3 rounds, Q for 2 rounds or H round before
                # one_option = f'({symb("S", *location, num_round - 1)} & {symb("S", *location, num_round - 2)} & {symb("S", *location, num_round - 3)})'
                # second_option = f'({symb("H", *location, num_round - 1)})'
                if self.pol > 0:
                    apa = "(" + " | ".join(
                        [f'{symb("P" + str(pp), *location, num_round - 3)}' for pp in range(self.pol)]) + ")"
                    # third_option = f'({symb("Q", *location, num_round - 1)} & {symb("Q", *location, num_round - 2)} & {symb("S", *location, num_round - 3)} & {apa})'
                    # all_ways = f'(({symb("H", *location, num_round)}) >> ({one_option} | {second_option} | {third_option}))'
                    all_ways = f'({symb("H", *location, num_round - 1)} | {symb("S", *location, num_round - 3)} | ~{symb("H", *location, num_round)}) & ({symb("H", *location, num_round - 1)} | {symb("S", *location, num_round - 3)} | {symb("Q", *location, num_round - 2)} | ~{symb("H", *location, num_round)}) & ({symb("H", *location, num_round - 1)} | {symb("S", *location, num_round - 3)} | {symb("Q", *location, num_round - 1)} | ~{symb("H", *location, num_round)}) & ({symb("H", *location, num_round - 1)} | {symb("S", *location, num_round - 3)} | {symb("S", *location, num_round - 2)} | ~{symb("H", *location, num_round)}) & ({symb("H", *location, num_round - 1)} | {symb("S", *location, num_round - 3)} | {apa} | ~{symb("H", *location, num_round)}) & ({symb("H", *location, num_round - 1)} | {symb("S", *location, num_round - 3)} | {symb("S", *location, num_round - 1)} | ~{symb("H", *location, num_round)}) & ({symb("H", *location, num_round - 1)} | {symb("Q", *location, num_round - 2)} | {symb("S", *location, num_round - 2)} | ~{symb("H", *location, num_round)}) & ({symb("H", *location, num_round - 1)} | {symb("Q", *location, num_round - 2)} | {symb("S", *location, num_round - 1)} | ~{symb("H", *location, num_round)}) & ({symb("H", *location, num_round - 1)} | {symb("Q", *location, num_round - 1)} | {symb("S", *location, num_round - 2)} | ~{symb("H", *location, num_round)}) & ({symb("H", *location, num_round - 1)} | {symb("Q", *location, num_round - 1)} | {symb("S", *location, num_round - 1)} | ~{symb("H", *location, num_round)}) & ({symb("H", *location, num_round - 1)} | {symb("S", *location, num_round - 2)} | {apa} | ~{symb("H", *location, num_round)}) & ({symb("H", *location, num_round - 1)} | {apa} | {symb("S", *location, num_round - 1)} | ~{symb("H", *location, num_round)})'
                else:
                    # all_ways = f'(({symb("H", *location, num_round)}) >> ({one_option} | {second_option}))'
                    all_ways = f'({symb("S", *location, num_round - 1)} | {symb("H", *location, num_round - 1)} | ~{symb("H", *location, num_round)}) & ({symb("S", *location, num_round - 3)} | {symb("H", *location, num_round - 1)} | ~{symb("H", *location, num_round)}) & ({symb("S", *location, num_round - 2)} | {symb("H", *location, num_round - 1)} | ~{symb("H", *location, num_round)})'

                self.KB.tell(all_ways, False)

                all_police_round_t = lambda location_pol: "(" + " | ".join(
                    [f'{symb("P" + str(pp), *location_pol, num_round)}' for pp in range(self.pol)]) + ")"
                locs = lambda loc, direction: tuple(np.array(loc) + np.array(dirs[direction]))
                police_dirs = {direction: all_police_round_t(locs((i, j), direction)) for direction in dirs}
                if self.pol > 0:
                    contagious_neighbor = "(" + " | ".join(
                        [f'({symb("S", *locs((i, j), direction), num_round)} & ~{police_dirs[direction]})' for direction
                         in dirs if is_legal(*locs((i, j), direction), n, m) and self.pol > 0]) + ")"
                else:
                    contagious_neighbor = "(" + " | ".join(
                        [f'({symb("S", *locs((i, j), direction), num_round)})' for direction in dirs if
                         is_legal(*locs((i, j), direction), n, m) and self.pol == 0]) + ")"

                # if someone will be S next turn and now H then he has neighbor who is not policed
                # self.KB.tell(f'(({symb("H", *location, num_round)} & {symb("S", *location, num_round + 1)}) >> {contagious_neighbor})')
                # if someone is H for 2 turn then there was no sick who was not policed around
                if num_round + 1 < r:
                    chance_for_infection = False
                    for direction in dirs:
                        x, y = locs((i, j), direction)
                        if is_legal(x, y, n, m):
                            if self.observations[num_round, x, y] == '?' or self.observations[num_round, x, y] == 'S':
                                chance_for_infection = True
                    if chance_for_infection and (self.observations[num_round, i, j] == 'H' or self.observations[
                        num_round, i, j] == '?') and (
                            self.observations[num_round + 1, i, j] == 'H' or self.observations[
                        num_round + 1, i, j] == '?'):
                        self.KB.tell(
                            f'(({symb("H", *location, num_round)} & {symb("H", *location, num_round + 1)}) >> ~{contagious_neighbor})')

                    all_medics_round_t = "(" + " | ".join(
                        [f'{symb("M" + str(mm), *location, num_round)}' for mm in range(self.med)]) + ")"
                    if self.observations[num_round + 1, i, j] == 'H':
                        # sentecne is already true
                        continue
                    if self.observations[num_round, i, j] == '?' and self.observations[num_round + 1, i, j] == '?':
                        # H who has no neighhbor who is not policed, was not vaccinated then he will be H
                        if self.med > 0:
                            H_will_stay_H = f'(({symb("H", *location, num_round)} & ~({contagious_neighbor}) & ~{all_medics_round_t}) >> ({symb("H", *location, num_round + 1)}))'
                        else:
                            H_will_stay_H = f'(({symb("H", *location, num_round)} & ~({contagious_neighbor})) >> ({symb("H", *location, num_round + 1)}))'
                    elif self.observations[num_round, i, j] == 'H' and self.observations[num_round + 1, i, j] == '?':
                        if self.med > 0:
                            H_will_stay_H = f'((~({contagious_neighbor}) & ~{all_medics_round_t}) >> ({symb("H", *location, num_round + 1)}))'
                        else:
                            H_will_stay_H = f'((~({contagious_neighbor})) >> ({symb("H", *location, num_round + 1)}))'
                    else:
                        # next round it can't be H then we know it was vaccinated or infected
                        if self.med > 0:
                            # ~(~A & ~ B)
                            H_will_stay_H = f'~(({symb("H", *location, num_round)} & ~({contagious_neighbor}) & ~{all_medics_round_t}))'
                        else:
                            H_will_stay_H = f'~(({symb("H", *location, num_round)} & ~({contagious_neighbor})))'
                            # H_will_stay_H = f'({symb("H", *location, num_round)} | ~{symb("H", *location, num_round)})'
                        pass
                    self.KB.tell(H_will_stay_H)

    def quarantined_people(self):
        r, n, m = self.observations.shape
        for num_round in range(r):
            # locs = np.where(self.observations[num_round] != 'X')
            locs = np.where((self.observations[num_round] == "Q") | (self.observations[num_round] == '?'))
            for location in zip(locs[0], locs[1]):
                all_police_round_t_1 = "(" + " | ".join(
                    [f'{symb("P" + str(pp), *location, num_round - 1)}' for pp in range(self.pol)]) + ")"
                if self.pol > 0:
                    # option1 = f'({symb("Q", *location, num_round)} >> ({symb("S", *location, num_round - 1)} & {all_police_round_t_1} | ({symb("Q", *location, num_round - 1)})))'
                    option1 = f'({all_police_round_t_1} | {symb("Q", *location, num_round - 1)} | ~{symb("Q", *location, num_round)}) & ({symb("Q", *location, num_round - 1)} | {symb("S", *location, num_round - 1)} | ~{symb("Q", *location, num_round)})'
                    # option2 = f'({symb("Q", *location, num_round)} << ({symb("S", *location, num_round - 1)} & {all_police_round_t_1} | ({symb("Q", *location, num_round - 1)} & ~{symb("Q", *location, num_round - 2)})))'
                    option2 = f'({symb("Q", *location, num_round)} | {symb("Q", *location, num_round - 2)} | ~{symb("Q", *location, num_round - 1)}) & ({symb("Q", *location, num_round)} | ~{symb("S", *location, num_round - 1)} | ~{all_police_round_t_1})'
                    self.KB.tell(option1, False)
                    self.KB.tell(option2, False)
                    # will_be_H = f'(({symb("Q", *location, num_round)} & {symb("Q", *location, num_round - 1)}) >> ({symb("H", *location, num_round + 1)}))'
                    will_be_H = f'{symb("H", *location, num_round + 1)} | ~{symb("Q", *location, num_round - 1)} | ~{symb("Q", *location, num_round)}'
                    self.KB.tell(will_be_H, False)

    def immune_people(self):
        r, n, m = self.observations.shape
        for num_round in range(r):
            # locs = np.where(self.observations[num_round] != 'X')
            locs = np.where((self.observations[num_round] == "I") | (self.observations[num_round] == "H") | (
                        self.observations[num_round] == '?'))
            for location in zip(locs[0], locs[1]):
                all_medics_round_t_1 = "(" + " | ".join(
                    [f'{symb("M" + str(mm), *location, num_round - 1)}' for mm in range(self.med)]) + ")"
                all_medics_round_t = "(" + " | ".join(
                    [f'{symb("M" + str(mm), *location, num_round)}' for mm in range(self.med)]) + ")"
                if self.med > 0:
                    # opt1 = f'({symb("I", *location, num_round)} >> ({symb("I", *location, num_round - 1)} | ({symb("H", *location, num_round - 1)} & {all_medics_round_t_1})))'
                    opt1 = f'({symb("H", *location, num_round - 1)} | {symb("I", *location, num_round - 1)} | ~{symb("I", *location, num_round)}) & ({all_medics_round_t_1[1:-1]} | {symb("I", *location, num_round - 1)} | ~{symb("I", *location, num_round)})'
                    opt2 = f'({symb("I", *location, num_round)} << ({symb("I", *location, num_round - 1)} | ({symb("H", *location, num_round - 1)} & {all_medics_round_t_1[1:-1]})))'
                    opt2 = f'({symb("I", *location, num_round)} | ~{symb("I", *location, num_round - 1)}) & ({symb("I", *location, num_round)} | ~{symb("H", *location, num_round - 1)} | ~{all_medics_round_t_1})'

                    self.KB.tell(opt1, False)
                    self.KB.tell(opt2, False)
                    # if medic was activated then it worked on H and next turn it will be I and vice versa
                    # opt1 = f'(({all_medics_round_t}) >> ({symb("H", *location, num_round)} & {symb("I", *location, num_round + 1)}))'
                    opt1 = f'({symb("H", *location, num_round)} | ~{all_medics_round_t}) & ({symb("I", *location, num_round + 1)} | ~{all_medics_round_t})'
                    # opt2 = f'(({all_medics_round_t}) << ({symb("H", *location, num_round)} & {symb("I", *location, num_round + 1)}))'
                    opt2 = f'{all_medics_round_t} | ~{symb("H", *location, num_round)} | ~{symb("I", *location, num_round + 1)}'

                    self.KB.tell(opt1, False)
                    self.KB.tell(opt2, False)
                else:
                    # self.KB.tell(f'{all_medics_round_t}', False)
                    self.KB.tell(f'~{symb("I", *location, num_round)}', False)

        pass

    def teams_actions(self):
        r, n, m = self.observations.shape
        for num_round in range(r):
            # locs = np.where(self.observations[num_round] != 'X')
            locs = np.where((self.observations[num_round] == "H") | (self.observations[num_round] == "S") | (
                        self.observations[num_round] == '?'))
            for location in zip(locs[0], locs[1]):
                # sick not policed will be sick or healthy
                if self.pol > 0 and self.observations[num_round, location[0], location[1]] != 'H':
                    all_police_round_t = "(" + " | ".join(
                        [f'{symb("P" + str(pp), *location, num_round)}' for pp in range(self.pol)]) + ")"
                    # Q(t+1) & St -> Pt & Q(t+2)
                    # a = f'(({symb("S", *location, num_round)} & {symb("Q", *location, num_round + 1)}) >> ({all_police_round_t} & {symb("Q", *location, num_round + 2)}))'
                    a = f'({symb("Q", *location, num_round + 2)} | ~{symb("S", *location, num_round)} | ~{symb("Q", *location, num_round + 1)}) & ({all_police_round_t[1:-1]} | ~{symb("S", *location, num_round)} | ~{symb("Q", *location, num_round + 1)})'
                    self.KB.tell(a, False)

                    # police_implications = f'({all_police_round_t} >> ({symb("Q", *location, num_round + 1)} & {symb("S", *location, num_round)}))'
                    police_implications = f'({symb("Q", *location, num_round + 1)} | ~{all_police_round_t}) & ({symb("S", *location, num_round)} | ~{all_police_round_t})'
                    self.KB.tell(police_implications, False)

                    # sick_policed_will_be_Q = f'(({all_police_round_t} & {symb("S", *location, num_round)}) >> ({symb("Q", *location, num_round + 1)}))'
                    sick_policed_will_be_Q = f'{symb("Q", *location, num_round + 1)} | ~{all_police_round_t} | ~{symb("S", *location, num_round)}'
                    self.KB.tell(sick_policed_will_be_Q, False)

                    policed_implications = f'({all_police_round_t} >> ({symb("Q", *location, num_round + 1)} & {symb("S", *location, num_round)}))'
                    self.KB.tell(policed_implications)

                # vaccination means was healthy or immune
                if self.med > 0 and self.observations[num_round, location[0], location[1]] != 'S':
                    all_medics_round_t = "(" + " & ".join(
                        [f'~{symb("M" + str(mm), *location, num_round)}' for mm in range(self.med)]) + ")"
                    self.KB.tell(
                        f'((~{all_medics_round_t} & {symb("H", *location, num_round)}) >> ({symb("I", *location, num_round + 1)}))')
                    self.KB.tell(
                        f'(({all_medics_round_t} & {symb("H", *location, num_round)}) >> ({symb("H", *location, num_round + 1)} | {symb("S", *location, num_round + 1)}))')

                    all_medics_round_t = "(" + " | ".join(
                        [f'{symb("M" + str(mm), *location, num_round)}' for mm in range(self.med)]) + ")"
                    medic_implications = f'({all_medics_round_t} >> ({symb("I", *location, num_round + 1)} & {symb("H", *location, num_round)}))'
                    # medic_implications = f'({symb("Q", *location, num_round + 1)} | ~{all_police_round_t}) & ({symb("S", *location, num_round)} | ~{all_police_round_t})'
                    self.KB.tell(medic_implications)

                    all_medics_round_t = "(" + " | ".join(
                        [f'{symb("M" + str(mm), *location, num_round)}' for mm in range(self.med)]) + ")"
                    medic_implications = f'(({all_medics_round_t} & {symb("H", *location, num_round)}) >> ({symb("I", *location, num_round + 1)}))'
                    # medic_implications = f'({symb("Q", *location, num_round + 1)} | ~{all_police_round_t}) & ({symb("S", *location, num_round)} | ~{all_police_round_t})'
                    self.KB.tell(medic_implications)

    def teams(self, letter='P'):
        r, n, m = self.observations.shape
        free_letter = 'F' if letter == 'P' else 'G'
        max_teams = self.pol if letter == 'P' else self.med
        action_on = 'S' if letter == 'P' else 'H'
        effect = 'Q' if letter == 'P' else 'I'
        # team is available if it didnt work anywhere
        # if any team is available then there is a team available
        # if someone is can be worked on and there is team available then action will be made
        # team can work only once
        # 2 teams can't work in the same place

        # Only once and not 2 the same location
        for team_i in range(max_teams):
            for num_round in range(r - 1):
                # locs = np.where(self.observations[num_round] != 'X')
                locs = np.where((self.observations[num_round] == action_on) | (self.observations[num_round] == '?'))
                for location in zip(locs[0], locs[1]):
                    i, j = location
                    if self.observations[num_round + 1, i, j] != effect and self.observations[
                        num_round + 1, i, j] != "?":
                        continue
                    other_locations = "(" + " & ".join(
                        [f'~{symb(letter + str(team_i), *other_location, num_round)}' for other_location in
                         zip(locs[0], locs[1]) if other_location != location]) + ")"
                    if other_locations != "()":
                        only_once = f'({symb(letter + str(team_i), *location, num_round)} >> {other_locations})'
                        self.KB.tell(only_once)

                    other_teams = "(" + " & ".join(
                        [f'~{symb(letter + str(other_team_i), *location, num_round)}' for other_team_i in
                         range(self.pol) if other_team_i != team_i]) + ")"
                    if other_teams != '()':
                        only_one = f'({symb(letter + str(team_i), *location, num_round)} >> {other_teams})'
                        self.KB.tell(only_one)

        # availability
        for team_i in range(max_teams):
            for num_round in range(r):
                locs = np.where((self.observations[num_round] == action_on) | (self.observations[num_round] == '?'))
                # didnt_work_in_any_location = "~(" +    " | ".join([f'{symb(letter + str(team_i), *location, num_round)}' for location in zip(locs[0], locs[1])]) + ")"
                # available_team = f'({didnt_work_in_any_location} >> ({symb(free_letter + str(team_i), 0, 0, num_round)}))'
                didnt_work_in_any_location = " | ".join(
                    [f'{symb(letter + str(team_i), *location, num_round)}' for location in zip(locs[0], locs[1])])
                available_team = f'{didnt_work_in_any_location} | {symb(free_letter + str(team_i), 0, 0, num_round)}'
                self.KB.tell(available_team, False)

        for num_round in range(r):
            if max_teams > 0:
                available_police_team_i = "(" + " | ".join(
                    [f'({symb(free_letter + str(team_i), 0, 0, num_round)})' for team_i in range(max_teams)]) + ")"
                any_available_team = f'({available_police_team_i} >> {symb(free_letter + str(9), 0, 0, num_round)})'
                self.KB.tell(any_available_team)
                # TODO CNF is wrong
                # any_available_team = "&".join([f'(~{symb(free_letter + str(team_i), 0, 0, num_round)} | {symb(free_letter + str(9), 0, 0, num_round)})' for team_i in range(max_teams)])
                # self.KB.tell(any_available_team, False)

        # S and available -> police has to work

        for num_round in range(r):
            locs = np.where((self.observations[num_round] == action_on) | (self.observations[num_round] == '?'))
            for location in zip(locs[0], locs[1]):
                if max_teams > 0:
                    # team_worked_here = "(" + " | ".join([f'{symb(letter + str(team_i), *location, num_round)}' for team_i in range(max_teams)]) + ")"
                    # available_team_and_work = f'(({symb(action_on, *location, num_round)} & {symb(free_letter + str(9), 0, 0, num_round)}) >> {team_worked_here})'
                    team_worked_here = " | ".join(
                        [f'{symb(letter + str(team_i), *location, num_round)}' for team_i in range(max_teams)])
                    available_team_and_work = f'{team_worked_here} | ~{symb(free_letter + str(9), 0, 0, num_round)} | ~{symb(action_on, *location, num_round)}'
                    self.KB.tell(available_team_and_work, False)

    def answer_queries(self):
        dic = {}
        for query in self.queries:
            loc, roun, let = query
            if self.observations[roun, loc[0], loc[1]] != '?':
                dic[query] = 'F' if self.observations[roun, loc[0], loc[1]] != let else "T"
                continue
            if (self.pol == 0 and let == 'Q') or (self.med == 0 and let == 'I'):
                dic[query] = 'F'
                continue

            s = Glucose3()
            st = [string_to_nums(item) for item in pysat_to_cnf(symb(let, *loc, roun)).split(" & ")]
            s.append_formula(list(self.KB.clauses) + st)
            qu = s.solve()

            ss = Glucose3()
            my_symb = f'~({symb(let, *loc, roun)})'
            st = [string_to_nums(item) for item in pysat_to_cnf(my_symb).split(" & ")]
            ss.append_formula(self.KB.clauses + st)
            no_qu = ss.solve()

            if qu and no_qu:
                dic[query] = '?'
            elif qu and not no_qu:
                dic[query] = 'T'
            elif not qu:
                dic[query] = 'F'
        return dic


class KB:
    def __init__(self):
        self.clauses = list()

    def tell(self, sentence: str, convert_to_cnf=True):
        if convert_to_cnf:
            sentence = pysat_to_cnf(sentence)
        clauses = sentence.split(' & ')
        for clause in clauses:
            if string_to_nums(clause) not in self.clauses:
                self.clauses.append(string_to_nums(clause))


def solve_problem(input):
    mp = MedicalProblem(input)
    return mp.answer_queries()

    # put your solution here, remember the format needed
