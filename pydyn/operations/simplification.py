from pydyn.operations.addition import Add, MAdd, VAdd
from pydyn.operations.binary_tree import has_nested_scalars
from pydyn.operations.multiplication import Mul, SVMul, MVMul, SMMul, MMMul
from pydyn.operations.geometry import Dot, Cross, Hat
from pydyn.base.matrices import MatrixExpr, I, O
from pydyn.base.scalars import ScalarExpr, Scalar
from pydyn.base.vectors import VectorExpr, ZeroVector
from pydyn.operations.expansion import expand
from pydyn.operations.transpose import Transpose


def pull(expr):
    """
    将向量或矩阵中的标量元素提取出来 
    """
    if isinstance(expr, ScalarExpr):
        if isinstance(expr, Add):
            pulled_expr = Add()
            for n in expr.nodes:
                pulled_expr += pull(n)
            return pulled_expr
        elif isinstance(expr, Mul):
            return pull(expr.left) * pull(expr.right)
        elif isinstance(expr, Dot):
            if isinstance(expr.left, SVMul):
                return pull(expr.left.left) * pull(Dot(expr.left.right, expr.right))
            elif isinstance(expr.right, SVMul):
                return pull(expr.right.left) * pull(Dot(expr.left, expr.right.right))
            else:
                if has_nested_scalars(expr):
                    return pull(Dot(pull(expr.left), pull(expr.right)))
                else:
                    return expr
        else:
            return expr

    elif isinstance(expr, VectorExpr):
        if isinstance(expr, MVMul):
            if isinstance(expr.left, SMMul):
                return pull(SVMul(pull(expr.left.left), pull(MVMul(expr.left.right, expr.right))))
            elif isinstance(expr.right, SVMul):
                return pull(SVMul(pull(expr.right.left), pull(MVMul(expr.left, expr.right.right))))
            else:
                if has_nested_scalars(expr.left) or has_nested_scalars(expr.right):
                    return pull(MVMul(pull(expr.left), pull(expr.right)))
                else:
                    return expr
        elif isinstance(expr, SVMul):
            if isinstance(expr.right, SVMul):
                return pull(SVMul(pull(expr.left*expr.right.left), pull(expr.right.right)))
            else:
                if has_nested_scalars(expr):
                    return pull(SVMul(pull(expr.left), pull(expr.right)))
                else:
                    return expr
        else:
            return expr

    elif isinstance(expr, MatrixExpr):
        if isinstance(expr, MMMul):
            if isinstance(expr.left, SMMul) and isinstance(expr.right, SMMul):
                return pull(SMMul(pull(expr.left.left * expr.right.left), pull(expr.left.right * expr.right.right)))
            elif isinstance(expr.right, SMMul):
                return pull(SMMul(pull(expr.right.left), pull(MMMul(expr.left, expr.right.right))))
            elif isinstance(expr.left, SMMul):
                return pull(SMMul(pull(expr.left.left), pull(MMMul(expr.left.right, expr.right))))
            else:
                if has_nested_scalars(expr):
                    return pull(MMMul(pull(expr.left), pull(expr.right)))
                else:
                    return expr

        elif isinstance(expr, SMMul):
            if isinstance(expr.right, SMMul):
                return pull(SMMul(pull(expr.left*expr.right.left), pull(expr.right.right)))
            else:
                if has_nested_scalars(expr):
                    return pull(SMMul(pull(expr.left), pull(expr.right)))
                else:
                    return expr
        else:
            return expr

    else:
        return expr


def vector_rules(expr):
    """
        q'*q = 1, R'*R = I, 叉乘法则
        dq'*dq = 0,
    """
    # 标量加法
    if isinstance(expr, Add):
        ruled_expr = Add()
        for n in expr.nodes:
            ruled_expr += vector_rules(n)
        return ruled_expr
    # 标量乘法
    elif isinstance(expr, Mul):
        return vector_rules(expr.left) * vector_rules(expr.right)
    # Dot处理
    elif isinstance(expr, Dot):
        if isinstance(expr.right, MVMul):
            return Dot(expr.left, vector_rules(expr.right))
        else:
            if expr.left.isUnitNorm and expr.right.isUnitNorm and (expr.left == expr.right):
                return Scalar('1', value=1, attr=['Constant', 'Ones'])
            else:
                return expr
    
    elif isinstance(expr, MVMul):
        if isinstance(expr.right, MVMul):
            return vector_rules(expr.left) * vector_rules(expr.right)
        else:
            return expr

    elif isinstance(expr, MMMul):
        if isinstance(expr.left, Hat):
            return Hat(vector_rules(expr.left.expr)) * vector_rules(expr.right)
        elif isinstance(expr.left,MMMul):
            return vector_rules(expr.left) * expr.right
        else:
            return expr
    elif isinstance(expr, Hat):
        return Hat(vector_rules(expr.expr))
    elif isinstance(expr, Transpose):
        return Transpose(vector_rules(expr.expr))
        
    else:
        return expr


