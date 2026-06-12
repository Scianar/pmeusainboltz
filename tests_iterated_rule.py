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

class Test:
	def __init__(self, elts):
		self.flemish_giant = 0
		self.french_lop = 0
		self.rex_rabbit = 0
		for elt in elts:
			if elt == "flemish giant":
				self.flemish_giant += 1
			elif elt == "french lop":
				self.french_lop += 1
			else:
				self.rex_rabbit += 1

	def __repr__(self):
		return f"Number of rabbits:\nFlemish giants: {self.flemish_giant}\n French lops: {self.french_lop}\nRex rabbits: {self.rex_rabbit}"

def build_a(_):
	return "flemish giant"

def build_b(_):
	return "french lop"

def build_c(_):
	return "rex rabbit"

union = union_builder(build_a, build_b, build_c)

def build_node(tp):
	(_,token) = tp
	return union(token)

def build_all(tp):
	return Test(map(build_node, tp))

set = Grammar({B: LSet(z*(a+b+c))})
oracle = build_oracle({z: 10, B: exp(exp(2) - 1), a:3, b:3, c:3})
set_gen = PointedGenerator(set, B, oracle = oracle, k=2)
set_gen.set_builder(B, build_all)
res = set_gen.sample((1,100))
print_test_result(set, set_gen.grammar, res.obj)


"""
#Test on mobile directly stolen from usainboltz.
node = Atom()
Mobile = RuleName("Mobile")
grammar = Grammar({Mobile: node * (Epsilon() + Cycle(Mobile))})
gen = PointedGenerator(grammar, Mobile)
res = generator.sample((10,20))
print_test_result(grammar, gen.grammar, res.obj)"""