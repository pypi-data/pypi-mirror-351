from recsa import Assembly, BindsiteIdConverter
from recsa.algorithms.assembly_separation import separate_product_if_possible


def perform_intra_exchange(
        assembly: Assembly,
        metal_bs: str, leaving_bs: str, entering_bs: str,
        ) -> tuple[Assembly, Assembly | None]:
    assembly = assembly.deepcopy()
    assembly.remove_bond(metal_bs, leaving_bs)
    assembly.add_bond(entering_bs, metal_bs)

    id_converter = BindsiteIdConverter()
    metal_comp, _ = id_converter.global_to_local(metal_bs)
    # Separate the leaving assembly if possible
    assembly, leaving_assem = separate_product_if_possible(
        assembly, metal_comp)
    return assembly, leaving_assem
