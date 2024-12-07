import sys
sys.path.append('/home/hyy/pydyn_on_manifolds')
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


def point_mass():
    """
    Derives Newton's equation of motion for 3d point mass

    Variables
    scalars: mass: m [kg]
             gravity: g [m/s^2]

    vectors: neg gravity direction: e3 [0,0,1] [No units]
             point-mass position: x  [m]
             input force: f [N]

    :return: None
    """
    m, g = getScalars('m g', attr=['Constant'])
    e3 = Vector('e3', attr=['Constant'], value=np.array([0., 0., 1]))
    x, f = getVectors(['x', 'f'])

    v = x.diff()

    # computing energies
    PE = m * x.dot(g * e3)
    KE = m * Dot(v, v) * 0.5

    # Lagrangian
    L = KE - PE

    # infinitesimal work
    deltaW = Dot(x.delta(), f)

    eqs = compute_eom(L, deltaW, [[], [x], []])
    print_latex(eqs)

    print('done')


if __name__ == "__main__":
    point_mass()
