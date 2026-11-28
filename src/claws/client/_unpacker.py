import pickle
from enum import IntEnum, IntFlag, StrEnum, unique
from typing import Protocol, cast, Final

import numpy as np
import numpy.typing as npt

from claws.errors import UnpackerError

@unique
class Access(IntFlag):
    RO = 1
    WO = 2
    RW = RO | WO


@unique
class Attr(StrEnum):
    GET = "get"
    SET = "set"


class UnpackProtocol[ValueType](Protocol):
    def unpack(self, response: bytes) -> ValueType: ...
    def pack(self, path: str, attr: Attr, value: ValueType) -> bytes: ...


def _pickle_load[T](response: bytes, expected_type: type[T]) -> T:
    unpacked = pickle.loads(response)

    if isinstance(unpacked, Exception):
        raise UnpackerError("Server execution failed!") from unpacked

    if not isinstance(unpacked, expected_type):
        raise UnpackerError(
            f"Expected {expected_type.__name__}, "
            f"got {type(unpacked).__name__}"
        )

    return unpacked


def _pack_no_conversion(path: str, attr: Attr, value: object) -> bytes:
    return pickle.dumps(
            {
                "path": path,
                "attr": attr.value,
                "args": (value),
                "kwargs": {},
            }
    )


class UnpackIntEnum[T: IntEnum]:
    __slots__ = ["_enum_type"]

    def __init__(self, enum_type: type[T]) -> None:
        self._enum_type = enum_type

    def pack(self, path: str, attr: Attr, value: IntEnum) -> bytes:
        return _pack_no_conversion(path, attr, value)

    def unpack(self, response: bytes) -> T:
        unpacked = pickle.loads(response)

        if isinstance(unpacked, Exception):
            raise UnpackerError("Server execution failed!") from unpacked

        if isinstance(unpacked, bool):
            unpacked = 0 if not unpacked else 1

        if not isinstance(unpacked, int):
            raise UnpackerError(
                f"Invalid type! Expected int, got: {type(unpacked).__name__}!"
            )

        try:
            return self._enum_type(unpacked)
        except ValueError as err:
            raise UnpackerError(
                f"'{unpacked}' can not be converted to a "
                f"'{self._enum_type.__name__}' enum!"
            ) from err


class UnpackInt:
    __slots__ = ["_size", "_unsigned", "_min", "_max"]

    def __init__(self, unsigned: bool = True, bits: int = 32):
        self._unsigned = unsigned
        self._size = bits
        self._min = 0 if self._unsigned else -(2 ** (self._size - 1))
        self._max = (
            2 ** (self._size) - 1
            if self._unsigned
            else 2 ** (self._size - 1) - 1
        )


    def pack(self, path: str, attr: Attr, value: int) -> bytes:
        if value.bit_length() > self._size:
            raise UnpackerError(f"Given Integer requires at least {value.bit_length()} bits! "f"Max allowed bits: {self._size}")
        return _pack_no_conversion(path, attr, value)

    def unpack(self, response: bytes) -> int:
        unpacked = _pickle_load(response, int)

        if self._unsigned and unpacked < 0:
            raise UnpackerError(f"Expected unsigned int, got {unpacked}!")

        if not self._min <= unpacked <= self._max:
            raise UnpackerError(
                f"Integer out of range! Expected [{self._min}, {self._max}], "
                f"got {unpacked}!"
            )

        return unpacked


class UnpackNumpyArray[T: np.generic]:
    __slots__ = ["_expected_dtype", "_expected_size"]

    def __init__(
        self,
        expected_dtype: type[T],
        expected_size: int,
    ) -> None:
        self._expected_dtype = np.dtype(expected_dtype)
        self._expected_size = expected_size

    def pack(self, path: str, attr: Attr, value: npt.NDArray[T]) -> bytes:
        if value.size != self._expected_size:
            raise UnpackerError(f"Expected size {self._expected_size}, got: {value.size}!")
        if value.dtype != self._expected_dtype:
            raise UnpackerError(f"Expected size '{self._expected_dtype}', got: '{value.dtype}'!")

        return _pack_no_conversion(path, attr, value)


    def unpack(self, response: bytes) -> npt.NDArray[T]:
        unpacked = _pickle_load(response, np.ndarray)

        if unpacked.dtype != self._expected_dtype:
            raise UnpackerError(
                f"Expected dtype {self._expected_dtype}, got {unpacked.dtype}"
            )

        if unpacked.size != self._expected_size:
            raise UnpackerError(
                f"Expected array size {self._expected_size}, "
                f"got {unpacked.size}"
            )

        return cast(npt.NDArray[T], response)


class UnpackReadWriteRequest:
    __slots___ = []

    def pack(self, path: str, attr: Attr, value: bool) -> bytes:
        return _pack_no_conversion(path, attr, value)

    def unpack(self, response: bytes) -> bool:
        unpacked = pickle.loads(response)
        if isinstance(unpacked, Exception):
            raise UnpackerError("Server execution failed!") from unpacked

        return True
