from claws.gui._pydm_gui import start_gui
from claws.data import ZMQCfg


def main() -> None:
    cfg = ZMQCfg()
    start_gui(cfg)


if __name__ == "__main__":
    main()
