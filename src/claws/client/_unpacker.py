import pickle
from enum import IntEnum
from typing import Protocol, cast

import numpy as np
import numpy.typing as npt


class UnpackProtocol[T](Protocol):
    def unpack(self, response: bytes) -> T: ...


class UnpackIntEnum[T: IntEnum]:
    __slots__ = ["_enum_type"]

    def __init__(self, enum_type: type[T]) -> None:
        self._enum_type = enum_type

    def unpack(self, response: bytes) -> T:
        unpacked = pickle.loads(response)

        if isinstance(unpacked, Exception):
            raise TypeError("Server execution failed!") from unpacked

        if isinstance(unpacked, bool):
            unpacked = 0 if not unpacked else 1

        if not isinstance(unpacked, int):
            raise TypeError(
                f"Invalid type! Expected int, got: {type(unpacked).__name__}!"
            )

        try:
            return self._enum_type(unpacked)
        except ValueError as err:
            raise ValueError(
                f"'{unpacked}' can not be converted to a "
                f"'{self._enum_type.__name__}' enum!"
            ) from err


class UnpackInt:
    __slots__ = ["_size", "_unsigned"]

    def __init__(self, unsigned: bool = True, bytes: int = 4):
        self._unsigned = unsigned
        self._size = bytes

    def unpack(self, response: bytes) -> int:
        unpacked = pickle.loads(response)
        if isinstance(unpacked, Exception):
            raise TypeError("Server execution failed!") from unpacked

        if isinstance(unpacked, bool):
            unpacked = 0 if not unpacked else 1

        if not isinstance(unpacked, int):
            raise TypeError(
                f"Invalid type! Expected int, got: {type(unpacked).__name__}!"
            )

        if self._unsigned and unpacked < 0:
            raise ValueError(f"Expected unsigned int, got {unpacked}!")

        lower = 0 if self._unsigned else -(2 ** (8 * self._size - 1))
        upper = (
            2 ** (8 * self._size) - 1
            if self._unsigned
            else 2 ** (8 * self._size - 1) - 1
        )

        if not lower <= unpacked <= upper:
            raise ValueError(
                f"Integer out of range! Expected [{lower}, {upper}], "
                f"got {unpacked}!"
            )

        return unpacked


class UnpackNumpyArray[T: np.generic]:
    __slots__ = ("_expected_dtype", "_expected_size")

    def __init__(
        self,
        expected_dtype: type[T],
        expected_size: int,
    ) -> None:
        self._expected_dtype = np.dtype(expected_dtype)
        self._expected_size = expected_size

    def unpack(self, response: bytes) -> npt.NDArray[T]:
        unpacked = pickle.loads(response)
        if isinstance(unpacked, Exception):
            raise TypeError("Server execution failed!") from unpacked

        if not isinstance(unpacked, np.ndarray):
            raise TypeError(
                f"Expected np.ndarray, got {type(unpacked).__name__}"
            )

        if unpacked.dtype != self._expected_dtype:
            raise TypeError(
                f"Expected dtype {self._expected_dtype}, got {unpacked.dtype}"
            )

        if unpacked.size != self._expected_size:
            raise TypeError(
                f"Expected array size {self._expected_size}, "
                f"got {unpacked.size}"
            )

        return cast(npt.NDArray[T], response)
