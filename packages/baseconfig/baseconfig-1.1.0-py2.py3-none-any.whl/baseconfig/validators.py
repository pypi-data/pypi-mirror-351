import baseconfig
import numbers
import typing


class Validator:
    def __init__(self, is_valid: typing.Callable[[typing.Any], bool]) -> None:
        self._is_valid = is_valid

    @property
    def is_valid(self) -> typing.Callable[[typing.Any], bool]:
        return self._is_valid

    def ensure_valid(self, value: typing.Any) -> None:
        if not self._is_valid(value):
            raise baseconfig.InvalidValueException(
                f"The value {value} was rejected by the validator.")


class LengthValidator(Validator):
    def __init__(self, expected_length: int) -> None:
        super().__init__(lambda x: len(x) == expected_length)
        self._expected_length = expected_length

    def ensure_valid(self, value: typing.Sized) -> None:
        if not self._is_valid(value):
            raise baseconfig.InvalidValueException(
                f"The length of value {value} is {len(value)}. The expected "
                f"length is {self._expected_length}.")


class MaxLengthValidator(Validator):
    def __init__(self, max_length: int) -> None:
        super().__init__(lambda x: len(x) <= max_length)
        self._max_length = max_length

    def ensure_valid(self, value: typing.Any) -> None:
        if not self._is_valid(value):
            raise baseconfig.InvalidValueException(
                f"The length of value {value} is {len(value)}. The maximum "
                f"allowed length is {self._max_length}.")


class OneOfValidator(Validator):
    def __init__(self, *allowed: list) -> None:
        super().__init__(lambda x: x in allowed)
        self._allowed = allowed

    def ensure_valid(self, value: typing.Any) -> None:
        if not self._is_valid(value):
            raise baseconfig.InvalidValueException(
                f"The value {value} is not among the allowed values "
                f"{self._allowed}.")


class RangeValidator(Validator):
    def __init__(
            self,
            inclusive_min: numbers.Number,
            inclusive_max: numbers.Number) -> None:
        super().__init__(lambda x: x >= inclusive_min and x <= inclusive_max)
        self._min = inclusive_min
        self._max = inclusive_max

    def ensure_valid(self, value: typing.Any) -> None:
        if not self._is_valid(value):
            raise baseconfig.InvalidValueException(
                f"The value {value} is outside the range "
                f"{self._min}..{self._max}.")


class OfTypeValidator(Validator):
    def __init__(self, of_type: type):
        super().__init__(lambda x: isinstance(x, of_type))
        self._of_type = of_type

    def ensure_valid(self, value: typing.Any) -> None:
        if not self._is_valid(value):
            actual: str = type(value).__name__
            expected: str = self._of_type.__name__

            if actual == expected:
                actual = str(type(value))
                expected = str(self._of_type)

            raise baseconfig.InvalidValueException(
                f"The value {value} of type {actual} is not of type "
                f"{expected}.")
