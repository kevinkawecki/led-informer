#!/usr/bin/env python
import time
import sys
import os

from helper import from_minutes, get_hour, get_minutes, get_month_day_dow

sys.path.append(os.path.abspath(os.path.dirname(__file__)
                               + '/../rpi-rgb-led-matrix/bindings/python/'))
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions


# GLOBALS for this class 
RED = graphics.Color(255, 0, 0)
PURP = graphics.Color(100, 0, 255)
YELLOW = graphics.Color(155, 255, 100)
BLUE = graphics.Color(0, 0, 255)
WHITE = graphics.Color(155, 155, 155)

CLK1 = graphics.Color(200, 220, 215)
CLK2 = graphics.Color(210, 200, 255)

TIME_CALENDAR = 20

class DisplayDriver:
    def __init__(self): 
        # Configuration for the matrix
        self.options = RGBMatrixOptions()
        self.options.rows = 32
        self.options.cols = 64
        self.options.chain_length = 1
        self.options.parallel = 1
        self.options.hardware_mapping = 'adafruit-hat'
        self.options.brightness = 50

        self.matrix = RGBMatrix(options = self.options)
        self.canvas = self.matrix.CreateFrameCanvas()
        self.bigfont = graphics.Font()
        self.bigfont.LoadFont(os.path.dirname(__file__) + "/../rpi-rgb-led-matrix/fonts/5x8.bdf")
        self.smallfont = graphics.Font()
        self.smallfont.LoadFont("../rpi-rgb-led-matrix/fonts/4x6.bdf")
        self.monthfont = graphics.Font()
        self.monthfont.LoadFont("../rpi-rgb-led-matrix/fonts/7x13B.bdf")
        self.timefont = graphics.Font()
        self.timefont.LoadFont("../rpi-rgb-led-matrix/fonts/9x18B.bdf")

        self.N_times = []
        self.S_times = []

        self.hcolor = CLK1
        self.mcolor = CLK2

        self.hcount = 0
        self.mcount = 30
        self.count = 0

        self.showClock = True
        self.showTick = True


    def loop(self):
        try:
            self.canvas.Clear()

            if self.showClock: 
                self.displayClock()
            else: 
                self.displayCal()
            #self.printLines()
            if len(self.N_times) == 0 and len(self.S_times) == 0: 
                #print("no times to show")
                self.theLisDown()
            else:
                self.displayTimes()

            self.tick()

            self.canvas = self.matrix.SwapOnVSync(self.canvas)

        except Exception as e:
            print("Display has failed!")
            print(e)

    def theLisDown(self):
        graphics.DrawText(self.canvas, self.bigfont, 30, 12, 
                          PURP, "The L ")
        graphics.DrawText(self.canvas, self.bigfont, 35, 20, 
                          PURP, "is")
        graphics.DrawText(self.canvas, self.bigfont, 30, 28, 
                          RED, "DOWN!")

    def displayCal(self):
        print("TEST")
        month, day, dow = get_month_day_dow()
        graphics.DrawText(self.canvas, self.monthfont, 2, 10, 
                          self.hcolor, dow)
        graphics.DrawText(self.canvas, self.monthfont, 2, 20, 
                          self.hcolor, month)
        graphics.DrawText(self.canvas, self.monthfont, 9, 30, 
                          self.hcolor, day)

    def displayClock(self):
        hour = get_hour()
        minutes = get_minutes()

        graphics.DrawText(self.canvas, self.timefont, 3, 14, 
                          self.hcolor, hour)
        graphics.DrawText(self.canvas, self.timefont, 3, 27, 
                          self.mcolor, minutes)

    def tick(self):
        if self.hcolor == CLK1:
            self.hcolor = CLK2
        else:
            self.hcolor = CLK1 

        if self.mcolor == CLK1:
            self.mcolor = CLK2
        else:
            self.mcolor = CLK1

        self.hcolor = CLK1
        self.mcolor = CLK1

        if self.count % TIME_CALENDAR == 0: 
            self.showClock = not self.showClock
            self.count = 0

        if self.showTick: 
            graphics.DrawText(self.canvas, self.bigfont, -2, 32, 
                          PURP, ".")
        self.showTick = not self.showTick

        self.count += 1

    def setNTimes(self, N_times):
        self.N_times = N_times

    def setSTimes(self, S_times):
        self.S_times = S_times

    def displayTimes(self):
        # generate northbound col
        graphics.DrawText(self.canvas, self.bigfont, 24, 8, BLUE, "Man")
        if len(self.N_times) == 0:
            graphics.DrawText(self.canvas, self.smallfont, 24, 16, 
                              BLUE, "DOWN!")
        else:
            self.printTimeCol(self.N_times, 1)

        # generate southbound col
        graphics.DrawText(self.canvas, self.bigfont, 45, 8, YELLOW, "Bkn")
        if len(self.S_times) == 0:
            graphics.DrawText(self.canvas, self.smallfont, 45, 16, 
                              YELLOW, "DOWN!")
        else:
            self.printTimeCol(self.S_times, 2)

    def printLines(self): 
            graphics.DrawLine(self.canvas, 21, 4, 21, 28, WHITE)
            graphics.DrawLine(self.canvas, 43, 4, 43, 28, WHITE)

    def printTimeCol(self, times, col):
        if col == 1:
            color = BLUE
        elif col == 2:
            color = YELLOW
        else:
            color = RED

        printcol = col * 24
        if col == 2: 
            printcol -= 1

        printrow = 9
        nstring = ''
        firstTime = True
        for t in times: 
            printrow += 7
            nextmin, nextsec = from_minutes(t)
            if firstTime: 
                firstTime = False
                if nextmin == 0: 
                    nstring = f":{nextsec:02d}"
                elif nextmin <= 5:
                    nstring = f"{nextmin}:{nextsec:02d}"
                else: 
                    nstring = f"{nextmin}"
            else: 
                nstring = f"{nextmin}"

            graphics.DrawText(self.canvas, self.smallfont, 
                              printcol, printrow, 
                              color, nstring )

    def runTest(self):
        try:
            print("Press CTRL-C to stop.")
            self.canvas.Clear()

            graphics.DrawLine(self.canvas, 5, 5, 22, 23, RED)
            len = graphics.DrawText(self.canvas, self.font, 0, 10,
                                    YELLOW, "Hi Alex")
            len = graphics.DrawText(self.canvas, self.font, 0, 24, BLUE, "from kevin")
            self.canvas = self.matrix.SwapOnVSync(self.canvas)

        except Exception as e:
            print("Display has failed!")
            print(e)


    def genStringFromTimes_old(self, times):
        nstring = ''
        firstTime = True
        for t in times: 
            nextmin, nextsec = from_minutes(t)
            if firstTime: 
                firstTime = False
                if nextmin == 0: 
                    nstring += f".{nextsec:02d}"
                elif nextmin <= 5:
                    nstring += f"{nextmin}.{nextsec:02d}"
                else: 
                    nstring += f"{nextmin}"
            else: 
                nstring += f",{nextmin}"
        return nstring


