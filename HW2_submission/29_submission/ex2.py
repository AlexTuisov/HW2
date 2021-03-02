import itertools
from utils import *

ids = ['314771692']

def is_symbol(s):
    return isinstance(s, str) and s[:1].isalpha()

def dissociate(op, args):
    """Given an associative op, return a flattened list result such
    that Expr(op, *result) means the same as Expr(op, *args).
    >>> dissociate('&', [A & B])
    [A, B]
    """
    result = []

    def collect(subargs):
        for arg in subargs:
            if arg.op == op:
                collect(arg.args)
            else:
                result.append(arg)

    collect(args)
    return result

_op_identity = {'&': True, '|': False, '+': 0, '*': 1}

def associate(op, args):
    args = dissociate(op, args)
    if len(args) == 0:
        return _op_identity[op]
    elif len(args) == 1:
        return args[0]
    else:
        return Expr(op, *args)

def eliminate_implications(s):
    s = expr(s)
    if not s.args or is_symbol(s.op):
        return s  # Atoms are unchanged.
    args = list(map(eliminate_implications, s.args))
    a, b = args[0], args[-1]
    if s.op == '==>':
        return b | ~a
    elif s.op == '<==':
        return a | ~b
    elif s.op == '<=>':
        return (a | ~b) & (b | ~a)
    elif s.op == '^':
        assert len(args) == 2  # TODO: relax this restriction
        return (a & ~b) | (~a & b)
    else:
        assert s.op in ('&', '|', '~')
        return Expr(s.op, *args)

def move_not_inwards(s):
    s = expr(s)
    if s.op == '~':
        def NOT(b):
            return move_not_inwards(~b)

        a = s.args[0]
        if a.op == '~':
            return move_not_inwards(a.args[0])  # ~~A ==> A
        if a.op == '&':
            return associate('|', list(map(NOT, a.args)))
        if a.op == '|':
            return associate('&', list(map(NOT, a.args)))
        return s
    elif is_symbol(s.op) or not s.args:
        return s
    else:
        return Expr(s.op, *list(map(move_not_inwards, s.args)))

def distribute_and_over_or(s):
    s = expr(s)
    if s.op == '|':
        s = associate('|', s.args)
        if s.op != '|':
            return distribute_and_over_or(s)
        if len(s.args) == 0:
            return False
        if len(s.args) == 1:
            return distribute_and_over_or(s.args[0])
        conj = first(arg for arg in s.args if arg.op == '&')
        if not conj:
            return s
        others = [a for a in s.args if a is not conj]
        rest = associate('|', others)
        return associate('&', [distribute_and_over_or(c | rest)
                               for c in conj.args])
    elif s.op == '&':
        return associate('&', list(map(distribute_and_over_or, s.args)))
    else:
        return s

def to_cnf(s):
    s = expr(s)
    if isinstance(s, str):
        s = expr(s)
    s = eliminate_implications(s)  # Steps 1, 2 from p. 253
    s = move_not_inwards(s)  # Step 3
    return distribute_and_over_or(s)  # Step 4

def conjuncts(s):
    return dissociate('&', [s])

class PropKB():

    def __init__(self):
        self.clauses = []

    def tell(self, sentence):
        """Add the sentence's clauses to the KB."""
        self.clauses.extend(conjuncts(to_cnf(sentence)))

# Symbols
def implies(lhs, rhs):
    return Expr('==>', lhs, rhs)

def equiv(lhs, rhs):
    return Expr('<=>', lhs, rhs)

def get_expr(X, i, j, time):

    expression = None
    if X != '?':
        expression = Expr(X, i, j, time)

    return expression

def new_disjunction(sentences):
    t = sentences[0]
    for i in range(1, len(sentences)):
        t |= sentences[i]
    return t

def new_conjunction(sentences):
    t = sentences[0]
    for i in range(1, len(sentences)):
        t &= sentences[i]
    return t

def is_prop_symbol(s):
    return is_symbol(s) and s[0].isupper()

def prop_symbols(x):
    if not isinstance(x, Expr):
        return set()
    elif is_prop_symbol(x.op):
        return {x}
    else:
        return {symbol for arg in x.args for symbol in prop_symbols(arg)}

def pl_true(exp, model={}):
    if exp in (True, False):
        return exp
    op, args = exp.op, exp.args
    if is_prop_symbol(op):
        return model.get(exp)
    elif op == '~':
        p = pl_true(args[0], model)
        if p is None:
            return None
        else:
            return not p
    elif op == '|':
        result = False
        for arg in args:
            p = pl_true(arg, model)
            if p is True:
                return True
            if p is None:
                result = None
        return result
    elif op == '&':
        result = True
        for arg in args:
            p = pl_true(arg, model)
            if p is False:
                return False
            if p is None:
                result = None
        return result
    p, q = args
    if op == '==>':
        return pl_true(~p | q, model)
    elif op == '<==':
        return pl_true(p | ~q, model)
    pt = pl_true(p, model)
    if pt is None:
        return None
    qt = pl_true(q, model)
    if qt is None:
        return None
    if op == '<=>':
        return pt == qt
    elif op == '^':  # xor or 'not equivalent'
        return pt != qt
    else:
        raise ValueError('Illegal operator in logic expression' + str(exp))

