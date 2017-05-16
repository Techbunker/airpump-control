from nanpy import (ArduinoApi, SerialManager)

class ArduinoConnection():
    def __init__(self):
        #self.connect()
        pass

    def connect(self):
        try:
            self.connection = SerialManager()
            self.a = ArduinoApi(self.connection = self.connection)
            print "Connection established!"
        except:
	        print "Connection Error!"
        return self.a