def combine(expr):
    if isinstance(expr, Mul):
        return combine(expr.left) * combine(expr.right)
    elif expr.value is not None:
        return expr.value
    else:
        return 1


def has_zeros(expr):
    if isinstance(expr, Mul):
        return has_zeros(expr.left) or has_zeros(expr.right)
    elif expr.value is not None:
        if expr.value == 0:
            return True
        else:
            return False
    else:
        return False


def any_terms(expr):
    if isinstance(expr, Mul):
        return any_terms(expr.left) or any_terms(expr.right)
    elif expr.value is not None:
        return False
    else:
        return True


def terms(expr):
    if isinstance(expr, Mul):
        if expr.left.value is not None:
            return terms(expr.right)
        elif expr.right.value is not None:
            return terms(expr.left)
        else:
            if any_terms(expr.left) and any_terms(expr.right):
                return terms(expr.left) * terms(expr.right)
            elif any_terms(expr.left):
                return terms(expr.left)
            else:
                return terms(expr.right)
    else:
        return expr


def simplify(expr):
    """
        常量计算，挤掉零元和单位元
    """
    if isinstance(expr, ScalarExpr):  
        if isinstance(expr, Add):
            """Remove zeros"""
            value = 0
            sym_exprs = []
            for n in expr.nodes:
                if n.isZero:
                    continue
                elif n.value is not None:
                    value += n.value
                else:
                    sym_exprs.append(simplify(n))
            if value != 0:
                sym_exprs.append(Scalar(str(value), value=value, attr=['Constant', 'Zero']))
            return Add(sym_exprs)

        elif isinstance(expr, Mul):
            if has_zeros(expr):
                return Scalar('0', value=0, attr=['Constant', 'Zero'])
            elif expr.left.value == 1:
                return expr.right
            elif expr.right.value == 1:
                return expr.left
            elif expr.left.value is not None or expr.right.value is not None:
                val = combine(expr)
                left = Scalar('(' + str(val) + ')', value=val, attr=['Constant'])
                right = terms(expr)
                if val == 1:
                    return right
                return Mul(left, right)
            else:
                return Mul(simplify(expr.left), simplify(expr.right))
            
        elif isinstance(expr, Dot):
            if isinstance(expr.left, MVMul) and isinstance(expr.right, MVMul):
                if expr.left.left.isManifold and expr.right.left.isManifold and expr.left.left == expr.right.left:
                    return simplify(Dot(expr.left.right, expr.right.right))
            return Dot(simplify(expr.left), simplify(expr.right))
        else:
            return expr

    elif isinstance(expr, VectorExpr):
        if isinstance(expr, VAdd):
            sym_exprs = []
            for n in expr.nodes:
                if n.isZero:
                    continue
                elif isinstance(n, SVMul) and n.value == 0:
                    continue
                else:
                    sym_exprs.append(simplify(n))
            return VAdd(sym_exprs)
        elif isinstance(expr, SVMul):
            return SVMul(simplify(expr.left), simplify(expr.right))
        elif isinstance(expr, MVMul):
            if expr.left == I:
                return expr.right
            elif expr.left == O:
                return ZeroVector
            else:
                return MVMul(simplify(expr.left), simplify(expr.right))
        else:
            return expr

    elif isinstance(expr, MatrixExpr):
        if isinstance(expr, MAdd):
            sym_exprs = []
            for n in expr.nodes:
                if n.isZero:
                    continue
                elif isinstance(n, SMMul) and n.value == 0:
                    continue
                else:
                    sym_exprs.append(simplify(n))
            return MAdd(sym_exprs)
        elif isinstance(expr, SMMul):
            return SMMul(simplify(expr.left), simplify(expr.right))
        elif isinstance(expr, MMMul):
            if expr.left == O or expr.right == O:
                return O
            elif expr.left == I:
                return simplify(expr.right)
            elif expr.right == I:
                return simplify(expr.left)
            else:
                return MMMul(simplify(expr.left), simplify(expr.right))
        elif isinstance(expr, Hat):
            return Hat(simplify(expr.expr))
        return expr
    elif isinstance(expr, Transpose):
        return Transpose(simplify(expr.expr))

    return expr


def full_simplify(expr):
    """simplifies expr using standard operations"""

    # 展开表达式
    expr_ = expand(expr)
    
    # 提取出向量和矩阵中的标量,消除SM和SV，只剩SS
    expr_ = pull(expr_)

    # 常量计算，消去零元和单位元
    expr_ = simplify(expr_)
    
    return expr_
