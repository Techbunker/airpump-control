# -- Imports --
import ArduinoConnection
import SensorUpdate
import MotorControl

import time

import kivy
kivy.require('1.9.1')
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

# -- Define Variables
buzzerpin = 3
sensorpin = "A0"
motorpin = 2

sensorthresh = 28
shishathresh = 35

runtime = 120
shisharuntime = 180
motorstarttimestamp = 0
motorstoptimestamp = 0
motorrunning = False

arduinoconnection = None
sensor = None
motor = None
arduino = None

class SteuerungApp(App):
    def update(self, modeAuto, modeShisha):
    	global sensorthresh
    	global shishathresh
    	global runtime
    	global shisharuntime
    	global motorstarttimestamp
    	global motorstoptimestamp
    	global motorrunning

    	global sensor
    	global motor
    	global arduino


        sensorvalue = sensor.sensupdate()
        actualtime = time.time()

        try:
	        if modeAuto:
	        	if motorrunning and motorstoptimestamp <= actualtime:
	        		print "Stop Motor!"
	        		motor.stopMotor()

	        	if modeShisha == False and sensorvalue > sensorthresh and motorrunning == False:
	        		print "Activating!"
	        		motorrunning = True
	        		motorstarttimestamp = time.time()
	        		motorstoptimestamp = motorstarttimestamp+runtime
	        		motor.startMotor()
	        		print "GOTO: Normal Loop"
	        	elif modeShisha and sensorvalue > shishathresh and motorrunning == False:
	        		print "Activating (ShishaMode)!"
	        		motorrunning = True
	        		motorstarttimestamp = time.time()
	        		motorstoptimestamp = motorstarttimestamp+shisharuntime
	        		motor.startMotor()
	        		print "GOTO: Normal Loop"
	        	elif motorrunning:
	        		print "Motor is already running."
	        	else:
	        		print "Not activated."

	        print "Smoke Sensor: "+str(sensorvalue)
	    except:
	    	print "Error in update()! Making new connection..."
	    	arduino = arduinoconnection.connect()
	    	print "New connection established."


    def press_callback(self, obj):
    	global motor
    	global arduino

        try:
            if obj.text == 'Shisha Modus An/Aus' and self.modeAuto == True:
			if obj.state == "down":
				print ("button on")
				self.modeShisha = True
			else:
				print ("button off")
				self.modeShisha = False
		elif obj.text == 'Shisha Modus An/Aus' and self.modeAuto == False:
			obj.state = "normal"

		if obj.text == 'Manueller Modus An/Aus':
			if obj.state == "down" and self.threadRunning == False:
				print ("button on")
				self.modeAuto = False
				self.modeShisha = False
			else:
				print ("button off")
				self.modeAuto = True

		if obj.text == 'Motor An/Aus' and self.modeAuto == False:
			if obj.state == "down":
				print ("button on")
				motor.startMotor()
			else:
				print ("button off")
				motor.stopMotor()
		elif obj.text == 'Motor An/Aus' and self.modeAuto == True:
			obj.state="normal"
	except:
		print "Error in press_callback()! Making new connection..."
		try:
			arduino = arduinoconnection.connect()
			print "New connection established"
			press_callback(obj)
		except:
			print "Could not establish new connetion!"

    # Set up the layout:
	def build(self):
		global sensorpin
		global motorpin
		
		global arduinoconnection
		global sensor
		global motor
		global arduino

		# Instatiate the various Objects needed in the Application.
		arduinoconnection = ArduinoConnection()
		sensor = SensorUpdate(sensorpin)
		motor = MotorControl(motorpin)

		# Connect to Arduino
		arduino = arduinoconnection.connect()

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
        Clock.schedule_interval(self.update(self.modeAuto, self.modeShisha), 1.0/10.0)

        return layout





if __name__ == '__main__':
    SteuerungApp().run()