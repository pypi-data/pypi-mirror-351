import re

from ed_domain.core.validation import ABCValidator, ValidationErrorType


class NameValidator(ABCValidator[str]):
    def validate(
        self,
        value: str,
        location: str | None = None,
    ) -> None:
        name = value
        location = location or self._location

        if not name:
            self._errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.MISSING_FIELD,
                    "message": "Name is required.",
                    "input": name,
                }
            )

            return

        if not re.match(r"^[a-zA-Z]+$", name):
            self._errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "Name must contain only alphabetic characters.",
                    "input": name,
                }
            )
            return

        if len(name) < 2 or len(name) > 50:
            self._errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "Name must be between 2 and 15 characters long.",
                    "input": name,
                }
            )
            return
