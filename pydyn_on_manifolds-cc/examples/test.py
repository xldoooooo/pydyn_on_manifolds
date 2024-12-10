from pydyn.operations.expansion import expand
from pydyn import *
from pydyn.operations.print_tree import print_latex
m, g = getScalars('m g', attr=['Constant'])
M = m*g
M = expand(M)
print_latex(M)
