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
	Seq,
	IteratedRule,
	Set as LSet,
	Cycle
)
from typing import List, Set, Union as TypeUnion

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

def _minus_one(i: TypeUnion[None, int]) -> TypeUnion[None, int]:
	"""
	If i is not None or zero diminish its value by one, otherwise return None.
	"""
	if i == None or i>0:
		return i
	return i-1

def pointed_rule_name(name: str, k:int = 1) -> str:
	"""
	Given a rule name, return its pointed name.

	If k is specified, repeat the operation k times.
	"""
	return name + PointedSuffix*k

def pointed_rulename(r: RuleName, k:int = 1) -> RuleName:
	"""
	Given a rulename, return the pointed rulename.

	If k is specified, repeat the operation k times.
	"""
	return RuleName(pointed_rule_name(r.name, k))

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

def point_rulename(r: RuleName, point_to_empty: Set[RuleName]) -> RuleName:
	"""
	Return the pointed RuleName.

	If the rulenamme appears in point_to_empty, i.e. is empty, return None instead.
	"""
	if r in point_to_empty:
		return None
	return pointed_rulename(r)

def point_union_rule(u: Union, point_to_empty: Set[RuleName]) -> PointedRule:
	"""
	Return the pointed union.
	The pointed union of elements is just the union
	of pointed elements.
	"""
	union_args = []
	for arg in u.args:
		pointed_arg = point_rule(arg, point_to_empty)
		if not pointed_arg is None: 
			union_args.append(pointed_arg)

	return union_from_args(union_args)

def point_product_rule(p: Product, point_to_empty: Set[RuleName]) -> PointedRule:
	"""
	Return the pointed product.
	"""
	union_args = []
	for (i, arg) in enumerate(p.args):
		pointed_arg = point_rule(arg, point_to_empty)
		if not pointed_arg is None:
			product_args = p.args[:i] + [pointed_arg] + p.args[(i+1):]
			union_args.append(Product(*product_args))

	return union_from_args(union_args)

def point_epsilon_rule(e: Epsilon, _: Set[RuleName]) -> None:
	"""
	Return the pointed epsilon.
	The pointed class for epsilon is empty.
	Therefore, this function always return None.
	"""
	return None

def point_atom_rule(z: Atom, _: Set[RuleName]) -> Atom:
	"""
	Return the pointed atom.
	A pointed atom is an atom.
	"""
	return Atom()

def point_marker_rule(m: Marker, _: Set[RuleName]) -> None:
	"""
	Identical to the epsilon rule.
	"""
	return None

def point_sequence_rule(seq: Seq, point_to_empty: Set[RuleName]) -> Seq:
	"""
	The definition used for pointing here is:
	Pointed(Seq(A)) = Seq(A)*Pointed(A)*Seq(A).
	"""
	pointed_arg = point_rule(seq.arg, point_to_empty)
	if pointed_arg == None:
		raise Exception("A sequence of a class containing empty elements can't exist.")
	return Product(seq,pointed_arg,seq)

def point_set_rule(set: LSet, point_to_empty: Set[RuleName]):
	"""
	For a set (labelled), the pointing operation gives Pointed(Set(A)) = Pointed(A)*Set(A).
	Because each atom is labelled differently, an element appearing in Pointed(A) can't appear
	in Set(A), so at the end, Pointed(A)*Set(A) can still be considered to represent a set.
	"""
	pointed_arg = point_rule(set.arg, point_to_empty)
	if pointed_arg == None:
		raise Exception("A set of a class containing empty elements can't exist.")
	return Product(pointed_arg,set)

def point_cycle_rule(cycle: Cycle, point_to_empty: Set[RuleName]):
	"""
	For a cycle (labelled), the pointing operation gives Pointed(Cycle(A)) = Pointed(A)*Seq(A).
	Having an element pointed "anchor" the cycle at a given point, the cycle can then be considered
	a sequence.
	"""
	pointed_arg = point_rule(cycle.arg, point_to_empty)
	if pointed_arg == None:
		raise Exception("A cycle of a class containing empty elements can't exist.")
	return pointed_arg*Seq(cycle.arg)
	"""
	For now, arguments are not supported for different contraints.
	return Product(pointed_arg, 
		#One element of the cycle is contained in the pointed argument,
		#therefore lower and greater size must be diminished.
		Seq(cycle.arg,
			geq = _minus_one(cycle.lower_size),
			leq = _minus_one(cycle.upper_size))
		)
	"""

