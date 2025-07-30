from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from ed_domain.core.validation.validation_error import ValidationError

T = TypeVar("T", bound=type)


class ABCValidator(Generic[T], ABC):
    def __init__(
        self,
        value: T,
    ):
        self._is_valid: bool = False
        self._errors: list[ValidationError] = []
        self._value: T = value

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    @property
    def errors(self) -> Optional[list[ValidationError]]:
        return self._errors

    @property
    def input(self) -> T:
        return self._value

    @abstractmethod
    def validate(self) -> None: ...
