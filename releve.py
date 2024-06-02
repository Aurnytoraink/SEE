import spidev
import time
import matplotlib.pyplot as plt
import pandas as pd
from time import sleep

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


def acquerir(temps_acquisition):
    nb_sample = int(temps_acquisition * 1e4)
    i = 0
    times, amp = [], []

    # Acquisition des n sample
    for i in range(nb_sample):
        value = read_ADC(0)
        value = convert_values(value)
        
        times.append(i*1e-4) #100 ksps
        amp.append(value)
        
        i+=1
        
        sleep(1e-4)
    
    return times, amp

# Afficher dans un graph
times, amp = acquerir(0.010)

plt.plot(times,amp)
plt.xlabel("Temps (s)")
plt.ylabel("Amplitude (V)")
plt.show()