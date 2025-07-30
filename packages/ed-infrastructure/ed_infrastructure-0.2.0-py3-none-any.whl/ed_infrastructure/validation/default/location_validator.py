from typing import Literal

from ed_domain.core.validation import ABCValidator, ValidationErrorType


class _LatitudeLongitudeValidator(ABCValidator[float]):
    def __init__(self, name: Literal["Latitude", "Longitude"]):
        super().__init__()
        self._name = name

    def validate(self, value: float, location: str | None = None) -> None:
        error_location = location or self.DEFAULT_ERROR_LOCATION

        if self._name == "Latitude" and not (8.8 <= value <= 9.1):
            self._errors.append(
                {
                    "location": error_location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": f"{self._name} must be between 8.8 and 9.1 degrees to be valid for Addis Ababa.",
                    "input": f"{location}",
                }
            )
            return

        if self._name == "Longitude" and not (38.6 <= value <= 39.0):
            self._errors.append(
                {
                    "location": error_location,
                    "type": ValidationErrorType.INVALID_VALUE,
                    "message": f"{self._name} must be between 38.6 and 39.0 degrees to be valid for Addis Ababa.",
                    "input": f"{location}",
                }
            )
            return


class LatitudeValidator(_LatitudeLongitudeValidator):
    def __init__(self):
        super().__init__("Latitude")


class LongitudeValidator(_LatitudeLongitudeValidator):
    def __init__(self):
        super().__init__("Longitude")
