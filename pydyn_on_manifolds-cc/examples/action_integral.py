import sys
sys.path.append('/home/hyy/Desktop/pydyn_on_manifolds-cc')
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
from pydyn.operations.simplification import  pull
from pydyn.operations.expansion import *
from pydyn.operations.collection import *

if __name__ == "__main__":

    print('\n-----------------------------------\n')
    """double rigid pendulum"""
    J1 = Matrix('J_1', attr=['Constant', 'SymmetricMatrix'])
    J2 = Matrix('J_2', attr=['Constant', 'SymmetricMatrix'])
    rho1 = Vector('\\rho_1', attr=['Constant'])
    rho2 = Vector('\\rho_2', attr=['Constant'])
    l1 = Vector('l_1', attr=['Constant'])
    m1, m2, g = getScalars('m_1 m_2 g', attr=['Constant'])
    e3 = Vector('e_3', attr=['Constant'], value=np.array([0., 0., 1]))

    M1, M2 = getVectors('M_1 M_2')
    R1, R2 = SO3('R_1'), SO3('R_2')
    Om1, eta1 = R1.get_tangent_vector(), R1.get_variation_vector()
    Om2, eta2 = R2.get_tangent_vector(), R2.get_variation_vector()

    x1 = R1 * rho1
    x2 = R1 * l1 + R2 * rho2
    v1 = x1.diff()
    v2 = x2.diff()

    KE = Dot(Om1, J1 * Om1) * 0.5 + Dot(Om2, J2 * Om2) * 0.5 + Dot(v1, v1) * m1 * 0.5 + Dot(v2, v2) * m2 * 0.5
    PE = (m1 * g * Dot(R1 * rho1, e3)) + (m2 * g * Dot(R2 * rho2, e3))
    L = KE - PE

    deltaW = Dot(eta1, M1) + Dot(eta2, M2)

    eqns = compute_eom(L, deltaW, [[], [], [R1, R2]])
    print_latex(eqns)

    print('done')
  





            



