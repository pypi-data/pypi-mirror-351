import base64
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from ..reflection.types.base import ConceptType
from .noun_phrase import NounPhrase

T = TypeVar("T")
NounPhrasesStringLiteral = TypeVar("NounPhrasesStringLiteral", bound=str)


class Question(Generic[NounPhrasesStringLiteral, T]):
    id: str
    noun_phrases: List[NounPhrase]
    concept_type: ConceptType
    choices: List[T]
    text: Optional[str]

    @staticmethod
    def generate_question_id(noun_phrases: NounPhrasesStringLiteral, identifier: str = "") -> str:
        concat = (noun_phrases + identifier).encode("utf-8")
        return base64.b64encode(concat).decode("utf-8")  # NOTE: using base64 instead of hash because the rust's PyO3 yields inconsistent results with it

    def __init__(self, noun_phrases: NounPhrasesStringLiteral, concept_type: Type[T], choices: Optional[List[T]] = None, text: Optional[str] = None, identifier: str = ""):
        """
        Initialize a Question object.

        Args:
            noun_phrases: The name of the concept whose value you want to ask for.
            concept_type: The type that you expect the answer to be.
            choices: The choices for the user to select (if any).
            text: The text you want to present to the user (if any).
            identifier: If for some reason you need to ask for the same
                noun phrases twice, but you expect different answers, use
                this as a 'nonce' to differentiate between them.
        """
        from ..reflection.factory.types import ConceptTypeFactory

        if not isinstance(noun_phrases, str):
            raise TypeError("noun_phrases must be a string literal")
        self.id = self.generate_question_id(noun_phrases, identifier)
        self.noun_phrases = [NounPhrase.from_str(noun_phrase) for noun_phrase in noun_phrases.split("'s ")]
        self.concept_type = ConceptTypeFactory.from_type(concept_type)
        self.choices = choices if choices else []
        self.text = text

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Question) and self.id == other.id

    def __str__(self) -> str:
        ret = "Question("
        nps_text = "'s ".join(str(np) for np in self.noun_phrases)
        if self.text:
            ret += f"{self.text}, "

        ret += f"noun_phrases='{nps_text}'"

        if self.choices:
            ret += f", choices={self.choices}"

        return ret + ")"

    def __repr__(self) -> str:
        return str(self)


class AnswerStorage(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError()

    @abstractmethod
    def set(self, key: str, answer_value: Any):
        raise NotImplementedError()

    @abstractmethod
    def clear(self):
        raise NotImplementedError()

    @abstractmethod
    def unset(self, key: str, fail_if_not_set: bool):
        raise NotImplementedError()


class InMemoryAnswerStorage(AnswerStorage):
    def __init__(self):
        self._answer_map: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self._answer_map.get(key)

    def set(self, key: str, answer_value: Any):
        self._answer_map[key] = answer_value

    def unset(self, key: str, fail_if_not_set: bool):
        if key in self._answer_map:
            del self._answer_map[key]
        elif fail_if_not_set:
            raise ValueError(f"Key {key} is not set")

    def clear(self):
        self._answer_map.clear()


# Use the InMemoryAnswerStorage by default
answer_storage = InMemoryAnswerStorage()


def get_from_context(key: str) -> Optional[Any]:
    return answer_storage.get(key)


def set_answer(key: str, answer_value: Any):
    answer_storage.set(key, answer_value)


def unset_answer(key: str, fail_if_not_set: bool = False):
    answer_storage.unset(key, fail_if_not_set)


def clear_answers():
    answer_storage.clear()


def ask(
    concept_name: NounPhrasesStringLiteral, concept_type: Type[T], text: Optional[str] = None, choices: Optional[List[T]] = None, identifier: str = ""
) -> Union[T, Question[NounPhrasesStringLiteral, T]]:
    """
    Ask a question and get an answer (if available) or a Question object to be
    returned to the user.

    Args:
        concept_name: The name of the concept whose value you want to ask for.
        concept_type: The type that you expect the answer to be.
        choices: The choices for the user to select (if any).
        text: The text you want to present to the user (if any).
        identifier: If for some reason you need to ask for the same
            noun phrases twice, but you expect different answers, use
            this as a 'nonce' to differentiate between them.

    Returns:
        Answer containing the value from the answer map, typed as T (the
        `concept_type`) or a Question (typed as `Question[Literal[concept_name], T]`)
        if the question is not answered yet.
    """

    key = Question.generate_question_id(concept_name, identifier)
    return get_from_context(key) or Question(concept_name, concept_type, choices, text, identifier)
