from __future__ import annotations

from typing import Iterator, Self
from library import annotation, base, stmt, utils

__all__ = ["EnumValue", "Enum", "CustomEnum"]


class EnumValue(base.Node):
    # Enum type is circular?
    def __init__(
        self,
        value: str,
        enum: Enum,
        user_name: str | None = None,
        hidden: bool = False,
    ) -> None:
        """A possible value of an enum.

        value: The value of the enum. Should be all-caps seperated by underscores.
        user_name: A user facing name.
        hidden: Whether to mark the enum value as hidden. Has no effect if the enum is not ui.
        """
        self.value = value.upper()
        self.hidden = hidden
        self.enum = enum

        if user_name is None:
            self.user_name = self.make_user_name()
        else:
            self.user_name = user_name

    def make_user_name(self) -> str:
        words = self.value.lower().split(sep="_")
        words[0] = words[0].capitalize()
        return " ".join(words)

    def __str__(self) -> str:
        dict = {}
        if self.user_name is not None:
            dict["Name"] = self.user_name
        if self.hidden:
            dict["Hidden"] = "true"

        if dict != {}:
            return "annotation {}\n {}".format(
                str(annotation.Map(dict, quote_values=True)), self.value
            )
        return self.value

    def camel_case(self, capitalize: bool = False) -> str:
        words = self.make_user_name().split()
        words = [word.capitalize() for word in words]
        result = "".join(words)
        if capitalize:
            return result
        return utils.lower_first(result)


class Enum(stmt.Statement):
    def __init__(
        self,
        name: str,
        *,
        parent: stmt.Parent,
        default_parameter_name: str | None = None,
        export: bool = True,
    ) -> None:
        """An enum.

        name: A capital case (LikeThis) string.
        values: A list of strings which are used to construct enum values. EnumValues may also be registered afterwards.
        default_parameter_name: A default parameter name to use. If not specified, the default is generated automatically by lowercasing the first letter of name.
        """
        self.register_parent(parent)

        self.name = name
        self.default_parameter_name = (
            utils.lower_first(name)
            if default_parameter_name is None
            else default_parameter_name
        )
        self.export = export
        self.values = []

    def __getattribute__(self, name: str) -> EnumValue:
        """
        Overload get_attribute to type hint EnumValue access for users.
        """
        return super().__getattribute__(name)

    def __contains__(self, value: EnumValue) -> bool:
        return value in self.values

    def __iter__(self) -> Iterator[EnumValue]:
        return self.values.__iter__()

    def add_value(
        self,
        value: str,
        user_name: str | None = None,
        hidden: bool = False,
    ) -> Self:
        enum_value = EnumValue(value, self, user_name=user_name, hidden=hidden)
        self.values.append(enum_value)
        setattr(self, value, enum_value)
        return self

    def __str__(self) -> str:
        string = utils.export(self.export)
        string += "enum {} \n{{\n".format(self.name)
        string += utils.to_str(self.values, sep=",\n", tab=True)
        return string + "\n}\n"


class CustomEnum(Enum):
    def add_custom(self) -> Self:
        return self.add_value("CUSTOM")
