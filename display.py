#!/usr/bin/env python
import time
import sys
import os

from helper import from_minutes, get_hour, get_minutes, get_month_day_dow

sys.path.append(os.path.abspath(os.path.dirname(__file__)
							   + '/../rpi-rgb-led-matrix/bindings/python/'))
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions

CLOCK = 0
MOVE_UP = 1
SHOW_CAL = 2
SHOW_ALERTS = 3
MOVE_DOWN = 4
STATE_MAX = 5

TIME_CLOCK =  15
TIME_CALENDAR = 5
TIME_TEMP = 15
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
		self.perfont = graphics.Font()
		self.perfont.LoadFont("../rpi-rgb-led-matrix/fonts/6x10.bdf")

		self.N_times = []
		self.S_times = []

		self.hcolor = CLK1
		self.mcolor = CLK2

		self.STATE = CLOCK
		#self.STATE = SHOW_ALERTS
		self.stateTime = time.time()

		self.showTick = True
		self.showTemp = True
		self.lastWeatherTime = time.time()

		self.y_pos = 0
		self.x_pos = 0

		self.curTemp = 0.
		self.dailyData = []

		self.alert = {}
		self.alertString = ""
		self.delays = []

	def setCurTemp(self, temp):
		self.curTemp = temp

	def setDailyData(self, data):
		self.dailyData = data

	def setState(self, new_state):
		self.STATE = new_state
		self.stateTime = time.time()

	def setAlerts(self, alerts):
		if len(alerts):
			self.alert = alerts[0]
			# try to just get something useful
			try: 
				start_time = alerts[0]["periods"][0]["start_time"]
				start_date = alerts[0]["periods"][0]["start_date"]
				end_time = alerts[0]["periods"][0]["end_time"]
				end_date = alerts[0]["periods"][0]["end_date"]
				header = alerts[0]["header"]
				self.alertString = f"{start_date} {start_time} -> {end_date} {end_time} : {header}"
			except KeyError as e:
				print(f"Error: The key {e} was not found in the dictionary.")
				self.alertString = ""
		
		# anticipate a range of dates and show in a useful way 
		try:
			# if multiple, find the most recent 
			if len(alerts) > 1:
				min_start = alerts[0]["periods"][0]["start_full"]
				for alert in alerts:
					if int(alert["periods"][0]["start_full"]) < int(min_start):
						min_start = alert["periods"][0]["start_full"]
						self.alert = alert

			print(self.alert)
			alert_string = ""
			count = 1
			for period in self.alert["periods"]:
				if count == 1: 
					day_1_start = period["start_date"]
					day_1_end = period["end_date"]
				elif count == len(self.alert["periods"]): 
					day_end = period["end_date"]
				
				count += 1
				# expecting start/end times + header to be identical 
				start_time = period["start_time"]
				end_time = period["end_time"]
				header = self.alert["header"]

			alert_string = f"Outage: {day_1_start} {start_time} -> {day_1_end} {end_time} each day until {day_end}"
			print(alert_string)
			self.alertString = alert_string
		except KeyError as e:
			print(f"Error: The key {e} was not found in the dictionary.")
			self.alertString = ""

	def setDelays(self, delays):
		self.delays = delays

	async def loop(self, x_offset, y_offset):
		try:
			self.canvas.Clear()

			cur_time = time.time()

			# loop through display states
			if self.STATE == CLOCK:
				if cur_time - self.stateTime >= TIME_CLOCK:
					self.incrementState()
			elif self.STATE == MOVE_UP:
				self.x_pos = 0
				if self.y_pos <= -9: 
					self.incrementState()
				else:
					self.y_pos -= 1
			elif self.STATE == SHOW_CAL:
				self.y_pos = -9
				if cur_time - self.stateTime >= TIME_CALENDAR: 
					self.incrementState()
			elif self.STATE == SHOW_ALERTS:
				self.y_pos = -9
				alert_pixel_len = len(self.alertString) * 5 + 64
				if self.x_pos <= -alert_pixel_len: 
					self.incrementState()
				else:
					self.x_pos -= 1
			elif self.STATE == MOVE_DOWN: 
				if self.y_pos >= 0: 
					self.x_pos = 0
					self.incrementState()
				else:
					self.y_pos += 1
				
			else:
				self.STATE = CLOCK
				print("ERR found default!")

			# KK 
			#self.displayClock(1, 10)
			self.displayHour(1,10)
			self.displayMinute(1, 11 + self.y_pos)

			self.displayTrainTimes(True, 3, -1 + self.y_pos)
			#self.theLisDown(x_offset, y_offset)

			if self.showTemp: 
				self.displayCurrentTemp(2, 28 + self.y_pos)
				if cur_time - self.lastWeatherTime >= TIME_TEMP:
					self.showTemp = False
					self.lastWeatherTime = cur_time
			else:
				self.displayCurrentRain(2, 31 + self.y_pos)
				if cur_time - self.lastWeatherTime >= TIME_RAIN:
					self.showTemp = True
					self.lastWeatherTime = cur_time

			self.displayCal(2 + self.x_pos, 41 + self.y_pos)
			self.displayAlert(64 + self.x_pos, 40 + self.y_pos)

			#self.tick()

			self.canvas = self.matrix.SwapOnVSync(self.canvas)

		except Exception as e:
			print("Display has failed!")
			print(e)

	def incrementState(self):
		self.stateTime = time.time()
		self.STATE += 1
		if self.STATE >= STATE_MAX:
			self.STATE = 0


	def displayCurrentTemp(self, x_offset, y_offset):
		if self.curTemp <= 0:
			# make everything this cold full blue / handle negatives 
			tempcolor = graphics.Color(0, 0, 255)
		elif self.curTemp > 100:
			# make everything this hot full red / handle > 100 
			tempcolor = graphics.Color(255, 0, 0)
		else:
			tempcolor = graphics.Color(255 * (self.curTemp/100), 255 - 255 * (self.curTemp/200), 255 - 255 * (self.curTemp/100))

		graphics.DrawText(self.canvas, self.monthfont, x_offset, 3 + y_offset, 
						  tempcolor, f"{self.curTemp:.0f}")
		# make a degree symbol 
		x_pos = 2 + len(f"{self.curTemp:.0f}") * 6
		graphics.DrawText(self.canvas, self.smallfont, x_pos + x_offset, -4 + y_offset, 
						tempcolor, "o")

	def displayCurrentRain(self, x_offset, y_offset):
		if self.dailyData["precipitation_probability_max"][0] or self.dailyData["precipitation_probability_max"][0] == 0:
			rain_prob = self.dailyData["precipitation_probability_max"][0]
			# make everything this low full white
			if rain_prob <= 5:
				raincolor = CLK1
			else:
				raincolor = graphics.Color(255 - 255 * (rain_prob/100), 255 - 255 * (rain_prob/100), 255)

			graphics.DrawText(self.canvas, self.monthfont, x_offset, y_offset, 
							raincolor, f"{rain_prob:.0f}%")
			#x_pos = 2 + len(f"{rain_prob:.0f}") * 5
			#graphics.DrawText(self.canvas, self.perfont, x_pos + x_offset, y_offset, 
			#				raincolor, "%")

	def theLisDown(self, x_offset, y_offset):
		graphics.DrawText(self.canvas, self.bigfont, 32 + x_offset, 10 + y_offset, 
						  PURP, "The")
		graphics.DrawText(self.canvas, self.bigfont, 32 + x_offset, 18 + y_offset, 
						  PURP, "L is")
		graphics.DrawText(self.canvas, self.bigfont, 30 + x_offset, 26 + y_offset, 
						  RED, "DOWN!")

 # KK
	def displayAlert(self, x_offset, y_offset):
		graphics.DrawText(self.canvas, self.bigfont, x_offset, y_offset, 
						  PURP, self.alertString)
	def displayCal(self, x_offset, y_offset):
		month, day, dow = get_month_day_dow()
		graphics.DrawText(self.canvas, self.monthfont, x_offset, y_offset, 
						  self.mcolor, f"{month} {day}")
		#graphics.DrawText(self.canvas, self.monthfont, 2, 20 + y_offset, 
						  #self.hcolor, month)
		#graphics.DrawText(self.canvas, self.monthfont, 9, 30 + y_offset, 
						  #self.hcolor, day)

	def displayHour(self, x_offset, y_offset):
		hour = get_hour()
		graphics.DrawText(self.canvas, self.monthfont, x_offset, y_offset, 
						  self.hcolor, f"{hour}")
	def displayMinute(self, x_offset, y_offset):
		minutes = get_minutes()
		graphics.DrawText(self.canvas, self.monthfont, 14 + x_offset, 8 + y_offset, 
						  self.hcolor, f"{minutes}")
	def displayClock(self, x_offset, y_offset):
		hour = get_hour()
		minutes = get_minutes()

		graphics.DrawText(self.canvas, self.monthfont, x_offset, y_offset, 
						  self.hcolor, f"{hour}")
		graphics.DrawText(self.canvas, self.monthfont, 14 + x_offset, 8 + y_offset, 
						  self.hcolor, f"{minutes}")

		#graphics.DrawText(self.canvas, self.bigfont, x_offset + 16, y_offset - 4, 
		#				  self.hcolor, f"{minutes}")
		#graphics.DrawText(self.canvas, self.bigfont, x_offset + 13, y_offset - 2, 
		#				  self.hcolor, f":")
		#graphics.DrawText(self.canvas, self.timefont, 3, 27 + y_offset, 
		#				  self.mcolor, minutes)

	def displayDeg(self, x_offset, y_offset):
		graphics.DrawText(self.canvas, self.bigfont, x_offset, y_offset, 
						PURP, ".")
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

	def displayTrainTimes(self, showLabel, x_offset, y_offset):
		if len(self.N_times) == 0 and len(self.S_times) == 0: 
			self.theLisDown(x_offset, y_offset)
			return

		# generate northbound col
		if showLabel: 
			graphics.DrawText(self.canvas, self.bigfont, 27 + x_offset, 8 + y_offset, BLUE, "Man")
		if len(self.N_times) == 0:
			graphics.DrawText(self.canvas, self.smallfont, 27 + x_offset, 16 + y_offset, 
							  RED, "DOWN!")
		else:
			self.printTimeCol(self.N_times, 1, 3 + x_offset, y_offset)

		# generate southbound col
		if showLabel: 
			graphics.DrawText(self.canvas, self.bigfont, 45 + x_offset, 8 + y_offset, YELLOW, "Bkn")
		if len(self.S_times) == 0:
			graphics.DrawText(self.canvas, self.smallfont, 45 + x_offset, 16 + y_offset, 
							  RED, "DOWN!")
		else:
			self.printTimeCol(self.S_times, 2, x_offset, y_offset)

	def printLines(self): 
			graphics.DrawLine(self.canvas, 21, 4, 21, 28, WHITE)
			graphics.DrawLine(self.canvas, 43, 4, 43, 28, WHITE)

	# KK

	def displayTimeCol(self, times, col, x_offset, y_offset):
		if col == 1:
			color = BLUE
		elif col == 2:
			color = YELLOW
		else:
			color = RED

		printrow = y_offset
		printcol = x_offset
		nstring = ''
		firstTime = True
		count = 1
		for t in times: 
			if count == 3: 
				printrow = y_offset
				printcol = x_offset + 20
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
				# KK DEBUG REMOVE
				nstring = f"{nextmin}:{nextsec:02d}"
			else: 
				nstring = f"{nextmin}"

			graphics.DrawText(self.canvas, self.smallfont, 
							  printcol, printrow, 
							  color, nstring )
			count += 1 
		
	def printTimeCol(self, times, col, x_offset, y_offset):
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
							  printcol + x_offset, printrow + y_offset, 
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
