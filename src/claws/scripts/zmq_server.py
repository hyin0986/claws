import argparse

import pyrogue

from claws.server import ZMQServer
from claws.data import DeviceCfg, RootCfg, ZMQCfg


class _Arguments(argparse.Namespace):
    zmq_host: str
    zmq_base_port: int

    device_host: str
    device_mem_port: int
    device_adc_base_port: int


def parse_args() -> _Arguments:
    parser = argparse.ArgumentParser()

    zmq_args = parser.add_argument_group(title="ZMQ")
    zmq_args.add_argument(
        "--zmq_host",
        type=str,
        default="0.0.0.0",
        help="ZMQ host address, default '0.0.0.0'.",
    )
    zmq_args.add_argument(
        "--zmq_base_port",
        type=int,
        default=9099,
        help="ZMQ base port, default 9099.",
    )

    dev_args = parser.add_argument_group(title="Device")
    dev_args.add_argument(
        "--device_host",
        default="10.0.123.100",
        help="IP address of the RedPitaya",
    )
    dev_args.add_argument(
        "--device_mem_port",
        type=int,
        default=9000,
        help="AXI register port of RedPitaya, default 9000.",
    )
    dev_args.add_argument(
        "--device_adc_base_port",
        type=int,
        default=10000,
        help="AXI stream base port of RedPitaya, default 10000.",
    )

    return parser.parse_args(namespace=_Arguments())


def main() -> None:
    args = parse_args()

    zmq_cfg = ZMQCfg(host=args.zmq_host, port=args.zmq_base_port)
    ADCS = 2
    dev_cfg = DeviceCfg(
        host=args.device_host,
        mem_map_port=args.device_mem_port,
        adc_port_map={
            channel: args.device_adc_base_port + channel
            for channel in range(ADCS)
        },
    )
    root_cfg = RootCfg(timeout=1)

    with ZMQServer(
        root_cfg=root_cfg, zmq_cfg=zmq_cfg, device_cfg=dev_cfg
    ) as _:
        pyrogue.waitCntrlC()


if __name__ == "__main__":
    main()
