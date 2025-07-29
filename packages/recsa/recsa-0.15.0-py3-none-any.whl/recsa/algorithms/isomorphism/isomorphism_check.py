from collections.abc import Mapping

from recsa import Assembly, Component
from recsa.algorithms.aux_edge_existence import has_aux_edges
from recsa.algorithms.isomorphism.pure_isomorphism_check import \
    pure_is_isomorphic
from recsa.algorithms.isomorphism.rough_isomorphism_check import \
    is_roughly_isomorphic

__all__ = ['is_isomorphic']


def is_isomorphic(
        assem1: Assembly, assem2: Assembly,
        component_structures: Mapping[str, Component]
        ) -> bool:
    """Check if two assemblies are isomorphic."""
    if assem1.component_kinds != assem2.component_kinds:
        return False
    
    if has_aux_edges(assem1, component_structures):
        return pure_is_isomorphic(assem1, assem2, component_structures)
    else:
        return is_roughly_isomorphic(assem1, assem2)
