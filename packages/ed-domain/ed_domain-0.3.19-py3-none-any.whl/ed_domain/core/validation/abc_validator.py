from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from ed_domain.core.validation.validation_error import ValidationError

T = TypeVar("T")


class ABCValidator(Generic[T], ABC):
    DEFAULT_ERROR_LOCATION: str = "body"

    def __init__(self, location: str = DEFAULT_ERROR_LOCATION):
        self._is_valid: bool = False
        self._errors: list[ValidationError] = []
        self._location: str = location

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    @property
    def errors(self) -> Optional[list[ValidationError]]:
        return self._errors

    def validate_many(
        self,
        values: list[T],
    ) -> None:
        for index, value in enumerate(values):
            self.validate(value, f"{self._location}:{index + 1}")

    @abstractmethod
    def validate(
        self,
        value: T,
        location: Optional[str] = None,
    ) -> None: ...
