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
"""
grammar_1 = Grammar({A: Seq(B, leq = 2, geq = 1), B:z})
grammar_1_P = grammar_1
for i in range(2):
	grammar_1_P = point_grammar(grammar_1_P)[0]
print_test(grammar_1, grammar_1_P)

grammar_2 = Grammar({A: Cycle(B, leq = 2, geq = 1), B:z})
grammar_2_P = grammar_2
for i in range(2):
	grammar_2_P = point_grammar(grammar_2_P)[0]
print_test(grammar_2, grammar_2_P)

grammar_3 = Grammar({A: LSet(B, leq = 2, geq = 1), B:z})
grammar_3_P = grammar_3
for i in range(2):
	grammar_3_P = point_grammar(grammar_3_P)[0]
print_test(grammar_3, grammar_3_P)

grammar_4 = Grammar({A: Seq(B, geq = 2), B:z})
grammar_4_P = grammar_4
for i in range(2):
	grammar_4_P = point_grammar(grammar_4_P)[0]
print_test(grammar_4, grammar_4_P)
"""

#----------------Builders---------------------

def print_test_builders(expected_format, real_format):
	print("\n\nThe builder has outputed:")
	print(real_format)
	print("When was expected:")
	print(expected_format)
	print("\n\n\n")

grammar_5 = Grammar({A: Seq(z, leq = 4, geq = 1)})
builder_1 = pointed_builder(grammar_5.rules[A], {})
input_1 = (2,([z,z], z, [z])) #z*z*zP*z
output_1 = builder_1(input_1)
print_test_builders([z,z,z,z], output_1)
input_2 = (3,([z,z,z], z)) #z*z*z*zP
output_2 = builder_1(input_1)
print_test_builders([z,z,z,z], output_2)

grammar_6 = Grammar({A: Seq(z, eq = 3)})
builder_2 = pointed_builder(grammar_6.rules[A], {})
input_3 = (1,(z,z,z)) #z*zP*z
output_3 = builder_2(input_3)
print_test_builders([z,z,z], output_3)

grammar_7 = Grammar({A: Seq(z, eq = 1)})
builder_3 = pointed_builder(grammar_7.rules[A], {})
input_4 = (z) #zP
output_4 = builder_3(input_4)
print_test_builders(z, output_4)

#Todo: add one test for set and one for cycle.