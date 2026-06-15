"""
Set of tests on iterated rules which have arguments.
"""

from pointing import *
from usainboltz.grammar import *
from pointed_generator import *

#----------Grammar-------------

def print_test(g, g_pointed):
	print("\n\nGrammar of G:")
	print(g)
	print("Pointed grammar of pointed grammar of G:")
	print(g_pointed)
	print("\n\n\n")

z = Atom()
A, B = RuleName("A"), RuleName("B")
cycle_grammar_1 = Grammar({A: Seq(B, leq = 2, geq = 1), B:z})
cycle_grammar_1_P = cycle_grammar_1
for i in range(2):
	cycle_grammar_1_P = point_grammar(cycle_grammar_1_P)[0]
print_test(cycle_grammar_1, cycle_grammar_1_P)

cycle_grammar_2 = Grammar({A: Cycle(B, leq = 2, geq = 1), B:z})
cycle_grammar_2_P = cycle_grammar_2
for i in range(2):
	cycle_grammar_2_P = point_grammar(cycle_grammar_2_P)[0]
print_test(cycle_grammar_2, cycle_grammar_2_P)

cycle_grammar_3 = Grammar({A: LSet(B, leq = 2, geq = 1), B:z})
cycle_grammar_3_P = cycle_grammar_3
for i in range(2):
	cycle_grammar_3_P = point_grammar(cycle_grammar_3_P)[0]
print_test(cycle_grammar_3, cycle_grammar_3_P)

cycle_grammar_4 = Grammar({A: Seq(B, geq = 2), B:z})
cycle_grammar_4_P = cycle_grammar_4
for i in range(2):
	cycle_grammar_4_P = point_grammar(cycle_grammar_4_P)[0]
print_test(cycle_grammar_4, cycle_grammar_4_P)