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
	Seq,
	Set as LSet,
	Cycle
)
from usainboltz.generator import Generator
from typing import List, Union as TypeUnion
from pointing import *

def identity_builder(tp: tuple):
	"""
	Always return the entry value.
	"""
	return tp

def compute_pointed_index(rules: List[Rule], point_to_empty: Set[RuleName]) -> List[int]:
	"""
	Build a list which associate to each index i, the ith element of rules which is not pointed
	to an empty class.
	"""
	pointed_index = []
	for (i,rule) in enumerate(rules):
		pointed_rule = point_rule(rule, point_to_empty)
		if not pointed_rule is None:
			pointed_index.append(i)
	return pointed_index

def tc_union_rule_builder(u: Union, point_to_empty: Set[RuleName]):
	"""
	Some elements in the union might disappear (for instance epsilon + z gives z when pointed).
	Therefore, the resulting tuple of an union migth differ.
	"""
	pointed_index = compute_pointed_index(u.args, point_to_empty)

	if len(pointed_index) == 0: #This case should be impossible.
		raise Exception("In theory, empty rules shouldn't have an associated builder.")

	sub_builders = list(
		map(lambda rule_id: tc_rule_builder(u.args[rule_id], point_to_empty), pointed_index)
		)
	if len(pointed_index) == 1: #The union has been removed during the pointing.
		sub_builder = sub_builders[0]
		def builder(tp: tuple):
			return (pointed_index[0], sub_builder(tp))
	else:
		def builder(tp: tuple):
			(chosen_index, chosen_tp) = tp
			sub_builder = sub_builders[chosen_index]
			return (pointed_index[chosen_index], sub_builder(chosen_tp))
	return builder

def tc_product_rule_builder(p: Product, point_to_empty: Set[RuleName]):
	"""
	The problemen encountered is identical to the one in tc_union_rule.
	Some elements might disappear in the resulting pointed union.
	"""
	pointed_index = compute_pointed_index(p.args, point_to_empty)

	if len(pointed_index) == 0: #This case should be impossible.
		raise Exception("In theory, empty rules shouldn't have an associated builder.")
	

	sub_builders = list(
		map(lambda rule_id: tc_rule_builder(p.args[rule_id], point_to_empty), pointed_index)
		)

	#When pointing a product, a product rule will always be produced, not always in an union.
	#The product tuple has only one element modified, the one corresponding to the pointed rule.
	if len(pointed_index) == 1: #The union has been removed during the pointing.
		real_index = pointed_index[0]
		sub_builder = sub_builders[0]
		def builder(tp: tuple):
			result_tp = tp[:real_index] + (sub_builder(tp[real_index]),) + tp[real_index+1:]
			return result_tp
	else:
		def builder(tp: tuple):
			(chosen_index, chosen_tp) = tp
			real_index = pointed_index[chosen_index]
			sub_builder = sub_builders[chosen_index]
			result_tp = chosen_tp[:real_index] + (sub_builder(chosen_tp[real_index]),) + chosen_tp[real_index+1:]
			return result_tp

	return builder

def tc_atom_rule_builder(z: Atom, point_to_empty: Set[RuleName]):
	"""
	Given an atom, the pointed tuple is strictly identical to a non pointed tuple.
	"""
	return identity_builder

def tc_rulename_builder(r: RuleName, point_to_empty: Set[RuleName]):
	"""
	Given a rulename, the corresponding tuple should be identical to a non pointed tuple.
	Indeed, if the rulename is pointed, the tuple has been build using the builder for pointed associated rule in the grammar.
	Otherwise nothing is changed.
	"""
	return identity_builder

def tc_sequence_rule_builder(seq: Seq, point_to_empty: Set[RuleName]):
	"""
	A pointed sequence is a product: Seq(A)*pointed(A)*Seq(A).
	To unpoint the sequence, we just need to "flatten" the tuple.
	"""
	sub_builder = tc_rule_builder(seq.arg, point_to_empty)
	def builder(tp: tuple):
		left_seq, pointed_arg, right_seq = tp
		return left_seq + [sub_builder(pointed_arg)] + right_seq
	return builder

def tc_set_rule_builder(set: Set, point_to_empty: Set[RuleName]):
	"""
	A pointed set is a product Pointed(A)*Set(A).
	"""
	sub_builder = tc_rule_builder(set.arg, point_to_empty)
	def builder(tp: tuple):
		pointed_arg, set = tp
		return [sub_builder(pointed_arg)] + set
	return builder

def tc_cycle_rule_builder(cycle: Cycle, point_to_empty: Set[RuleName]):
	"""
	A pointed cycle is a product Pointed(A)*Seq(A).
	"""
	sub_builder = tc_rule_builder(cycle.arg, point_to_empty)
	def builder(tp: tuple):
		pointed_arg, cycle = tp
		return [sub_builder(pointed_arg)] + cycle
	return builder

def tc_rule_builder(r: Rule, point_to_empty: Set[RuleName]):
	"""
	Create a builder which convert the tuple associated to the pointed rule
	obtained from r to a tuple associated with r.

	point_to_empty: set of rulenames which when pointed are the empty class.
	"""
	match r:
		case Union():
			return tc_union_rule_builder(r, point_to_empty)
		case Product():
			return tc_product_rule_builder(r, point_to_empty)
		case Epsilon():
			raise Exception("In theory, empty rules shouldn't have an associated builder.")
		case Marker():
			raise Exception("In theory, empty rules shouldn't have an associated builder.")
		case Atom():
			return tc_atom_rule_builder(r, point_to_empty)
		case RuleName():
			return tc_rulename_builder(r, point_to_empty)
		case Seq():
			return tc_sequence_rule_builder(r, point_to_empty)
		case LSet():
			return tc_set_rule_builder(r, point_to_empty)
		case Cycle():
			return tc_cycle_rule_builder(r, point_to_empty)
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
	return tc_rule_builder(non_pointed_rule, point_to_empty)

class PointedGenerator(Generator):
	"""
	Class inherited from Generator from usainboltz.

	Add the possibility to point the generator. Can only be pointed when initialised
	"""
	def __init__(self, grammar: Grammar, rule_name: RuleName , singular = None, expectations = None, oracle = None, k:int = 1):
		"""
		arguments are almost identical to the one for the generator.
		The rule_name must be specified.
		One optional argument k is added.
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
		rule_name = pointed_rulename(rule_name, k)
		super().__init__(self.grammar, rule_name, singular, expectations, oracle)

		for rule in self.non_pointed_rulenames: #To associate all pointed rulenames to a builder.
			self.set_builder(rule, identity_builder)

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

		unpointed_builder = builder
		for _ in range(self.nb_pointed):
			non_terminal = pointed_rulename(non_terminal)
			composed_builder = self._create_pointed_builder(non_terminal, unpointed_builder)	
			super().set_builder(non_terminal, composed_builder)
			unpointed_builder = composed_builder
			#The default_pointed_builders unpoint the argument tuple once.
			#When a generator has been pointed several times, it needs to
			#compose its builders.

	def _create_pointed_builder(self, non_terminal: RuleName, builder):
		"""
		Return a new builder over non_terminal.
		non_terminal is a rule name pointed and builder is the builder of the unpointed rulename.
		"""
		def composed_builder(tp: tuple):
			return builder(self.default_pointed_builders[non_terminal](tp))
		return composed_builder