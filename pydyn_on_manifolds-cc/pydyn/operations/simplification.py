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
    若最终结果为标量，则只剩SS乘法
    若最终结果为向量，则只剩SS和一个SV乘法
    若最终结果为矩阵，则只剩一个SM乘法
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
            elif has_nested_scalars(expr):
                # print(expr)
                return pull(Dot(pull(expr.left), pull(expr.right)))
            else:
                return expr
        else:
            return expr

    elif isinstance(expr, VectorExpr):
        if isinstance(expr, VAdd):
            pulled_expr = VAdd()
            for n in expr.nodes:
                # print(n)
                # print(pull(n))
                # if isinstance(pull(n),SVMul):
                #     print(pull(n).left)
                # print(type(pull(n)))
                pulled_expr += pull(n)
            return pulled_expr
        elif isinstance(expr, MVMul):
            if isinstance(expr.left, SMMul):
                return pull(SVMul(expr.left.left, MVMul(expr.left.right, expr.right)))
            elif isinstance(expr.right, SVMul):
                return pull(SVMul(expr.right.left, MVMul(expr.left, expr.right.right)))
            elif has_nested_scalars(expr):
                return pull(MVMul(pull(expr.left), pull(expr.right)))
            else:
                return expr
        elif isinstance(expr, SVMul):
            if isinstance(expr.right, SVMul):
                return pull(SVMul(expr.left*expr.right.left, expr.right.right))
            elif has_nested_scalars(expr.right):
                return pull(SVMul(pull(expr.left), pull(expr.right)))
            else:
                return expr
        elif isinstance(expr, Cross):
            if isinstance(expr.left, SVMul) and isinstance(expr.right, SVMul):
                return pull(SVMul(expr.left.left * expr.right.left, Cross(expr.left.right, expr.right.right)))
            elif isinstance(expr.left, SVMul):
                return pull(SVMul(expr.left.left, Cross(expr.left.right, expr.right)))
            elif isinstance(expr.right, SVMul):
                return pull(SVMul(expr.right.left, Cross(expr.left, expr.right.right)))
            elif has_nested_scalars(expr):
                return pull(Cross(pull(expr.left), pull(expr.right)))
            else:
                return expr
        else:
            return expr

    elif isinstance(expr, MatrixExpr):
        if isinstance(expr, MMMul):
            if isinstance(expr.left, SMMul) and isinstance(expr.right, SMMul):
                return pull(SMMul(expr.left.left * expr.right.left, expr.left.right * expr.right.right))
            elif isinstance(expr.right, SMMul):
                return pull(SMMul(expr.right.left, MMMul(expr.left, expr.right.right)))
            elif isinstance(expr.left, SMMul):
                return pull(SMMul(expr.left.left, MMMul(expr.left.right, expr.right)))
            elif has_nested_scalars(expr):
                return pull(MMMul(pull(expr.left), pull(expr.right)))
            else:
                return expr

        elif isinstance(expr, SMMul):
            if isinstance(expr.right, SMMul):
                return pull(SMMul(expr.left*expr.right.left, expr.right.right))
            elif has_nested_scalars(expr.right):
                return pull(SMMul(expr.left, pull(expr.right)))
            else:
                return expr
        else:
            return expr

    else:
        return expr


def MM2MV(expr):
    """
    对于标量，将MM去掉，全部拆成MV，方便提取Dot两边的矩阵元素
    对于向量，将MM去掉，全部拆成MV
    将Hat全部转化为Cross
    """
    if isinstance(expr, ScalarExpr):
        if isinstance(expr, Add):
            MM2MV_expr = Add()
            for n in expr.nodes:
                MM2MV_expr += MM2MV(n)
            return MM2MV_expr
        elif isinstance(expr, Mul):
            return MM2MV(expr.left) * MM2MV(expr.right)
        elif isinstance(expr, Dot):
            if isinstance(expr.left, MVMul) and isinstance(expr.right, MVMul):
                return Dot(MM2MV(expr.left), MM2MV(expr.right))
            elif isinstance(expr.right, MVMul):
                return Dot(expr.left, MM2MV(expr.right))
            elif isinstance(expr.left, MVMul):
                return Dot(MM2MV(expr.left), expr.right)
            else:
                return expr
        else:
            return expr

    elif isinstance(expr, VectorExpr):
        if isinstance(expr, VAdd):
            MM2MV_expr = VAdd()
            for n in expr.nodes:
                print(n)
                print(MM2MV(n))
                MM2MV_expr += MM2MV(n)
            return MM2MV_expr
        elif isinstance(expr, SVMul):
            return SVMul(expr.left, MM2MV(expr.right))
        elif isinstance(expr, MVMul):
            if isinstance(expr.left, Hat):
                return Cross(expr.left.expr, MM2MV(expr.right))
            elif isinstance(expr.left, MMMul):
                return MM2MV(MVMul(expr.left.left, MM2MV(MVMul(expr.left.right, expr.right))))
            elif isinstance(expr.right, MVMul):
                return MVMul(expr.left, MM2MV(expr.right))
            else:
                return expr
        else:
            return expr
    else:
        return expr


