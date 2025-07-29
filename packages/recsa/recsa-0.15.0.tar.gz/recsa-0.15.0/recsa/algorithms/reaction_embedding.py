from typing import overload

from recsa import (Assembly, InterReaction, InterReactionEmbedded,
                   IntraReaction, IntraReactionEmbedded)


@overload
def embed_assemblies_into_reaction(
    reaction: IntraReaction,
    id_to_assembly: dict[int, Assembly]
    ) -> IntraReactionEmbedded: ...
@overload
def embed_assemblies_into_reaction(
    reaction: InterReaction,
    id_to_assembly: dict[int, Assembly]
    ) -> InterReactionEmbedded: ...
def embed_assemblies_into_reaction(
        reaction: IntraReaction | InterReaction,
        id_to_assembly: dict[int, Assembly]):
    """Embed the assemblies into the reaction."""
    init_assem = id_to_assembly[reaction.init_assem_id]
    product_assem = id_to_assembly[reaction.product_assem_id]
    
    if reaction.leaving_assem_id is None:
        leaving_assem = None
    else:
        leaving_assem = id_to_assembly[reaction.leaving_assem_id]

    if isinstance(reaction, IntraReaction):
        return IntraReactionEmbedded(
            init_assem, product_assem, leaving_assem,
            reaction.metal_bs, reaction.leaving_bs, reaction.entering_bs,
            reaction.duplicate_count
        )
    elif isinstance(reaction, InterReaction):
        entering_assem = id_to_assembly[reaction.entering_assem_id]
        return InterReactionEmbedded(
            init_assem, entering_assem, product_assem, leaving_assem,
            reaction.metal_bs, reaction.leaving_bs, reaction.entering_bs,
            reaction.duplicate_count
        )
    else:
        raise ValueError("Invalid reaction type")
