from dataclasses import dataclass, field, asdict
from typing import Final

from pyrogue._Root import Root

@dataclass(slots=True, frozen=True)
class ZMQCfg:
    host: str = "localhost"
    port: int = 9099


@dataclass(slots=True, frozen=True)
class DeviceCfg:
    host: str = "localhost"
    mem_map_port: int = 9000
    adc_port_map: dict[int, int] = field(default_factory=)

    @staticmethod
    def _default_adc_port_map(base_port: int = 10000) -> dict[int, int]:
        ADCS: Final[int] = 2
        return {adc : base_port + adc for adc in range(ADCS)}


@dataclass(slots=True, frozen=True)
class RootCfg:
    name: str | None = None,
    description: str = '',
    expand: bool = True,
    timeout: float = 1.0,
    initRead: bool = False,
    initWrite: bool = False,
    pollEn: bool = True,
    maxLog: int = 1000,
    unifyLogs: bool = False

class ZMQServer(Root):
    def __init__(self, zmq_cfg: ZMQCfg = ZMQCfg(), device_cfg: DeviceCfg = DeviceCfg(), root_cfg = RootCfg) -> None:
        super().__init__(**asdict(root_cfg))

        
        

