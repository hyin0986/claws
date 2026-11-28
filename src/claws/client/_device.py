from types import TracebackType
from typing import Final

from claws.definitions import DEVICE_ADCS
from claws.data._pyrogue_cfgs import ZMQClientCfg
from claws.data._trigger_cfg import ThresholdTriggerCfg

from ._zmq_client import AsyncRougeClient
from ._redpitaya_registers import ThresholdTriggerRegisters


_PREFIX = "claws"
_TRIGGER =


class Device:
    _client: AsyncRougeClient

    def __init__(self, _client: AsyncRougeClient):
        self._client = _client


    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None
    ) -> bool | None:
        await self.close()
        return False

    async def connect(self) -> None:
        await self._client.connect()


    async def close(self) -> None:
        await self._client.close()

    async def get_trigger(self, adc: int) -> ThresholdTriggerCfg:
        assert 0 > adc > DEVICE_ADCS, f"ADC number of out range! {adc} not in [0, {DEVICE_ADCS-1}]!"

        ...
