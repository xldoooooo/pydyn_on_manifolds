from pydyn.data_types.expr import Expr, Expression
from pydyn.utils.errors import ExpressionMismatchError, UndefinedCaseError


class ScalarExpr(Expr):
    """
    ScalarExpr class and its properties
    """

    def __init__(self):
        super().__init__()
        self.size = (1,)
        self.type = Expression.SCALAR

    def __str__(self):
        raise NotImplementedError

    def __add__(self, other):
        from pydyn.operations.addition import Add
        if other.type == Expression.SCALAR:
            return Add(self, other)
        else:
            raise ExpressionMismatchError('Add', self.type, other.type)

    def __sub__(self, other):
        from pydyn.operations.addition import Add
        from pydyn.operations.multiplication import Mul
        if other.type == Expression.SCALAR:
            return Add(self, Mul(other, -1))
        else:
            raise ExpressionMismatchError('Add', self.type, other.type)

    def __mul__(self, other):
        from pydyn.operations.multiplication import Mul, SVMul, SMMul
        if type(other) == float or type(other) == int:
            other = Scalar('(' + str(other) + ')', attr=['Constant'])
        if other.type == Expression.SCALAR:
            return Mul(self, other)
        elif other.type == Expression.VECTOR:
            return SVMul(other, self)
        elif other.type == Expression.MATRIX:
            return SMMul(other, self)
        else:
            raise UndefinedCaseError

    def delta(self):
        print('im in ScalarExpr')
        pass


class Scalar(ScalarExpr):
    """
    Scalar Variable
    """

    def __init__(self, s=None, value=None, attr=None):
        super().__init__()
        self.name = s
        self.value = value
        self.attr = attr

    def __str__(self):
        return self.name

    def delta(self):
        if self.isConstant:
            return Scalar('0', value=0)
        else:
            from pydyn.operations.geometry import Delta
            return Delta(self)


def getScalars(input, attr=None):
    if isinstance(input, list):
        vars = input
    elif isinstance(input, str):
        vars = input.split()
    else:
        return None
    s = []
    for v in vars:
        s.append(Scalar(v, attr=attr))
    return tuple(s)
