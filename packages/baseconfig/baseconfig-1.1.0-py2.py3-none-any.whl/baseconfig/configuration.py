import baseconfig
import json
import platform
import typing


Chain = list[str]
SourceName = str
SourceNames = list[SourceName]
Source = dict


class DefaultLoader:
    def load(self, name: SourceName, chain: Chain) -> Source:
        source = self._load_source(name)
        return DefaultFinder().find(source, chain)

    def _load_source(self, name: SourceName) -> Source:
        try:
            with open(f"{name}.json") as f:
                return json.load(f)
        except FileNotFoundError:
            raise baseconfig.ConfigurationNotFoundException()


class DefaultFinder:
    def find(self, source: Source, chain: Chain) -> typing.Any:
        return self._find_value_in(source, chain)

    def _find_value_in(
            self,
            obj: Source,
            remaining_chain: Chain,
            processed_chain: Chain=[]) -> typing.Any:
        key = remaining_chain[0]
        try:
            value = obj[key]
        except (KeyError, TypeError):
            path = "/".join(processed_chain)
            error = f"The value {key} wasn't found in {path} node."
            raise baseconfig.ValueMissingException(error)

        if len(remaining_chain) == 1:
            return value

        return self._find_value_in(
            value, remaining_chain[1:], processed_chain + [key])


class Configuration:
    def __init__(
            self,
            load: typing.Callable[[SourceName, Chain], Source]=DefaultLoader().load,
            names: SourceNames | None=None) -> None:
        self._load = load
        self._names = names or self._default_names

    def find_value(
            self,
            key: str,
            validators: list[baseconfig.Validator] | baseconfig.Validator=[]
        ) -> typing.Any:
        if isinstance(validators, baseconfig.Validator):
            validators = [validators]

        chain = key.split("/")

        last_ex: baseconfig.ConfigurationException | None = None
        for name in self._names:
            try:
                value = self._load(name, chain)
                if validators:
                    self._validate(value, validators)
                return value
            except (baseconfig.ConfigurationNotFoundException,
                    baseconfig.ValueMissingException) as ex:
                # Raise the exception only if the code reached the last
                # element. Exceptions encountered on all but last elements can
                # simply be ignored, since there is a chance to get the value
                # from the next sources.
                last_ex = ex

        raise last_ex or baseconfig.ValueMissingException()

    def check_all(self) -> typing.Generator[
            tuple[str, baseconfig.ConfigurationException | None],
            None,
            None]:
        members = dir(self)
        for member in members:
            if not member.startswith("_"):
                member_type = getattr(type(self), member)
                if isinstance(member_type, property):
                    try:
                        member_type.__get__(self)
                        yield (member, None)
                    except baseconfig.InvalidValueException as ex:
                        yield (member, ex)

    @property
    def _default_names(self) -> SourceNames:
        return [f"config.{platform.node()}", "config"]

    def _validate(
            self,
            value: typing.Any,
            validators: list[baseconfig.Validator]) -> None:
        for validator in validators:
            validator.ensure_valid(value)
