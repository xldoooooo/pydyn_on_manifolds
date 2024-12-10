from pydyn.base.expr import Expression
from pydyn.operations.collection import col
from pydyn.operations.expansion import expand
from pydyn.operations.simplification import MM2MV, simplify, pull
from pydyn.operations.geometry import Dot
from pydyn.operations.addition import Add
from pydyn.operations.multiplication import Mul


def ibp(_expr, _expr_int):
    """implements integration by parts on a collection term
    :_expr_int: expression to be integrated
    :_expr
    """
    if _expr_int.type == Expression.VECTOR:
        if isinstance(_expr, Mul):
            return Mul(ibp(_expr.left, _expr_int), ibp(_expr.right, _expr_int))
        elif isinstance(_expr, Add):
            ibp_expr = Add()
            for n in _expr.nodes:
                ibp_expr += ibp(n, _expr_int)
            return ibp_expr
        elif isinstance(_expr, Dot):
            if _expr.left == _expr_int:
                return Dot(_expr.left.integrate() * (-1), _expr.right.diff())
            else:
                return _expr
        else:
            return _expr
    elif _expr_int.type == Expression.SCALAR:
        raise NotImplementedError
    return _expr


def integrate_by_parts_vectors(expr, vectors):

    # 展开表达式
    expr = expand(expr)
    print("展开表达式")
    print(expr)

    # 提取出向量和矩阵中的标量,消除SM和SV，只剩SS
    expr = pull(expr)
    print("提取标量")
    print(expr)

    # 将MM转为MV, Hat转为Cross
    expr = MM2MV(expr)
    print("MM转为MV")
    print(expr)

    # 常量计算，消去零元和单位元
    expr = simplify(expr)
    print("符号计算，并消去零元和单位元")
    print(expr)

    for vector in vectors:
        
        expr = expand(expr)
        print("再次展开表达式")
        print(expr)

        expr = col(expr, vector)
        print("将需要分部积分的项进行整理")  
        print(expr)

        # expr = pull(expr)
        # expr = MM2MV(expr)
        expr = simplify(expr)
        print("再次化简")  
        print(expr)

        expr = ibp(expr, vector)
        print("分部积分")
        print(expr)

        expr = expand(expr)
        expr = pull(expr)
        expr = MM2MV(expr)
        expr = simplify(expr)
        print("再次化简")  
        print(expr)

    return expr

