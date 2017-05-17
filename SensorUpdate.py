from nanpy import ArduinoApi

class SensorUpdate():

    def __init__(self, sensorpin):
        self.sensorpin = sensorpin

    def sensupdate(self, sensorObject):
        self.sensorvalue = sensorObject.analogRead(self.sensorpin)
        return self.sensorvalue