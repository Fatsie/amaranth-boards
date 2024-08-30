from amaranth import *
from amaranth.build import *
from ._zynq import XilinxZynqPlatform

from .resources import *


__all__ = ["ZynqBerry"]


# ZynqBerry is also know as Trenz TE0726.
# TE0726-03 is taken as input for this board definition
class ZynqBerry(XilinxZynqPlatform):
    device     = "xc7z010"
    package    = "clg225"
    speed      = "1"
    default_clk = "clk33"
    resources  = [
        Resource("clk33", 0,
            Pins("C7", dir="i"), Clock(33.333e6), Attrs(IOSTANDARD="LVCMOS33"),
        ),

        I2CResource("i2c_mux", 0, scl="B12", sda="D13"),
        *SPIFlashResources(0,
            cs_n="A5", clk="A10", copi="A8", cipo="A7", wp_n="C8", hold_n="A9",
        ),
        *SDCardResources(0,
            clk="B7", cmd="B10", dat0="D6", dat1="C6", dat2="B9", dat3="D10",
        ),
        ULPIResource(0,
            data="E15 C11 D15 A14 A15 C14 A13 D14",
            clk="B14", dir="D11", nxt="C12", stp="B15",
        ),

        # Combined reset for ULPI transceiver + USB HUB & LAN
        Resource("rst_usb", 0,
            PinsN("D9", dir="o"),
            Attrs(IOSTANDARD="LVCMOS33"),
        ),

        Resource("hdmi", 0,
            # For I2C an external mulitplexer is used
            Subsignal("cec",     Pins("K12"), Attrs(IOSTANDARD="LVCMOS33")),
            # Subsignal("clk",     DiffPairs("R8", "R7", dir="o")),
            # Avoid negative/positive package pin errors
            Subsignal("clk",     DiffPairsN("R7", "R8", dir="o")),
            # Subsignal("d",       DiffPairs("P9 P10 P11", "P8 R10 R11", dir="o")),
            # Avoid negative/positive package pin errors
            Subsignal("d",       DiffPairs("P8 P10 P11", "P9 R10 R11", dir="o")),
            Attrs(IOSTANDARD="TMDS_33"),
        ),
        Resource("dsi", 0,
            # For I2C an external mulitplexer is used
            Subsignal("clk",     DiffPairs("E12", "E11")),
            Subsignal("d",       DiffPairs("F14 E13", "F13 F12")),
            Attrs(IOSTANDARD="TMDS_33"),
        ),
        Resource("csi", 0,
            Subsignal("clk",     DiffPairs("N11", "N12")),
            Subsignal("d",       DiffPairs("M10 P13", "M11 P14")),
            Subsignal("lp",      DiffPairs("N9", "M9")),
            Attrs(IOSTANDARD="TMDS_33"),
        ),
    ]
    connectors = [
        Connector("J8", 0, # Raspberry Pi header
            "-   -  " # 1  2
            "K15 -  " # 3  4
            "J14 -  " # 5  6
            "H12 M12" # 7  8
            "-   N13" # 9  10
            "G11 H11" # 11 12
            "G12 -  " # 13 14
            "H13 J11" # 15 16
            "-   K11" # 17 18
            "H14 -  " # 19 20
            "J13 K13" # 21 22
            "J15 L15" # 23 24
            "-   L14" # 25 26
            "-   -  " # 27 28; ID_SDA and ID_SCL output from I2C MUX
            "N14 -  " # 29 30
            "R15 M15" # 31 32
            "R13 -  " # 33 34
            "R12 L13" # 35 36
            "L12 M14" # 37 38
            "-   P15" # 39 40
        )
    ]

if __name__ == "__main__":
    class Top(Elaboratable):
        def elaborate(self, platform: Platform):
            m = Module()

            ps_clk = platform.request("ps_clk")
            # rst = platform.request("rst_usb")
            # m.d.comb += rst.io.o.eq(0)

            hdmi = platform.request("hdmi", 0)
            counter = Signal(8)
            m.d.sync += counter.eq(counter + 1)
            m.d.comb += (
                hdmi.cec.o.eq(counter[-1]),
                hdmi.cec.oe.eq(1),
                hdmi.clk.o.eq(ps_clk.i),
            )

            return m

    ZynqBerry().build(Top(), do_program=False)
