from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from ed_domain.core.validation.validation_error import ValidationError

T = TypeVar("T")


class ABCValidator(Generic[T], ABC):
    DEFAULT_ERROR_LOCATION: str = "body"

    def __init__(
        self,
        value: T | list[T],
    ):
        self._is_valid: bool = False
        self._errors: list[ValidationError] = []
        self._value: T | list[T] = value

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    @property
    def errors(self) -> Optional[list[ValidationError]]:
        return self._errors

    @property
    def input(self) -> T | list[T]:
        return self._value

    @abstractmethod
    def validate(self) -> None: ...
