from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from ed_domain.core.validation.validation_response import ValidationResponse

T = TypeVar("T")


class ABCValidator(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def validate(self, value: T) -> ValidationResponse: ...

    @abstractmethod
    def validate_many(self, value: list[T]) -> ValidationResponse: ...
