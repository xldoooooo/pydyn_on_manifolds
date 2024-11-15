from pydyn.operations.multiplication import Mul, MVMul
from pydyn.operations.addition import Add
from pydyn.operations.geometry import Dot, Cross, Hat
from pydyn.operations.binary_tree import is_member
from pydyn.operations.transpose import Transpose
from pydyn.operations.algebraic_manipulation import getAB


def col(_scalar, _vector):
    """Collect scalar expression with respect to vector"""
    # Base Cases
    #
    # ADDITION
    if isinstance(_scalar, Add):
        collected_scalars = Add()
        for n in _scalar.nodes:
            collected_scalars += col(n, _vector)
        return collected_scalars

    #  MULTIPLICATION
    elif isinstance(_scalar, Mul):
        return col(_scalar.left, _vector) * col(_scalar.right, _vector)

    elif isinstance(_scalar, Dot):

        if _scalar.right == _vector:
            return Dot(_scalar.right, _scalar.left)

        elif _scalar.left == _vector:
            return _scalar

        # 这里问题在于：如何整理表达式，合并变分项
        elif is_member(_scalar.left, _vector):
            if isinstance(_scalar.left, MVMul):
                if _scalar.left.right == _vector:
                    return Dot(_scalar.left.right, MVMul(_scalar.left.left.T(),_scalar.right))
                else:
                    A, B = getAB(_scalar.left.left, _vector)
                    return Dot(_vector, MVMul(Hat(MVMul(B,_scalar.left.right)),MVMul(A.T(),_scalar.right)))
            else:
                raise NotImplementedError
        
        elif is_member(_scalar.right, _vector):
            if isinstance(_scalar.right, MVMul):
                if _scalar.right.right == _vector:
                    return Dot(_scalar.right.right, MVMul(_scalar.right.left.T(), _scalar.left))
                else:
                    A, B = getAB(_scalar.left.left, _vector)
                    return Dot(_vector, MVMul(Hat(MVMul(B,_scalar.right.right)),MVMul(A.T(),_scalar.left)))
            else:
                raise NotImplementedError
        else:
            return _scalar
    else:
        return _scalar


