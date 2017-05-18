from nanpy import ArduinoApi

class MotorControl():
    def __init__(self, motorpin):
        self.motorpin = motorpin

    def startMotor(self, motorObject, motorpin):
        motorObject.digitalWrite(motorpin, motorObject.HIGH)

    def stopMotor(self, motorObject):
        motorObject.digitalWrite(motorpin, motorObject.LOW)