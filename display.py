#!/usr/bin/env python
import time
import sys
import os

from helper import from_minutes

sys.path.append(os.path.abspath(os.path.dirname(__file__)
                               + '/../rpi-rgb-led-matrix/bindings/python/'))
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions

RED = graphics.Color(255, 0, 0)
PURP = graphics.Color(100, 0, 255)
YELLOW = graphics.Color(155, 255, 100)
BLUE = graphics.Color(0, 0, 255)
WHITE = graphics.Color(155, 155, 155)

CLK1 = graphics.Color(200, 220, 215)
CLK2 = graphics.Color(210, 200, 255)

class DisplayDriver:
    def __init__(self): 
        # Configuration for the matrix
        self.options = RGBMatrixOptions()
        self.options.rows = 32
        self.options.cols = 64
        self.options.chain_length = 1
        self.options.parallel = 1
        self.options.hardware_mapping = 'adafruit-hat'
        self.options.brightness = 40

        self.matrix = RGBMatrix(options = self.options)
        self.canvas = self.matrix.CreateFrameCanvas()
        self.bigfont = graphics.Font()
        self.bigfont.LoadFont(os.path.dirname(__file__) + "/../rpi-rgb-led-matrix/fonts/5x8.bdf")
        self.smallfont = graphics.Font()
        self.smallfont.LoadFont("../rpi-rgb-led-matrix/fonts/4x6.bdf")
        self.biggerfont = graphics.Font()
        self.biggerfont.LoadFont("../rpi-rgb-led-matrix/fonts/9x18B.bdf")

        self.N_times = []
        self.S_times = []

        self.hcolor = CLK1
        self.mcolor = CLK2

        self.hcount = 0
        self.mcount = 30


    def loop(self):
        try:
            self.canvas.Clear()

            self.displayClock()
            #self.printLines()
            if len(self.N_times) == 0 and len(self.S_times) == 0: 
                #print("no times to show")
                self.theLisDown()
            else:
                self.displayTimes()
            #self.tick()

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

    def displayClock(self):
        hour = time.localtime().tm_hour
        if hour > 12: 
            hour -= 12
        elif hour == 0: 
            hour = 12

        minutes = time.localtime().tm_min
        clockstring = f"{hour}:{minutes:02d}"
        hrstring = f"{hour:02d}"

        mnstring = f"{minutes:02d}"
        if False:
            hrstring = f"{self.hcount:02d}"
            if self.hcount == 12:
                self.hcount = 0
            else:
                self.hcount += 1
            mnstring = f"{self.mcount:02d}"
            if self.mcount == 59:
                self.mcount = 0
            else:
                self.mcount += 1


        graphics.DrawText(self.canvas, self.biggerfont, 3, 14, 
                          self.hcolor, hrstring)
        graphics.DrawText(self.canvas, self.biggerfont, 3, 27, 
                          self.mcolor, mnstring)
    def tick(self):
        if self.hcolor == CLK1:
            self.hcolor = CLK2
        else:
            self.hcolor = CLK1 

        if self.mcolor == CLK1:
            self.mcolor = CLK2
        else:
            self.mcolor = CLK1

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
        graphics.DrawText(self.canvas, self.bigfont, 45, 8, YELLOW, "Can")
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

        printrow = 8
        nstring = ''
        firstTime = True
        for t in times: 
            printrow += 8
            nextmin, nextsec = from_minutes(t)
            if firstTime: 
                firstTime = False
                if nextmin == 0: 
                    nstring = f".{nextsec:02d}"
                elif nextmin <= 5:
                    nstring = f"{nextmin}.{nextsec:02d}"
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


