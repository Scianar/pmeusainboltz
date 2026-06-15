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
from typing import List, Set, Union as TypeUnion, Optional

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

def minus_one(i: TypeUnion[None, int], k: Optional[int] = 1) -> TypeUnion[None, int]:
	"""
	If i is not None or zero diminish its value by one, otherwise return None.

	If k is provided, repeat the operations k times.
	"""
	if i == None:
		return i
	return max(i-k,0)

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

def _seq_from_size_args(arg: Rule, lower_size: TypeUnion[int, None], upper_size: TypeUnion[int, None]) -> Rule:
	"""
	Similar to union from args, takes as input the rule inside the sequence, the lower and upper
	size of the sequence (number of times the rule appears).

	If the sequence contains exatcly zero elements, return Epsilon(), if it contains exactly one
	element, return the rule, all other cases, return the sequence.
	"""
	if lower_size == 1 == upper_size:
		return arg
	if upper_size == 0:
		return Epsilon()
	return Seq(arg, geq = lower_size, leq = upper_size)

def _product_from_args(*args: Rule) -> Rule:
	"""
	Return a product of args performing the following reductions:
	If a rule in the product is an epsilon, remove it.
	If there are no arguments remaining, return Epsilon().
	If there is one argument remaining, return the arguement.
	Otherwise return a product.
	"""
	product_args = []
	for arg in args:
		if not arg is Epsilon():
			product_args.append(arg)
	if len(product_args) == 0:
		return Epsilon()
	if len(product_args) == 1:
		return product_args[0]
	return Product(*product_args)

def point_sequence_rule(seq: Seq, point_to_empty: Set[RuleName]) -> Seq:
	"""
	The definition used for pointing here is:
	Pointed(Seq(A)) = Seq(A)*Pointed(A)*Seq(A).

	When seq has sizes conditions, realise union over the repartition on the left and the right
	of the number of elements.
	If an element (on the left or right), would be a sequence of zero elements, it disappears
	from the product. One element, it becomes its argument. Otherwise nothing is changed.
	For the union, reduction follows the same rules as for product and union.
	"""
	pointed_arg = point_rule(seq.arg, point_to_empty)
	if pointed_arg == None:
		raise Exception("A sequence of a class containing empty elements can't exist.")
	
	up_size = minus_one(seq.upper_size)
	lo_size = minus_one(seq.lower_size)
	if lo_size == None: #Having no lower size is equivalent to having a lower size of 0.
		lo_size = 0
	
	#seq.arg will be designated as A for the following comentaries.

	#The disjunction is always made on the number of A on the left of the pointed A.
	union_args = []
	if up_size != None:
		nb_iterations = up_size + 1
	else:
		nb_iterations = lo_size

	for i in range(nb_iterations):#i is the number of A on the left.
		left = _seq_from_size_args(seq.arg, i, i)
		right = _seq_from_size_args(seq.arg, minus_one(lo_size, i), minus_one(up_size, i))
		union_args.append(_product_from_args(left, pointed_arg, right))

	if up_size == None: #In this case, there can be any number of A on the left.
		union_args.append(Product(Seq(seq.arg, geq = lo_size), pointed_arg, Seq(seq.arg)))
	return union_from_args(union_args)

def point_set_rule(set: LSet, point_to_empty: Set[RuleName]):
	"""
	For a set (labelled), the pointing operation gives Pointed(Set(A)) = Pointed(A)*Set(A).
	Because each atom is labelled differently, an element appearing in Pointed(A) can't appear
	in Set(A), so at the end, Pointed(A)*Set(A) can still be considered to represent a set.
	"""
	pointed_arg = point_rule(set.arg, point_to_empty)
	if pointed_arg == None:
		raise Exception("A set of a class containing empty elements can't exist.")
	return Product(pointed_arg,
		LSet(set.arg,
		geq = minus_one(set.lower_size),
		leq = minus_one(set.upper_size)))

def point_cycle_rule(cycle: Cycle, point_to_empty: Set[RuleName]):
	"""
	For a cycle (labelled), the pointing operation gives Pointed(Cycle(A)) = Pointed(A)*Seq(A).
	Having an element pointed "anchor" the cycle at a given point, the cycle can then be considered
	a sequence.
	"""
	pointed_arg = point_rule(cycle.arg, point_to_empty)
	if pointed_arg == None:
		raise Exception("A cycle of a class containing empty elements can't exist.")
	return Product(pointed_arg, 
		#One element of the cycle is contained in the pointed argument,
		#therefore lower and greater size must be diminished.
		Seq(cycle.arg,
			geq = minus_one(cycle.lower_size),
			leq = minus_one(cycle.upper_size))
		)
	
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