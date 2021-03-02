from pysat.solvers import Glucose3
from sympy.logic.boolalg import to_cnf
import sympy
import string
import itertools
from sympy import symbols

ids = ['205460686']


class AnalyzeDynamics:
    def __init__(self, observations, police, medics):
        self.observations = observations
        self.max_t = len(observations) - 1
        self.police = police
        self.medics = medics
        self.n_rows = len(self.observations[0])
        self.n_columns = len(self.observations[0][0])
        if self.police == 0 and self.medics == 0:
            self.status_list = ['U', 'H', 'S', 'SN', 'Healed']
            self.variables_dict = {'U': {}, 'H': {}, 'S': {}}
        elif self.police == 0 and self.medics > 0:
            self.status_list = ['U', 'H', 'S', 'I', 'SN', 'Healed', 'got_I']
            self.variables_dict = {'U': {}, 'H': {}, 'S': {}, 'I': {}}
        elif self.police > 0 and self.medics == 0:
            self.status_list = ['U', 'H', 'S', 'Q', 'SN', 'Healed', 'got_Q', 'Q_over']
            self.variables_dict = {'U': {}, 'H': {}, 'S': {}, 'Q': {}}
        else:
            self.status_list = ['U', 'H', 'S', 'Q', 'I', 'SN', 'Healed', 'got_I', 'got_Q', 'Q_over']
            self.variables_dict = {'U': {}, 'H': {}, 'S': {}, 'Q': {}, 'I': {}}

        # literal_dict keys are (status, t, i, j)
        self.literal_dict = {}
        self.build_literal_dict()

        self.build_variables_dict()

        self.kb_clauses = []
        self.find_knowledge_base_clauses()

    def build_literal_dict(self):
        """
        ONLY IMPLEMENTED FOR POLICE == 0 AND MEDICS == 0

        builds the literal dict:
        keys: all the possible literals
        values: the integer that represents the literal in the SAT solver
        """
        counter = 1
        for status in self.status_list:
            for t in range(self.max_t + 1):
                for i in range(self.n_rows):
                    for j in range(self.n_columns):
                        self.literal_dict[(status, t, i, j)] = counter
                        counter += 1

    def build_false_matrix(self):
        return [[False for i in range(self.n_columns)] for j in range(self.n_rows)]

    def build_variables_dict(self):
        """
        builds the variables_dict that represents what we know about the map
        variables_dict[status][t][i][j] contains:
            True if the status in time t, in the location (i,j) is status
            False if it contains another status
            ? if it contains a ?
        """
        t = 0
        for observation in self.observations:
            for status in self.variables_dict.keys():
                self.variables_dict[status][t] = self.build_false_matrix()
            for i in range(self.n_rows):
                for j in range(self.n_columns):
                    status = observation[i][j]
                    if status == '?':
                        for status_key in self.variables_dict.keys():
                            self.variables_dict[status_key][t][i][j] = '?'
                    else:
                        self.variables_dict[status][t][i][j] = True
            t = t + 1
        # in t=0 no 'Q', 'I', 'got_I', 'got_Q', 'Q_over'
        if self.police > 0 or self.medics > 0:
            for i in range(self.n_rows):
                for j in range(self.n_columns):
                    for status in set(self.status_list).intersection(['Q', 'I']):
                        self.variables_dict[status][0][i][j] = False

    def find_knowledge_base_clauses(self):
        """
        ONLY IMPLEMENTED FOR POLICE == 0 AND MEDICS == 0
        adds all the literals that are directly taken from the variables dict
        this doesn't include the query
        """
        # updating predicates that refer to the given observations
        for status in list(self.variables_dict.keys()):
            for t, bool_matrix in self.variables_dict[status].items():
                for i in range(self.n_rows):
                    for j in range(self.n_columns):
                        if bool_matrix[i][j] != '?':
                            literal_number = self.literal_dict[(status, t, i, j)]
                            sign = bool_matrix[i][j] - (not bool_matrix[i][j])
                            self.kb_clauses.append([sign*literal_number])
        # predicates that make sure that no area is healed or Q_over before time 3
        for t in range(min(self.max_t + 1, 3)):
            for i in range(self.n_rows):
                for j in range(self.n_columns):
                    self.kb_clauses.append([-self.literal_dict[('Healed', t, i, j)]])
                    if self.police > 0:
                        self.kb_clauses.append([-self.literal_dict[('Q_over', t, i, j)]])
        # no got_Q and got_I in t=0
        if self.police > 0 or self.medics > 0:
            for i in range(self.n_rows):
                for j in range(self.n_columns):
                    if self.medics > 0:
                        self.kb_clauses.append([-self.literal_dict[('got_I', 0, i, j)]])
                    if self.police > 0:
                        self.kb_clauses.append([-self.literal_dict[('got_Q', 0, i, j)]])
        pass

    def U_t_clauses(self, t, i, j):
        # U(t) <==> U(t-1)
        a = self.literal_dict[('U', t - 1, i, j)]
        b = self.literal_dict[('U', t, i, j)]
        return [[-a, b], [-b, a]]

    def H_t_clauses(self, t, i, j):
        # H(t) <==> (H(t-1) and ~SN(t-1) and ~got_I(t)) or Healed(t) or Q_over(t)
        a = self.literal_dict[('H', t, i, j)]
        b = self.literal_dict[('H', t - 1, i, j)]
        c = self.literal_dict[('SN', t - 1, i, j)]
        d = self.literal_dict[('Healed', t, i, j)]
        if self.police == 0 and self.medics == 0:
            return [[b, d, -a], [d, -a, -c], [a, -d], [a, c, -b]]
        if self.police > 0 and self.medics == 0:
            e = self.literal_dict[('Q_over', t, i, j)]
            return [[a, -d], [a, -e], [a, c, -b], [b, d, e, -a], [d, e, -a, -c]]
        if self.medics > 0 and self.police == 0:
            f = self.literal_dict[('got_I', t, i, j)]
            return [[a, -d], [b, d, -a], [d, -a, -c], [d, -a, -f], [a, c, f, -b]]
        if self.medics > 0 and self.police > 0:
            e = self.literal_dict[('Q_over', t, i, j)]
            f = self.literal_dict[('got_I', t, i, j)]
            return [[a, -d], [a, -e], [a, c, f, -b], [b, d, e, -a], [d, e, -a, -c], [d, e, -a, -f]]


    def S_t_clauses(self, t, i, j):
        # s(t) <==> (s(t-1) and ~Healed(t) and ~got_Q(t)) or (H(t-1) and SN(t-1) and ~got_I(t))
        a = self.literal_dict[('S', t, i, j)]
        b = self.literal_dict[('S', t - 1, i, j)]
        c = self.literal_dict[('Healed', t, i, j)]
        d = self.literal_dict[('H', t - 1, i, j)]
        e = self.literal_dict[('SN', t - 1, i, j)]
        if self.police == 0 and self.medics == 0:
            return [[a, c,  -b], [b, d,  -a], [b, e,  -a], [a, -d,  -e], [d, -a,  -c], [e, -a, -c]]
        if self.police > 0 and self.medics == 0:
            f = self.literal_dict[('got_Q', t, i, j)]
            return [[b, d, -a], [b, e, -a], [a, -d, -e], [d, -a, -c], [d, -a, -f], [e, -a, -c], [e, -a, -f], [a, c, f, -b]]
        if self.medics > 0 and self.police == 0:
            g = self.literal_dict[('got_I', t, i, j)]
            return [[a, c, -b], [b, d, -a], [b, e, -a], [b, -a,  -g], [d, -a, -c], [e, -a, -c], [-a, -c, -g], [a, g, -d, -e]]
        if self.medics > 0 and self.police > 0:
            f = self.literal_dict[('got_Q', t, i, j)]
            g = self.literal_dict[('got_I', t, i, j)]
            return [[b, d, -a], [b, e, -a], [b, -a, -g], [d, -a, -c], [d, -a, -f], [e, -a, -c], [e, -a, -f], [a, c, f, -b],
                    [-a, -c, -g], [-a, -f, -g], [a, g, -d, -e]]


    def Healed_t_clauses(self, t, i, j):
        # Healed(t) <==> (s(t-3) and s(t-2) and s(t-1) and ~got_Q(t)
        a = self.literal_dict[('Healed', t, i, j)]
        b = self.literal_dict[('S', t - 1, i, j)]
        c = self.literal_dict[('S', t - 2, i, j)]
        d = self.literal_dict[('S', t - 3, i, j)]
        if self.police > 0:
            e = self.literal_dict[('got_Q', t, i, j)]
            return [[b, -a], [c, -a], [d, -a], [-a, -e], [a, e, -b, -c, -d]]
        return [[a, -b, -c, -d], [b, -a], [c, -a], [d, -a]]


    def SN_t_clauses(self, t, i, j):
        # SN(t) <==> has Sick Neighbour(t) that isn't got_Q(t+1)
        clauses = []
        s_list = []
        got_Q_list = []
        a = self.literal_dict[('SN', t, i, j)]
        symbol_a = symbols(str(a))
        indexes = []
        if i - 1 >= 0:
            if self.variables_dict['S'][t][i-1][j]:
                indexes.append((i - 1, j))
        if i + 1 < self.n_rows:
            # if self.variables_dict['S'][t][i+1][j]:
            indexes.append((i + 1, j))
        if j - 1 >= 0:
            # if self.variables_dict['S'][t][i][j-1]:
            indexes.append((i, j - 1))
        if j + 1 < self.n_columns:
            # if self.variables_dict['S'][t][i][j+1]:
            indexes.append((i, j + 1))
        if len(indexes) == 0:
            return []
        for index in indexes:
            s_list.append(self.literal_dict[('S', t) + index])
            if self.police > 0:
                got_Q_list.append(self.literal_dict[('got_Q', t + 1) + index])
        if self.police == 0:
            for neighbour in s_list:
                clauses.append([a, -neighbour])
            clauses.append(s_list + [-a])
            return clauses

        s_got_Q_pair_list = list(zip(got_Q_list, s_list))
        symbol_list = set([abs(j) for j in got_Q_list + s_list])
        symbol_string = ''
        for symbol in symbol_list:
            symbol_string += str(symbol) + ' '
        x = symbols(symbol_string)
        symbol_dict = dict(zip(symbol_list, list(range(len(symbol_list)))))
        expression_b = None
        for pair in s_got_Q_pair_list:
            if expression_b is None:
                expression_b = ~x[symbol_dict[abs(pair[0])]] & x[symbol_dict[abs(pair[1])]]
            else:
                expression_b = expression_b | ~x[symbol_dict[abs(pair[0])]] & x[symbol_dict[abs(pair[1])]]
        expression_c = ((symbol_a >> expression_b) & (expression_b >> symbol_a))
        return self.expression_to_cnf(expression_c)

    def must_be_status_clauses(self, t, i, j):
        clause = []
        for status in self.variables_dict.keys():
            clause.append(self.literal_dict[(status, t, i, j)])
        return [clause]

    def cant_be_two_statuses(self, t, i, j):
        clauses = []
        statuses = list(self.variables_dict.keys())
        for k in range(len(statuses) - 1):
            for l in range(k + 1, len(statuses)):
                clauses.append([-self.literal_dict[(statuses[k], t, i, j)], -self.literal_dict[(statuses[l], t, i, j)]])
        return clauses

    def I_t_clauses(self, t, i, j):
        # I(t) <==> I(t-1) or got_I(t)
        a = self.literal_dict[('I', t, i, j)]
        b = self.literal_dict[('I', t - 1, i, j)]
        c = self.literal_dict[('got_I', t, i, j)]
        return [[a, -b], [a, -c], [b, c, -a]]

    def Q_t_clauses(self, t, i, j):
        a = self.literal_dict[('Q', t, i, j)]
        b = self.literal_dict[('Q', t - 1, i, j)]
        c = self.literal_dict[('Q_over', t, i, j)]
        d = self.literal_dict[('got_Q', t, i, j)]
        return [[a, -d], [a, c, -b], [b, d, -a], [d, -a, -c]]

    def Q_over_t_clauses(self, t, i, j):
        # Q_over(t) <==> (Q(t-2) and Q(t-1))
        a = self.literal_dict[('Q_over', t, i, j)]
        d = self.literal_dict[('got_Q', t - 2, i, j)]
        return [a, -d], [d, -a]

    def got_I_t_clauses(self, t, i, j):
        # got_I(t) <==> (H(t-1) and I(t))
        a = self.literal_dict[('got_I', t, i, j)]
        b = self.literal_dict[('H', t - 1, i, j)]
        c = self.literal_dict[('I', t, i, j)]
        return [[b, -a], [c, -a], [a, -b, -c]]

    def got_Q_t_clauses(self, t, i, j):
        # got_Q(t) <==> (S(t-1) and Q(t))
        a = self.literal_dict[('got_Q', t, i, j)]
        b = self.literal_dict[('S', t - 1, i, j)]
        c = self.literal_dict[('Q', t, i, j)]
        return [[b, -a], [c, -a], [a, -b, -c]]

    def expression_to_cnf(self, expression, simplify=False):
        cnf_expression = to_cnf(expression, simplify=simplify)
        cnf_expression2 = [str.split(x, '|') for x in str.split(str(cnf_expression).replace('(', '').replace(')', '').replace(' ', '').replace('~', '-'), '&')]
        for i in range(len(cnf_expression2)):
            for j in range(len(cnf_expression2[i])):
                cnf_expression2[i][j] = int(cnf_expression2[i][j])
        return cnf_expression2

    def dnf_to_cnf_list(self, dnf_clauses):
        symbol_list = list(set([str(abs(j)) for sub in dnf_clauses for j in sub]))
        amount_of_symbols = len(symbol_list)
        letter_list = ["".join(p) for i in range(1, (amount_of_symbols//26 + 2)) for p in itertools.product(string.ascii_lowercase, repeat=i+1)]
        letter_list.remove('as')
        letter_list = letter_list[:amount_of_symbols]
        symbol_dict = dict(zip(symbol_list + ['-', '], [', ', ', '[[', ']]'], letter_list + ['~', ')|(', '&', '(', ')']))
        dnf_clauses_string = str(dnf_clauses)
        for key, value in symbol_dict.items():
            dnf_clauses_string = dnf_clauses_string.replace(key, value)
        expression = sympy.parsing.sympy_parser.parse_expr(dnf_clauses_string)
        cnf_expression = str(to_cnf(expression, simplify=False))
        symbol_dict2 = dict(zip(letter_list + ['~', '(', ')'], symbol_list + ['-', '', '']))
        for key, value in sorted(list(symbol_dict2.items()), key=lambda x: len(x[0]), reverse=True):
            cnf_expression = cnf_expression.replace(key, value)
        cnf_expression2 = [str.split(x, '|') for x in str.split(cnf_expression, '&')]
        for i in range(len(cnf_expression2)):
            for j in range(len(cnf_expression2[i])):
                cnf_expression2[i][j] = int(cnf_expression2[i][j])
        return cnf_expression2

    def build_possible_action_indexes(self, pre, effect, index_set, t):
        possibly_index_set = []
        for index in index_set:
            pre_possible = self.variables_dict[pre][t-1][index[0]][index[1]]
            if not pre_possible:
                continue
            effect_possible = True
            if effect == 'I':
                for time in range(t, self.max_t + 1):
                    if not self.variables_dict[effect][time][index[0]][index[1]]:
                        effect_possible = False
                        break
            else:
                for time in range(t, min(t + 2, self.max_t + 1)):
                    if not self.variables_dict[effect][time][index[0]][index[1]]:
                        effect_possible = False
                        break
            if not effect_possible:
                continue
            possibly_index_set.append(index)
        return possibly_index_set

    def build_definitely_action_indexes(self, pre, effect, index_set, t):
        definitely_index_set = []
        for index in index_set:
            if self.observations[t-1][index[0]][index[1]] == pre and self.observations[t][index[0]][index[1]]  == effect:
                definitely_index_set.append(index)
        return definitely_index_set

    def all_staff_used_t_clauses(self, t, staff):
        if staff == 'police':
            action = 'got_Q'
            pre = 'S'
            effect = 'Q'
            staff_amount = min([self.police, self.n_rows * self.n_columns])
        else:
            action = 'got_I'
            pre = 'H'
            effect = 'I'
            staff_amount = min([self.medics, self.n_rows * self.n_columns])
        """# checking all options of applying action
        # if k = staff_amount: got_action(t) for every index in subset and ~got_action(t) for every index out of subset
        # if k < staff_amount: got_action(t) for every index in subset and ~got_action(t) for every index out of subset and ~pre(t-1)
        # or between every clause"""
        dnf_clauses = []
        index_set = [(i, j) for i in range(self.n_rows) for j in range(self.n_rows)]
        definitely_index_set = self.build_definitely_action_indexes(pre, effect, index_set, t)
        definitely_index_clauses = []
        for index in definitely_index_set:
            definitely_index_clauses.append(self.literal_dict[(action, t) + index])
        possibly_index_set = self.build_possible_action_indexes(pre, effect, index_set, t)
        possibly_index_set = list(set(possibly_index_set) - set(definitely_index_set))
        # checking how many places in t-1 are of type pre
        amount_of_pre = [j for sub in self.observations[t-1] for j in sub].count(pre)
        for k in range(staff_amount - len(definitely_index_set), min(staff_amount - len(definitely_index_set), amount_of_pre)-1, -1):
            # checking if the places in the subset are of type pre
            for subset in itertools.combinations(possibly_index_set, k):
                sub_clause = []
                for index in index_set:
                    if index in subset:
                        symbol = self.literal_dict[(action, t) + index]
                        sub_clause.append(symbol)
                    if index not in subset + tuple(definitely_index_set):
                        symbol = self.literal_dict[(action, t) + index]
                        sub_clause.append(-symbol)
                        if k < staff_amount - len(definitely_index_set):
                            symbol = self.literal_dict[(pre, t-1) + index]
                            sub_clause.append(-symbol)
                dnf_clauses.append(sub_clause)
        if len(dnf_clauses) == 0:
            return []
        return self.dnf_to_cnf_list(dnf_clauses) + [definitely_index_clauses]

    def find_base_clauses_help(self):
        """
        base clauses refer to clauses that are relevant for cases where police == 0 and medics ==0
        includes the query literal
        :return: base_clauses list
        """
        base_clauses = []
        for t in range(self.max_t + 1):
            if t > 0:
                if self.medics > 0:
                    base_clauses += self.all_staff_used_t_clauses(t, 'medics')
                if self.police > 0:
                    base_clauses += self.all_staff_used_t_clauses(t, 'police')
            for i in range(self.n_rows):
                for j in range(self.n_columns):
                    if t > 0:
                        #  U(t) <==> U(t-1)
                        base_clauses += self.U_t_clauses(t, i, j)
                        # H(t) <==> (H(t-1) and ~SN(t-1)) or Healed(t) or Q_over(t)
                        base_clauses += self.H_t_clauses(t, i, j)
                        # s(t) <==> (s(t-1) and ~Healed(t)) or (H(t-1) and SN(t-1))
                        base_clauses += self.S_t_clauses(t, i, j)
                        if self.medics > 0:
                            # I(t) <==> I(t-1) or got_I(t)
                            base_clauses += self.I_t_clauses(t, i, j)
                            # got_I(t) <==> (H(t-1) and I(t))
                            base_clauses += self.got_I_t_clauses(t, i, j)
                        if self.police > 0:
                            # Q(t) <==> (Q(t-1) and ~Q_over(t)) or got_Q(t)
                            base_clauses += self.Q_t_clauses(t, i, j)
                            # got_Q(t) <==> (S(t-1) and Q(t))
                            base_clauses += self.got_Q_t_clauses(t, i, j)
                    if t >= 3:
                        # Healed(t) <==> (s(t-3) and s(t-2) and s(t-1)
                        base_clauses += self.Healed_t_clauses(t, i, j)
                        if self.police > 0:
                            # Q_over(t) <==> (Q(t-2) and Q(t-1)
                            base_clauses += self.Q_over_t_clauses(t, i, j)

                    # SN(t) <==> has Sick Neighbour
                    if t < self.max_t:
                        base_clauses += self.SN_t_clauses(t, i, j)
                    base_clauses += self.must_be_status_clauses(t, i, j)
                    base_clauses += self.cant_be_two_statuses(t, i, j)
        return base_clauses

    def find_base_clauses(self, query):
        base_clauses = []
        q_index, q_t, q_status = query
        # add query as part of Knowledge Base
        base_clauses.append([self.literal_dict[(q_status, q_t) + q_index]])
        for status in list(self.variables_dict.keys()):
            if status != q_status:
                base_clauses.append([-self.literal_dict[(status, q_t) + q_index]])
        for status in list(self.variables_dict.keys()):
            self.variables_dict[status][q_t][q_index[0]][q_index[1]] = (q_status == status)

        base_clauses += self.find_base_clauses_help()
        return base_clauses

    def check_query(self, query):
        """
        finds the answer of a query
        :param query: given query
        :param police: amount of police
        :param medics: amount of medics
        :return: True False or uncertain
        """
        result = ''
        if query[2] == 'I' and self.medics == 0 or query[2] == 'Q' and self.police == 0:
            return 'F'
        base_clauses = self.find_base_clauses(query)
        with Glucose3(bootstrap_with=base_clauses + self.kb_clauses) as g:
            there_is_solution = g.solve()
            if there_is_solution:
                # ############################### for printing the model found
                # a = g.get_model()
                # key_list = list(self.literal_dict.keys())
                # val_list = list(self.literal_dict.values())
                # for value in a:
                #     if value < 0:
                #         position = val_list.index(-value)
                #         print('not' + str(key_list[position]))
                #     else:
                #         position = val_list.index(value)
                #         print(str(key_list[position]))
                other_solution = False
                for other_status in list(self.variables_dict.keys()):
                    if other_status == query[2]:
                        continue
                    base_clauses = self.find_base_clauses((query[0], query[1], other_status))
                    with Glucose3(bootstrap_with=base_clauses + self.kb_clauses) as g:
                        there_is_other_solution = g.solve()
                        if there_is_other_solution:
                            result = '?'
                            other_solution = True
                            break
                if not other_solution:
                    result = 'T'
            else:
                # # ############################### for printing the predicates if there is no solution
                # key_list = list(self.literal_dict.keys())
                # val_list = list(self.literal_dict.values())
                # for value in self.kb_clauses + base_clauses:
                #     for v in value:
                #         if v > 0:
                #             position = val_list.index(v)
                #             print(str(key_list[position]))
                #         else:
                #             position = val_list.index(-v)
                #             print('not ' + str(key_list[position]))
                #     print('new_predicate')
                result = 'F'
        for status in list(self.variables_dict.keys()):
            self.variables_dict[status][query[1]][query[0][0]][query[0][1]] = '?'

        return result

# def to_cnf_print(original_clause):
#     original = to_cnf(original_clause, simplify=True, force=True)
#     print(original)
#     temp = str(original).replace('(', '').replace(')', '').replace('~', '-').lower().split('&')
#     predicates = []
#     for pred in temp:
#         predicates.append(pred.split('|'))
#     print(str(predicates).replace("'", '').replace(' ,', ',').replace('[ ', '[').replace(' ]', ']').replace('  ', ' '))

def solve_problem(input):
    ad = AnalyzeDynamics(input['observations'], input['police'], input['medics'])
    result = {}
    for query in input['queries']:
        result[query] = ad.check_query(query)
    return result

