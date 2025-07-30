import re

from ed_domain.core.validation import ABCValidator, ValidationErrorType


class PasswordValidator(ABCValidator[str]):
    def validate(
        self,
        value: str,
        location: str | None = None,
    ) -> None:
        password = value
        location = location or self._location

        if not password:
            self._errors.append(
                {
                    "message": "Password is required.",
                    "location": location,
                    "type": ValidationErrorType.MISSING_FIELD,
                    "input": password,
                }
            )
            return

        if len(password) < 8:
            self._errors.append(
                {
                    "message": "Password must be at least 8 characters long.",
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "input": password,
                }
            )

        if not re.search(r"\d", password):
            self._errors.append(
                {
                    "message": "Password must include at least one digit.",
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "input": password,
                }
            )

        if not re.search(r"[A-Z]", password):
            self._errors.append(
                {
                    "message": "Password must include at least one uppercase letter.",
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "input": password,
                }
            )

        if not re.search(r"[a-z]", password):
            self._errors.append(
                {
                    "message": "Password must include at least one lowercase letter.",
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "input": password,
                }
            )

        if not re.search(r"[@#$%^&*()_+=!-]", password):
            self._errors.append(
                {
                    "message": "Password must include at least one special character.",
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "input": password,
                }
            )
