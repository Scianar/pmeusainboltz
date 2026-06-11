"""
Set of tests involving trees.

For some print the grammar and pointed grammar. For all, print the result for a pointed tree.
"""

from pointing import *
from usainboltz.grammar import *
from usainboltz.generator import *
from pointed_generator import *
from usainboltz.generator import rng_seed
rng_seed(1635)

def print_test_grammar(g, g_pointed):
	print("\n\nGrammar of G:")
	print(g.rules)
	print("Pointed grammar of G:")
	print(g_pointed.rules)
	print("\n\n\n")

def print_test_result(g, result):
	print("\n\nGrammar of G")
	print(g.rules)
	print("Element of G:")
	print(result)
	print("\n\n\n")

class Leaf:
	def print(self, _):
		return ""

class Tree:
	def __init__(self, children):
		self.children = children

	def print(self, t:int):
		result = ""
		branch = "|\t"*(t-1)
		if t>0:
			branch += "|-----"
			branch += "\t"
		result += branch+"Z\n"
		result += "".join([child.print(t+1) for child in self.children])
		return result

	def __repr__(self):
		return self.print(0)

def build_bin_leaf(_):
	return Leaf()

def build_bin_node(tupl):
	z, left, right = tupl
	return Tree([left, right])

def build_node(tupl):
	(_, children) = tupl
	return Tree(children)

e,z = Epsilon(), Atom()
B = RuleName("B")
T = RuleName("T")

bin_tree = Grammar({B: e + z*B*B})
bin_tree_gen = PointedGenerator(bin_tree, B, expectations = {z:100})
bin_tree_gen.set_builder(B, union_builder(build_bin_leaf, build_bin_node))
res	= bin_tree_gen.sample((1,100))
print_test_result(bin_tree, res.obj)


tree = Grammar({T: z*Seq(T)})
tree_gen = PointedGenerator(tree, T, expectations = {z:100})
print_test_grammar(tree, tree_gen.grammar)
tree_gen.set_builder(T, build_node)
res = tree_gen.sample((1,100))
print_test_result(tree, res.obj)

