from pointing import *
from usainboltz.grammar import *
#from usainboltz.generator import *
#from pointed_generator import *
#from usainboltz.generator import rng_seed

"""
This module tests the pointing method on grammars with important amount of empty elements.

For now, only contain tests on the grammar.

Print the output, its up to the user to check the correcness of the answer.
"""
def print_test(g, g_pointed):
	print("\n\nGrammar of G:")
	print(g.rules)
	print("Pointed grammar of G:")
	print(g_pointed.rules)
	print("\n\n\n")



a,b,e = Marker("a"), Marker("b"), Epsilon()
z = Atom()
A = RuleName("A")
B = RuleName("C")
C = RuleName("B")
D = RuleName("D")
E = RuleName("E")
F = RuleName("F")
G = RuleName("G")

g_direct = Grammar({A: e + z*a*z})

(g_direct_pointed,_) = point_grammar(g_direct)
print_test(g_direct, g_direct_pointed)

g_disappearing_class = Grammar({
	A: a + b,
	B: C*Seq(z),
	C: b*A
	})

(g_disappearing_class_pointed,_) = point_grammar(g_disappearing_class)
print_test(g_disappearing_class, g_disappearing_class_pointed)

g_complex_dependance = Grammar({
	A: a + B,
	B: C + D,
	E: A+B*z+F,
	C: a + b,
	F: E+F*D,
	G: E+F+A+B+D,
	D: e*(a+e),
	})
(g_complex_dependance_pointed,_) = point_grammar(g_complex_dependance)
print_test(g_complex_dependance, g_complex_dependance_pointed)