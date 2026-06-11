"""
A set of tests on iterated rules: sequence, set, cycle.
"""

from pointing import *
from usainboltz.grammar import *
from usainboltz.generator import *
from pointed_generator import *

def print_test_result(g, result):
	print("\n\nGrammar of G")
	print(g.rules)
	print("Element of G\n:")
	print(result)
	print("\n\n\n")

e,z = Epsilon(), Atom()
A = RuleName("A")
seq = Grammar({A: Seq(z)})
seq_gen = PointedGenerator(seq, A, expectations = {z:100})
res	= seq_gen.sample((1,100))
print_test_result(seq, res.obj)