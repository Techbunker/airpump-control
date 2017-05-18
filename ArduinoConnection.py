from nanpy import (ArduinoApi, SerialManager)

class ArduinoConnection():
    def __init__(self):
        #self.connect()
        pass

    def connect(self):
        try:
            connection = SerialManager()
            a = ArduinoApi(connection = connection)
            print "Connection established!"
            print a
            return a
        except:
            print "Connection Error!"
            self.connect()