def combine(expr):
    """
    计算每一项的常数标量系数
    """
    if isinstance(expr, Mul):
        return combine(expr.left) * combine(expr.right)
    elif expr.value is not None:
        return expr.value
    else:
        return 1


def has_zeros(expr):
    """
    检查单个表达式中是否存在零元，存在则返回True
    """
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
    """
    返回表达式中的符号部分
    """
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
    elif expr.isNumeric:
        return None
    else:
        return expr


def simplify(expr):
    """
        常量计算+符号计算，挤掉零元和单位元
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
                    # print(n)
                    # print(simplify(n))
                    simplified_n = simplify(n)
                    if simplified_n.isZero:
                        continue
                    else:
                        sym_exprs.append(simplified_n)
            if value != 0:
                sym_exprs.append(Scalar(str(value), value=value, attr=['Constant']))
            return Add(sym_exprs)

        elif isinstance(expr, Mul):
            # print(expr)
            # print(expr.left)
            # print(expr.right)
            if has_zeros(expr):
                return Scalar('0', value=0, attr=['Constant', 'Zero'])
            elif expr.left.value == 1:
                return simplify(expr.right)
            elif expr.right.value == 1:
                return simplify(expr.left)
            elif expr.left.value is not None and expr.right.value is not None:
                val = expr.left.value * expr.right.value
                return Scalar('(' + str(val) + ')', value=val, attr=['Constant'])
            elif expr.left.value is not None or expr.right.value is not None: # 存在非0和1的常量系数
                # print(expr)
                val = combine(expr)
                # print(val)
                left = Scalar('(' + str(val) + ')', value=val, attr=['Constant'])
                right = terms(expr)
                if right:
                    if val == 1: # 系数为1，则扔掉系数
                        return simplify(right)
                    return Mul(left, simplify(right))
                else:
                    return left
            else:
                left = simplify(expr.left)
                # print(left)
                right = simplify(expr.right)
                # print(right)
                if left.value is not None or right.value is not None:
                    return simplify(Mul(left, right))
                else:
                    return Mul(simplify(expr.left), simplify(expr.right))
            
        elif isinstance(expr, Dot):
            if isinstance(expr.left, MVMul) and isinstance(expr.right, MVMul):
                if expr.left.left.isManifold and expr.right.left.isManifold and expr.left.left == expr.right.left:
                    return simplify(Dot(expr.left.right, expr.right.right))
            if isinstance(expr.left, Cross):
                if expr.left.right == expr.right:
                    return Scalar('0', value=0, attr=['Constant', 'Zero'])
            if isinstance(expr.left, Cross) and isinstance(expr.right, Cross):
                if isinstance(expr.left.left, Cross) and expr.left.right == expr.right.right:
                    if expr.left.left.left == expr.right.left:
                        return simplify(Dot(Cross(expr.right.left, Cross(expr.left.left.right, expr.left.right)), expr.right))
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
                    # print(n)
                    # print(simplify(n))
                    sym_exprs.append(simplify(n))
            return VAdd(sym_exprs)
        elif isinstance(expr, SVMul):
            # print(expr.left)
            # print(simplify(expr.left))
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

    expr = pull(expr)
    expr = MM2MV(expr)
    expr = simplify(expr)
    return expr
    

