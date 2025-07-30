from typing import Optional

from ed_domain.core.validation.validation_error import ValidationError


class ValidationResponse:
    def __init__(
        self,
        is_valid: bool,
        errors: Optional[list[ValidationError]] = None,
        input: Optional[type] = None,
    ):
        self._is_valid = is_valid
        self._errors = errors
        self._input = input

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    @property
    def errors(self) -> Optional[list[ValidationError]]:
        return self._errors

    @property
    def input(self) -> Optional[type]:
        return self._input

    @staticmethod
    def valid() -> "ValidationResponse":
        return ValidationResponse(is_valid=True)

    @staticmethod
    def invalid(errors: list[ValidationError]) -> "ValidationResponse":
        return ValidationResponse(is_valid=False, errors=errors)
