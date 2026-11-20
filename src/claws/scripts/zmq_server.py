import argparse
from pathlib import Path

import pyrogue

from claws.data import DeviceCfg, RootCfg, ZMQCfg
from claws.definitions import (
    DISCOVERY_PORT_OFFSET,
    get_adc_stream_ports,
)
from claws.scripts._parse_args_helper import (
    DeviceArgs,
    ZMQArgs,
    add_device_args,
    add_zmq_args,
)
from claws.server._device_discovery_server import (
    DiscoveryServer,
    DiscoveryServerContext,
    discover_device_tree,
)
from claws.server._zmq_server import compose_root
from claws.data._yaml_serialization import YAMLFile
from claws.data._pr_node import LeafNode


class _Arguments(ZMQArgs, DeviceArgs):
    dump_variables: Path


def _is_writeable_path(arg: str) -> Path:
    path = Path(arg)

    try:
        with path.open("wb"):
            ...
    except OSError as err:
        raise argparse.ArgumentTypeError(f"'{arg}' is not writeable!") from err

    return path


def parse_args() -> _Arguments:
    parser = argparse.ArgumentParser()

    parser = add_zmq_args(parser)
    parser = add_device_args(parser)

    parser.add_argument(
        "--dump_variables",
        type=_is_writeable_path,
        default=None,
        help="Dump all variables to the specified path, default is `None`.",
    )

    return parser.parse_args(namespace=_Arguments())


def _dump_variables(path: Path, variables: list[LeafNode]) -> None:
    with path.open("wb") as file, YAMLFile(file, compress=False) as serializer:
        serializer.write(variables)


def main() -> None:
    args = parse_args()

    zmq_cfg = ZMQCfg(host=args.zmq_host, port=args.zmq_base_port)
    dev_cfg = DeviceCfg(
        host=args.device_host,
        mem_map_port=args.device_mem_port,
        adc_port_map=get_adc_stream_ports(base_port=args.device_adc_base_port),
    )
    root_cfg = RootCfg(timeout=1, name="claws")

    root = compose_root(root_cfg=root_cfg, zmq_cfg=zmq_cfg, device_cfg=dev_cfg)
    args.dump_variables=Path("variables.yml")

    with root:
        if args.dump_variables is not None:
            _dump_variables(args.dump_variables, discover_device_tree(root))
        server = DiscoveryServer(
            root=root,
            host=zmq_cfg.host,
            port=zmq_cfg.port + DISCOVERY_PORT_OFFSET,
        )
        with DiscoveryServerContext(server) as discovery_server:
            pyrogue.waitCntrlC()
            discovery_server.stop()


if __name__ == "__main__":
    main()
