from pydyn.operations.multiplication import Mul, MVMul, MMMul
from pydyn.operations.addition import Add
from pydyn.operations.geometry import Dot, Cross, Hat
from pydyn.operations.transpose import Transpose
from pydyn.operations.simplification import MM2MV, simplify, pull 
from pydyn.operations.algebraic_manipulation import getA, leftMulTrans


# 从标量中提取指定的向量
def col(expr, _vector):
    """Collect scalar expression with respect to vector"""
    # Base Cases
    #
    # ADDITION
    if isinstance(expr, Add):
        collected_exprs = Add()
        for n in expr.nodes:
            collected_exprs += col(n, _vector)
            # print(col(n, _vector))
        return collected_exprs

    #  MULTIPLICATION
    elif isinstance(expr, Mul):
        return col(expr.left, _vector) * col(expr.right, _vector)

    elif isinstance(expr, Dot):
        # 这里问题在于：如何整理表达式，合并变分项
        if expr.left.has(_vector):
            if expr.left == _vector:
                return expr
            elif isinstance(expr.left, MVMul):
                if expr.left.right == _vector:
                    a, expr = leftMulTrans(expr.right, expr.left.left)
                    return a*Dot(_vector, expr)
                    # return Dot(_vector, MVMul(expr.left.left.T(), expr.right))
                elif isinstance(expr.left.right, Cross):
                    A = getA(expr.left.right, _vector)
                    a1, expr1 = leftMulTrans(expr.right, expr.left.left)
                    a2, expr2 = leftMulTrans(expr1, A)
                    expr = a1*a2*Dot(_vector, expr2)
                    return expr
            elif isinstance(expr.left, Cross):
                if expr.left.left == _vector:
                    return Dot(expr.left.left, Cross(expr.left.right, expr.right))
                elif expr.left.right == _vector:
                    return Dot(expr.left.right, Cross(expr.right, expr.left.left))
                else:
                    A = getA(expr.left.right, _vector)
                    a, expr = leftMulTrans(Cross(expr.right, expr.left.left), A)
                    expr = a*Dot(_vector, expr)
                return expr
        
        elif expr.right.has(_vector):
            return col(Dot(expr.right, expr.left))
        
        else:
            return expr
    else:
        return expr
    



