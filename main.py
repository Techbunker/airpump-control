# Import Libraries
from nanpy import (ArduinoApi, SerialManager)
from time import sleep

# Define Variables
buzzer = 3
smoke = "A0"
relais = 2

sensorthresh = 220
sensorvalue = 0

# Establish connection to Arduino
try:
    connection = SerialManager()
    a = ArduinoApi(connection = connection)
    print "Connection established!"
except:
    print "Connection Error!"

# Setup Pinmodes
a.pinMode(relais, a.OUTPUT)
a.pinMode(smoke, a.INPUT)

while True:
	sensorvalue = a.analogRead(smoke)
	print sensorvalue

	if sensorvalue > sensorthresh:
		print "Activating!"
		a.digitalWrite(relais, a.HIGH)
		sleep(120)
		print "GOTO: Normal Loop"
	else:
		a.digitalWrite(relais, a.LOW)