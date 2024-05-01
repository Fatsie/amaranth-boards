from typing import Tuple, Union

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out
from amaranth.build import Platform

__all__ = ["VGA"]


# Constants for standard 640x480 VGA timing
# See: http://www.tinyvga.com/vga-timing/640x480@60Hz
ACTPIXEL = 640
HPORCH_FRONT = 16
HPORCH_SYNC = 96
HPORCH_BACK = 48
HTOTAL = ACTPIXEL + HPORCH_FRONT + HPORCH_SYNC + HPORCH_BACK

ACTLINE = 480
VPORCH_FRONT = 10
VPORCH_SYNC = 2
VPORCH_BACK = 33
VTOTAL = ACTLINE + VPORCH_FRONT + VPORCH_SYNC + VPORCH_BACK


class RGBOn(wiring.Component):
    """Component giving rgb color values for a pixel that is on.
    It takes into acocunt a halfbrite signal.
    """
    def __init__(self, *,
        r_shape: wiring.ShapeCastable,
        g_shape: wiring.ShapeCastable,
        b_shape: wiring.ShapeCastable,
    ):
        super().__init__({
            "halfbrite": In(1),

            "r_on": Out(r_shape),
            "b_on": Out(b_shape),
            "g_on": Out(g_shape),
        })

    def elaborate(self, platform):
        m = Module()

        m.d.comb += (
            self.r_on.eq(~0),
            self.g_on.eq(~0),
            self.b_on.eq(~0),
        )
        with m.If(self.halfbrite):
            m.d.comb += (
                self.r_on[-1].eq(0),
                self.g_on[-1].eq(0),
                self.b_on[-1].eq(0),
            )

        return m


