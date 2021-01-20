from pydyn.operations.algebraic_manipulation import extract_coeff
from pydyn.operations.expansion import expand
from pydyn.operations.integration import integrate_by_parts_vectors
from pydyn.operations.simplification import full_simplify


def compute_eom(lagrangian, inf_work, variables):
    """
    Computes Lagrange-Hamiltonian dynamics using principle of least action
    """

    # taking variation of lagrangian
    dL = lagrangian.delta()
    # infinitesimal action integral
    dS = dL + inf_work
    dS = full_simplify(dS)

    # integration by parts
    variation_vectors = []
    vector_dots = []
    for v in variables[1]:
        variation_vectors.append(v.variation_vector())
        vector_dots.append(v.variation_vector().diff())

    dS = integrate_by_parts_vectors(dS, vector_dots)

    # simplify Tree
    dS = expand(dS)
    # TODO applyConstraints
    # TODO expand
    # TODO full_simplify
    # TODO organize
    # TODO split
    # TODO cancelTerms
    # extract
    eom_dict = separate_variations(dS, variation_vectors)
    return eom_dict


def separate_variations(inf_action_integral, variation_vectors):
    _dict = {}

    for vec in variation_vectors:
        _dict[vec.__str__()] = (vec, extract_coeff(inf_action_integral, vec))

    return _dict
