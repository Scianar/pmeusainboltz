"""
The buidlers use as arguments tuple trees.

Those trees have a different structures depending
on the pointed class or non pointed class.

tc stands for tuple conversion.
"""
import usainboltz
from usainboltz.grammar import (
	Rule,
	RuleName,
	Union,
	Product,
	Atom,
	Epsilon,
	Grammar,
	Seq
)
from usainboltz.generator import Generator
from typing import List, Union as TypeUnion
from pointing import *

def tc_union_rule(u: Union, tp: tuple, point_to_empty: Set[RuleName]) -> PointedRule:
	"""
	Some elements in the union might disappear (for instance epsilon + z gives z when pointed).
	Therefore, the resulting tuple of an union migth differ.
	"""
	#Todo: implement a more efficient way to know if a rule is empty.
	#Also, for knowing if an union has been reduced.
	pointed_index = []
	for (i,arg) in enumerate(u.args):
		pointed_arg = point_rule(arg, point_to_empty)
		if not pointed_arg is None: #In this case, an element in the union has disappeared in the pointed union.
			pointed_index.append(i)

	if len(pointed_index) == 0: #This case should be impossible.
		raise Exception("The generator has outputed an element from an empty pointed class.")
	if len(pointed_index) == 1: #The union has been removed during the pointing.
		return (pointed_index[0], tc_rule(u.args[pointed_index[0]], tp, point_to_empty))
	
	(chosen_index, chosen_rule) = tp

	real_index = pointed_index[chosen_index]
	return (real_index, tc_rule(u.args[real_index],chosen_rule,point_to_empty))

def tc_product_rule(p: Product, tp:tuple, point_to_empty: Set[RuleName]) -> PointedRule:
	"""
	The problemen encountered is identical to the one in tc_union_rule.
	Some elements might disappear in the resulting pointed union.
	"""
	pointed_index = []
	for (i,arg) in enumerate(p.args):
		pointed_arg = point_rule(arg, point_to_empty)
		if not pointed_arg is None: #In this case, an element in the product has disappeared in the pointed union.
			pointed_index.append(i)

	if len(pointed_index) == 0: #This case should be impossible.
		raise Exception("The generator has outputed an element from an empty pointed class.")
	
	#When pointing a product, a product rule will always be produced, not always in an union.
	if len(pointed_index) == 1: #The union has been removed during the pointing.
		real_index = pointed_index[0]
		product_tp = tp
	else:	
		(chosen_index, chosen_rule) = tp
		real_index = pointed_index[chosen_index]
		product_tp = chosen_rule

	#The product tuple has only one element modified, the one corresponding to the pointed rule.
	result_tp = product_tp[:real_index] + (tc_rule(p.args[real_index], product_tp[real_index], point_to_empty),) + product_tp[real_index+1:]
	return result_tp

def tc_atom_rule(z: Atom, tp: tuple, point_to_empty: Set[RuleName]) -> tuple:
	"""
	Given an atom, the pointed tuple is strictly identical to a non pointed tuple.
	"""
	return tp

def tc_rulename(r: RuleName, tp: tuple, point_to_empty: Set[RuleName]) -> tuple:
	"""
	Given a rulename, the corresponding tuple should be identical to a non pointed tuple.
	Indeed, if the rulename is pointed, the tuple has been build using the builder for pointed associated rule in the grammar.
	Otherwise nothing is changed.
	"""
	return tp

def tc_sequence_rule(seq: Seq, tp: tuple, point_to_empty: Set[RuleName]) -> tuple:
	"""
	A pointed sequence is a product: Seq(A)*pointed(A)*Seq(A).
	To unpoint the sequence, we just need to "flatten" the tuple.
	"""
	left_seq, pointeg_arg, right_seq = tp
	return left_seq + [tc_rule(seq.arg, pointed_arg, point_to_empty)] + right_seq

def tc_rule(r: Rule, tp: tuple, point_to_empty: Set[RuleName]) -> tuple:
	"""
	Convert the tuple associated to the pointed rule obtained from r to a tuple associated with r.

	point_to_empty: set of rulenames which when pointed are the empty class.
	"""
	match r:
		case Union():
			return tc_union_rule(r, tp, point_to_empty)
		case Product():
			return tc_product_rule(r, tp, point_to_empty)
		case Epsilon():
			raise Exception("The generator has outputed an element from an empty pointed class.")
		case Marker():
			raise Exception("The generator has outputed an element from an empty pointed class.")
		case Atom():
			return tc_atom_rule(r, tp, point_to_empty)
		case RuleName():
			return tc_rulename(r, tp, point_to_empty)
		case Seq():
			return tc_sequence_rule(r, tp, point_to_empty)
		case _:
			#Todo: finish each case.
			print(r)
			raise Exception("Not yet implemented")

def pointed_builder(non_pointed_rule: Rule, point_to_empty: Set[RuleName]):
	"""
	Buiders for pointed class are different from the normal builders.
	The tuple structure for pointed class is different from the one for their associated non pointed class.
	To always return a tuple for non pointed class, all pointed class must have a special builder.

	point_to_empty: set of rulenames which when pointed are the empty class.
	"""
	def build(tp: tuple):
		return tc_rule(non_pointed_rule, tp, point_to_empty)
	return build


class PointedGenerator(Generator):
	"""
	Class inherited from Generator from usainboltz.

	Add the possibility to point the generator. Can only be pointed when initialised
	"""

	def __init__(self, grammar: Grammar, *args, k:int = 1):
		"""
		arguments are identical to the one for the generator. One optional argument k is added.
		k is the number of time the generator must be pointed, by default k = 1. k can't be modified
		after initialising the generator.
		"""
		self.grammar = grammar
		self.nb_pointed = 0
		self.default_pointed_builders = {}
		#The default pointed builders refer to the builders without
		#a builder specified by the user.

		self.non_pointed_rulenames = set(self.grammar.rules.keys())
		#Refers to the set of rulenames which come from the non pointed grammar.

		self._point(k)

		super().__init__(self.grammar, *args)

		self.rule_name = pointed_rulename(self.rule_name, k)

	def _point(self, k:int = 1) -> Grammar:
		"""
		Point the generator k times (by default k=1). Can only be called before initialisation of the super class.
		"""
		for i in range(0, k):
			self._point_once()
			self.nb_pointed += 1

	def _point_once(self):
		"""
		Point the generator once. Can only be called before initialisation of the super class.
		"""
		(self.grammar, added_unpointed, point_to_empty) = point_grammar(self.grammar)
		for rule in added_unpointed:
			pointed_rule_name = pointed_rulename(rule)
			new_builder = pointed_builder(self.grammar.rules[rule], point_to_empty)

			self.default_pointed_builders[pointed_rule_name] = new_builder

	def set_builder(self, non_terminal:RuleName, builder):
		"""
		Almost identical to the Generator.set_builder function.

		Also add corresponding builders for pointed non_terminal
		"""
		super().set_builder(non_terminal, builder)

		for _ in range(self.nb_pointed):
			non_terminal = pointed_rulename(non_terminal)
			def composed_builder(tp: tuple):
				return builder(self.default_pointed_builders[non_terminal](tp))
			super().set_builder(non_terminal, composed_builder)