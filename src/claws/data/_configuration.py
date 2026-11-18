from dataclasses import dataclass, field
from typing import Final


@dataclass(slots=True, frozen=True)
class ZMQCfg:
    host: str = "localhost"
    port: int = 9099


_DEFAULT_ADC_BASE_PORT: Final[int] = 10000
_NUM_ADCS: Final[int] = 2


def _default_adc_port_map(
    base_port: int = _DEFAULT_ADC_BASE_PORT,
) -> dict[int, int]:
    return {adc: base_port + adc for adc in range(_NUM_ADCS)}


@dataclass(slots=True, frozen=True)
class DeviceCfg:
    host: str = "localhost"
    mem_map_port: int = 9000
    mem_map_offset: int = 0x4000_0000
    adc_port_map: dict[int, int] = field(default_factory=_default_adc_port_map)
    sample_rate_hz: int = 125e6


@dataclass(slots=True, frozen=True)
class RootCfg:
    name: str | None = ""
    description: str = ""
    expand: bool = True
    timeout: float = 1.0
    initRead: bool = False
    initWrite: bool = False
    pollEn: bool = True
    maxLog: int = 1000
    unifyLogs: bool = False
