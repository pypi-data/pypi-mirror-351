import re

from ed_domain.core.validation import ABCValidator, ValidationErrorType
from ed_domain.core.validation.validation_error import ValidationError
from ed_domain.core.validation.validation_response import ValidationResponse


class NameValidator(ABCValidator[str]):
    def validate(
        self,
        value: str,
        location: str = ABCValidator.DEFAULT_ERROR_LOCATION,
    ) -> ValidationResponse:
        name = value
        errors: list[ValidationError] = []

        if not name:
            errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.MISSING_FIELD,
                    "message": "Name is required.",
                    "input": name,
                }
            )
            return ValidationResponse(errors)

        if not re.match(r"^[a-zA-Z]+$", name):
            errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "Name must contain only alphabetic characters.",
                    "input": name,
                }
            )

        if len(name) < 2 or len(name) > 50:
            errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "Name must be between 2 and 15 characters long.",
                    "input": name,
                }
            )

        return ValidationResponse(errors)
