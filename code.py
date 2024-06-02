import spidev
import time
#from matplotlib.pyplot import plot
import os

bus=0
device=0

channels = [0,1,2,3]

liaison = spidev.SpiDev(bus, device)
liaison.max_speed_hz = 2000000 # en Hertz

def read_ADC(channel):
    to_send = [4 | 2 | (channel>>2), (channel &3)<<6,0] # voir documentation

    data = liaison.xfer2(to_send)
    return (data[1]<<8) | data[2]


i = 0
f = os.open("result.csv",os.O_RDWR)
while True:
    value = read_ADC(0)
    
    print(value)
    
    os.write(f,f"{i},{value}\r\n".encode())
    i+=1