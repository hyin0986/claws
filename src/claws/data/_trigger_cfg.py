from enum import IntEnum, unique


@unique
class Enabled(IntEnum):
    DISABLED = 0
    ENABLED = 1


@unique
class TriggerDirection(IntEnum):
    ABOVE = 0
    BELOW = 1
