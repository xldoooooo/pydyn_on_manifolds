from pydyn.operations.algebraic_manipulation import extract_coeff
from pydyn.operations.expansion import expand
from pydyn.operations.integration import integrate_by_parts_vectors
from pydyn.operations.simplification import full_simplify
from pydyn.operations.print_tree import print_latex

def compute_eom(lagrangian, inf_work, variables):
    """
    Computes Lagrange-Hamiltonian dynamics using principle of least action
    """

    # taking variation of lagrangian
    dL = lagrangian.delta()

    # infinitesimal action integral
    dS = dL + inf_work

    # gather the variations (vectors)
    variation_vectors = []
    variation_vector_dots = []
    for vec in variables[1]:
        x = vec.get_variation_vector()
        variation_vectors.append(x)
        variation_vector_dots.append(x.diff())
    for mat in variables[2]:
        x = mat.get_variation_vector()
        variation_vectors.append(x)
        variation_vector_dots.append(x.diff())

    dS = integrate_by_parts_vectors(dS, variation_vector_dots)

    eom_dict = separate_variations(dS, variation_vectors)
    return eom_dict


def separate_variations(inf_action_integral, variation_vectors):
    _dict = {}
    for vec in variation_vectors:
        dyn_eqn = extract_coeff(inf_action_integral, vec)
        print("分离广义坐标的变分，生成动力学方程")
        print(dyn_eqn)
        dyn_eqn = full_simplify(dyn_eqn)
        print("化简后")
        print(dyn_eqn)
        _dict[vec.__str__()] = (vec, dyn_eqn)

    return _dict