class LineGen(wiring.Component):
    """Component that generates a test color pattern for a line.

    Fields:
      * vporch: wether vertical scan is in porch region
      * halfbrite: wether line has to be drawn with half brightness
      * r, g, b: pixel color values
      * hsync: active when corresponding VGA hsync is asserted.
      * newline: single cycle pulse indicating next pixel is start of new line.
    """
    def __init__(self, *,
        r_shape: Shape, g_shape: Shape, b_shape: Shape,
        block_cycles: int=(ACTPIXEL//8),
        hporch_front: int=HPORCH_FRONT, hporch_sync: int=HPORCH_SYNC, hporch_back=HPORCH_BACK,
    ):
        super().__init__({
            "vporch": In(1),
            "halfbrite": In(1),

            "r": Out(r_shape),
            "g": Out(g_shape),
            "b": Out(b_shape),
            "hsync": Out(1),
            "newline": Out(1),
        })

        self._block_cycles = block_cycles
        self._actpixel = 8*block_cycles
        self._hporch_front = hporch_front
        self._hporch_sync = hporch_sync
        self._hporch_back = hporch_back
        self._htotal = 8*block_cycles + hporch_front + hporch_sync + hporch_back

    def elaborate(self, platform: Platform):
        m = Module()

        rgb_on = RGBOn(
            r_shape=self.r.shape(),
            b_shape=self.b.shape(),
            g_shape=self.g.shape(),
        )
        m.submodules["rgb_on"] = rgb_on

        m.d.comb += rgb_on.halfbrite.eq(self.halfbrite)
        r_on = rgb_on.r_on
        b_on = rgb_on.b_on
        g_on = rgb_on.g_on

        # Increase pixel number with each clock cycle
        # pixel 0 is first active pixel
        pixel = Signal(range(0, self._htotal))
        m.d.sync += pixel.eq(Mux(pixel == (self._htotal - 1), 0, pixel + 1))

        # Increase block number each number of self._block_cycles
        block_pixel = Signal(range(0, self._block_cycles))
        block = Signal(range(0, 9))
        with m.If(pixel == (self._htotal - 1)):
            m.d.sync += (
                block_pixel.eq(0),
                block.eq(0),
            )
        with m.Elif(block_pixel == (self._block_cycles - 1)):
            m.d.sync += block_pixel.eq(0)
            with m.If(block < 8):
                m.d.sync += block.eq(block + 1)
        with m.Else():
            m.d.sync += block_pixel.eq(block_pixel + 1)

        # r, g and b value for blocks of 80 pixels wide
        with m.If(self.vporch):
            # Give black pixel if not in an active line
            m.d.comb += (
                self.r.eq(0),
                self.g.eq(0),
                self.b.eq(0),
            )
        with m.Else():
            with m.Switch(block):
                with m.Case(0):
                    m.d.comb += (
                        self.r.eq(r_on),
                        self.g.eq(0),
                        self.b.eq(0),
                    )
                with m.Case(1):
                    m.d.comb += (
                        self.r.eq(0),
                        self.g.eq(g_on),
                        self.b.eq(0),
                    )
                with m.Case(2):
                    m.d.comb += (
                        self.r.eq(0),
                        self.g.eq(0),
                        self.b.eq(b_on),
                    )
                with m.Case(3):
                    m.d.comb += (
                        self.r.eq(0),
                        self.g.eq(0),
                        self.b.eq(0),
                    )
                with m.Case(4):
                    m.d.comb += (
                        self.r.eq(r_on),
                        self.g.eq(g_on),
                        self.b.eq(0),
                    )
                with m.Case(5):
                    m.d.comb += (
                        self.r.eq(r_on),
                        self.g.eq(0),
                        self.b.eq(b_on),
                    )
                with m.Case(6):
                    m.d.comb += (
                        self.r.eq(0),
                        self.g.eq(g_on),
                        self.b.eq(b_on),
                    )
                with m.Case(7):
                    m.d.comb += (
                        self.r.eq(r_on),
                        self.g.eq(g_on),
                        self.b.eq(b_on),
                    )
                with m.Default():
                    # block is > 7 if not in active pixel; give black pixel
                    m.d.comb += (
                        self.r.eq(0),
                        self.g.eq(0),
                        self.b.eq(0),
                    )

        m.d.comb += (
            # new line when end of hsync
            self.newline.eq(pixel == (self._htotal - 1)),
            # hsync after hporch_front
            self.hsync.eq(
                (pixel >= (self._actpixel + self._hporch_front))
                & (pixel < (self._actpixel + self._hporch_front + self._hporch_sync))
            ),
        )

        return m


class VScanGen(wiring.Component):
    """Component that generate the vertical VGA scan pattern.

    Fields:
      * newline: single clock cycle pulse that indicates a new line is started.
      * vporch: active when in a line not displayed.
      * vsync: active with corresponding VGA vsync need to be asserted
      * halfbrite: active for a line to be shown at half brightness
      * newframe: single cycle pulse that indicates next line is a new frame
    """
    newline: In(1)

    vporch: Out(1)
    vsync: Out(1)
    halfbrite: Out(1)
    newframe: Out(1)

    def elaborate(self, platform: Platform):
        m = Module()

        # generate line number
        # line 0 is first active line
        line = Signal(range(0, VTOTAL))
        with m.If(self.newline):
            m.d.sync += line.eq(Mux(line == (VTOTAL - 1), 0, line + 1))

        m.d.comb += (
            self.vporch.eq(line >= ACTLINE),
            self.vsync.eq(
                (line >= (ACTLINE + VPORCH_FRONT))
                & (line < (ACTLINE + VPORCH_FRONT + VPORCH_SYNC))
            ),
            self.halfbrite.eq(line[6]), # Toggle every 64 lines
            self.newframe.eq((line == (VTOTAL - 1)) & self.newline)
        )

        return m


class VGA(Elaboratable):
    """640x480 VGA test pattern output. It generates a block pattern
    of primary colors. It also generate block with half brightness to
    check the endianess of the color bits.

    Optionally a clock frequency can be provided that will be used to
    stretch the pixels so a standard 640x480@60Hz pattern is generated.
    The clock frequency has to be at least 25.2MHz.
    If clock frequency is not given it is assumed that this module is run
    with 25.2MHz clock frequency.
    """
    def __init__(self,
        res_name: str="vga", res_num: int=0,
        *, clk_freq: float=25.2e6
    ) -> None:
        self._res_name = res_name
        self._res_num = res_num

        self._freq_ratio = ratio = round(clk_freq/25.2e6, 4)
        if ratio < 1.0:
            raise ValueError("VGA test pattern has to be run with a min. freq. of 25.2MHz")

    def elaborate(self, platform: Platform):
        vga = platform.request(self._res_name, self._res_num)
        ratio = self._freq_ratio

        m = Module()

        if ratio < 1.01:
            linegen = LineGen(
                r_shape=vga.r.width,
                g_shape=vga.g.width,
                b_shape=vga.b.width,
            )
        else:
            hporch_sync = round(ratio*HPORCH_SYNC)
            hporch_back = round(ratio*HPORCH_BACK)
            block_cycles = round(ratio*ACTPIXEL/8)
            htotal = round(ratio*HTOTAL)
            hporch_front = htotal - (8*block_cycles + hporch_sync + hporch_back)

            linegen = LineGen(
                r_shape=vga.r.width,
                g_shape=vga.g.width,
                b_shape=vga.b.width,
                block_cycles=block_cycles,
                hporch_front=hporch_front, hporch_sync=hporch_sync, hporch_back=hporch_back,
            )
        m.submodules["linegen"] = linegen

        m.submodules["vgen"] = vgen = VScanGen()

        m.d.comb += (
            linegen.vporch.eq(vgen.vporch),
            linegen.halfbrite.eq(vgen.halfbrite),
            vgen.newline.eq(linegen.newline),
            vga.r.o.eq(linegen.r),
            vga.g.o.eq(linegen.g),
            vga.b.o.eq(linegen.b),
            vga.hs.o.eq(~linegen.hsync),
            vga.vs.o.eq(~vgen.vsync),
        )

        return m