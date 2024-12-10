from pydyn.operations.binary_tree import has_nested_add
from pydyn.operations.geometry import Dot, Cross, Vee, Hat
from pydyn.operations.addition import Add, VAdd, MAdd
from pydyn.operations.multiplication import Mul, SMMul, SVMul, MVMul, VVMul, MMMul
from pydyn.base.expr import Expression
from pydyn.base.matrices import MatrixExpr
from pydyn.base.scalars import ScalarExpr
from pydyn.base.vectors import VectorExpr
from pydyn.utils.errors import UndefinedCaseError


def expand_scalar(expr):
    if isinstance(expr, Add): # 标量加法
        expanded_expr = Add()
        for n in expr.nodes:
            expanded_expr += expand(n)
        return expanded_expr

    elif isinstance(expr, Mul): # 标量乘法
        if isinstance(expr.left, Add) and isinstance(expr.right, Add):
            """(a+b)(c+d) = ac + ad + bc + bd"""
            expanded_expr = Add()
            for nl in expr.left.nodes:
                for nr in expr.right.nodes:
                    expanded_expr += expand(nl * nr)
            return expanded_expr

        elif isinstance(expr.left, Add):
            """(a+b)c = ac + bc"""
            expanded_expr = Add()
            for n in expr.left.nodes:
                expanded_expr += expand(n * expr.right)
            return expanded_expr

        elif isinstance(expr.right, Add):
            """a(b+c) = ab + ac"""
            expanded_expr = Add()
            for n in expr.right.nodes:
                expanded_expr += expand(expr.left * n)
            return expanded_expr

        else:
            if has_nested_add(expr):
                return expand(expand(expr.left) * expand(expr.right))
            else:
                return expr

    elif isinstance(expr, Dot): # 向量点乘
        if isinstance(expr.left, VAdd) and isinstance(expr.right, VAdd):
            """(x+y).(u+v) = x.u + x.v + y.u + y.v"""
            expanded_expr = Add()
            for nl in expr.left.nodes:
                for nr in expr.right.nodes:
                    expanded_expr += expand(Dot(nl, nr))
            return expanded_expr
        elif isinstance(expr.right, VAdd):
            """x.(u+v) = x.u + x.v"""
            expanded_expr = Add()
            for n in expr.right.nodes:
                expanded_expr += expand(Dot(expr.left, n))
            return expanded_expr
        elif isinstance(expr.left, VAdd):
            """(x+y).u = x.u + y.u"""
            expanded_expr = Add()
            for n in expr.left.nodes:
                expanded_expr += expand(Dot(n, expr.right))
            return expanded_expr
        else:
            if has_nested_add(expr):
                return expand(Dot(expand(expr.left), expand(expr.right)))
            else:
                return expr # 如果没有嵌套加法，则返回自身

    elif isinstance(expr, VVMul):
        raise NotImplementedError

    return expr # 无法化简则返回自身


def expand_vector(expr):
    if isinstance(expr, VAdd): # 向量加法
        expanded_expr = VAdd()
        for n in expr.nodes:
            expanded_expr += expand(n)
        return expanded_expr

    elif isinstance(expr, MVMul): # 矩阵乘向量
        if isinstance(expr.left, MAdd): # 矩阵拆分
            """(A+B)x = Ax+Bx"""
            expanded_expr = VAdd()
            for n in expr.left.nodes:
                expanded_expr += expand(MVMul(n, expr.right))
            return expanded_expr
        elif isinstance(expr.right, VAdd): # 向量拆分
            """A(x+y) = Ax + Ay"""
            expanded_expr = VAdd()
            for n in expr.right.nodes:
                expanded_expr += expand(MVMul(expr.left, n))
            return expanded_expr
        else:
            if has_nested_add(expr):
                return expand(MVMul(expand(expr.left), expand(expr.right)))
            else:
                return expr # 如果没有嵌套加法，则返回自身

    elif isinstance(expr, SVMul): # 标量乘向量
        if isinstance(expr.right, VAdd):
            """(x+y)a=xa+ya"""
            expanded_expr = VAdd()
            for n in expr.right.nodes:
                expanded_expr += expand(SVMul(expr.left, n))
            return expanded_expr
        else:
            if has_nested_add(expr):
                return expand(SVMul(expand(expr.left), expand(expr.right)))
            else:
                return expr

    elif isinstance(expr, Cross): 
        if isinstance(expr.left, VAdd) and isinstance(expr.right, VAdd):
            expanded_expr = VAdd()
            for nl in expr.left.nodes:
                for nr in expr.right.nodes:
                    expanded_expr += expand(Cross(nl, nr))
            return expanded_expr
        elif isinstance(expr.left, VAdd):
            expanded_expr = VAdd()
            for n in expr.left.nodes:
                expanded_expr += expand(Cross(n, expr.right))
            return expanded_expr
        elif isinstance(expr.right, VAdd):
            """x.(u+v) = x.u + x.v"""
            expanded_expr = VAdd()
            for n in expr.right.nodes:
                expanded_expr += expand(Cross(expr.left, n))
            return expanded_expr
        else:
            if has_nested_add(expr):
                return expand(Cross(expand(expr.left), expand(expr.right)))
            else:
                return expr

    elif isinstance(expr, Vee):
        return Vee(expand(expr))

    return expr


def expand_matrix(expr):
    if isinstance(expr, MAdd):
        expanded_expr = MAdd()
        for n in expr.nodes:
            expanded_expr += expand(n)
        return expanded_expr

    elif isinstance(expr, MMMul):
        if isinstance(expr.left, MAdd) and isinstance(expr.right, MAdd):
            expanded_expr = MAdd()
            for nl in expr.left.nodes:
                for nr in expr.right.nodes:
                    expanded_expr += expand(nl * nr)
            return expanded_expr
        elif isinstance(expr.left, MAdd):
            expanded_expr = MAdd()
            for nl in expr.left.nodes:
                expanded_expr += expand(nl * expr.right)
            return expanded_expr
        elif isinstance(expr.right, MAdd):
            expanded_expr = MAdd()
            for nr in expr.right.nodes:
                expanded_expr += expand(expr.left * nr)
            return expanded_expr
        else:
            if has_nested_add(expr):
                return expand(MMMul(expand(expr.left), expand(expr.right)))
            else:
                return expr

    elif isinstance(expr, SMMul):
        raise Exception('SSMul in expand_matrix is not implemented')

    elif isinstance(expr, VVMul):
        raise Exception('VVMul in expand_matrix is not implemented')

    elif isinstance(expr, Hat):
        if isinstance(expr.expr, VAdd):
            expanded_expr = MAdd()
            for n in expr.expr.nodes:
                expanded_expr += Hat(expand(n))
            return expanded_expr
        return Hat(expr.expr)

    return expr


def expand(self):
    if self.type == Expression.SCALAR:
        return expand_scalar(self)
    elif self.type == Expression.VECTOR:
        return expand_vector(self)
    elif self.type == Expression.MATRIX:
        return expand_matrix(self)
    else:
        raise UndefinedCaseError