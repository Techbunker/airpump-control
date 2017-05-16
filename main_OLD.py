# -- Imports --
import threading

import kivy
kivy.require('1.9.1')
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

from nanpy import (ArduinoApi, SerialManager)
from time import sleep

# -- Define Variables --
global a
global sensorvalue

threadRunning = False

buzzer = 3
smoke = "A0"
relais = 2
sensorthresh = 28
shishathresh = 35
sensorvalue = 0

modeAuto = True
modeShisha = False

sensorclock = 0.2

def establish_connection():
	global a
	# Establish connection to Arduino
	try:
	    connection = SerialManager()
	    a = ArduinoApi(connection = connection)
	    print "Connection established!"
	except:
	    print "Connection Error!"

	# Setup Pinmodes
	try:
		a.pinMode(relais, a.OUTPUT)
		a.pinMode(smoke, a.INPUT)
		print "PinModes set!"
	except:
		print "Could not set PinModes!"
	return True

establish_connection()

class sensorupdateThread(threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		global sensorvalue
		global a
		global modeShisha
		global modeAuto
		global sensorthresh
		global shishathresh
		global threadRunning

		threadRunning = True
		try:
			if modeAuto:
				if modeShisha==False and sensorvalue > sensorthresh:
					print "Activating!"
					a.digitalWrite(relais, a.HIGH)
					sleep(120)
					a.digitalWrite(relais, a.LOW)
					print "GOTO: Normal Loop"
				elif modeShisha and sensorvalue > shishathresh:
					print "Activating!"
					a.digitalWrite(relais, a.HIGH)
					sleep(180)
					a.digitalWrite(relais, a.LOW)
				else:
					a.digitalWrite(relais, a.LOW)
			sensorvalue = a.analogRead(smoke)
			print "Smoke Sensor: "+str(sensorvalue)
			#sensorvalue = 450
		except:
			print "Error in sensorupdate()! Making new connection..."
			establish_connection()
			#threadRunning = False
			#sensorupdate(asdf)

		threadRunning = False

def press_callback(obj):
	global a
	global modeShisha
	global modeAuto
	global btnShisha
	global btnStart
	global threadRunning

	try:
		if obj.text == 'Shisha Modus An/Aus' and modeAuto == True:
			if obj.state == "down":
				print ("button on")
				modeShisha = True
			else:
				print ("button off")
				modeShisha = False
		elif obj.text == 'Shisha Modus An/Aus' and modeAuto == False:
			obj.state = "normal"

		if obj.text == 'Manueller Modus An/Aus':
			if obj.state == "down" and threadRunning == False:
				print ("button on")
				modeAuto = False
				modeShisha = False
			else:
				print ("button off")
				modeAuto = True

		if obj.text == 'Motor An/Aus' and modeAuto == False:
			if obj.state == "down":
				print ("button on")
				a.digitalWrite(relais, a.HIGH)
			else:
				print ("button off")
				a.digitalWrite(relais, a.LOW)
		elif obj.text == 'Motor An/Aus' and modeAuto == True:
			obj.state="normal"
	except:
		print "Error in press_callback()! Making new connection..."
		try:
			establish_connection()
			print "New connection established"
			press_callback(obj)
		except:
			print "Could not establish new connetion!"



class SteuerungApp(App):

	def sensorupdate(self, asdf):
		global threadRunning

		if threadRunning == False:
			thread1 = sensorupdateThread(1, "Thread-1", 1)
			thread1.start()


	# Set up the layout:
	def build(self):
		layout = GridLayout(cols=3, spacing=30, padding=30, row_default_height=150)


		# Make the background gray:
		with layout.canvas.before:
				Color(.2,.2,.2,1)
				self.rect = Rectangle(size=(800,600), pos=layout.pos)


		# Instantiate the various Widgets
		labelTemp=Label(text="[size=30]Temperatur: "+"--"+"C[/size]", markup=True)
		labelHum=Label(text="[size=30]Luftfeuchtigkeit: "+"--"+"%[/size]", markup=True)
		labelQual=Label(text="[size=30]Luftqualitaet: "+"--"+"[/size]", markup=True)
		btnShisha=ToggleButton(text="Shisha Modus An/Aus")
		btnShisha.bind(on_press=press_callback)
		btnMan=ToggleButton(text="Manueller Modus An/Aus")
		btnMan.bind(on_press=press_callback)
		btnStart=ToggleButton(text="Motor An/Aus")
		btnStart.bind(on_press=press_callback)

		# Add the Widgets to the Layout
		layout.add_widget(labelTemp)
		layout.add_widget(labelHum)
		layout.add_widget(labelQual)
		layout.add_widget(btnShisha)
		layout.add_widget(btnMan)
		layout.add_widget(btnStart)

		# Schedule update of Sensordata
		Clock.schedule_interval(self.sensorupdate, 1.0/10.0)

		return layout




if __name__ == '__main__':
	SteuerungApp().run()