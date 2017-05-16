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
sensorthresh = 160
shishathresh = 200
sensorvalue = 0
runtime = 10 #Seconds
shisharuntime = 20 # Seconds

airqual = "Gut"
airqualcolor = "008000" # Set color to GREEN

modeAuto = True
modeShisha = False

sensorclock = 0.2

def qual_interpret(value):
	global airqual
	global airqualcolor
	#global labelQual

	print "Interpreting Sensorvalue..."
	print "Value: "+str(value)
	if value < 50:
		airqual = "Gut"
		airqualcolor = "008000" # Set color to GREEN

	elif value > 50 and value < 60:
		airqual = "Mittel"
		airqualcolor = "FFFF00" # Set color to YELLOW

	elif value > 60:
		airqual = "Schlecht"
		airqualcolor = "FF0000" # Set color to RED
	print "Sensorvalue interpreted!"
	print "AirQualColor is now: "+airqualcolor

	#print "Updating Texture..."
	#labelQual.texture_update()
	#print "Texture updated!"


# Method to establish a connection to slave the Arduino
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

# Class to set up a Thread which updates the Sensorvalues
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
			qual_interpret(sensorvalue)
			if modeAuto:
				if modeShisha==False and sensorvalue > sensorthresh:
					print "Activating!"
					a.digitalWrite(relais, a.HIGH)
					sleep(runtime) # Time in seconds for the Motor to run
					a.digitalWrite(relais, a.LOW)
					print "GOTO: Normal Loop"
				elif modeShisha and sensorvalue > shishathresh:
					print "Activating!"
					a.digitalWrite(relais, a.HIGH)
					sleep(shisharuntime) # Time in seconds for the Motor to run
					a.digitalWrite(relais, a.LOW)
				else:
					a.digitalWrite(relais, a.LOW)
			sensorvalue = a.analogRead(smoke)
			#sensorvalue = 450 # Fake Sensorvalue for Debugging
		except:
			print "Error in sensorupdate()! Making new connection..."
			establish_connection()
			#threadRunning = False
			#sensorupdate(asdf)

		threadRunning = False

# Method which is called when a Button is pressed.
def press_callback(obj):
	global a
	global modeShisha
	global modeAuto
	global btnShisha
	global btnStart
	global threadRunning
	global airqualcolor

	try:
		# Shisha Mode Button
		if obj.text == 'Shisha Modus An/Aus' and modeAuto == True:
			if obj.state == "down":
				print ("button on")
				modeShisha = True
			else:
				print ("button off")
				modeShisha = False
		elif obj.text == 'Shisha Modus An/Aus' and modeAuto == False:
			obj.state = "normal"

		# Manual Mode Button
		if obj.text == 'Manueller Modus An/Aus':
			if obj.state == "down" and threadRunning == False:
				print ("button on")
				modeAuto = False
				modeShisha = False
			else:
				print ("button off")
				modeAuto = True

		# Motor Start Button
		if obj.text == 'Motor An/Aus' and modeAuto == False:
			if obj.state == "down":
				print ("button on")
				a.digitalWrite(relais, a.HIGH)
			else:
				print ("button off")
				a.digitalWrite(relais, a.LOW)
		elif obj.text == 'Motor An/Aus' and modeAuto == True:
			obj.state="normal"

	# If one of the Button tasks fails, a new connection is going
	# to get established
	except:
		print "Error in press_callback()! Making new connection..."
		try:
			establish_connection()
			print "New connection established"
			press_callback(obj)
		except:
			print "Could not establish new connetion!"



class SteuerungApp(App): # The Part of the name before "App" is the Window Name

	def sensorupdate(self, asdf):
		global threadRunning

		if threadRunning == False: # If already an Update Thread is running, the new Thread wont be started
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
		labelQual=Label(text="[size=30]Luftqualitaet: "+"[color="+airqualcolor+"]"+airqual+"[/color][/size]", markup=True)
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

		# Schedule update of labelQual
		Clock.schedule_interval(labelQual.texture_update, 1.0/10.0)

		return layout



# -- Start the App --
if __name__ == '__main__':
	SteuerungApp().run()