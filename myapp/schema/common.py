from enum import Enum


class EnabledEnum(str, Enum):
    enabled = "enabled"
    disabled = "disabled"
