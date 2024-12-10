from abc import ABC

from pydyn.base.expr import Expr, Expression
from pydyn.base.nodes import UnaryNode
from pydyn.utils.errors import ExpressionMismatchError



class Transpose(Expr, UnaryNode, ABC):
    def __init__(self, expr=None):
        super().__init__()
        if expr is not None:
            self.expr = expr
            self.type = expr.type

    def __str__(self):
        return '('+self.expr.__str__() + ')\''

    def __add__(self, other):
        from pydyn.operations.addition import Add, VAdd, MAdd
        if self.type == Expression.SCALAR and other.type == Expression.SCALAR:
            return Add(self, other)
        elif self.type == Expression.VECTOR and other.type == Expression.VECTOR:
            return VAdd(self, other)
        elif self.type == Expression.MATRIX and other.type == Expression.MATRIX:
            return MAdd(self, other)
        else:
            raise ExpressionMismatchError('mul', 'Transpose(' + self.type + ')', other.type)

    def __mul__(self, other):
        from pydyn.operations.multiplication import MVMul, SVMul, VVMul
        if other.type == Expression.SCALAR:
            return Transpose(SVMul(self, other))
        elif other.type == Expression.VECTOR:
            return VVMul(self, other)
        elif other.type == Expression.MATRIX:
            return MVMul(self, other)
        else:
            raise ExpressionMismatchError('mul', 'Transpose(' + self.type + ')', other.type)

    def delta(self):
        return Transpose(self.expr.delta())
    
    def diff(self):
        return self.expr.diff().T()