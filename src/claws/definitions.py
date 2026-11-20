###############################################################################
# Device Settings
###############################################################################
DEVICE_ADCS = 2
DEVICE_MEM_MAP_OFFSET = 0x4000_0000
DEVICE_MAX_BUFFER_SIZE = 2**14
DEVICE_SAMPLE_RATE_HZ = 125_000_000

###############################################################################
# ROGUE Streaming Ports
###############################################################################
ROGUE_MEM_MAP_PORT = 9000
ROUGE_ADC_BASE_PORT = 10000
ROUGE_DEFAULT_ZMQ_BASE_PORT = 9099


def get_adc_stream_ports(
    base_port: int = ROUGE_ADC_BASE_PORT, adcs: int = DEVICE_ADCS
) -> dict[int, int]:
    return {adc: base_port + 2 * adc for adc in range(adcs)}


###############################################################################
# Discovery Server
###############################################################################
DISCOVERY_PORT_OFFSET = 3
