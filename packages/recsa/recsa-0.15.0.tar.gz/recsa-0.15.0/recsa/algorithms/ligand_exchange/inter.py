from recsa import Assembly, BindsiteIdConverter
from recsa.algorithms.assembly_separation import separate_product_if_possible
from recsa.algorithms.union import union_assemblies


def perform_inter_exchange(
        init_assem: Assembly, entering_assem: Assembly,
        metal_bs: str, leaving_bs: str, entering_bs: str,
        ) -> tuple[Assembly, Assembly | None]:
    init_relabel = {
        comp_id: f'init_{comp_id}'
        for comp_id in init_assem.component_ids}
    init_assem = init_assem.rename_component_ids(init_relabel)

    entering_relabel = {
        comp_id: f'entering_{comp_id}'
        for comp_id in entering_assem.component_ids}
    entering_assem = entering_assem.rename_component_ids(entering_relabel)

    metal_bs = f'init_{metal_bs}'
    leaving_bs = f'init_{leaving_bs}'
    entering_bs = f'entering_{entering_bs}'

    init_assem = union_assemblies(init_assem, entering_assem)

    init_assem.remove_bond(metal_bs, leaving_bs)
    init_assem.add_bond(entering_bs, metal_bs)

    # Separate the leaving assembly if possible
    id_converter = BindsiteIdConverter()
    metal_comp, rel_bindsite = id_converter.global_to_local(metal_bs)
    main_assem, leaving_assem = separate_product_if_possible(
        init_assem, metal_comp)
    return main_assem, leaving_assem