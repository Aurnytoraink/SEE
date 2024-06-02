import spidev
import time
import matplotlib.pyplot as plt
from time import time, sleep
import pandas as pd
import RPi.GPIO as GPIO
import numpy as np
from scipy.signal import find_peaks
import os

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(18, GPIO.OUT)

GPIO.output(18, GPIO.LOW)

bus=0
device=0

channels = [0,1,2,3]

liaison = spidev.SpiDev(bus, device)
liaison.max_speed_hz = 2000000 # en Hertz

t_acquisition = 1/10


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
    
        sleep(t_acquisition)
    
    return times, amp


def autocorr(x):
    result = np.correlate(x,x,mode='full')
    return result[result.size // 2:] #On prend la moitié

def get_pulse_frequency(times,peaks):
    pulse = times[peaks][1:len(peaks)] - times[peaks][0:len(peaks)-1]
    return 60/np.average(pulse)
    

def oxygene(channel, temps_acquisition):
    t_conv_start = time()
    times = np.array([])
    RED = np.array([])
    IR = np.array([])

    # Acquisition des n sample
    while time() - t_conv_start < temps_acquisition:
        GPIO.output(18, GPIO.LOW)
            
        IR = np.append(IR,read_ADC(channel))
        
        sleep(t_acquisition/2)
        GPIO.output(18, GPIO.HIGH)
        
        RED = np.append(RED,read_ADC(channel))
        
        t_conv_end = time()

        times = np.append(times,(t_conv_end - t_conv_start)) #100 ksps
        
        sleep(t_acquisition/2)
        
    #ratio = (RED/np.average(RED))/(IR/np.average(IR))
    
    #return times, 110-25*ratio
    return times, IR, RED

times, IR, RED = oxygene(0,5)
amp = (RED/np.average(RED))/(IR/np.average(IR))
amp = np.asarray(amp)*100
print(np.average(amp),"%")
# plt.plot(times,amp)
# plt.title("Oxymétrie")
# plt.show()


# Lancer acquisition
times, amp = acquerir(0,5)

# Afficher dans un graph
plt.subplot(211)
plt.plot(times,amp)
plt.xlabel("Temps (s)")
plt.ylabel("Amplitude (V)")

# Autocorrelation
auto = amp - np.average(amp)
auto = autocorr(auto)

peaks, _ = find_peaks(auto,height=0.2,distance=1)

times = np.asarray(times)


print(round(get_pulse_frequency(times,peaks),2),'bpm')

plt.subplot(212)
plt.plot(times,auto)
plt.plot(times[peaks], auto[peaks], "x")
plt.title("BPM")
plt.show()