import argparse

import pyrogue

from claws.server._zmq_server import compose_root
from claws.data import DeviceCfg, RootCfg, ZMQCfg

from ._parse_args_helper import (
    ZMQArgs,
    add_zmq_args,
    DeviceArgs,
    add_device_args,
)


class _Arguments(ZMQArgs, DeviceArgs): ...


def parse_args() -> _Arguments:
    parser = argparse.ArgumentParser()

    parser = add_zmq_args(parser)
    parser = add_device_args(parser)

    return parser.parse_args(namespace=_Arguments())


def main() -> None:
    args = parse_args()

    zmq_cfg = ZMQCfg(host=args.zmq_host, port=args.zmq_base_port)
    ADCS = 2
    dev_cfg = DeviceCfg(
        host=args.device_host,
        mem_map_port=args.device_mem_port,
        adc_port_map={
            channel: args.device_adc_base_port + 2 * channel
            for channel in range(ADCS)
        },
        sample_rate_hz=125e6,
    )
    root_cfg = RootCfg(timeout=1, name="claws")

    with compose_root(
        root_cfg=root_cfg, zmq_cfg=zmq_cfg, device_cfg=dev_cfg
    ) as _:
        pyrogue.waitCntrlC()


if __name__ == "__main__":
    main()