def point_rule(r: Rule, point_to_empty: Set[RuleName]) -> PointedRule:
	"""
	Return the pointed rule.
	Such a rule might be empty (pointed epsilon for instance).
	In such a case, the None value is returned.

	point_to_empty contains the set of rulenames which have been established
	to point to an empty class. In this case, None should be returned.
	"""
	match r:
		case Union():
			return point_union_rule(r, point_to_empty)
		case Product():
			return point_product_rule(r, point_to_empty)
		case Epsilon():
			return point_epsilon_rule(r, point_to_empty)
		case Atom():
			return point_atom_rule(r, point_to_empty)
		case RuleName():
			return point_rulename(r, point_to_empty)
		case Marker():
			return point_marker_rule(r, point_to_empty)
		case Seq():
			return point_sequence_rule(r, point_to_empty)
		case LSet():
			return point_set_rule(r, point_to_empty)
		case Cycle():
			return point_cycle_rule(r, point_to_empty)
		case _:
			#Todo: finish each case.
			print(r)
			raise Exception("Not yet implemented")

#----------------------------------------------------------------
"""
This code section is dedicated to establish the order in which rulenames should be pointed.
"""
def rulenames_appearing(r: Rule) -> Set[RuleName]:
	"""
	Return the set of rulenames which appear in the rule r.
	"""
	match r:
		case IteratedRule():
			return rulenames_appearing(r.arg)
		case Epsilon() | Atom() | Marker():
			return set()
		case RuleName():
			return set([r])
		case Union() | Product():
			s = set()
			for arg in r.args:
				s = s.union(rulenames_appearing(arg))
			return s
		case _:
			raise Exception("This case is not handled")

def order_from_rulename(start: RuleName, g: Grammar, explored: Set[RuleName], order: List[RuleName]):
	"""
	Auxiliary function for order_to_point.

	Explore the graph of dependancy of the grammar starting from the given rulename. Add
	at the end of order rulenames in the inverse order in which they should be explored.

	explored: set of rulenames which have been explored before.

	Both order and explored will be modified to obtain the correct result.
	"""
	if start in explored:
		return

	explored.add(start)
	for rule in rulenames_appearing(g.rules[start]).difference(explored):
		order_from_rulename(rule, g, explored, order)

	order.append(start)

def order_to_point(g: Grammar) -> List[RuleName]:
	"""
	Establish the order in which rulenames should be pointed.

	A rulename which is pointed to the empty class should always be pointed after the rulenames present in its
	specifcation. There are no cycle, indeed such a cycle would give an infinite number of empty elements.
	"""
	order = []
	explored = set()
	for rulename in g.rules.keys():
		order_from_rulename(rulename, g, explored, order)
	
	return order

#---------------------------------------------------------------

#Todo: rework the function to return a dictionnary whith values as rulenames which have been created
#by pointing and which did not appear before in g and keys as the rulenames which point to their key.
def point_grammar(g: Grammar) -> (Grammar, Set[RuleName], Set[RuleName]):
	"""
	Return the pointed grammar.
	Return an associated set which corresponds to all rulenames which pointed version appear in the grammar
	and didn't appear before. 
	Return an associated set which corresponds to rulenames which when pointed, lead to empty class.

	A pointed grammar is composed of all intermediates rules
	present in the original grammar and their pointed version.
	"""
	pointed_rules = g.rules.copy()
	point_to_empty = set()
	added_unpointed = set()

	for rulename in order_to_point(g):
		rulename_pointed = pointed_rulename(rulename)
		if rulename_pointed in pointed_rules.keys():
			continue #The rulename has already been pointed and added to g in an anterior call to point_grammar.
		rule = g.rules[rulename]

		new_rule = point_rule(rule, point_to_empty)
		if new_rule is None: #The rule associated to rulename points to the empty class. 
			point_to_empty.add(rulename)
		else:
			pointed_rules[rulename_pointed] = new_rule
			added_unpointed.add(rulename)

	return (Grammar(pointed_rules, labelled = g.labelled), added_unpointed, point_to_empty)