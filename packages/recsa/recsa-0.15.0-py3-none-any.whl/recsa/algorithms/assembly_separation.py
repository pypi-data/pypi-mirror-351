from recsa import Assembly
from recsa.algorithms.assembly_connectivity import extract_connected_assemblies

__all__ = ['separate_product_if_possible']


def separate_product_if_possible(
        assembly: Assembly, component_to_be_in_main: str
        ) -> tuple[Assembly, Assembly | None]:
    main_assembly = None
    leaving_assembly = None

    assems = list(extract_connected_assemblies(assembly))
    assert len(assems) in (1, 2)

    if len(assems) == 1:
        return assembly, None

    # Case where leaving assembly exists
    assem1, assem2 = assems
    if component_to_be_in_main in assem1.component_ids:
        return assem1, assem2
    else:
        assert component_to_be_in_main in assem2.component_ids
        return assem2, assem1
