import re

from ed_domain.core.validation import ABCValidator, ValidationErrorType


class PhoneNumberValidator(ABCValidator[str]):
    def validate(
        self,
        value: str,
        location: str | None = None,
    ) -> None:
        phone_number = value
        location = location or self._location

        if not phone_number:
            self._errors.append(
                {
                    "location": "body",
                    "type": ValidationErrorType.MISSING_FIELD,
                    "message": "Phone number is required.",
                    "input": phone_number,
                }
            )
            return

        if not re.match(r"^(\+251|0|251)?9\d{8}$", phone_number):
            self._errors.append(
                {
                    "location": "body",
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "Invalid phone number format. It should be in one of the following formats: +2519XXXXXXXX, 2519XXXXXXXX, or 09XXXXXXXX.",
                    "input": phone_number,
                }
            )
