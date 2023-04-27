import enum as std_enum

__all__ = ["UiHint", "remember_hint"]


class UiHint(std_enum.StrEnum):
    ALWAYS_HIDDEN = '"ALWAYS_HIDDEN"'
    READ_ONLY = '"READ_ONLY"'
    UNCONFIGURABLE = '"UNCONFIGURABLE"'
    REMEMBER_PREVIOUS_VALUE = '"REMEMBER_PREVIOUS_VALUE"'
    HORIZONTAL_ENUM = '"HORIZONTAL_ENUM"'
    SHOW_LABEL = '"SHOW_LABEL"'
    SHOW_EXPRESSION = '"SHOW_EXPRESSION"'
    OPPOSITE_DIRECTION = '"OPPOSITE_DIRECTION"'
    OPPOSITE_DIRECTION_CIRCULAR = '"OPPOSITE_DIRECTION_CIRCULAR"'


remember_hint = [UiHint.REMEMBER_PREVIOUS_VALUE]
