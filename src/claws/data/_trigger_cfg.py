from enum import IntEnum, unique
from dataclasses import dataclass

@unique
class Enabled(IntEnum):
    DISABLED = 0
    ENABLED = 1


@unique
class TriggerDirection(IntEnum):
    ABOVE = 0
    BELOW = 1


@dataclass(slots=True, frozen=True)
class ThresholdTriggerCfg:
    trigger_threshold: int = 0
    release_threshold: int = 0
    enable_release_threshold: Enabled = Enabled.ENABLED
    keep_rearming: Enabled = Enabled.ENABLED
    trigger_direction: TriggerDirection = TriggerDirection.ABOVE
