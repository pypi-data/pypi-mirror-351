from collections.abc import Callable
from typing import TypeAlias

from recsa import InterReactionEmbedded, IntraReactionEmbedded

ReactionDetailed: TypeAlias = IntraReactionEmbedded | InterReactionEmbedded


class ReactionClassifier:
    def __init__(
            self, 
            classification_rule: Callable[[ReactionDetailed], str]
            ) -> None:
        self.classification_rule = classification_rule

    def classify(self, reaction: ReactionDetailed) -> str:
        return self.classification_rule(reaction)
