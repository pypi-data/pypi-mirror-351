import re

from ed_domain.core.validation import ABCValidator, ValidationErrorType


class EmailValidator(ABCValidator[str]):
    def validate(
        self,
        value: str,
        location: str | None = None,
    ) -> None:
        email = value
        location = location or self._location

        if not email:
            self._errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.MISSING_FIELD,
                    "message": "Email is required.",
                    "input": email,
                }
            )

            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self._errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "Invalid email format.",
                    "input": email,
                }
            )
