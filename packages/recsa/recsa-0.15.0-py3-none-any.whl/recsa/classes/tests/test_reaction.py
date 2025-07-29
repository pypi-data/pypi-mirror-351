import pytest

from recsa import InterReaction, IntraReaction


def test_num_of_reactants():
    intra_reaction = IntraReaction(
        init_assem_id=0,
        product_assem_id=1,
        leaving_assem_id=None,
        metal_bs='M0.a',
        leaving_bs='X0.a',
        entering_bs='L0.a',
        duplicate_count=1
    )
    inter_reaction = InterReaction(
        init_assem_id=0,
        entering_assem_id=1,
        product_assem_id=2,
        leaving_assem_id=None,
        metal_bs='M0.a',
        leaving_bs='X0.a',
        entering_bs='L0.a',
        duplicate_count=1
    )

    # The number of reactants for intra-reaction should always be 1.
    assert intra_reaction.num_of_reactants == 1
    # The number of reactants for inter-reaction should always be 2.
    assert inter_reaction.num_of_reactants == 2


def test_num_of_products_of_intra_reaction():
    """
    Test the number of products in IntraReaction and InterReaction classes.
    """
    intra_with_leaving = IntraReaction(
        init_assem_id=0,
        product_assem_id=1,
        leaving_assem_id=2,
        metal_bs='M0.a',
        leaving_bs='X0.a',
        entering_bs='L0.a',
        duplicate_count=1
    )
    intra_without_leaving = IntraReaction(
        init_assem_id=0,
        product_assem_id=1,
        leaving_assem_id=None,
        metal_bs='M0.a',
        leaving_bs='X0.a',
        entering_bs='L0.a',
        duplicate_count=1
    )

    # The number of products for reactions with leaving assembly should be 2.
    assert intra_with_leaving.num_of_products == 2
    # The number of products for reactions without leaving assembly should be 1.
    assert intra_without_leaving.num_of_products == 1


def test_num_of_products_of_inter_reaction():
    """
    Test the number of products in IntraReaction and InterReaction classes.
    """
    inter_with_leaving = InterReaction(
        init_assem_id=0,
        entering_assem_id=1,
        product_assem_id=2,
        leaving_assem_id=3,
        metal_bs='M0.a',
        leaving_bs='X0.a',
        entering_bs='L0.a',
        duplicate_count=1
    )
    inter_without_leaving = InterReaction(
        init_assem_id=0,
        entering_assem_id=1,
        product_assem_id=2,
        leaving_assem_id=None,
        metal_bs='M0.a',
        leaving_bs='X0.a',
        entering_bs='L0.a',
        duplicate_count=1
    )

    # The number of products for reactions with leaving assembly should be 2.
    assert inter_with_leaving.num_of_products == 2
    # The number of products for reactions without leaving assembly should be 1.
    assert inter_without_leaving.num_of_products == 1


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
