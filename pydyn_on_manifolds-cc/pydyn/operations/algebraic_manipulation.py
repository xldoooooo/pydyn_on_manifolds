from pydyn.operations.transpose import Transpose
from pydyn.base.matrices import Matrix, ZeroMatrix, I
from pydyn.base.vectors import Vector
from pydyn.base.expr import Expression
from pydyn.utils.errors import UndefinedCaseError
from pydyn.operations.addition import Add, VAdd, MAdd
from pydyn.operations.multiplication import Mul, SVMul, SMMul, VVMul, MVMul, MMMul
from pydyn.operations.geometry import Dot, Cross, Hat
from pydyn.base.scalars import One, Number
from pydyn.operations.simplification import MM2MV, simplify, pull 


def extract_coeff(expr, sym):
    if expr.type == Expression.SCALAR:
        return efs(expr, sym)
    elif expr.type == Expression.VECTOR:
        raise NotImplementedError
    elif expr.type == Expression.MATRIX:
        raise NotImplementedError
    else:
        raise UndefinedCaseError


def efs(expr, vec):
    """Extract From Scalar"""
    # Add
    if isinstance(expr, Add):
        sym_efs_exprs = []
        for n in expr.nodes:
            if n.has(vec): 
                sym_efs_exprs.append(efs(n, vec))
        return VAdd(sym_efs_exprs)

    elif isinstance(expr, Mul):
        if expr.left.has(vec) and expr.right.has(vec):
            raise NotImplementedError
        elif expr.left.has(vec):
            return SVMul(expr.right, efs(expr.left, vec))
        elif expr.right.has(vec):
            return SVMul(expr.left, efs(expr.right, vec))
        else:
            return Vector('O', attr=['Constant', 'Zero'])

    elif isinstance(expr, Dot):
        if expr.left.has(vec) and expr.right.has(vec):
            raise NotImplementedError
        
        elif expr.left.has(vec):
            if expr.left == vec:
                return expr.right
            elif isinstance(expr.left, MVMul):
                if expr.left.right == vec:
                    return MVMul(expr.left.left.T(), expr.right)
                elif isinstance(expr.left.right, Cross):
                    A = getA(expr.left.right, vec)
                    expr = MVMul(A.T(), MVMul(expr.left.left.T(), expr.right))
                    return expr
                else:
                    raise UndefinedCaseError
            elif isinstance(expr.left, Cross):
                A = getA(expr.left, vec)
                expr = MVMul(A.T(), expr.right)
                return expr
            else:
                raise UndefinedCaseError
            
        elif expr.right.has(vec):
            return efs(Dot(expr.right, expr.left))
        else:
            return Vector('O', attr=['Constant', 'Zero'])

    elif isinstance(expr, VVMul):
        raise NotImplementedError

    return expr


def getA(expr, vec):
    """
    从cross向量中提取vec的左边矩阵，即 Cross=A * vec
    """
    if expr == vec:
        return I
    elif isinstance(expr, Cross):
        if expr.left.has(vec):
            A = getA(expr.left, vec)
            if A == I:
                return Number(-1)*Hat(expr.right)
            else:
                return Number(-1)*MMMul(Hat(expr.right), A)
        elif expr.right.has(vec):
            A = getA(expr.right, vec)
            if A == I:
                return Hat(expr.left)
            else:    
                return MMMul(Hat(expr.left), A)
    else:
        raise UndefinedCaseError

def leftMulTrans(expr, A):
    """
    将复合矩阵A的转置左乘到expr向量上
    """
    AT = A.T()
    AT = pull(AT)
    if isinstance(AT, SMMul):
        a = simplify(AT.left)
        M = AT.right
    else:
        a = One
        M = AT
    while isinstance(M, MMMul):
        expr = MVMul(M.right, expr)
        M = M.left
    expr = MVMul(M, expr)
    return a, expr
    



