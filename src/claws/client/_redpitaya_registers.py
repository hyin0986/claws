from dataclasses import dataclass
from typing import Final

from claws.data._trigger_cfg import Enabled, TriggerDirection

from ._register import Access, Register
from ._unpacker import UnpackInt, UnpackIntEnum

_UNPACK_UINT32: Final[UnpackInt] = UnpackInt(unsigned=True, bytes=4)
_UNPACK_ENABLED_ENUM: Final[UnpackIntEnum[Enabled]] = UnpackIntEnum(
    enum_type=Enabled
)
_UNPACK_TRIGGER_DIRECTION_ENUM: Final[UnpackIntEnum[TriggerDirection]] = (
    UnpackIntEnum(enum_type=TriggerDirection)
)

TRIGGER_THRESHOLD_REGISTER: Final[Register[int]] = Register(
    access=Access.RW,
    path="Threshold",
    unpacker=_UNPACK_UINT32,
)
RELEASE_THRESHOLD_REGISTER: Final[Register[int]] = Register(
    access=Access.RW, path="Hysteresis", unpacker=_UNPACK_UINT32
)
ENABLE_RELEASE_THRESHOLD_REGISTER: Final[Register[Enabled]] = Register(
    access=Access.RW,
    path="HysteresisEn",
    unpacker=_UNPACK_ENABLED_ENUM,
)
KEEP_ARMING_REGISTER: Final[Register[Enabled]] = Register(
    access=Access.RW,
    path="KeepArm",
    unpacker=_UNPACK_ENABLED_ENUM,
)
TRIGGER_DIRECTION_REGISTER: Final[Register[TriggerDirection]] = Register(
    access=Access.RW,
    path="Direction",
    unpacker=_UNPACK_TRIGGER_DIRECTION_ENUM,
)


@dataclass(slots=True, frozen=True)
class ThresholdTriggerRegisters:
    trigger_threshold: Register[int] = TRIGGER_THRESHOLD_REGISTER
    release_threshold: Register[int] = RELEASE_THRESHOLD_REGISTER
    enable_release_threshold: Register[Enabled] = (
        ENABLE_RELEASE_THRESHOLD_REGISTER
    )
    keep_rearming: Register[Enabled] = KEEP_ARMING_REGISTER
    trigger_direction: Register[TriggerDirection] = TRIGGER_DIRECTION_REGISTER
