import spidev
import RPi.GPIO as GPIO

class ADC():
    def __init__(self, channel):
        self.channel = channel
        self.bus=0
        self.device=0

        self.liaison = spidev.SpiDev(self.bus, self.device)
        self.liaison.max_speed_hz = 2000000 # en Hertz
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(18, GPIO.OUT)

        GPIO.output(18, GPIO.LOW)
    
    def read_ADC(self):
        to_send = [4 | 2 | (self.channel>>2), (self.channel &3)<<6,0]
        data = self.liaison.xfer2(to_send)
        return (data[1]<<8) | data[2]

    def convert_values(self):
        return self.read_ADC()*5/4095
    
    def set_LED(self,state):
        if state:
            GPIO.output(18, GPIO.HIGH)
        else:
            GPIO.output(18, GPIO.LOW)
