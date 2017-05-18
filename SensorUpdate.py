from nanpy import ArduinoApi

class SensorUpdate():

    def __init__(self, sensorpin):
        self.sensorpin = sensorpin

    def sensupdate(self, sensorObject, sensorpin):
        self.sensorvalue = sensorObject.analogRead(sensorpin)
        return self.sensorvalue