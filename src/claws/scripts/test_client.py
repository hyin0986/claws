import asyncio
from typing import Any, cast

import numpy as np
import numpy.typing as npt

from claws.data._trigger_cfg import ThresholdTriggerCfg

from claws.client._redpitaya_registers import ThresholdTriggerRegisters
from claws.client._zmq_client import AsyncRougeClient, ZMQClientCfg

PREFIX = "claws.Zynq7SoC.Application.AbortTrigs.ThrTrig[0]"
THRESHOLD_TRIGGER_REGISTERS = ThresholdTriggerRegisters.with_parent_path(PREFIX)


async def read_threhsold_trigger(client: AsyncRougeClient):
    tasks = [
        client.get_value(THRESHOLD_TRIGGER_REGISTERS.trigger_threshold),
        client.get_value(THRESHOLD_TRIGGER_REGISTERS.release_threshold),
        client.get_value(THRESHOLD_TRIGGER_REGISTERS.enable_release_threshold),
        client.get_value(THRESHOLD_TRIGGER_REGISTERS.keep_rearming),
        client.get_value(THRESHOLD_TRIGGER_REGISTERS.trigger_direction),
    ]

    values = await asyncio.gather(*tasks, return_exceptions=True)
    for value in values:
        if isinstance(value, Exception):
            raise value

    trigger = ThresholdTriggerCfg(
        trigger_threshold=values[0],
        release_threshold=values[1],
        enable_release_threshold=value[2],
        keep_rearming=value[3],
        trigger_direction=value[4],
    )

    print(trigger)

async def run() -> None:

    async with AsyncRougeClient(cfg=ZMQClientCfg(host="10.0.123.100")) as client:
        await read_threhsold_trigger(client)


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
