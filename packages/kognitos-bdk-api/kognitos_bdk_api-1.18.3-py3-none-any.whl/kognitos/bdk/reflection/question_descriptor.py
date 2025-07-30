from dataclasses import dataclass
from typing import List

from ..api.noun_phrase import NounPhrase
from .types import ConceptType


@dataclass
class QuestionDescriptor:
    noun_phrases: List[NounPhrase]
    type: ConceptType
