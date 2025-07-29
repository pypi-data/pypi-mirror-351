from dataclasses import asdict, dataclass
from functools import cached_property
from typing import ClassVar, Literal

from .assembly import Assembly


@dataclass
class IntraReaction:
    init_assem_id: int
    entering_assem_id: ClassVar[None] = None
    product_assem_id: int
    leaving_assem_id: int | None
    metal_bs: str
    leaving_bs: str
    entering_bs: str
    duplicate_count: int

    def to_dict(self):
        d = asdict(self)
        d['entering_assem_id'] = self.entering_assem_id
        return d
    
    @property
    def num_of_reactants(self) -> Literal[1]:
        """Number of reactants in the reaction."""
        return 1
    
    @property
    def num_of_products(self) -> Literal[1, 2]:
        """Number of products in the reaction."""
        if self.leaving_assem_id is None:
            return 1
        return 2


@dataclass
class InterReaction:
    init_assem_id: int
    entering_assem_id: int
    product_assem_id: int
    leaving_assem_id: int | None
    metal_bs: str
    leaving_bs: str
    entering_bs: str
    duplicate_count: int

    def to_dict(self):
        return asdict(self)
    
    @property
    def num_of_reactants(self) -> Literal[2]:
        """Number of reactants in the reaction."""
        return 2
    
    @property
    def num_of_products(self) -> Literal[1, 2]:
        """Number of products in the reaction."""
        if self.leaving_assem_id is None:
            return 1
        return 2


@dataclass(frozen=True)
class IntraReactionEmbedded:
    init_assem: Assembly
    entering_assem: ClassVar[None] = None
    product_assem: Assembly
    leaving_assem: Assembly | None
    metal_bs: str
    leaving_bs: str
    entering_bs: str
    duplicate_count: int

    @cached_property
    def metal_kind(self) -> str:
        return self.init_assem.get_component_kind_of_bindsite(
            self.metal_bs)
    
    @cached_property
    def leaving_kind(self) -> str:
        return self.init_assem.get_component_kind_of_bindsite(
            self.leaving_bs)
    
    @cached_property
    def entering_kind(self) -> str:
        return self.init_assem.get_component_kind_of_bindsite(
            self.entering_bs)


@dataclass(frozen=True)
class InterReactionEmbedded:
    init_assem: Assembly
    entering_assem: Assembly
    product_assem: Assembly
    leaving_assem: Assembly | None
    metal_bs: str
    leaving_bs: str
    entering_bs: str
    duplicate_count: int

    @cached_property
    def metal_kind(self) -> str:
        return self.init_assem.get_component_kind_of_bindsite(
            self.metal_bs)
    
    @cached_property
    def leaving_kind(self) -> str:
        return self.init_assem.get_component_kind_of_bindsite(
            self.leaving_bs)
    
    @cached_property
    def entering_kind(self) -> str:
        return self.entering_assem.get_component_kind_of_bindsite(
            self.entering_bs)
