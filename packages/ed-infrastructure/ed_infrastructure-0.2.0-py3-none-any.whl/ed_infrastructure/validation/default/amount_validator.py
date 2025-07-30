from ed_domain.core.validation import ABCValidator, ValidationErrorType


class AmountValidator(ABCValidator[float]):
    def validate(
        self,
        value: float,
        location: str | None = None,
    ) -> None:
        amount = value
        location = location or self._location

        if not isinstance(amount, (float, int)):
            self._errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_TYPE,
                    "message": "Amount must be a number.",
                    "input": amount,
                }
            )
            return

        if amount <= 0:
            self._errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "Amount must be greater than zero.",
                    "input": f"{amount}",
                }
            )
            return

        if amount > 1_000_000:
            self._errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "Amount must not exceed 1,000,000.",
                    "input": f"{amount}",
                }
            )
            return
