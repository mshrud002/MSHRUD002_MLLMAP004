#!/usr/bin/python
#from numpy import interp
import RPi.GPIO as GPIO
#import Adafruit_MCP3008
import spidev
import time
import os
import sys


GPIO.setmode(GPIO.BCM)

#define switches
reset_button = 14
frequency_button = 15
stop_button = 23
display_button =24
default_button = 17

#Set the pins to pull_up and pull_down
GPIO.setup(reset_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(frequency_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(stop_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(display_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(default_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

spi_max_speed = 1000
spi = spidev.SpiDev()   # create spi object
spi.open(0,0)
#RPI has one bus(#0) and two devices (#0 & #1)

# function to read ADC data from a channel
def ReadChannel(channel):             #channel must be an integer 0-7
    adc = spi.xfer2([1,(8+channel)<<4,0]) #sending 3 bytes
    data = ((adc[1]&3) << 8) + adc[2]
    return data
#function to convert data to voltage level,
#places: number of decimal places needed

def ConvertVolts(data, decimal_places):
    volts = (data * 3.3)/float(1023)
    volts = round(volts,decimal_places)
    return volts

#function to converts temperature from temperature data
def ConvertTemp(data,decimal_places):
    temp = ((data*330)/float(1023))
    temp = round(temp,decimal_places)
    return temp
    
    
def read_sensors():
   if monitor == True:
      x = 1
      #Read the data from light sensor
      light_sensor = ReadChannel(LDR_channel)
      light_volts = ConvertVolts(light_sensor, 2)
      percent = int((light_volts/3.3)*100)

      #Read the data from temperature sensor
      temp_sensor = ReadChannel(temp_channel)
      temp_volts = ConvertVolts(temp_sensor, 2)
      temp       = ConvertTemp(temp_sensor,2)
      if temp == 0:
         temp ="00.00"
     
      #Read the data from potentiometer
      pot_turn = ReadChannel(Pot_channel)
      pot_volts = ConvertVolts(pot_turn, 2)
      
      while (i < 15):
         values[i] = pot_volts
         i = i + 1
         values[i]= temp
         i = i+1
         values[i]= percent
         i = i+ 1
   
      time.sleep(delay_freq)
      
def timer():
   milli +=0.5
   if milli == 99:
      milli =0
      sec +=1
      if sec == 59:
         sec = 0
         min +=1
         if min ==59:
            min = 0
            hr +=1
            if hr ==24:
               hr = 0 
  
def display_values():
    display = "%02d:%02d:%02d:%02d" %(hr,min,sec,milli)
    # print resutls
    TIME = time.strftime("%H:%M:%S")
    print TIME ,"      ", display , "      {}V".format(pot_volts),"         {}C".format(temp),"         {}%".format(percent)
    print"_____________________________________________________________________"
   
    time.sleep(delay)

#Define sensor channels
LDR_channel = 0
temp_channel = 1
Pot_channel = 2
#Define delay between readings
delay = 0.5
delay_freq = 0.5
x= 0
i = 0
k = 0
values = [0]*15
monitor = True
milli = 0
sec = 0
min = 0
hr = 0
display = ''


print"_____________________________________________________________________"
print"Time            Timer             Pot            Temp          Lighht"
print"_____________________________________________________________________"

def callback1(reset_button):
   milli = 0
   sec = 0
   min = 0
   hr = 0
   unused_variable = os.system("clear")
def callback2(frequency_button):
    if delay_freq == 0.5:
       delay_freq = 1
    else:
       delay_freq = 2
   
def callback3(stop_button):
   if x == 1:
      monitor = False
   else:
      read_sensors()
   
def callback4(display_button):
   
   timer()
   display = "%02d:%02d:%02d:%02d" %(hr,min,sec,milli)
   TIME = time.strftime("%H:%M:%S")
   
   while(k <= 12):
      print TIME ,"      ", display , "      {}V".format(values[k]),"         {}C".format(values[k+1]),"         {}%".format(values[k+2])
      print"_____________________________________________________________________"
      k = k+1

   time.sleep(delay)
   
def callback5(default_button):
   display_values()

#while True:

try:
   
   while True:
      timer()
      GPIO.add_event_detect(reset_button, GPIO.FALLING, callback=callback1,
      bouncetime=200)

      GPIO.add_event_detect(frequency_button, GPIO.FALLING, callback=callback2,
      bouncetime=200)

      GPIO.add_event_detect(stop_button, GPIO.FALLING, callback=callback3,
      bouncetime=200)

      GPIO.add_event_detect(display_button, GPIO.FALLING, callback=callback4,
      bouncetime=200)

      GPIO.add_event_detect(default_button, GPIO.FALLING, callback=callback5,
      bouncetime=200)
   
except keyboardInterrupt:
      
      GPIO.cleanup()

