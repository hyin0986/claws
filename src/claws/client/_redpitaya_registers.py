from dataclasses import dataclass, replace, fields
from typing import Final, Self

from claws.data._trigger_cfg import Enabled, TriggerDirection

from ._register import Access, Register
from ._unpacker import UnpackProtocol, UnpackInt, UnpackIntEnum, UnpackReadWriteRequest

_UNPACK_UINT32: Final[UnpackProtocol[int]] = UnpackInt(unsigned=True, bits=32)
_UNPACK_ENABLED_ENUM: Final[UnpackIntEnum[Enabled]] = UnpackIntEnum(
    enum_type=Enabled
)
_UNPACK_TRIGGER_DIRECTION_ENUM: Final[UnpackProtocol[TriggerDirection]] = (
    UnpackIntEnum(enum_type=TriggerDirection)
)
_UNPACK_READ_WRITE_DEVICE: Final[UnpackProtocol[bool]]  = UnpackReadWriteRequest()


READ_DEVICE_REGISTER: Final[Register[bool]] = Register(
    access = Access.WO, path="ReadDevice", unpacker=_UNPACK_READ_WRITE_DEVICE,
)

WRITE_DEVICE_REGISTER: Final[Register[bool]] = Register(
    access = Access.WO, path="WriteDevice", unpacker=_UNPACK_READ_WRITE_DEVICE,
)

@dataclass(slots=True, frozen=True)
class ReadWriteDeviceRegister:
    read_device: Register[bool] = READ_DEVICE_REGISTER
    write_device: Register[bool] = READ_DEVICE_REGISTER

    @staticmethod
    def with_parent_path(parent: str) -> "ReadWriteDeviceRegister":
        registers = ReadWriteDeviceRegister()

        return ReadWriteDeviceRegister(
            **{
                field.name: replace(
                    register := getattr(registers, field.name),
                    path=f"{parent}.{register.path}" if parent else register.path,
                )
                for field in fields(registers)
            }
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
class ThresholdTriggerRegisters(ReadWriteDeviceRegister):
    trigger_threshold: Register[int] = TRIGGER_THRESHOLD_REGISTER
    release_threshold: Register[int] = RELEASE_THRESHOLD_REGISTER
    enable_release_threshold: Register[Enabled] = ENABLE_RELEASE_THRESHOLD_REGISTER
    keep_rearming: Register[Enabled] = KEEP_ARMING_REGISTER
    trigger_direction: Register[TriggerDirection] = TRIGGER_DIRECTION_REGISTER

    @staticmethod
    def with_parent_path(parent: str) -> "ThresholdTriggerRegisters":
        registers = ThresholdTriggerRegisters()

        return ThresholdTriggerRegisters(
            **{
                field.name: replace(
                    register := getattr(registers, field.name),
                    path=f"{parent}.{register.path}" if parent else register.path,
                )
                for field in fields(registers)
            }
        )


TRIGGER_OVERTHRESHOLD_DURATION: Final[Register[int]] = Register(
    access=Access.RW, path="TotCountTrig", unpacker=_UNPACK_UINT32,
)


@dataclass(slots=True, frozen=True)
class TimeOverThresholdTriggerRegisters(ThresholdTriggerRegisters):
    duration_threshold: Register[int] = TRIGGER_OVERTHRESHOLD_DURATION

    @staticmethod
    def with_parent_path(parent: str) -> "TimeOverThresholdTriggerRegisters":
        registers = TimeOverThresholdTriggerRegisters()

        return TimeOverThresholdTriggerRegisters(
            **{
                field.name: replace(
                    register := getattr(registers, field.name),
                    path=f"{parent}.{register.path}" if parent else register.path,
                )
                for field in fields(registers)
            }
        )

