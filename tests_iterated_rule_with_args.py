"""
Set of tests on iterated rules which have arguments.
"""
"""
from pointing import *
from usainboltz.grammar import *
from usainboltz.generator import *
from pointed_generator import *

z = Atom()
A = RuleName("A")
cycle_grammar_1 = Grammar({A: Cycle(z*z+z, leq = 2, geq = 1)})
cycle_gen = PointedGenerator(cycle_grammar_1, A, k=1)
res = cycle_gen.sample((1,100))
assert(0 <= len(res.obj) <= 1)
pritn("Success for the first test.")

cycle_grammar_2 = Grammar({A: Cycle(z*z+z, eq = 5)})
cycle_gen = PointedGenerator(cycle_grammar_1, A, k=1)
res = cycle_gen.sample((1,100))
assert(len(res.obj) == 5)
pritn("Success for the second test.")"""