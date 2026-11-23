import asyncio

from claws.client._zmq_client import AsyncRougeClient, Cfg
from claws.client._register import Register, Access


async def run() -> None:
    register = Register(
        access=Access.RO,
        path="claws.AdcProcessor[0].WaveformData",
        to_value=None,
    )
    async with AsyncRougeClient(cfg=Cfg()) as client:
        print("test:", await client.get_value(register))


def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()