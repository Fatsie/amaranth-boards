from amaranth.build import *
from amaranth.vendor import XilinxPlatform
from .resources import *


__all__ = [
    "TE0710_03_42C21_APlatform", "TE0710_03_42I21_APlatform",
    "TE0710_03_72C21_APlatform", "TE0710_03_72I21_APlatform",
]


class _TE0710(XilinxPlatform):
    """Common class for the Trenz Electronic TE710 boards.
    There are different boards with different size Artix 7 FPGA but they use pin
    compatible 
    """
    package = "csg324"
    default_clk = "ddr_pllclk"
    resources = [
        Resource("ddr_pllclk", 0,
            Pins("F4", dir="i"), Clock(100e6), Attrs(IOSTANDARD="SSTL15"),
        ),
        *LEDResources(pins="L15", invert=True, attrs=Attrs(IOSTANDARD="LVCMOS33")),
        *QSPIResource(0,
            cs_n="L13", clk="E9", dq0="K17", dq1="K18", dq2="L14", dq3="M14",
            attrs=Attrs(IOSTANDARD="LVCMOS33"),
        ),
        DDR3Resource(0,
            clk_p="A4", clk_n="A3", clk_en="H2", cs_n="H5", we_n="G4",
            ras_n="J2", cas_n="H6",
            a="D3 B2 G1 D4 E1 D2 F1 D5 C1 B3 E3 A1 E2 B4 C2 H1",
            ba="J4 F3 G2", dqs_p="A6", dqs_n="A5",
            dq="C5 B7 B6 C6 C7 D8 E5 E7", dm="E6", odt="G6",
            diff_attrs=Attrs(IOSTANDARD="LVDS"),
            attrs=Attrs(IOSTANDARD="LVCMOS15"),
        ),
    ]
    connectors = [
        Connector("JM1", 0,
            "-   -  " #  1: VIN, GND
            "-   -  " #  3: VIN, ETH_TD_P
            "-   -  " #  5: VIN, ETH_TD_N
            "-   -  " #  7: NOSEQ, GND
            "-   -  " #  9: VCCIO15, ETH_RD_P
            "-   -  " # 11: VCCIO15, ETH_RD_N
            "-   -  " # 13: 3.3VIN, 3.3V
            "-   -  " # 15: 3.3VIN, ETH2_TD_P
            "C11 -  " # 17: B16_L13_P, ETH2_TD_N
            "C10 -  " # 19: B16_L13_N, GND
            "A10 -  " # 21: B16_L14_P, ETH2_RD_P
            "A9  -  " # 23: B16_L14_N, ETH2_RD_N
            "C9  -  " # 25: B16_L11_P, GND
            "B9  -  " # 27: B16_L11_N, EN1
            "-   -  " # 29: GND, PGOOD
            "F13 -  " # 31: B15_L5_P, BOOTMODE
            "F15 -  " # 33: B15_L5_N, GND
            "H14 E18" # 35: B15_L15_P, B15_L21_P
            "G14 D18" # 37: B15_L15_N, B15_L21_N
            "-   J18" # 39: 1.8V, B15_L23_N
            "B18 J17" # 41: B15_L10_P, B15_L23_P
            "A18 -  " # 43: B15_L10_N, GND
            "B17 G18" # 45: B17_L7_N, B15_L22_P
            "B16 F18" # 47: B17_L7_P, B15_L22_N
            "J14 C12" # 49: B15_L19_P, B15_L3_P
            "H15 B12" # 51: B15_L19_N, B15_L3_N
            "-   -  " # 53: GND, GND
            "A16 K13" # 55: B15_L8_N, B15_L17_P
            "A15 J13" # 57: B15_L8_P, B15_L17_N
            "G16 K15" # 59: B15_L13_N, B15_L24_P
            "H16 J15" # 61: B15_L13_P, B15_L24_N
            "-   -  " # 63: GND, GND
            "F16 B15" # 65: B15_L14_N, B15_L11_N
            "F15 E15" # 67: B15_L14_P, B15_L11_P
            "A14 H17" # 69: B15_L9_N, B15_L18_P
            "A13 G17" # 71: B15_L9_P, B15_L18_N
            "-   -  " # 73: GND, GND
            "C15 E17" # 75: B15_L12_N, B15_L16_P
            "D15 D17" # 77: B15_L12_P, B15_L16_N
            "-   C17" # 79: VBATT (NC), B15_L20_N
            "A11 C16" # 81: B15_L4_N, B15_L20_P
            "B11 -  " # 83: B15_L4_P, GND
            "B8  D14" # 85: B16_IO0, B15_L1_P
            "R13 C14" # 87: B14_IO1, B15_L1_N
            "-   -  " # 89: JTAGSEL, GND
          "-   -  " # 17: NC, SC_nRST
            "-   -  " # 19: 1.5V, GND
            "-   -  " # 21: NC, NC
            "-   -  " # 23: NC, NC
            "-   -  " # 25: NC, NC
            "-   -  " # 27: NC, NC
            "-   -  " # 29: NC, GND
            "-   V9 " # 31: NC, B34_L21_N
            "-   U9 " # 33: NC, B34_L21_P
            "-   N6 " # 35: NC, B34_L18_N
            "-   M6 " # 37: NC, B34_L18_P
            "-   -  " # 39: GND, GND
            "R8  V7 " # 41: B34_L24_P, B34_L20_P
            "T8  V6 " # 43: B34_L24_N, B34_L20_N
            "U7  T5 " # 45: B34_L22_P, B34_L12_P
            "U6  T4 " # 47: B34_L22_N, N34_L12_N
            "-   -  " # 49: GND, GND
            "P4  R3 " # 51: B34_L14_P, B34_L11_P
            "P3  T3 " # 53: B34_L14_N, B34_L11_N
            "M3  N5 " # 55: B34_L4_P, B34_L13_P
            "M2  P5 " # 57: B34_L4_N, B34_L13_N
            "-   -  " # 59: GND, GND
            "L3  V5 " # 61: B34_L2_N, B34_L10_P
            "K3  V4 " # 63: B34_L2_P, B34_L10_N
            "K5  R7 " # 65: B34_L5_P, B34_L23_P
            "L4  T6 " # 67: B34_L5_N, B34_L23_N
            "-   -  " # 69: GNd, GND
            "M4  U4 " # 71: B34_L16_P, B34_L8_P
            "N4  U3 " # 73: B34_L16_N, B34_L8_N
            "T1  V1 " # 75: B34_L17_N, B34_L7_N
            "R1  U1 " # 77: B34_L17_P, B34_L7_P
            "-   -  " # 79: GND, GND
            "L5  V2 " # 81: B34_L6_N, B34_L9_N
            "L6  U2 " # 83: B34_L6_P, B34_L9_P
            "N1  R2 " # 85: B34_L3_N, B35_L15_N
            "N2  P2 " # 87: B34_L3_P, B34_L15_P
            "-   -  " # 89: B34_25, GND
            "-   R6 " # 91: 3.3V, B34_L19_P
            "-   R5 " # 93: TMS, B34_L19_N
            "-   M1 " # 95: TDI, B34_L1_N
            "-   L1 " # 97: TDO, B34_L1_P
            "-   K6 " # 99: TCK, B34_0
        ),
    ]


class TE0710_03_42C21_APlatform(_TE0710):
    device = "xc7a35t"
    speed = "2"
class TE0710_03_42I21_APlatform(_TE0710):
    device = "xc7a35t"
    speed = "2"
class TE0710_03_72C21_APlatform(_TE0710):
    device = "xc7a100t"
    speed = "2"
class TE0710_03_72I21_APlatform(_TE0710):
    device = "xc7a100t"
    speed = "2"


if __name__ == "__main__":
    from .test.blinky import Blinky
    TE0710_03_42C21_APlatform().build(Blinky(), do_program=True)
