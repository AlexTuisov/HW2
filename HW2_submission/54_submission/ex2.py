from itertools import combinations
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Minisat22

'''
######################################################################################
######################################################################################
######################################################################################
                                    Utils.py
######################################################################################
######################################################################################
######################################################################################
'''
"""Provides some utilities widely used by other modules"""

import bisect
import collections
import collections.abc
import functools
import heapq
import operator
import os.path
import random
from itertools import chain, combinations
from statistics import mean

import numpy as np

# ______________________________________________________________________________
# Functions on Sequences and Iterables


def sequence(iterable):
    """Converts iterable to sequence, if it is not already one."""
    return iterable if isinstance(iterable, collections.abc.Sequence) else tuple([iterable])


def remove_all(item, seq):
    """Return a copy of seq (or string) with all occurrences of item removed."""
    if isinstance(seq, str):
        return seq.replace(item, '')
    elif isinstance(seq, set):
        rest = seq.copy()
        rest.remove(item)
        return rest
    else:
        return [x for x in seq if x != item]


def unique(seq):
    """Remove duplicate elements from seq. Assumes hashable elements."""
    return list(set(seq))


def count(seq):
    """Count the number of items in sequence that are interpreted as true."""
    return sum(map(bool, seq))


def multimap(items):
    """Given (key, val) pairs, return {key: [val, ....], ...}."""
    result = collections.defaultdict(list)
    for (key, val) in items:
        result[key].append(val)
    return dict(result)


def multimap_items(mmap):
    """Yield all (key, val) pairs stored in the multimap."""
    for (key, vals) in mmap.items():
        for val in vals:
            yield key, val


def product(numbers):
    """Return the product of the numbers, e.g. product([2, 3, 10]) == 60"""
    result = 1
    for x in numbers:
        result *= x
    return result


def first(iterable, default=None):
    """Return the first element of an iterable; or default."""
    return next(iter(iterable), default)


def is_in(elt, seq):
    """Similar to (elt in seq), but compares with 'is', not '=='."""
    return any(x is elt for x in seq)


def mode(data):
    """Return the most common data item. If there are ties, return any one of them."""
    [(item, count)] = collections.Counter(data).most_common(1)
    return item


