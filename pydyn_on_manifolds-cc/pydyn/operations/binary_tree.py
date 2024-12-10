from pydyn.operations.addition import Add, VAdd, MAdd
from pydyn.operations.multiplication import SVMul, SMMul
from pydyn.base.matrices import MatrixExpr
from pydyn.base.scalars import ScalarExpr
from pydyn.base.vectors import VectorExpr
from pydyn.base.nodes import BinaryNode, NaryNode
from pydyn.operations.geometry import Hat, Cross


def is_leaf(expr):
    if isinstance(expr, BinaryNode):
        return False
    else:
        return True



def has_nested_add(expr):
    if isinstance(expr, NaryNode):
        return True
    elif isinstance(expr, BinaryNode):
        return has_nested_add(expr.left) or has_nested_add(expr.right)
    elif isinstance(expr, Hat):
        return has_nested_add(expr.expr)
    else:
        return False


def has_nested_scalars(expr):
    if isinstance(expr, ScalarExpr):
        if isinstance(expr, BinaryNode):
            return has_nested_scalars(expr.left) or has_nested_scalars(expr.right)
        else:
            return False 

    elif isinstance(expr, VectorExpr):
        if isinstance(expr, BinaryNode):
            if isinstance(expr, SVMul):
                return True
            else:
                return has_nested_scalars(expr.left) or has_nested_scalars(expr.right)
        else:
            return False

    elif isinstance(expr, MatrixExpr):
        if isinstance(expr, BinaryNode):
            if isinstance(expr, SMMul):
                return True
            else:
                return has_nested_scalars(expr.left) or has_nested_scalars(expr.right)
        else:
            return False
    else:
        return False
