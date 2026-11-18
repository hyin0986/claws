from argparse import ArgumentParser, Namespace
from typing import Final


class ZMQArgs(Namespace):
    zmq_host: str
    zmq_base_port: int


_ZMQ_DESCRIPTION: Final[str] = """
The ZMQ server distributes the device tree over
[zmq_host]:[zmq_base_port]. The provided data is plain JSON.
A binary protocol is available over
[zmq_host]:[zmq_base_port + 1].
"""

_DEFAULT_ZMQ_HOST: Final[str] = "0.0.0.0"
_DEFAULT_ZMQ_BASE_PORT: Final[int] = 9099


def add_zmq_args(parser: ArgumentParser) -> ArgumentParser:
    group = parser.add_argument_group(
        title="ZMQ", description=_ZMQ_DESCRIPTION
    )
    group.add_argument(
        "--zmq_host",
        type=str,
        default=_DEFAULT_ZMQ_HOST,
        help=f"ZMQ host address, default '{_DEFAULT_ZMQ_HOST}'.",
    )
    group.add_argument(
        "--zmq_base_port",
        type=int,
        default=_DEFAULT_ZMQ_BASE_PORT,
        help=f"ZMQ base port, default JSON: {_DEFAULT_ZMQ_BASE_PORT}.",
    )
    return parser


class DeviceArgs(Namespace):
    device_host: str
    device_mem_port: int
    device_adc_base_port: int


_DEVICE_DESCRIPTION: Final[str] = """
The DMA registers are accessed over TCP via [device_host]:[mem_map_port].
The two ADC data streams are available at
[device_host]:[adc_base_port] and [device_host]:[adc_base_port + 2].
"""

_DEFAULT_DEVICE_HOST: Final[str] = "10.0.123.100"
_DEFAULT_DEVICE_MEM_PORT: Final[int] = "9000"
_DEFAULT_DEVICE_ADC_BASE_PORT: Final[int] = "10000"


def add_device_args(parser: ArgumentParser) -> ArgumentParser:
    group = parser.add_argument_group(
        title="Device", description=_DEVICE_DESCRIPTION
    )
    group.add_argument(
        "--device_host",
        default=_DEFAULT_DEVICE_HOST,
        help=(
            f"IP address of the RedPitaya, default '{_DEFAULT_DEVICE_HOST}'"
        ),
    )
    group.add_argument(
        "--device_mem_port",
        type=int,
        default=_DEFAULT_DEVICE_MEM_PORT,
        help=(
            "AXI register port of RedPitaya, "
            f"default {_DEFAULT_DEVICE_MEM_PORT}."
        ),
    )
    group.add_argument(
        "--device_adc_base_port",
        type=int,
        default=_DEFAULT_DEVICE_ADC_BASE_PORT,
        help=(
            "AXI stream base port of RedPitaya, "
            f"default {_DEFAULT_DEVICE_ADC_BASE_PORT}."
        ),
    )
    return parser
