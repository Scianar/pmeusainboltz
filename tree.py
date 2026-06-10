from pointing import *
from usainboltz.grammar import *
from usainboltz.generator import *
from pointed_generator import *
from usainboltz.generator import rng_seed


class BinaryTree:
	def __init__(self, left, right):
		self.left = left
		self.right = right

	def print(self, t):
		if self.left == None:
			left = ""
		else:
			left = self.left.print(t+1)
		if self.right == None:
			right = ""
		else:
			right = self.right.print(t+1)
		return left + t*"\t" + "Z\n" + right

	def __repr__(self):
		return self.print(0)

def build_leaf(_):
	return None

def build_node(tupl):
	z, left, right = tupl
	return BinaryTree(left, right)


e,z = Epsilon(), Atom()
B = RuleName("B")

grammar = Grammar({B: Seq(z)})
generator = Generator(grammar, B, expectations = {z:100})
#generator.set_builder(B, union_builder(build_leaf, build_node))
generator = point_generator(generator)
print(generator.grammar)
#print(generator.grammar)
res	= generator.sample((2,100))
print(res.obj)