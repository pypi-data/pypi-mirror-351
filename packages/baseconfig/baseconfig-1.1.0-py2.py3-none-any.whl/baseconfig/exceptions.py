class ConfigurationException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ConfigurationNotFoundException(ConfigurationException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ValueMissingException(ConfigurationException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidValueException(ConfigurationException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
