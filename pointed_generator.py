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

def tc_union_rule(u: Union, tp: tuple) -> PointedRule:
	"""
	Some elements in the union might disappear (for instance epsilon + z gives z when pointed).
	Therefore, the resulting tuple of an union migth differ.
	"""
	#Todo: implement a more efficient way to know if a rule is empty.
	#Also, for knowing if an union has been reduced.
	pointed_index = []
	for (i,arg) in enumerate(u.args):
		pointed_arg = point_rule(arg)
		if not pointed_arg is None: #In this case, an element in the union has disappeared in the pointed union.
			pointed_index.append(i)

	if len(pointed_index) == 0: #This case should be impossible.
		raise Exception("The generator has outputed an element from an empty pointed class.")
	if len(pointed_index) == 1: #The union has been removed during the pointing.
		return (pointed_index[0], tc_rule(u.args[pointed_index[0]], tp))
	
	(chosen_index, chosen_rule) = tp
	real_index = pointed_index[chosen_index]
	return (real_index, tc_rule(u.args[real_index],chosen_rule))

def tc_product_rule(p: Product, tp:tuple) -> PointedRule:
	"""
	The problemen encountered is identical to the one in tc_union_rule.
	Some elements might disappear in the resulting pointed union.
	"""
	pointed_index = []
	for (i,arg) in enumerate(p.args):
		pointed_arg = point_rule(arg)
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
	result_tp = product_tp[:real_index] + (tc_rule(p.args[real_index],product_tp[real_index]),) + product_tp[real_index+1:]
	return result_tp

def tc_atom_rule(z: Atom, tp: tuple) -> tuple:
	"""
	Given an atom, the pointed tuple is strictly identical to a non pointed tuple.
	"""
	return tp

def tc_rulename(r: RuleName, tp: tuple) -> tuple:
	"""
	Given a rulename, the corresponding tuple should be identical to a non pointed tuple.
	Indeed, if the rulename is pointed, the tuple has been build using the builder for pointed associated rule in the grammar.
	Otherwise nothing is changed.
	"""
	return tp

def tc_sequence_rule(seq: Seq, tp: tuple) -> tuple:
	"""
	A pointed sequence is a product: Seq(A)*pointed(A)*Seq(A).
	To unpoint the sequence, we just need to "flatten" the tuple.
	"""
	left_seq, pointeg_arg, right_seq = tp
	return left_seq + [tc_rule(seq.arg, pointed_arg)] + right_seq

def tc_rule(r: Rule, tp: tuple) -> tuple:
	"""
	Convert the tuple associated to the pointed rule obtained from r to a tuple associated with r.
	"""
	match r:
		case Union():
			return tc_union_rule(r, tp)
		case Product():
			return tc_product_rule(r, tp)
		case Epsilon():
			raise Exception("The generator has outputed an element from an empty pointed class.")
		case Marker():
			raise Exception("The generator has outputed an element from an empty pointed class.")
		case Atom():
			return tc_atom_rule(r, tp)
		case RuleName():
			return tc_rulename(r, tp)
		case Seq():
			return tc_sequence_rule(r, tp)
		case _:
			#Todo: finish each case.
			print(r)
			raise Exception("Not yet implemented")

def pointed_builder(non_pointed_rule: Rule, original_builder):
	"""
	A construction builder for an unique pointed rulename. See pointed_builders for more information.
	non_pointed_rule must correspond to rule associted with the unpointed rulename in the grammar.
	original_builder: the builder which is normally used on the non pointed class. Can be the default
	one or the one specified by the user.
	"""
	def build(tp: tuple):
		
		return original_builder(tc_rule(non_pointed_rule, tp))
	return build

def pointed_builders(g: Generator):
	"""
	Buiders for pointed class are different from the normal builders.
	The tuple structure for pointed class is different from the one for their associated non pointed class.
	To always return a tuple for non pointed class, all pointed class must have a special builder.

	Will search for the pointed rules inside the generator.
	"""
	for rulename in sorted(g.grammar.rules.keys(), key = lambda rulename: len(rulename.name)):
		name = rulename.name
		if name.endswith(PointedSuffix):
			unpointed_name = name[:len(name)-len(PointedSuffix)]
			unpointed_rulename = RuleName(unpointed_name)
			builder = pointed_builder(g.grammar.rules[unpointed_rulename], g.get_builder(unpointed_rulename))
			g.set_builder(rulename, builder)

def point_generator(g: Generator, k:int = 1) -> Generator:
	"""
	Return a new generator which has been pointed k times.
	Assume that all necessary builders have already been provided.
	"""
	pointed_grammar = g.grammar
	for _ in range(k):
		pointed_grammar = point_grammar(pointed_grammar)
	pointed_g = Generator(
		pointed_grammar,
		RuleName(g.rule_name.name + PointedSuffix * k), 
		#The rule to generate is the pointed version of the one to normally generate.
		None,
		None,
		None)

	for rulename in g.grammar.rules.keys():
		builder = g.get_builder(rulename)
		pointed_g.set_builder(rulename, builder)

	pointed_builders(pointed_g)
	return pointed_g