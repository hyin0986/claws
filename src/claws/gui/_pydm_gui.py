import pyrogue.pydm

from axi_soc_7000_core.hardware.red_pitaya_stemlab_125_14.gui.GuiTop import (
    GuiTop,
)

from claws.data import ZMQCfg


def start_gui(cfg: ZMQCfg):
    pyrogue.pydm.runPyDM(
        serverList=f"{cfg.host}:{cfg.port}",
        display_factory=lambda parent=None, args=[], macros=None: GuiTop(
            parent=parent,
            args=args + ["numAdcCh=2", "numDacCh=0"],
            macros=macros,
        ),
        sizeX=800,
        sizeY=800,
    )
