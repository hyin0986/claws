from dataclasses import dataclass, field

from claws.definitions import (
    DEVICE_ADCS,
    DEVICE_MAX_BUFFER_SIZE,
    DEVICE_MEM_MAP_OFFSET,
    DEVICE_SAMPLE_RATE_HZ,
    ROGUE_MEM_MAP_PORT,
    ROUGE_ADC_BASE_PORT,
    ROUGE_DEFAULT_ZMQ_BASE_PORT,
    get_adc_stream_ports,
)


@dataclass(slots=True, frozen=True)
class ZMQCfg:
    host: str = "localhost"
    port: int = ROUGE_DEFAULT_ZMQ_BASE_PORT


@dataclass(slots=True, frozen=True)
class DeviceCfg:
    host: str = "localhost"
    mem_map_port: int = ROGUE_MEM_MAP_PORT
    mem_map_offset: int = DEVICE_MEM_MAP_OFFSET
    adc_port_map: dict[int, int] = field(
        default_factory=lambda: get_adc_stream_ports(
            ROUGE_ADC_BASE_PORT, DEVICE_ADCS
        )
    )
    max_buffer_size: int = DEVICE_MAX_BUFFER_SIZE
    sample_rate_hz: int = DEVICE_SAMPLE_RATE_HZ


@dataclass(slots=True, frozen=True)
class RootCfg:
    name: str | None = ""
    description: str = ""
    expand: bool = True
    timeout: float = 1.0
    initRead: bool = True
    initWrite: bool = False
    pollEn: bool = True
    maxLog: int = 1000
    unifyLogs: bool = False
