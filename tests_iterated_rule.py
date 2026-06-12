"""
A set of tests on iterated rules: sequence, set, cycle.
"""

from pointing import *
from usainboltz.grammar import *
from usainboltz.grammar import Set as LSet
from usainboltz.generator import *
from pointed_generator import *
from math import exp

def print_test_result(g, pointed_g, result):
	print("\n\nGrammar of G")
	print(g.rules)
	print("\n\nGrammar of pointed G")
	print(pointed_g.rules)
	print("Element of G\n:")
	print(result)
	print("\n\n\n")

e,z,a,b,c = Epsilon(), Atom(), Marker("a"), Marker("b"), Marker("c")
A = RuleName("A")
B = RuleName("B")

seq = Grammar({A: Seq(z)})
seq_gen = PointedGenerator(seq, A, expectations = {z:100})
res	= seq_gen.sample((1,100))
print_test_result(seq, seq_gen.grammar, res.obj)

set = Grammar({B: LSet(z*c)})
oracle = build_oracle({z: 10, B: exp(exp(2) - 1), c:3})
set_gen = PointedGenerator(set, B, oracle = oracle,k=1)
res = set_gen.sample((1,100))
print_test_result(set, set_gen.grammar, res.obj)