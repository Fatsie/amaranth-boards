from amaranth.build import *
from .de10_nano import DE10NanoPlatform
from .resources import *


__all__ = ["MisterPlatform"]


# The MiSTer platform is using the DE10 nano as the base FPGA platform
# with standardized expansion ports
class MisterPlatform(DE10NanoPlatform):
    resources   = [
        *DE10NanoPlatform.resources,

        # MiSTer SDRAM Board (required)
        # https://github.com/MiSTer-devel/Hardware_MiSTer/blob/master/releases/sdram_xs_2.2.pdf
        SDRAMResource(0,
            clk="20", cs_n="33", we_n="27", ras_n="32", cas_n="31",
            ba="34 35", a="37 38 39 40 28 25 26 23 24 21 36 22 19",
            dq="1 2 3 4 5 6 7 8 18 17 16 15 14 13 9 10",
            dqm="", conn=("gpio", 0), attrs=Attrs(io_standard="3.3-V LVCMOS")),

        # MiSTer I/O Board (optional, but highly recommended)
        # https://github.com/MiSTer-devel/Hardware_MiSTer/blob/master/releases/iobrd_6.0.pdf
        Resource("power_led", 0, PinsN("1", dir="o", conn=("gpio", 1)), Attrs(io_standard="3.3-V LVTTL")),
        Resource("disk_led", 0, PinsN("3", dir="o", conn=("gpio", 1)), Attrs(io_standard="3.3-V LVTTL")),
        Resource("user_led", 0, PinsN("5", dir="o", conn=("gpio", 1)), Attrs(io_standard="3.3-V LVTTL")),

        Resource("reset_switch", 0, PinsN("17", dir="i", conn=("gpio", 1)), Attrs(io_standard="3.3-V LVTTL")),
        Resource("osd_switch", 0, PinsN("13", dir="i", conn=("gpio", 1)), Attrs(io_standard="3.3-V LVTTL")),
        Resource("user_switch", 0, PinsN("15", dir="i", conn=("gpio", 1)), Attrs(io_standard="3.3-V LVTTL")),

        Resource("audio", 0,
            Subsignal("l", Pins("2", dir="o", conn=("gpio", 1))),
            Subsignal("r", Pins("7", dir="o", conn=("gpio", 1))),
            Attrs(io_standard="3.3-V LVTTL")),

        Resource("toslink", 0, Pins("9", dir="o", conn=("gpio", 1))),

        *SDCardResources(0,
            clk="13", cmd="8", 
            dat0="16", dat1="18", dat2="4", dat3="6",
            conn=("gpio", 1), attrs=Attrs(io_standard="3.3-V LVTTL")),

        # The schematic is difficult to understand here...
        VGAResource(0,
            r="28 32 34 36 38 40",
            g="27 31 33 35 37 39",
            b="21 23 25 26 24 24",
            hs="20", vs="19",
            conn=("gpio", 1),
            attrs=Attrs(io_standard="3.3-V LVTTL"))
    ]


if __name__ == "__main__":
    from .test.blinky import Blinky
    MisterPlatform().build(Blinky(), do_program=True)
