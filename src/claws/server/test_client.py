import asyncio
from typing import Any, cast

import numpy as np
import numpy.typing as npt

from claws.client._register import Access, Register
from claws.client._zmq_client import AsyncRougeClient, Cfg


class ToNumpyArray[T: np.generic]:
    __slots__ = ("_expected_dtype", "_expected_size")

    def __init__(
        self,
        expected_dtype: type[T],
        expected_size: int,
    ) -> None:
        self._expected_dtype = np.dtype(expected_dtype)
        self._expected_size = expected_size

    def __call__(self, response: Any) -> npt.NDArray[T]:
        if not isinstance(response, np.ndarray):
            raise TypeError(
                f"Expected np.ndarray, got {type(response).__name__}"
            )

        if response.dtype != self._expected_dtype:
            raise TypeError(
                f"Expected dtype {self._expected_dtype}, got {response.dtype}"
            )

        if response.size != self._expected_size:
            raise TypeError(
                f"Expected array size {self._expected_size}, "
                f"got {response.size}"
            )

        return cast(npt.NDArray[T], response)


async def run() -> None:
    register = Register(
        access=Access.RO,
        path="claws.AdcProcessor[0].WaveformData",
        to_value=ToNumpyArray(expected_dtype=np.int16, expected_size=0x4000),
    )
    async with AsyncRougeClient(cfg=Cfg()) as client:
        print("test:", await client.get_value(register))


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
