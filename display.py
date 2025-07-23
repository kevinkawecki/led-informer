#!/usr/bin/env python
import time
import sys
import os

from helper import from_minutes, get_hour, get_minutes, get_month_day_dow

sys.path.append(os.path.abspath(os.path.dirname(__file__)
							   + '/../rpi-rgb-led-matrix/bindings/python/'))
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions

CLOCK = 0
CLOCK_CALENDAR_T = 1
CALENDAR = 2
CALENDAR_WEATHER_T = 3
CURRENT_TEMP = 4
TEMP_RAIN_T = 5
CURRENT_RAIN = 6
STATE_MAX = 7
DAILY_WEATHER = 5

TIME_CLOCK =  15
TIME_CALENDAR = 3
TIME_TEMP = 10
TIME_RAIN = 5

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

		self.STATE = CLOCK
		self.stateTime = time.time()

		self.showTick = True

		self.curTemp = 0.
		self.dailyData = []

	def setCurTemp(self, temp):
		self.curTemp = temp

	def setDailyData(self, data):
		self.dailyData = data

	def loop(self):
		try:
			self.canvas.Clear()

			cur_time = time.time()

			# loop through display states
			if self.STATE == CLOCK:
				self.displayClock(0)
				self.displayTrainTimes(True, 0)
				if cur_time - self.stateTime >= TIME_CLOCK:
					self.incrementState()
			elif self.STATE == CLOCK_CALENDAR_T:
				for i in range(34):
					self.canvas.Clear()
					self.displayClock(-i)
					self.displayCal(32-i)
					self.displayTrainTimes(True, 0)
					time.sleep(.1)
					self.canvas = self.matrix.SwapOnVSync(self.canvas)
				self.incrementState()
			elif self.STATE == CALENDAR:
				self.displayCal(0)
				self.displayTrainTimes(True, 0)
				if cur_time - self.stateTime >= TIME_CALENDAR:
					self.incrementState()
			elif self.STATE == CALENDAR_WEATHER_T:
				for i in range(34):
					self.canvas.Clear()
					self.displayCal(-i)
					self.displayClock(32-i)
					if i >= 8:
						self.displayTrainTimes(True, -8)
						self.displayCurrentTemp(0)
					else:
						self.displayTrainTimes(True, -i)
						self.displayCurrentTemp(8-i)
						
					time.sleep(.1)
					self.canvas = self.matrix.SwapOnVSync(self.canvas)
				self.incrementState()
			elif self.STATE == CURRENT_TEMP:
				self.displayClock(0)
				self.displayTrainTimes(True, -8)
				self.displayCurrentTemp(0)
				if cur_time - self.stateTime >= TIME_TEMP:
					self.incrementState()
			elif self.STATE == TEMP_RAIN_T:
				for i in range(10):
					self.canvas.Clear()
					self.displayCurrentTemp(i)
					self.displayCurrentRain(-8+i)
					self.displayClock(0)
					self.displayTrainTimes(False, -8+i)
					time.sleep(.1)
					self.canvas = self.matrix.SwapOnVSync(self.canvas)
				self.incrementState()
			elif self.STATE == CURRENT_RAIN:
				self.displayCurrentRain(0)
				self.displayClock(0)
				self.displayTrainTimes(False, 0)
				if cur_time - self.stateTime >= TIME_RAIN:
					self.incrementState()
				
			else:
				self.STATE = CLOCK
				print("ERR found default!")

			self.tick()

			self.canvas = self.matrix.SwapOnVSync(self.canvas)

		except Exception as e:
			print("Display has failed!")
			print(e)

	def incrementState(self):
		self.stateTime = time.time()
		self.STATE += 1
		if self.STATE >= STATE_MAX:
			self.STATE = 0


	def displayCurrentTemp(self, y_offset):
		if self.curTemp <= 0:
			# make everything this cold full blue / handle negatives 
			tempcolor = graphics.Color(0, 0, 255)
		elif self.curTemp > 100:
			# make everything this hot full red / handle > 100 
			tempcolor = graphics.Color(255, 0, 0)
		else:
			tempcolor = graphics.Color(255 * (self.curTemp/100), 255 - 255 * (self.curTemp/200), 255 - 255 * (self.curTemp/100))

		graphics.DrawText(self.canvas, self.bigfont, 22, 30 + y_offset, 
						  tempcolor, "Temp") 
		graphics.DrawText(self.canvas, self.bigfont, 45, 30 + y_offset, 
						  tempcolor, f"{self.curTemp:.0f}")
		# TODO make a degree symbol 

	def displayCurrentRain(self, y_offset):
		if self.dailyData["precipitation_probability_max"][0]:
			rain_prob = self.dailyData["precipitation_probability_max"][0]
			# make everything this low full white
			if rain_prob <= 5:
				raincolor = CLK1
			else:
				raincolor = graphics.Color(255 - 255 * (rain_prob/100), 255 - 255 * (rain_prob/100), 255)

			graphics.DrawText(self.canvas, self.bigfont, 24, 8 + y_offset, 
							raincolor, "Rain") 
			graphics.DrawText(self.canvas, self.bigfont, 45, 8 + y_offset, 
							raincolor, f"{rain_prob:.0f}%")

	def theLisDown(self, y_offset):
		graphics.DrawText(self.canvas, self.bigfont, 30, 12 + y_offset, 
						  PURP, "The L ")
		graphics.DrawText(self.canvas, self.bigfont, 35, 20 + y_offset, 
						  PURP, "is")
		graphics.DrawText(self.canvas, self.bigfont, 30, 28 + y_offset, 
						  RED, "DOWN!")

	def displayCal(self, y_offset):
		month, day, dow = get_month_day_dow()
		graphics.DrawText(self.canvas, self.monthfont, 2, 10 + y_offset, 
						  self.hcolor, dow)
		graphics.DrawText(self.canvas, self.monthfont, 2, 20 + y_offset, 
						  self.hcolor, month)
		graphics.DrawText(self.canvas, self.monthfont, 9, 30 + y_offset, 
						  self.hcolor, day)

	def displayClock(self, y_offset):
		hour = get_hour()
		minutes = get_minutes()

		graphics.DrawText(self.canvas, self.timefont, 3, 14 + y_offset, 
						  self.hcolor, hour)
		graphics.DrawText(self.canvas, self.timefont, 3, 27 + y_offset, 
						  self.mcolor, minutes)

	def tick(self):
		self.hcolor = CLK1
		self.mcolor = CLK1

		if self.showTick: 
			graphics.DrawText(self.canvas, self.bigfont, -2, 32, 
						  PURP, ".")
		self.showTick = not self.showTick

	def setNTimes(self, N_times):
		self.N_times = N_times

	def setSTimes(self, S_times):
		self.S_times = S_times

	def displayTrainTimes(self, showLabel, y_offset):
		if len(self.N_times) == 0 and len(self.S_times) == 0: 
			self.theLisDown(y_offset)
			return

		# generate northbound col
		if showLabel: 
			graphics.DrawText(self.canvas, self.bigfont, 24, 8 + y_offset, BLUE, "Man")
		if len(self.N_times) == 0:
			graphics.DrawText(self.canvas, self.smallfont, 24, 16 + y_offset, 
							  BLUE, "DOWN!")
		else:
			self.printTimeCol(self.N_times, 1, y_offset)

		# generate southbound col
		if showLabel: 
			graphics.DrawText(self.canvas, self.bigfont, 45, 8 + y_offset, YELLOW, "Bkn")
		if len(self.S_times) == 0:
			graphics.DrawText(self.canvas, self.smallfont, 45, 16 + y_offset, 
							  YELLOW, "DOWN!")
		else:
			self.printTimeCol(self.S_times, 2, y_offset)

	def printLines(self): 
			graphics.DrawLine(self.canvas, 21, 4, 21, 28, WHITE)
			graphics.DrawLine(self.canvas, 43, 4, 43, 28, WHITE)

	def printTimeCol(self, times, col, y_offset):
		if col == 1:
			color = BLUE
		elif col == 2:
			color = YELLOW
		else:
			color = RED

		printcol = col * 24
		if col == 2: 
			printcol -= 3

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
							  printcol, printrow + y_offset, 
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