def WalkSAT(clauses, p=0.5, max_flips=10000):
    # Set of all symbols in all clauses
    symbols = {sym for clause in clauses for sym in prop_symbols(clause)}
    # model is a random assignment of true/false to the symbols in clauses
    model = {s: random.choice([True, False]) for s in symbols}
    for i in range(max_flips):
        satisfied, unsatisfied = [], []
        for clause in clauses:
            (satisfied if pl_true(clause, model) else unsatisfied).append(clause)
        if not unsatisfied:  # if model satisfies all the clauses
            return model
        clause = random.choice(unsatisfied)
        if probability(p):
            sym = random.choice(list(prop_symbols(clause)))
        else:
            # Flip the symbol in clause that maximizes number of sat. clauses
            def sat_count(sym):
                # Return the the number of clauses satisfied after flipping the symbol.
                model[sym] = not model[sym]
                count = len([clause for clause in clauses if pl_true(clause, model)])
                model[sym] = not model[sym]
                return count

            sym = max(prop_symbols(clause), key=sat_count)
        model[sym] = not model[sym]
    # If no solution is found within the flip limit, we return failure
    return None

class VirusKB(PropKB):

    def __init__(self, input):
        super().__init__()

        self.police = input['police']
        self.medics = input['medics']
        self.world = input['observations']

        self.rows = self.cols = len(self.world[0])

        # adding constants
        for t, obs in enumerate(self.world):
            for i in range(self.rows):
                for j in range(self.cols):
                    e = get_expr(obs[i][j], i, j, t)
                    if e is not None:
                        self.tell(e)

        # adding temporal rules
        sicks = []
        healthy = []
        for t, obs in enumerate(self.world):
            for i in range(self.rows):
                for j in range(self.cols):
                    if obs[i][j] == 'S':
                        if i > 0:
                            E = implies(Expr('S', i, j, t) & ~Expr('Q', i, j, t+1) & Expr('H', i-1, j, t), Expr('S', i-1, j, t+1))
                            self.tell(E)
                        if i < self.rows-1:
                            E = implies(Expr('S', i, j, t) & ~Expr('Q', i, j, t+1) & Expr('H', i+1, j, t), Expr('S', i+1, j, t+1))
                            self.tell(E)
                        if j > 0:
                            E = implies(Expr('S', i, j, t) & ~Expr('Q', i, j, t+1) & Expr('H', i, j-1, t), Expr('S', i, j-1, t+1))
                            self.tell(E)
                        if j < self.rows-1:
                            E = implies(Expr('S', i, j, t) & ~Expr('Q', i, j, t+1) & Expr('H', i, j+1, t), Expr('S', i, j+1, t+1))
                            self.tell(E)
                        
                        E = implies(Expr('S', i, j, t) & ~(Expr('M', i, j, t) | Expr('P', i, j, t)), Expr('S', i, j, t))
                        self.tell(E)
                        sicks.append(Expr('S', i, j, t))
                    
                    elif obs[i][j] == 'H':
                        healthy.append(Expr('H', i, j, t))

        # adding action rules
        
        for t in range(len(self.world)):
            medics_list = []
            for i in range(self.rows):
                for j in range(self.cols):
                    m = Expr('M', i, j, t)
                    medics_list.append(m)

                    E = implies(Expr('S', i, j, t) & Expr('M', i, j, t), Expr('H', i, j, t+1))
                    self.tell(E)

            if self.medics > 0:
                for inds in itertools.combinations(range(len(medics_list)), self.medics):
                    ms = [medics_list[i] for i in inds]
                    inds = sorted(inds)
                    sentences = ms + [~medics_list[i] for i in range(len(medics_list)) if i not in inds]
                    E = new_conjunction(sentences)
                    self.tell(E)

        for t in range(len(self.world)):
            police_list = []
            for i in range(self.rows):
                for j in range(self.cols):
                    p = Expr('P', i, j, t)
                    police_list.append(p)

                    E = implies(Expr('S', i, j, t) & Expr('P', i, j, t), Expr('Q', i, j, t+1))
                    self.tell(E)

            if self.police > 0:
                con_police = []
                for inds in itertools.combinations(range(len(police_list)), self.police):
                    ps = [police_list[i] for i in inds]
                    ps = new_conjunction(ps)
                    con_police.append(ps)

                self.tell(new_disjunction(con_police))
                for a, b in itertools.combinations(con_police, 2):
                    self.tell(~a | ~b)

def solve_problem(input):
    # put your solution here, remember the format needed

    virus_kb = VirusKB(input)

    def WalkSAT_CNF(sentence, p=1, max_flips=1000000):
        return WalkSAT(conjuncts(to_cnf(sentence)), 0, max_flips)
    
    answers = {}
    for q in input['queries'][0]:
        
        E = Expr(q[-1], q[0][0], q[0][1], q[1])

        Sol = WalkSAT_CNF(new_conjunction(virus_kb.clauses))

        if E in Sol:
            answers[tuple(q)] = Bool(Sol[E])
        else:
            answers[tuple(q)] = Bool(False)

    return answers