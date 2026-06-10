import usainboltz
from usainboltz.grammar import (
	Rule,
	RuleName,
	Union,
	Product,
	Atom,
	Epsilon,
	Grammar,
	Marker,
	Seq
)
from typing import List, Union as TypeUnion

#When pointing, it is possible to have empty rules (like for the epsilon class).
#That's why, we need a new rule, represented by None, temporarily.
type PointedRule = TypeUnion[None, Rule]

#Suffix added at the end of a rulename to indicate that this is a pointed rulename.
"""
#Generated randomly, assume that this suffix will never randomly appear in a rulename name.
PointedSuffix = "1b38a28af420e18b5b1687cd816ca5dd"
"""
#For now, the suffix is _P for readability reasons
PointedSuffix = "_P"

def pointed_rulename(name: str) -> str:
	"""
	Given a rule name, return its pointed name.
	"""
	return name + PointedSuffix


def union_from_args(union_args: List[Rule]) -> PointedRule:
	"""
	From the arguments of an union rule, deduce corresponding rule.

	If there are no arguments, None is returned corresponding to the empty rule.

	If there is one argument, the argument is returned directly.

	Otherwise, return an union rule.
	"""
	if len(union_args) == 0:
		return None
	if len(union_args) == 1:
		return union_args[0] 
	return Union(*union_args)

def point_rulename(r: RuleName) -> RuleName:
	"""
	Return the pointed RuleName.
	For now, it is assumed that a rulename can't be associated to an empty rule inside a grammar.
	"""
	return RuleName(pointed_rulename(r.name))

def point_union_rule(u: Union) -> PointedRule:
	"""
	Return the pointed union.
	The pointed union of elements is just the union
	of pointed elements.
	"""
	union_args = []
	for arg in u.args:
		pointed_arg = point_rule(arg)
		if not pointed_arg is None: 
			union_args.append(pointed_arg)

	return union_from_args(union_args)

def point_product_rule(p: Product) -> PointedRule:
	"""
	Return the pointed product.
	"""
	union_args = []
	for (i, arg) in enumerate(p.args):
		pointed_arg = point_rule(arg)
		if not pointed_arg is None:
			#When an argument in the product 
			product_args = p.args[:i] + [point_rule(arg)] + p.args[(i+1):]
			union_args.append(Product(*product_args))

	return union_from_args(union_args)

def point_epsilon_rule(_: Epsilon) -> None:
	"""
	Return the pointed epsilon.
	The pointed class for epsilon is empty.
	Therefore, this function always return None.
	"""
	return None

def point_atom_rule(z: Atom) -> Atom:
	"""
	Return the pointed atom.
	A pointed atom is an atom.
	"""
	return Atom()

def point_marker_rule(m: Marker) -> None:
	"""
	Identical to the epsilon rule.
	"""
	return None

def point_sequence_rule(seq: Seq) -> Seq:
	"""
	The definition used for pointing here is:
	Pointed(Seq(A)) = Seq(A)*Pointed(A)*Seq(A).
	"""
	pointed_arg = point_rule(seq.arg)
	if pointed_arg == None:
		return None
	return seq*pointed_arg*seq

def point_rule(r: Rule) -> PointedRule:
	"""
	Return the pointed rule.
	Such a rule might be empty (pointed epsilon for instance).
	In such a case, the None value is returned.
	"""
	match r:
		case Union():
			return point_union_rule(r)
		case Product():
			return point_product_rule(r)
		case Epsilon():
			return point_epsilon_rule(r)
		case Atom():
			return point_atom_rule(r)
		case RuleName():
			return point_rulename(r)
		case Marker():
			return point_marker_rule(r)
		case Seq():
			return point_sequence_rule(r)
		case _:
			#Todo: finish each case.
			print(r)
			raise Exception("Not yet implemented")

def point_grammar(g: Grammar) -> Grammar:
	"""
	Return the pointed grammar.

	A pointed grammar is composed of all intermediates rules
	present in the original grammar and their pointed version.
	"""
	pointed_rules = g.rules.copy()
	for (rulename,rule) in g.rules.items():
		new_rule = point_rule(rule)
		if new_rule is None:
			#Todo: handle this case.
			raise Exception("For now, pointing non terminal symbols isomorph to the epsilon class is not handled.")
		pointed_rules[RuleName(pointed_rulename(rulename.name))] = new_rule

	return Grammar(pointed_rules, labelled = g.labelled)