def power_set(iterable):
    """power_set([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return list(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))[1:]


def extend(s, var, val):
    """Copy dict s and extend it by setting var to val; return copy."""
    return {**s, var: val}


def flatten(seqs):
    return sum(seqs, [])


# ______________________________________________________________________________
# argmin and argmax

identity = lambda x: x


def argmin_random_tie(seq, key=identity):
    """Return a minimum element of seq; break ties at random."""
    return min(shuffled(seq), key=key)


def argmax_random_tie(seq, key=identity):
    """Return an element with highest fn(seq[i]) score; break ties at random."""
    return max(shuffled(seq), key=key)


def shuffled(iterable):
    """Randomly shuffle a copy of iterable."""
    items = list(iterable)
    random.shuffle(items)
    return items


# ______________________________________________________________________________
# Statistical and mathematical functions


def histogram(values, mode=0, bin_function=None):
    """Return a list of (value, count) pairs, summarizing the input values.
    Sorted by increasing value, or if mode=1, by decreasing count.
    If bin_function is given, map it over values first."""
    if bin_function:
        values = map(bin_function, values)

    bins = {}
    for val in values:
        bins[val] = bins.get(val, 0) + 1

    if mode:
        return sorted(list(bins.items()), key=lambda x: (x[1], x[0]), reverse=True)
    else:
        return sorted(bins.items())


def dot_product(x, y):
    """Return the sum of the element-wise product of vectors x and y."""
    return sum(_x * _y for _x, _y in zip(x, y))


def element_wise_product(x, y):
    """Return vector as an element-wise product of vectors x and y."""
    assert len(x) == len(y)
    return np.multiply(x, y)


def matrix_multiplication(x, *y):
    """Return a matrix as a matrix-multiplication of x and arbitrary number of matrices *y."""

    result = x
    for _y in y:
        result = np.matmul(result, _y)

    return result


def vector_add(a, b):
    """Component-wise addition of two vectors."""
    return tuple(map(operator.add, a, b))


def scalar_vector_product(x, y):
    """Return vector as a product of a scalar and a vector"""
    return np.multiply(x, y)


def probability(p):
    """Return true with probability p."""
    return p > random.uniform(0.0, 1.0)


def weighted_sample_with_replacement(n, seq, weights):
    """Pick n samples from seq at random, with replacement, with the
    probability of each element in proportion to its corresponding
    weight."""
    sample = weighted_sampler(seq, weights)
    return [sample() for _ in range(n)]


def weighted_sampler(seq, weights):
    """Return a random-sample function that picks from seq weighted by weights."""
    totals = []
    for w in weights:
        totals.append(w + totals[-1] if totals else w)
    return lambda: seq[bisect.bisect(totals, random.uniform(0, totals[-1]))]


def weighted_choice(choices):
    """A weighted version of random.choice"""
    # NOTE: should be replaced by random.choices if we port to Python 3.6

    total = sum(w for _, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w >= r:
            return c, w
        upto += w


def rounder(numbers, d=4):
    """Round a single number, or sequence of numbers, to d decimal places."""
    if isinstance(numbers, (int, float)):
        return round(numbers, d)
    else:
        constructor = type(numbers)  # Can be list, set, tuple, etc.
        return constructor(rounder(n, d) for n in numbers)


def num_or_str(x):  # TODO: rename as `atom`
    """The argument is a string; convert to a number if possible, or strip it."""
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return str(x).strip()


def euclidean_distance(x, y):
    return np.sqrt(sum((_x - _y) ** 2 for _x, _y in zip(x, y)))


def manhattan_distance(x, y):
    return sum(abs(_x - _y) for _x, _y in zip(x, y))


def hamming_distance(x, y):
    return sum(_x != _y for _x, _y in zip(x, y))


def cross_entropy_loss(x, y):
    return (-1.0 / len(x)) * sum(_x * np.log(_y) + (1 - _x) * np.log(1 - _y) for _x, _y in zip(x, y))


def mean_squared_error_loss(x, y):
    return (1.0 / len(x)) * sum((_x - _y) ** 2 for _x, _y in zip(x, y))


def rms_error(x, y):
    return np.sqrt(ms_error(x, y))


def ms_error(x, y):
    return mean((_x - _y) ** 2 for _x, _y in zip(x, y))


def mean_error(x, y):
    return mean(abs(_x - _y) for _x, _y in zip(x, y))


def mean_boolean_error(x, y):
    return mean(_x != _y for _x, _y in zip(x, y))


def normalize(dist):
    """Multiply each number by a constant such that the sum is 1.0"""
    if isinstance(dist, dict):
        total = sum(dist.values())
        for key in dist:
            dist[key] = dist[key] / total
            assert 0 <= dist[key] <= 1  # probabilities must be between 0 and 1
        return dist
    total = sum(dist)
    return [(n / total) for n in dist]


def random_weights(min_value, max_value, num_weights):
    return [random.uniform(min_value, max_value) for _ in range(num_weights)]


def sigmoid(x):
    """Return activation value of x with sigmoid function."""
    return 1 / (1 + np.exp(-x))


def sigmoid_derivative(value):
    return value * (1 - value)


def elu(x, alpha=0.01):
    return x if x > 0 else alpha * (np.exp(x) - 1)


def elu_derivative(value, alpha=0.01):
    return 1 if value > 0 else alpha * np.exp(value)


def tanh(x):
    return np.tanh(x)


def tanh_derivative(value):
    return 1 - (value ** 2)


def leaky_relu(x, alpha=0.01):
    return x if x > 0 else alpha * x


def leaky_relu_derivative(value, alpha=0.01):
    return 1 if value > 0 else alpha


def relu(x):
    return max(0, x)


def relu_derivative(value):
    return 1 if value > 0 else 0


def step(x):
    """Return activation value of x with sign function"""
    return 1 if x >= 0 else 0


def gaussian(mean, st_dev, x):
    """Given the mean and standard deviation of a distribution, it returns the probability of x."""
    return 1 / (np.sqrt(2 * np.pi) * st_dev) * np.e ** (-0.5 * (float(x - mean) / st_dev) ** 2)


def linear_kernel(x, y=None):
    if y is None:
        y = x
    return np.dot(x, y.T)


def polynomial_kernel(x, y=None, degree=2.0):
    if y is None:
        y = x
    return (1.0 + np.dot(x, y.T)) ** degree


def rbf_kernel(x, y=None, gamma=None):
    """Radial-basis function kernel (aka squared-exponential kernel)."""
    if y is None:
        y = x
    if gamma is None:
        gamma = 1.0 / x.shape[1]  # 1.0 / n_features
    return np.exp(-gamma * (-2.0 * np.dot(x, y.T) +
                            np.sum(x * x, axis=1).reshape((-1, 1)) + np.sum(y * y, axis=1).reshape((1, -1))))


# ______________________________________________________________________________
# Grid Functions


orientations = EAST, NORTH, WEST, SOUTH = [(1, 0), (0, 1), (-1, 0), (0, -1)]
turns = LEFT, RIGHT = (+1, -1)


def turn_heading(heading, inc, headings=orientations):
    return headings[(headings.index(heading) + inc) % len(headings)]


def turn_right(heading):
    return turn_heading(heading, RIGHT)


def turn_left(heading):
    return turn_heading(heading, LEFT)


def distance(a, b):
    """The distance between two (x, y) points."""
    xA, yA = a
    xB, yB = b
    return np.hypot((xA - xB), (yA - yB))


def distance_squared(a, b):
    """The square of the distance between two (x, y) points."""
    xA, yA = a
    xB, yB = b
    return (xA - xB) ** 2 + (yA - yB) ** 2


# ______________________________________________________________________________
# Misc Functions

class injection:
    """Dependency injection of temporary values for global functions/classes/etc.
    E.g., `with injection(DataBase=MockDataBase): ...`"""

    def __init__(self, **kwds):
        self.new = kwds

    def __enter__(self):
        self.old = {v: globals()[v] for v in self.new}
        globals().update(self.new)

    def __exit__(self, type, value, traceback):
        globals().update(self.old)


def memoize(fn, slot=None, maxsize=32):
    """Memoize fn: make it remember the computed value for any argument list.
    If slot is specified, store result in that slot of first argument.
    If slot is false, use lru_cache for caching the values."""
    if slot:
        def memoized_fn(obj, *args):
            if hasattr(obj, slot):
                return getattr(obj, slot)
            else:
                val = fn(obj, *args)
                setattr(obj, slot, val)
                return val
    else:
        @functools.lru_cache(maxsize=maxsize)
        def memoized_fn(*args):
            return fn(*args)

    return memoized_fn


def name(obj):
    """Try to find some reasonable name for the object."""
    return (getattr(obj, 'name', 0) or getattr(obj, '__name__', 0) or
            getattr(getattr(obj, '__class__', 0), '__name__', 0) or
            str(obj))


def isnumber(x):
    """Is x a number?"""
    return hasattr(x, '__int__')


def issequence(x):
    """Is x a sequence?"""
    return isinstance(x, collections.abc.Sequence)


def print_table(table, header=None, sep='   ', numfmt='{}'):
    """Print a list of lists as a table, so that columns line up nicely.
    header, if specified, will be printed as the first row.
    numfmt is the format for all numbers; you might want e.g. '{:.2f}'.
    (If you want different formats in different columns,
    don't use print_table.) sep is the separator between columns."""
    justs = ['rjust' if isnumber(x) else 'ljust' for x in table[0]]

    if header:
        table.insert(0, header)

    table = [[numfmt.format(x) if isnumber(x) else x for x in row]
             for row in table]

    sizes = list(map(lambda seq: max(map(len, seq)), list(zip(*[map(str, row) for row in table]))))

    for row in table:
        print(sep.join(getattr(str(x), j)(size) for (j, size, x) in zip(justs, sizes, row)))


def open_data(name, mode='r'):
    aima_root = os.path.dirname(__file__)
    aima_file = os.path.join(aima_root, *['aima-data', name])

    return open(aima_file, mode=mode)


def failure_test(algorithm, tests):
    """Grades the given algorithm based on how many tests it passes.
    Most algorithms have arbitrary output on correct execution, which is difficult
    to check for correctness. On the other hand, a lot of algorithms output something
    particular on fail (for example, False, or None).
    tests is a list with each element in the form: (values, failure_output)."""
    return mean(int(algorithm(x) != y) for x, y in tests)


# ______________________________________________________________________________
# Expressions

# See https://docs.python.org/3/reference/expressions.html#operator-precedence
# See https://docs.python.org/3/reference/datamodel.html#special-method-names

class Expr:
    """A mathematical expression with an operator and 0 or more arguments.
    op is a str like '+' or 'sin'; args are Expressions.
    Expr('x') or Symbol('x') creates a symbol (a nullary Expr).
    Expr('-', x) creates a unary; Expr('+', x, 1) creates a binary."""

    def __init__(self, op, *args):
        self.op = str(op)
        self.args = args

    # Operator overloads
    def __neg__(self):
        return Expr('-', self)

    def __pos__(self):
        return Expr('+', self)

    def __invert__(self):
        return Expr('~', self)

    def __add__(self, rhs):
        return Expr('+', self, rhs)

    def __sub__(self, rhs):
        return Expr('-', self, rhs)

    def __mul__(self, rhs):
        return Expr('*', self, rhs)

    def __pow__(self, rhs):
        return Expr('**', self, rhs)

    def __mod__(self, rhs):
        return Expr('%', self, rhs)

    def __and__(self, rhs):
        return Expr('&', self, rhs)

    def __xor__(self, rhs):
        return Expr('^', self, rhs)

    def __rshift__(self, rhs):
        return Expr('>>', self, rhs)

    def __lshift__(self, rhs):
        return Expr('<<', self, rhs)

    def __truediv__(self, rhs):
        return Expr('/', self, rhs)

    def __floordiv__(self, rhs):
        return Expr('//', self, rhs)

    def __matmul__(self, rhs):
        return Expr('@', self, rhs)

    def __or__(self, rhs):
        """Allow both P | Q, and P |'==>'| Q."""
        if isinstance(rhs, Expression):
            return Expr('|', self, rhs)
        else:
            return PartialExpr(rhs, self)

    # Reverse operator overloads
    def __radd__(self, lhs):
        return Expr('+', lhs, self)

    def __rsub__(self, lhs):
        return Expr('-', lhs, self)

    def __rmul__(self, lhs):
        return Expr('*', lhs, self)

    def __rdiv__(self, lhs):
        return Expr('/', lhs, self)

    def __rpow__(self, lhs):
        return Expr('**', lhs, self)

    def __rmod__(self, lhs):
        return Expr('%', lhs, self)

    def __rand__(self, lhs):
        return Expr('&', lhs, self)

    def __rxor__(self, lhs):
        return Expr('^', lhs, self)

    def __ror__(self, lhs):
        return Expr('|', lhs, self)

    def __rrshift__(self, lhs):
        return Expr('>>', lhs, self)

    def __rlshift__(self, lhs):
        return Expr('<<', lhs, self)

    def __rtruediv__(self, lhs):
        return Expr('/', lhs, self)

    def __rfloordiv__(self, lhs):
        return Expr('//', lhs, self)

    def __rmatmul__(self, lhs):
        return Expr('@', lhs, self)

    def __call__(self, *args):
        """Call: if 'f' is a Symbol, then f(0) == Expr('f', 0)."""
        if self.args:
            raise ValueError('Can only do a call for a Symbol, not an Expr')
        else:
            return Expr(self.op, *args)

    # Equality and repr
    def __eq__(self, other):
        """x == y' evaluates to True or False; does not build an Expr."""
        return isinstance(other, Expr) and self.op == other.op and self.args == other.args

    def __lt__(self, other):
        return isinstance(other, Expr) and str(self) < str(other)

    def __hash__(self):
        return hash(self.op) ^ hash(self.args)

    def __repr__(self):
        op = self.op
        args = [str(arg) for arg in self.args]
        if op.isidentifier():  # f(x) or f(x, y)
            return '{}({})'.format(op, ', '.join(args)) if args else op
        elif len(args) == 1:  # -x or -(x + 1)
            return op + args[0]
        else:  # (x - y)
            opp = (' ' + op + ' ')
            return '(' + opp.join(args) + ')'


# An 'Expression' is either an Expr or a Number.
# Symbol is not an explicit type; it is any Expr with 0 args.


Number = (int, float, complex)
Expression = (Expr, Number)


def Symbol(name):
    """A Symbol is just an Expr with no args."""
    return Expr(name)


def symbols(names):
    """Return a tuple of Symbols; names is a comma/whitespace delimited str."""
    return tuple(Symbol(name) for name in names.replace(',', ' ').split())


def subexpressions(x):
    """Yield the subexpressions of an Expression (including x itself)."""
    yield x
    if isinstance(x, Expr):
        for arg in x.args:
            yield from subexpressions(arg)


def arity(expression):
    """The number of sub-expressions in this expression."""
    if isinstance(expression, Expr):
        return len(expression.args)
    else:  # expression is a number
        return 0


# For operators that are not defined in Python, we allow new InfixOps:


class PartialExpr:
    """Given 'P |'==>'| Q, first form PartialExpr('==>', P), then combine with Q."""

    def __init__(self, op, lhs):
        self.op, self.lhs = op, lhs

    def __or__(self, rhs):
        return Expr(self.op, self.lhs, rhs)

    def __repr__(self):
        return "PartialExpr('{}', {})".format(self.op, self.lhs)


def expr(x):
    """Shortcut to create an Expression. x is a str in which:
    - identifiers are automatically defined as Symbols.
    - ==> is treated as an infix |'==>'|, as are <== and <=>.
    If x is already an Expression, it is returned unchanged. Example:
    >>> expr('P & Q ==> Q')
    ((P & Q) ==> Q)
    """
    return eval(expr_handle_infix_ops(x), defaultkeydict(Symbol)) if isinstance(x, str) else x


infix_ops = '==> <== <=>'.split()


def expr_handle_infix_ops(x):
    """Given a str, return a new str with ==> replaced by |'==>'|, etc.
    >>> expr_handle_infix_ops('P ==> Q')
    "P |'==>'| Q"
    """
    for op in infix_ops:
        x = x.replace(op, '|' + repr(op) + '|')
    return x


class defaultkeydict(collections.defaultdict):
    """Like defaultdict, but the default_factory is a function of the key.
    >>> d = defaultkeydict(len); d['four']
    4
    """

    def __missing__(self, key):
        self[key] = result = self.default_factory(key)
        return result


class hashabledict(dict):
    """Allows hashing by representing a dictionary as tuple of key:value pairs.
    May cause problems as the hash value may change during runtime."""

    def __hash__(self):
        return 1


# ______________________________________________________________________________
# Queues: Stack, FIFOQueue, PriorityQueue
# Stack and FIFOQueue are implemented as list and collection.deque
# PriorityQueue is implemented here


class PriorityQueue:
    """A Queue in which the minimum (or maximum) element (as determined by f and
    order) is returned first.
    If order is 'min', the item with minimum f(x) is
    returned first; if order is 'max', then it is the item with maximum f(x).
    Also supports dict-like lookup."""

    def __init__(self, order='min', f=lambda x: x):
        self.heap = []
        if order == 'min':
            self.f = f
        elif order == 'max':  # now item with max f(x)
            self.f = lambda x: -f(x)  # will be popped first
        else:
            raise ValueError("Order must be either 'min' or 'max'.")

    def append(self, item):
        """Insert item at its correct position."""
        heapq.heappush(self.heap, (self.f(item), item))

    def extend(self, items):
        """Insert each item in items at its correct position."""
        for item in items:
            self.append(item)

    def pop(self):
        """Pop and return the item (with min or max f(x) value)
        depending on the order."""
        if self.heap:
            return heapq.heappop(self.heap)[1]
        else:
            raise Exception('Trying to pop from empty PriorityQueue.')

    def __len__(self):
        """Return current capacity of PriorityQueue."""
        return len(self.heap)

    def __contains__(self, key):
        """Return True if the key is in PriorityQueue."""
        return any([item == key for _, item in self.heap])

    def __getitem__(self, key):
        """Returns the first value associated with key in PriorityQueue.
        Raises KeyError if key is not present."""
        for value, item in self.heap:
            if item == key:
                return value
        raise KeyError(str(key) + " is not in the priority queue")

    def __delitem__(self, key):
        """Delete the first occurrence of key."""
        try:
            del self.heap[[item == key for _, item in self.heap].index(True)]
        except ValueError:
            raise KeyError(str(key) + " is not in the priority queue")
        heapq.heapify(self.heap)


# ______________________________________________________________________________
# Useful Shorthands


class Bool(int):
    """Just like `bool`, except values display as 'T' and 'F' instead of 'True' and 'False'."""
    __str__ = __repr__ = lambda self: 'T' if self else 'F'


T = Bool(True)
F = Bool(False)


'''
######################################################################################
######################################################################################
######################################################################################
                                    Logic.py
######################################################################################
######################################################################################
######################################################################################
'''
"""
Representations and Inference for Logic. (Chapters 7-9, 12)
Covers both Propositional and First-Order Logic. First we have four
important data types:
    KB            Abstract class holds a knowledge base of logical expressions
    KB_Agent      Abstract class subclasses agents.Agent
    Expr          A logical expression, imported from utils.py
    substitution  Implemented as a dictionary of var:value pairs, {x:1, y:x}
Be careful: some functions take an Expr as argument, and some take a KB.
Logical expressions can be created with Expr or expr, imported from utils, TODO
or with expr, which adds the capability to write a string that uses
the connectives ==>, <==, <=>, or <=/=>. But be careful: these have the
operator precedence of commas; you may need to add parens to make precedence work.
See logic.ipynb for examples.
Then we implement various functions for doing logical inference:
    pl_true          Evaluate a propositional logical sentence in a model
    tt_entails       Say if a statement is entailed by a KB
    pl_resolution    Do resolution on propositional sentences
    dpll_satisfiable See if a propositional sentence is satisfiable
    WalkSAT          Try to find a solution for a set of clauses
And a few other functions:
    to_cnf           Convert to conjunctive normal form
    unify            Do unification of two FOL sentences
    diff, simp       Symbolic differentiation and simplification
"""

import heapq
import itertools
import random
from collections import defaultdict, Counter

#from utils import unique, first, probability, isnumber, issequence, Expr, expr, subexpressions, extend, remove_all


class KB:
    """A knowledge base to which you can tell and ask sentences.
    To create a KB, first subclass this class and implement
    tell, ask_generator, and retract. Why ask_generator instead of ask?
    The book is a bit vague on what ask means --
    For a Propositional Logic KB, ask(P & Q) returns True or False, but for an
    FOL KB, something like ask(Brother(x, y)) might return many substitutions
    such as {x: Cain, y: Abel}, {x: Abel, y: Cain}, {x: George, y: Jeb}, etc.
    So ask_generator generates these one at a time, and ask either returns the
    first one or returns False."""

    def __init__(self, sentence=None):
        if sentence:
            self.tell(sentence)

    def tell(self, sentence):
        """Add the sentence to the KB."""
        raise NotImplementedError

    def ask(self, query):
        """Return a substitution that makes the query true, or, failing that, return False."""
        return first(self.ask_generator(query), default=False)

    def ask_generator(self, query):
        """Yield all the substitutions that make query true."""
        raise NotImplementedError

    def retract(self, sentence):
        """Remove sentence from the KB."""
        raise NotImplementedError


class PropKB(KB):
    """A KB for propositional logic. Inefficient, with no indexing."""

    def __init__(self, sentence=None):
        super().__init__(sentence)
        self.clauses = []

    def tell(self, sentence):
        """Add the sentence's clauses to the KB."""
        print('Add ', sentence)
        self.clauses.extend(conjuncts(to_cnf(sentence)))

    def ask_generator(self, query):
        """Yield the empty substitution {} if KB entails query; else no results."""
        if tt_entails(Expr('&', *self.clauses), query):
            yield {}

    def ask_if_true(self, query):
        """Return True if the KB entails query, else return False."""
        for _ in self.ask_generator(query):
            return True
        return False

    def retract(self, sentence):
        """Remove the sentence's clauses from the KB."""
        for c in conjuncts(to_cnf(sentence)):
            if c in self.clauses:
                self.clauses.remove(c)


# ______________________________________________________________________________


def KBAgentProgram(kb):
    """
    [Figure 7.1]
    A generic logical knowledge-based agent program.
    """
    steps = itertools.count()

    def program(percept):
        t = next(steps)
        kb.tell(make_percept_sentence(percept, t))
        action = kb.ask(make_action_query(t))
        kb.tell(make_action_sentence(action, t))
        return action

    def make_percept_sentence(percept, t):
        return Expr('Percept')(percept, t)

    def make_action_query(t):
        return expr('ShouldDo(action, {})'.format(t))

    def make_action_sentence(action, t):
        return Expr('Did')(action[expr('action')], t)

    return program


def is_symbol(s):
    """A string s is a symbol if it starts with an alphabetic char.
    >>> is_symbol('R2D2')
    True
    """
    return isinstance(s, str) and s[:1].isalpha()


def is_var_symbol(s):
    """A logic variable symbol is an initial-lowercase string.
    >>> is_var_symbol('EXE')
    False
    """
    return is_symbol(s) and s[0].islower()


def is_prop_symbol(s):
    """A proposition logic symbol is an initial-uppercase string.
    >>> is_prop_symbol('exe')
    False
    """
    return is_symbol(s) and s[0].isupper()


def variables(s):
    """Return a set of the variables in expression s.
    >>> variables(expr('F(x, x) & G(x, y) & H(y, z) & R(A, z, 2)')) == {x, y, z}
    True
    """
    return {x for x in subexpressions(s) if is_variable(x)}

def is_variable(x):
    """A variable is an Expr with no args and a lowercase symbol as the op."""
    return isinstance(x, Expr) and not x.args and x.op[0].islower()

def is_definite_clause(s):
    """Returns True for exprs s of the form A & B & ... & C ==> D,
    where all literals are positive. In clause form, this is
    ~A | ~B | ... | ~C | D, where exactly one clause is positive.
    >>> is_definite_clause(expr('Farmer(Mac)'))
    True
    """
    if is_symbol(s.op):
        return True
    elif s.op == '==>':
        antecedent, consequent = s.args
        return is_symbol(consequent.op) and all(is_symbol(arg.op) for arg in conjuncts(antecedent))
    else:
        return False


def parse_definite_clause(s):
    """Return the antecedents and the consequent of a definite clause."""
    assert is_definite_clause(s)
    if is_symbol(s.op):
        return [], s
    else:
        antecedent, consequent = s.args
        return conjuncts(antecedent), consequent


# Useful constant Exprs used in examples and code:
A, B, C, D, E, F, G, P, Q, a, x, y, z, u = map(Expr, 'ABCDEFGPQaxyzu')


# ______________________________________________________________________________


def tt_entails(kb, alpha):
    """
    [Figure 7.10]
    Does kb entail the sentence alpha? Use truth tables. For propositional
    kb's and sentences. Note that the 'kb' should be an Expr which is a
    conjunction of clauses.
    >>> tt_entails(expr('P & Q'), expr('Q'))
    True
    """
    assert not variables(alpha)
    symbols = list(prop_symbols(kb & alpha))
    return tt_check_all(kb, alpha, symbols, {})


def tt_check_all(kb, alpha, symbols, model):
    """Auxiliary routine to implement tt_entails."""
    if not symbols:
        if pl_true(kb, model):
            result = pl_true(alpha, model)
            assert result in (True, False)
            return result
        else:
            return True
    else:
        P, rest = symbols[0], symbols[1:]
        return (tt_check_all(kb, alpha, rest, extend(model, P, True)) and
                tt_check_all(kb, alpha, rest, extend(model, P, False)))


def prop_symbols(x):
    """Return the set of all propositional symbols in x."""
    if not isinstance(x, Expr):
        return set()
    elif is_prop_symbol(x.op):
        return {x}
    else:
        return {symbol for arg in x.args for symbol in prop_symbols(arg)}


def constant_symbols(x):
    """Return the set of all constant symbols in x."""
    if not isinstance(x, Expr):
        return set()
    elif is_prop_symbol(x.op) and not x.args:
        return {x}
    else:
        return {symbol for arg in x.args for symbol in constant_symbols(arg)}


def predicate_symbols(x):
    """Return a set of (symbol_name, arity) in x.
    All symbols (even functional) with arity > 0 are considered."""
    if not isinstance(x, Expr) or not x.args:
        return set()
    pred_set = {(x.op, len(x.args))} if is_prop_symbol(x.op) else set()
    pred_set.update({symbol for arg in x.args for symbol in predicate_symbols(arg)})
    return pred_set


def tt_true(s):
    """Is a propositional sentence a tautology?
    >>> tt_true('P | ~P')
    True
    """
    s = expr(s)
    return tt_entails(True, s)


def pl_true(exp, model={}):
    """Return True if the propositional logic expression is true in the model,
    and False if it is false. If the model does not specify the value for
    every proposition, this may return None to indicate 'not obvious';
    this may happen even when the expression is tautological.
    >>> pl_true(P, {}) is None
    True
    """
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


# ______________________________________________________________________________

# Convert to Conjunctive Normal Form (CNF)


def to_cnf(s):
    """
    [Page 253]
    Convert a propositional logical sentence to conjunctive normal form.
    That is, to the form ((A | ~B | ...) & (B | C | ...) & ...)
    >>> to_cnf('~(B | C)')
    (~B & ~C)
    """
    s = expr(s)
    if isinstance(s, str):
        s = expr(s)
    s = eliminate_implications(s)  # Steps 1, 2 from p. 253
    s = move_not_inwards(s)  # Step 3
    return distribute_and_over_or(s)  # Step 4


def eliminate_implications(s):
    """Change implications into equivalent form with only &, |, and ~ as logical operators."""
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
    """Rewrite sentence s by moving negation sign inward.
    >>> move_not_inwards(~(A | B))
    (~A & ~B)
    """
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
    """Given a sentence s consisting of conjunctions and disjunctions
    of literals, return an equivalent sentence in CNF.
    >>> distribute_and_over_or((A & B) | C)
    ((A | C) & (B | C))
    """
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


def associate(op, args):
    """Given an associative op, return an expression with the same
    meaning as Expr(op, *args), but flattened -- that is, with nested
    instances of the same op promoted to the top level.
    >>> associate('&', [(A&B),(B|C),(B&C)])
    (A & B & (B | C) & B & C)
    >>> associate('|', [A|(B|(C|(A&B)))])
    (A | B | C | (A & B))
    """
    args = dissociate(op, args)
    if len(args) == 0:
        return _op_identity[op]
    elif len(args) == 1:
        return args[0]
    else:
        return Expr(op, *args)


_op_identity = {'&': True, '|': False, '+': 0, '*': 1}


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


def conjuncts(s):
    """Return a list of the conjuncts in the sentence s.
    >>> conjuncts(A & B)
    [A, B]
    >>> conjuncts(A | B)
    [(A | B)]
    """
    return dissociate('&', [s])


def disjuncts(s):
    """Return a list of the disjuncts in the sentence s.
    >>> disjuncts(A | B)
    [A, B]
    >>> disjuncts(A & B)
    [(A & B)]
    """
    return dissociate('|', [s])


# ______________________________________________________________________________


def pl_resolution(kb, alpha):
    """
    [Figure 7.12]
    Propositional-logic resolution: say if alpha follows from KB.
    >>> pl_resolution(horn_clauses_KB, A)
    True
    """
    clauses = kb.clauses + conjuncts(to_cnf(~alpha))
    new = set()
    while True:
        n = len(clauses)
        pairs = [(clauses[i], clauses[j])
                 for i in range(n) for j in range(i + 1, n)]
        for (ci, cj) in pairs:
            resolvents = pl_resolve(ci, cj)
            if False in resolvents:
                return True
            new = new.union(set(resolvents))
        if new.issubset(set(clauses)):
            return False
        for c in new:
            if c not in clauses:
                clauses.append(c)


def pl_resolve(ci, cj):
    """Return all clauses that can be obtained by resolving clauses ci and cj."""
    clauses = []
    for di in disjuncts(ci):
        for dj in disjuncts(cj):
            if di == ~dj or ~di == dj:
                clauses.append(associate('|', unique(remove_all(di, disjuncts(ci)) + remove_all(dj, disjuncts(cj)))))
    return clauses


# ______________________________________________________________________________


class PropDefiniteKB(PropKB):
    """A KB of propositional definite clauses."""

    def tell(self, sentence):
        """Add a definite clause to this KB."""
        assert is_definite_clause(sentence), "Must be definite clause"
        self.clauses.append(sentence)

    def ask_generator(self, query):
        """Yield the empty substitution if KB implies query; else nothing."""
        if pl_fc_entails(self.clauses, query):
            yield {}

    def retract(self, sentence):
        self.clauses.remove(sentence)

    def clauses_with_premise(self, p):
        """Return a list of the clauses in KB that have p in their premise.
        This could be cached away for O(1) speed, but we'll recompute it."""
        return [c for c in self.clauses if c.op == '==>' and p in conjuncts(c.args[0])]


def pl_fc_entails(kb, q):
    """
    [Figure 7.15]
    Use forward chaining to see if a PropDefiniteKB entails symbol q.
    >>> pl_fc_entails(horn_clauses_KB, expr('Q'))
    True
    """
    count = {c: len(conjuncts(c.args[0])) for c in kb.clauses if c.op == '==>'}
    inferred = defaultdict(bool)
    agenda = [s for s in kb.clauses if is_prop_symbol(s.op)]
    while agenda:
        p = agenda.pop()
        if p == q:
            return True
        if not inferred[p]:
            inferred[p] = True
            for c in kb.clauses_with_premise(p):
                count[c] -= 1
                if count[c] == 0:
                    agenda.append(c.args[1])
    return False



# ______________________________________________________________________________
# Heuristics for SAT Solvers


def no_branching_heuristic(symbols, clauses):
    return first(symbols), True


def min_clauses(clauses):
    min_len = min(map(lambda c: len(c.args), clauses), default=2)
    return filter(lambda c: len(c.args) == (min_len if min_len > 1 else 2), clauses)


def moms(symbols, clauses):
    """
    MOMS (Maximum Occurrence in clauses of Minimum Size) heuristic
    Returns the literal with the most occurrences in all clauses of minimum size
    """
    scores = Counter(l for c in min_clauses(clauses) for l in prop_symbols(c))
    return max(symbols, key=lambda symbol: scores[symbol]), True


def momsf(symbols, clauses, k=0):
    """
    MOMS alternative heuristic
    If f(x) the number of occurrences of the variable x in clauses with minimum size,
    we choose the variable maximizing [f(x) + f(-x)] * 2^k + f(x) * f(-x)
    Returns x if f(x) >= f(-x) otherwise -x
    """
    scores = Counter(l for c in min_clauses(clauses) for l in disjuncts(c))
    P = max(symbols,
            key=lambda symbol: (scores[symbol] + scores[~symbol]) * pow(2, k) + scores[symbol] * scores[~symbol])
    return P, True if scores[P] >= scores[~P] else False


def posit(symbols, clauses):
    """
    Freeman's POSIT version of MOMs
    Counts the positive x and negative x for each variable x in clauses with minimum size
    Returns x if f(x) >= f(-x) otherwise -x
    """
    scores = Counter(l for c in min_clauses(clauses) for l in disjuncts(c))
    P = max(symbols, key=lambda symbol: scores[symbol] + scores[~symbol])
    return P, True if scores[P] >= scores[~P] else False


def zm(symbols, clauses):
    """
    Zabih and McAllester's version of MOMs
    Counts the negative occurrences only of each variable x in clauses with minimum size
    """
    scores = Counter(l for c in min_clauses(clauses) for l in disjuncts(c) if l.op == '~')
    return max(symbols, key=lambda symbol: scores[~symbol]), True


def dlis(symbols, clauses):
    """
    DLIS (Dynamic Largest Individual Sum) heuristic
    Choose the variable and value that satisfies the maximum number of unsatisfied clauses
    Like DLCS but we only consider the literal (thus Cp and Cn are individual)
    """
    scores = Counter(l for c in clauses for l in disjuncts(c))
    P = max(symbols, key=lambda symbol: scores[symbol])
    return P, True if scores[P] >= scores[~P] else False


def dlcs(symbols, clauses):
    """
    DLCS (Dynamic Largest Combined Sum) heuristic
    Cp the number of clauses containing literal x
    Cn the number of clauses containing literal -x
    Here we select the variable maximizing Cp + Cn
    Returns x if Cp >= Cn otherwise -x
    """
    scores = Counter(l for c in clauses for l in disjuncts(c))
    P = max(symbols, key=lambda symbol: scores[symbol] + scores[~symbol])
    return P, True if scores[P] >= scores[~P] else False


def jw(symbols, clauses):
    """
    Jeroslow-Wang heuristic
    For each literal compute J(l) = \sum{l in clause c} 2^{-|c|}
    Return the literal maximizing J
    """
    scores = Counter()
    for c in clauses:
        for l in prop_symbols(c):
            scores[l] += pow(2, -len(c.args))
    return max(symbols, key=lambda symbol: scores[symbol]), True


def jw2(symbols, clauses):
    """
    Two Sided Jeroslow-Wang heuristic
    Compute J(l) also counts the negation of l = J(x) + J(-x)
    Returns x if J(x) >= J(-x) otherwise -x
    """
    scores = Counter()
    for c in clauses:
        for l in disjuncts(c):
            scores[l] += pow(2, -len(c.args))
    P = max(symbols, key=lambda symbol: scores[symbol] + scores[~symbol])
    return P, True if scores[P] >= scores[~P] else False


# ______________________________________________________________________________
# DPLL-Satisfiable [Figure 7.17]


def dpll_satisfiable(s, branching_heuristic=no_branching_heuristic):
    """Check satisfiability of a propositional sentence.
    This differs from the book code in two ways: (1) it returns a model
    rather than True when it succeeds; this is more useful. (2) The
    function find_pure_symbol is passed a list of unknown clauses, rather
    than a list of all clauses and the model; this is more efficient.
    >>> dpll_satisfiable(A |'<=>'| B) == {A: True, B: True}
    True
    """
    return dpll(conjuncts(to_cnf(s)), prop_symbols(s), {}, branching_heuristic)


def dpll(clauses, symbols, model, branching_heuristic=no_branching_heuristic):
    """See if the clauses are true in a partial model."""
    unknown_clauses = []  # clauses with an unknown truth value
    for c in clauses:
        val = pl_true(c, model)
        if val is False:
            return False
        if val is None:
            unknown_clauses.append(c)
    if not unknown_clauses:
        return model
    P, value = find_pure_symbol(symbols, unknown_clauses)
    if P:
        return dpll(clauses, remove_all(P, symbols), extend(model, P, value), branching_heuristic)
    P, value = find_unit_clause(clauses, model)
    if P:
        return dpll(clauses, remove_all(P, symbols), extend(model, P, value), branching_heuristic)
    P, value = branching_heuristic(symbols, unknown_clauses)
    return (dpll(clauses, remove_all(P, symbols), extend(model, P, value), branching_heuristic) or
            dpll(clauses, remove_all(P, symbols), extend(model, P, not value), branching_heuristic))


def find_pure_symbol(symbols, clauses):
    """Find a symbol and its value if it appears only as a positive literal
    (or only as a negative) in clauses.
    >>> find_pure_symbol([A, B, C], [A|~B,~B|~C,C|A])
    (A, True)
    """
    for s in symbols:
        found_pos, found_neg = False, False
        for c in clauses:
            if not found_pos and s in disjuncts(c):
                found_pos = True
            if not found_neg and ~s in disjuncts(c):
                found_neg = True
        if found_pos != found_neg:
            return s, found_pos
    return None, None


def find_unit_clause(clauses, model):
    """Find a forced assignment if possible from a clause with only 1
    variable not bound in the model.
    >>> find_unit_clause([A|B|C, B|~C, ~A|~B], {A:True})
    (B, False)
    """
    for clause in clauses:
        P, value = unit_clause_assign(clause, model)
        if P:
            return P, value
    return None, None


def unit_clause_assign(clause, model):
    """Return a single variable/value pair that makes clause true in
    the model, if possible.
    >>> unit_clause_assign(A|B|C, {A:True})
    (None, None)
    >>> unit_clause_assign(B|~C, {A:True})
    (None, None)
    >>> unit_clause_assign(~A|~B, {A:True})
    (B, False)
    """
    P, value = None, None
    for literal in disjuncts(clause):
        sym, positive = inspect_literal(literal)
        if sym in model:
            if model[sym] == positive:
                return None, None  # clause already True
        elif P:
            return None, None  # more than 1 unbound variable
        else:
            P, value = sym, positive
    return P, value


def inspect_literal(literal):
    """The symbol in this literal, and the value it should take to
    make the literal true.
    >>> inspect_literal(P)
    (P, True)
    >>> inspect_literal(~P)
    (P, False)
    """
    if literal.op == '~':
        return literal.args[0], False
    else:
        return literal, True




'''
######################################################################################
######################################################################################
######################################################################################
                                    Our Code
######################################################################################
######################################################################################
######################################################################################
'''

ids = ['311153845', '308570928']


def neighbors(row, col, rows_num, col_num):
    neighbors_list = []
    for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        if (0 <= d_row + row < rows_num) and (0 <= d_col + col < col_num >= 0):
            neighbors_list.append([d_row + row, d_col + col])
    return neighbors_list


class cnf_problem:
    def __init__(self, problem):
        self.var_pool = IDPool()
        self.police_num = problem["police"]
        self.medics_num = problem["medics"]
        self.observations = problem["observations"]
        self.total_time = len(self.observations)
        self.row_num = len(self.observations[0])
        self.col_num = len(self.observations[0][0])
        self.queries = problem["queries"]
        self.states = {'H', 'S', 'I', 'Q', 'U'}
        self.cnf = CNF()
        self.unknown_list = []
        self.assumptions = self.make_assumptions()
        self.var_dict = self.make_var_dict()


    def make_var_dict(self):
        var_dict = {}
        for time in range(self.total_time):
            for row in range(self.row_num):
                for col in range(self.col_num):
                    for state in self.states:
                        var_dict[state, time, (row, col)] = self.var_pool.id(f'{state}, {time}, ({row},{col})')
                    var_dict['P', time, (row, col)] = self.var_pool.id(f'P, {time}, ({row},{col})')
                    var_dict['M', time, (row, col)] = self.var_pool.id(f'M, {time}, ({row},{col})')
        return var_dict

    def make_assumptions(self):
        assumptions = []
        for time, observation in enumerate(self.observations):
            for row in range(self.row_num):
                for col in range(self.col_num):
                    state = observation[row][col]
                    if state != '?':
                        assumptions += [self.var_pool.id(f'{state}, {time}, ({row},{col})')]
                    if time == 0 and state == '?':
                        assumptions += [-self.var_pool.id(f'Q, {time}, ({row},{col})')]
                        assumptions += [-self.var_pool.id(f'I, {time}, ({row},{col})')]
                    if state == '?':
                        self.unknown_list.append(((row, col), time))
        return assumptions

    def make_formula(self):

        for time in range(self.total_time):

            # upper limit for police and medics
            self.cnf.extend(CardEnc.atmost([self.var_dict['P', time, (row, col)]
                                            for row in range(self.row_num) for col in range(self.col_num)],
                                           bound=self.police_num, vpool=self.var_pool))
            self.cnf.extend(CardEnc.atmost([self.var_dict['M', time, (row, col)]
                                            for row in range(self.row_num) for col in range(self.col_num)],
                                           bound=self.medics_num, vpool=self.var_pool))
            ''' 
                Enforce the use of maximum possible police actions in every turn:
                Use aima's "to_cnf" function which takes a logic sentence as a string and outputs the equivalent 
                cnf expression.
                Use our own "logic_to_cnf" which wraps "to_cnf" and parse its' expr output in the PySAT format.
                For the logic part we use a flag marked by 'X(num_of_police),time,(-1,-1))' which acts as a middle
                variable in order to simplify the logic.
                For every possible max number of police (between 0 to self.police_num) we enforce the rule which says:
                if there's at one combination of 'police_num_pos' tile which are all sick, the same number of police
                actions must occur. Since it's done for every possible number, it acts as a lower bound on the number
                of police used. The maximum bound is already being enforced by PySAT own 'atmost' function.
                
                An example for the rule we add when enforcing use of 2 police when possible:
                (A & B) | (B & C) | (A & C) ==> X2
                &
                X2 ==> (PA & PB) | (PB & PC) | (PA & PC)
                
                While A,B and C represent 3 sick tiles (their value is true only when the tile is sick)
                PA, PB, PC represent 3 possible police actions to enforce on tiles A,B and C
                X2 is the flag which is assigned true whenever there are at least 2 sick tiles                       
            '''
            possible_tiles = [(t_row, t_col) for t_row in range(self.row_num) for t_col in range(self.col_num)
                              if self.observations[time][t_row][t_col] == 'S'
                              or self.observations[time][t_row][t_col] == '?'
                              if time + 1 == self.total_time
                              or self.observations[time+1][t_row][t_col] == 'Q'
                              or self.observations[time+1][t_row][t_col] == '?']

            for police_num_pos in range(1, self.police_num + 1):
                police_combinations = list(combinations(possible_tiles, police_num_pos))
                if police_combinations:
                    sick_list = []
                    police_list = []
                    for i, comb in enumerate(police_combinations):
                        sick_clause = ''
                        police_clause = ''
                        for j, (r, c) in enumerate(comb):
                            if j != 0:
                                sick_clause += " & "
                                police_clause += " & "
                            sick_clause += "x" + str(self.var_dict['S', time, (r, c)])
                            police_clause += "x" + str(self.var_dict['P', time, (r, c)])
                        sick_comb_key = self.var_pool.id(sick_clause + ',' + str(time) + ', S')
                        police_comb_key = self.var_pool.id(sick_clause + ',' + str(time) + ', P')
                        sick_clause += ' ==> x' + str(sick_comb_key)
                        police_clause = "x" + str(police_comb_key) + " ==> " + police_clause
                        self.cnf.extend(logic_to_cnf(sick_clause))
                        self.cnf.extend(logic_to_cnf(police_clause))
                        sick_list.append(sick_comb_key)
                        police_list.append(police_comb_key)
                    total_sick_clause = ' | '.join(['x' + str(clause_id) for clause_id in sick_list]) + \
                                        ' ==> x' + str(self.var_pool.id(f'X{police_num_pos}, {time}, (-1,-1)'))
                    total_police_clause = "x" + str(self.var_pool.id(f'X{police_num_pos}, {time}, (-1,-1)')) + " ==> " \
                                          + ' | '.join(['x' + str(clause_id) for clause_id in police_list])
                    self.cnf.extend(logic_to_cnf(total_sick_clause))
                    self.cnf.extend(logic_to_cnf(total_police_clause))

            # Do the same for medics
            possible_tiles = [(t_row, t_col) for t_row in range(self.row_num) for t_col in range(self.col_num)
                              if self.observations[time][t_row][t_col] == 'H'
                              or self.observations[time][t_row][t_col] == '?'
                              if time + 1 == self.total_time
                              or self.observations[time + 1][t_row][t_col] == 'I'
                              or self.observations[time + 1][t_row][t_col] == '?']

            for medic_num_pos in range(1, self.medics_num + 1):
                medic_combinations = list(combinations(possible_tiles, medic_num_pos))
                if medic_combinations:
                    healthy_list = []
                    medic_list = []
                    for i, comb in enumerate(medic_combinations):
                        healthy_clause = ''
                        medic_clause = ''
                        for j, (r, c) in enumerate(comb):
                            if j != 0:
                                healthy_clause += " & "
                                medic_clause += " & "
                            healthy_clause += "x" + str(self.var_dict['H', time, (r, c)])
                            medic_clause += "x" + str(self.var_dict['M', time, (r, c)])
                        healthy_comb_key = self.var_pool.id(healthy_clause + ',' + str(time) + ', H')
                        medic_comb_key = self.var_pool.id(healthy_clause + ',' + str(time) + ', M')
                        healthy_clause += ' ==> x' + str(healthy_comb_key)
                        medic_clause = "x" + str(medic_comb_key) + " ==> " + medic_clause
                        self.cnf.extend(logic_to_cnf(healthy_clause))
                        self.cnf.extend(logic_to_cnf(medic_clause))
                        healthy_list.append(healthy_comb_key)
                        medic_list.append(medic_comb_key)
                    total_healthy_clause = ' | '.join(['x'+str(clause_id) for clause_id in healthy_list]) + \
                                           ' ==> x' + str(self.var_pool.id(f'Y{medic_num_pos}, {time}, (-1,-1)'))
                    total_medic_clause = "x" + str(self.var_pool.id(f'Y{medic_num_pos}, {time}, (-1,-1)')) + " ==> "\
                                         + ' | '.join(['x' + str(clause_id) for clause_id in medic_list])
                    self.cnf.extend(logic_to_cnf(total_healthy_clause))
                    self.cnf.extend(logic_to_cnf(total_medic_clause))

            # Add all the rest of the game logic rules
            for row in range(self.row_num):
                for col in range(self.col_num):
                    # One state per tile encoding
                    self.cnf.extend(CardEnc.equals([self.var_dict[state, time, (row, col)] for state in self.states],
                                                   vpool=self.var_pool))

                    # add actions preconditions encoding Action ==> Precondition
                    # a0 => pre0
                    self.logical_imply([self.var_dict['M', time, (row, col)]], [self.var_dict['H', time, (row, col)]])
                    self.logical_imply([self.var_dict['P', time, (row, col)]], [self.var_dict['S', time, (row, col)]])

                    if time < 2 and time + 1 < self.total_time:
                        # s(x) & ~p(x) & time < 2 => s(x+1)
                        self.logical_imply([self.var_dict['S', time, (row, col)],
                                            -self.var_dict['P', time, (row, col)]],
                                           [self.var_dict['S', time + 1, (row, col)]])
                    if time == 0:
                        self.cnf.append([-self.var_dict['Q', time, (row, col)]])
                        self.cnf.append([-self.var_dict['I', time, (row, col)]])
                    if time > 0:
                        all_neighbors = neighbors(row, col, self.row_num, self.col_num)
                        for n_row, n_col in all_neighbors:
                            # sick_neighbor0 & not police on neighbor0 & tile healthy0 & not medics on healthy0 => s1
                            self.logical_imply(
                                [self.var_dict['S', time - 1, (n_row, n_col)],
                                 -self.var_dict['P', time - 1, (n_row, n_col)],
                                 self.var_dict['H', time - 1, (row, col)], -self.var_dict['M', time - 1, (row, col)]],
                                [self.var_dict['S', time, (row, col)]])

                        # s1 & h0 => at least one of neighbors must be (s0 & ~p0)
                        clause = f"x{self.var_dict['S', time, (row, col)]} & " \
                                 f"x{self.var_dict['H', time - 1, (row, col)]} ==> x" + \
                                 ' | x'.join([' & ~x'.join([str(self.var_dict['S', time - 1, (n_row, n_col)]),
                                                            str(self.var_dict['P', time - 1, (n_row, n_col)])])
                                              for (n_row, n_col) in all_neighbors])
                        self.cnf.extend(logic_to_cnf(clause))

                        # h(x-1) & ~m(x-1) & all_neighbors are (~s(x-1) | p(x-1)) => hx
                        clause = f"x{self.var_dict['H', time - 1, (row, col)]} & " \
                                 f"~x{self.var_dict['M', time - 1, (row, col)]} & (~x" + \
                                 ' & (~x'.join([' | x'.join([str(self.var_dict['S', time - 1, (n_row, n_col)]),
                                                            str(self.var_dict['P', time - 1, (n_row, n_col)])])+')'
                                              for (n_row, n_col) in all_neighbors]) + " ==> " + \
                                 f"x{self.var_dict['H', time, (row, col)]}"
                        self.cnf.extend(logic_to_cnf(clause))

                        # s1 & h0 => not medics on healthy0
                        self.logical_imply([self.var_dict['S', time, (row, col)],
                                            self.var_dict['H', time - 1, (row, col)]],
                                           [-self.var_dict['M', time - 1, (row, col)]])

                        # s1 => s0 | h0
                        self.logical_imply_or([self.var_dict['S', time, (row, col)]],
                                              [self.var_dict['S', time - 1, (row, col)],
                                               self.var_dict['H', time - 1, (row, col)]])
                        # i1 => i0 | h0
                        self.logical_imply_or([self.var_dict['I', time, (row, col)]],
                                              [self.var_dict['I', time - 1, (row, col)],
                                               self.var_dict['H', time - 1, (row, col)]])
                        # q1 => q0 | s0
                        self.logical_imply_or([self.var_dict['Q', time, (row, col)]],
                                              [self.var_dict['Q', time - 1, (row, col)],
                                               self.var_dict['S', time - 1, (row, col)]])

                    if time+1 < self.total_time:
                        # p0 => q1
                        self.logical_imply([self.var_dict['P', time, (row, col)]],
                                           [self.var_dict['Q', time+1, (row, col)]])
                        # m0 => i1
                        self.logical_imply([self.var_dict['M', time, (row, col)]],
                                           [self.var_dict['I', time + 1, (row, col)]])

                    if time == 1:
                        # p0 & s0 <=> q1
                        self.logical_equivalence(
                            [self.var_dict['P', time - 1, (row, col)], self.var_dict['S', time - 1, (row, col)]],
                            [self.var_dict['Q', time, (row, col)]])
                        # m0 & h0 <=> i1
                        self.logical_equivalence(
                            [self.var_dict['M', time - 1, (row, col)], self.var_dict['H', time - 1, (row, col)]],
                            [self.var_dict['I', time, (row, col)]])

                    if time >= 2:
                        # p0 & s0 <=> q1 & q2
                        self.logical_equivalence(
                            [self.var_dict['P', time - 2, (row, col)], self.var_dict['S', time - 2, (row, col)]],
                            [self.var_dict['Q', time - 1, (row, col)], self.var_dict['Q', time, (row, col)]])
                        # m1 & h1 => i2
                        self.logical_imply(
                            [self.var_dict['M', time - 1, (row, col)], self.var_dict['H', time - 1, (row, col)]],
                            [self.var_dict['I', time, (row, col)]])

                        if time + 1 < self.total_time:
                            # s(x) & ~p(x) & ~(s(x-1) & s(x-2)) => s(x+1)
                            # (A & ~B & ~(C & D)) -> E    <==>    (~A | B | C | E) & (~A | B | D | E)
                            self.cnf.extend([[-self.var_dict['S', time, (row, col)],      #
                                              self.var_dict['P', time, (row, col)],       #
                                              self.var_dict['S', time - 1, (row, col)],   #
                                              self.var_dict['S', time + 1, (row, col)]],  #  (~A | B | C | E)
                                                                                          #  &
                                             [-self.var_dict['S', time, (row, col)],      #  (~A | B | D | E)
                                              self.var_dict['P', time, (row, col)],       #
                                              self.var_dict['S', time - 2, (row, col)],   #
                                              self.var_dict['S', time + 1, (row, col)]]]) #

                    if time >= 3:
                        # s0 & s1 & s2 => h3
                        self.logical_imply(
                            [self.var_dict['S', time - 3, (row, col)], self.var_dict['S', time - 2, (row, col)],
                             self.var_dict['S', time - 1, (row, col)]], [self.var_dict['H', time, (row, col)]])
                        # q1 & q2 => h3
                        self.logical_imply(
                            [self.var_dict['Q', time - 2, (row, col)], self.var_dict['Q', time - 1, (row, col)]],
                            [self.var_dict['H', time, (row, col)]])

                    if time > 3:
                        # s1 & s2 & s3 => h4
                        self.logical_imply(
                            [self.var_dict['S', time - 3, (row, col)],
                             self.var_dict['S', time - 2, (row, col)],
                             self.var_dict['S', time - 1, (row, col)]], [self.var_dict['H', time, (row, col)]])
                        # s1 & s2 & s3 => ~s0
                        self.logical_imply(
                            [self.var_dict['S', time - 3, (row, col)],
                             self.var_dict['S', time - 2, (row, col)],
                             self.var_dict['S', time - 1, (row, col)]], [-self.var_dict['S', time - 4, (row, col)]])

                    if time + 1 < self.total_time:
                        # u0 <=> u1
                        self.logical_equivalence([self.var_dict['U', time, (row, col)]],
                                                 [self.var_dict['U', time + 1, (row, col)]])
                        # i0 => i1
                        self.logical_imply([self.var_dict['I', time, (row, col)]],
                                           [self.var_dict['I', time + 1, (row, col)]])


    def logical_imply(self, and_vars, implying_and_vars):
        # A&B&C ==> D&E&F
        for var in implying_and_vars:
            self.cnf.extend([[-a_var for a_var in and_vars] + [var]])

    def logical_equivalence(self, left_vars, right_vars):
        # A&B&C <=> D&E&F
        self.logical_imply(left_vars, right_vars)
        self.logical_imply(right_vars, left_vars)

    def logical_imply_or(self, and_vars, implying_or_vars):
        # A&B&C ==> D|E|F
        self.cnf.extend([[-a_var for a_var in and_vars] + [var for var in implying_or_vars]])

    def solve(self):
        res = {}
        with Minisat22(bootstrap_with=self.cnf) as sat_solver:
            kb_only = sat_solver.solve(self.assumptions)
            #print('KB only: ', kb_only)
            for query in self.queries:
                (row, col), time, state = query
                alpha = self.var_pool.id(f'{state}, {time}, ({row},{col})')
                kb_and_not_alpha = sat_solver.solve(self.assumptions + [-alpha])
                kb_and_alpha = sat_solver.solve(self.assumptions + [alpha])
                # True <==> kb with alpha is satisfiable, and with ~alpha it's not satisfiable
                if kb_and_alpha is True and kb_and_not_alpha is False:
                    res[query] = "T"
                # False <==> kb with alpha is not satisfiable, and with ~alpha *it is* satisfiable
                elif kb_and_alpha is False and kb_and_not_alpha is True:
                    res[query] = "F"
                # ? <==> Both kb with alpha and kb with ~alpha are satisfiable
                else:
                    res[query] = "?"
        return res

    def print(self):
        print(self.var_dict)
        print(self.cnf.clauses)
        print(len(self.cnf.clauses))

    def print_predicted(self):
        #
        printed_matrix = [[list(cell_val) for cell_val in row] for row in self.observations]

        for (row, col), time in self.unknown_list:
            pass
            res = {}
            queries = [((row, col), time, state) for state in self.states]
            # print(queries)
            with Minisat22(bootstrap_with=self.cnf) as sat_solver:
                kb_only = sat_solver.solve(self.assumptions)
                # print('KB only: ', kb_only)
                for query in queries:
                    (row, col), time, state = query
                    alpha = self.var_pool.id(f'{state}, {time}, ({row},{col})')
                    kb_and_not_alpha = sat_solver.solve(self.assumptions + [-alpha])
                    kb_and_alpha = sat_solver.solve(self.assumptions + [alpha])
                    # True <==> kb with alpha is satisfiable, and with ~alpha it's not satisfiable
                    if kb_and_alpha is True and kb_and_not_alpha is False:
                        res[query] = "T"
                    # False <==> kb with alpha is not satisfiable, and with ~alpha *it is* satisfiable
                    elif kb_and_alpha is False and kb_and_not_alpha is True:
                        res[query] = "F"
                    # ? <==> Both kb with alpha and kb with ~alpha are satisfiable
                    else:
                        res[query] = "?"

                    if res[query] == 'T':
                        printed_matrix[time][row][col] = f'{state}'
                        break
                    if res[query] == '?':
                        printed_matrix[time][row][col] = f'$'
                        break

        for time in range(self.total_time):
            print(f"Time: {time}")
            for row in range(self.row_num):
                    print(f"{self.observations[time][row]} --------> {printed_matrix[time][row]}")

''' Use the letter 'x' before any integer variable name '''
def logic_to_cnf(input_str):
    cnf_expr = to_cnf(input_str)

    if cnf_expr.op == '&':
       cnf_ready = parse_and(cnf_expr)
    elif cnf_expr.op == '|':
        cnf_ready = [parse_or(cnf_expr)]
    elif cnf_expr.op == '~':
        cnf_ready = [[parse_not(cnf_expr)]]
    else:
        cnf_ready = [[parse_lit(cnf_expr)]]

    return cnf_ready

def parse_and(input_expr):
    and_expr = set()
    for outer in input_expr.args:
        if outer.op == '|':
            and_expr.add(parse_or(outer))
        elif outer.op == '~':
            and_expr.add((parse_not(outer),))
        else:
            and_expr.add((parse_lit(outer),))

    return [[*var] for var in and_expr]

def parse_or(input_expr):
    or_expr = set()
    for inner in input_expr.args:
        lit = inner
        if lit.op == '~':
            lit = parse_not(lit)
        else:
            lit = parse_lit(lit)
        or_expr.add(lit)
    return tuple(or_expr)

def parse_not(input_expr):
    return -1 * int(input_expr.args[0].op.replace('x', ''))

def parse_lit(input_expr):
    return int(input_expr.op.replace('x', ''))

def solve_problem(input):
    problem = cnf_problem(input)
    # problem.solve(quaries)
    problem.make_var_dict()
    problem.make_formula()
    # problem.print()
    #problem.print_predicted()

    return problem.solve()
