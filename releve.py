import spidev
import time
import matplotlib.pyplot as plt
import pandas as pd
from time import time
import pandas as pd
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(18, GPIO.OUT)

GPIO.output(18, GPIO.HIGH)

bus=0
device=0

channels = [0,1,2,3]

liaison = spidev.SpiDev(bus, device)
liaison.max_speed_hz = 2000000 # en Hertz


def read_ADC(channel):
    to_send = [4 | 2 | (channel>>2), (channel &3)<<6,0] # voir documentation

    data = liaison.xfer2(to_send)
    return (data[1]<<8) | data[2]

def convert_values(value):
    return value*5/4095


def acquerir(channel, temps_acquisition):
    times, amp = [], []
    t_conv_start = time()

    # Acquisition des n sample
    while time() - t_conv_start < temps_acquisition:
        value = read_ADC(channel)
        value = convert_values(value)
        t_conv_end = time()
        
        times.append(t_conv_end - t_conv_start) #100 ksps
        amp.append(value)
    
        #sleep(1e-4)
    
    return times, amp


# Afficher dans un graph
times, amp = acquerir(0,5)

plt.plot(times,amp)
plt.xlabel("Temps (s)")
plt.ylabel("Amplitude (V)")
plt.show()
