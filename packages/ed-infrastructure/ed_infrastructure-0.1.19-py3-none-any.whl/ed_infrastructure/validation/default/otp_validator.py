from ed_domain.core.validation import ABCValidator, ValidationErrorType


class OtpValidator(ABCValidator[str]):
    def validate(
        self,
        value: str,
        location: str | None = None,
    ) -> None:
        otp = value
        location = location or self._location

        if not otp.isnumeric():
            self._errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_TYPE,
                    "message": "OTP must be numeric.",
                    "input": otp,
                }
            )
            return

        if len(otp) != 4:
            self._errors.append(
                {
                    "location": location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": "OTP must be exactly 4 digits long.",
                    "input": otp,
                }
            )
