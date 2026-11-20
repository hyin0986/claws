from argparse import ArgumentParser

from claws.data import ZMQCfg
from claws.gui import start_gui

from ._parse_args_helper import ZMQArgs, add_zmq_args


def parse_args() -> ZMQArgs:
    parser = add_zmq_args(ArgumentParser())
    return parser.parse_args(namespace=ZMQArgs())


def main() -> None:
    args = parse_args()
    cfg = ZMQCfg(host=args.zmq_host, port=args.zmq_base_port)
    start_gui(cfg)


if __name__ == "__main__":
    main()
