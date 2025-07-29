from collections.abc import Iterable
from typing import TypeAlias

import pandas as pd

from recsa import InterReaction, IntraReaction

Reaction: TypeAlias = IntraReaction | InterReaction


def reactions_to_df(reactions: Iterable[Reaction]) -> pd.DataFrame:
    reactions = list(reactions)
    df = pd.DataFrame(
        [reaction.to_dict() for reaction in reactions],
        columns=[
            'init_assem_id', 'entering_assem_id', 
            'product_assem_id', 'leaving_assem_id', 
            'metal_bs', 'leaving_bs', 'entering_bs', 
            'duplicate_count', 
        ]
    )
    if isinstance(next(iter(reactions)).init_assem_id, int):
        return df.astype({
            'init_assem_id': int, 'entering_assem_id': pd.Int64Dtype(), 
            'product_assem_id': int, 'leaving_assem_id': pd.Int64Dtype()
        })
    return df
