import sys
sys.path.append('/home/xld/pydyn_on_manifolds-cc')
from pydyn import *
from pydyn.base.scalars import Scalar, getScalars
from pydyn.base.vectors import Vector, S2, TS2, TSO3, ZeroVector, getVectors
from pydyn.base.matrices import Matrix, SO3, O, I, getMatrices

from pydyn.operations.addition import Add, VAdd, MAdd
from pydyn.operations.multiplication import Mul, MMMul, MVMul, SMMul, SVMul, VVMul
from pydyn.operations.transpose import Transpose
from pydyn.operations.geometry import Delta, Dot, Cross, Hat, Vee

from pydyn.operations.dynamics import compute_eom
from pydyn.operations.print_tree import print_latex
from pydyn.utils.errors import ExpressionMismatchError
import numpy as np
from pydyn.base.expr import Expr
from pydyn.base.matrices import MatrixExpr, ZeroMatrix
from pydyn.base.scalars import ScalarExpr, Zero
from pydyn.base.vectors import VectorExpr
from pydyn.utils.errors import UndefinedCaseError
from pydyn.operations.simplification import full_simplify, pull
from pydyn.operations.expansion import *
from pydyn.operations.collection import *
from pydyn.operations.algebraic_manipulation import efs,efv,efm
from pydyn.operations.simplification import vector_rules

if __name__ == "__main__":

    print('\n-----------------------------------\n')
    J = Matrix('J', attr=['Constant', 'SymmetricMatrix'])
    rho = Vector('\\rho', attr=['Constant'])
    m, g = getScalars('m g', attr=['Constant'])
    e3 = Vector('e_3', attr=['Constant'], value=np.array([0., 0., 1]))

    M = Vector('M')
    R = SO3('R')
    Om = R.get_tangent_vector()
    eta = R.get_variation_vector()
    x = R * rho
    v = x.diff()
    KE = Dot(Om, J * Om) * 0.5 + Dot(v, v) * m * 0.5

    PE = m * g * Dot(x, e3)
    L = KE - PE

    deltaW = Dot(eta, M)
    eqns = compute_eom(L, deltaW, [[], [], [R]])
    print_latex(eqns)

    print('done')

  





            



