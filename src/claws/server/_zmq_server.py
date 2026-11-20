from dataclasses import asdict
from typing import Final

import abort_trigger_daq_rpty_stmlb125_14 as target
import axi_soc_7000_core.hardware.red_pitaya_stemlab_125_14 as hardware_core
import rogue

from pyrogue._Root import Root
from pyrogue.interfaces import ZmqServer
from pyrogue.interfaces.stream import Fifo

from claws.data import DeviceCfg, RootCfg, ZMQCfg

_DEFAULT_ROOT_CFG: Final[RootCfg] = RootCfg()
_DEFAULT_ZMQ_CFG: Final[ZMQCfg] = ZMQCfg()
_DEFAULT_DEVICE_CFG: Final[DeviceCfg] = DeviceCfg()


def compose_root(
    root_cfg: RootCfg = _DEFAULT_ROOT_CFG,
    zmq_cfg: ZMQCfg = _DEFAULT_ZMQ_CFG,
    device_cfg: DeviceCfg = _DEFAULT_DEVICE_CFG,
) -> Root:
    root = Root(**asdict(root_cfg))
    root.addInterface(
        ZmqServer(root=root, addr=zmq_cfg.host, port=zmq_cfg.port)
    )
    root.add(
        target.Zynq7SoC(
            memBase=rogue.interfaces.memory.TcpClient(
                device_cfg.host, device_cfg.mem_map_port
            ),
            offset=device_cfg.mem_map_offset,  # 32-bit address space
            n_adc_channels=len(device_cfg.adc_port_map),
            expand=True,
        )
    )
    ring_buffers = [
        rogue.interfaces.stream.TcpClient(device_cfg.host, port)
        for port in device_cfg.adc_port_map.values()
    ]

    for channel, buffer in zip(device_cfg.adc_port_map, ring_buffers):
        drop_fifo = Fifo(
            name=f"AdcDropFifo[{channel}]",
            maxDepth=1,
            hidden=False,
        )
        ring_proc = hardware_core.RingBufferProcessor(
            name=f"AdcProcessor[{channel}]",
            sampleRate=device_cfg.sample_rate_hz,
            maxSize=device_cfg.max_buffer_size,
        )

        buffer >> drop_fifo >> ring_proc
        root.add(drop_fifo)
        root.add(ring_proc)

    return root
