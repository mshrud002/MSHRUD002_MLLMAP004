6#!/usr/bin/python

import RPi.GPIO as GPIO
import spidev
import time
import os
import sys
from collections import deque


GPIO.setmode(GPIO.BCM)

# defined switches
reset_button = 17
frequency_button = 22
stop_button = 23
display_button = 24

GPIO.setup(reset_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(frequency_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(stop_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(display_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#spi.max_speed_hz = 1000
spi = spidev.SpiDev()   # spi object
spi.open(0,0)
spi.max_speed_hz = 1000000
#RPI has one bus(#0) and two devices (#0 & #1)

# defined variables
LDR_channel = 2
temp_channel = 1
Pot_channel = 0
x = 0
count = 0
i = 0
k = 0
values = deque()
monitor = True
milli = 0
sec = 0
min = 0
hr = 0
display = ''
delay = 0.3
delay_freq = 0.5    # delay between readings


# function to read sensor data from a channel
def ReadChannel(channel):       # channel is an integer 0-7
    adc = spi.xfer2([1,(8+channel)<<4,0]) # sends 3 bytes
    data = ((adc[1]&3) << 8) + adc[2]
    return data

# function to convert sensor data to voltage level
def ConvertVolts(data, decimal_places):
    volts = (data * 3.3)/float(1023)
    volts = round(volts,decimal_places)
    return volts

#function to convert to temperature from sensor data
def ConvertTemp(volts, decimal_places):
    temp = ((volts*33000)/(1023))
    #temp = (0.01*25) + ConvertVolts(volts, decimal_places)  # formula from datasheet
    #temp_volt = (0.01*25) + 0.5  # sensor voltage
    #temp = (volts - 0.5)*0.01
    temp = round(temp,decimal_places)
    return temp

def read_sensors():
   global x
   global i
   global values
   if monitor == True:
      x = 1
      #Read the data from light sensor
      light_sensor = ReadChannel(LDR_channel)
      light_volts = ConvertVolts(light_sensor, 2)
      #percent = int((light_volts/3.3)*100)
      percent = round(((light_volts/3.3)*100), 0)

      #Read the data from temperature sensor
      temp_sensor = ReadChannel(temp_channel)
      temp_volts = ConvertVolts(temp_sensor, 2)
      temperature = ConvertTemp(temp_volts, 2)
      if temperature == 0:
         temperature ="0.00"

      #Read the data from potentiometer
      pot_turn = ReadChannel(Pot_channel)
      pot_volts = ConvertVolts(pot_turn, 2)

      

      time.sleep(delay_freq)

def timer():
   global milli
   global sec
   global min
   global hr
   global delay_freq 

   if delay_freq == 0.5:
         milli = milli + 5
   if milli >= 100:
      milli =0
      sec = sec + 1
      if sec >= 60:
         sec = 0
         min = min + 1
         if min >= 60:
            min = 0
            hr = hr + 1
            if hr >= 24:
               hr = 0 
   if delay_freq != 0.5:
      sec = sec + delay_freq

def display_values():
    global display
    display = "%02d:%02d:%02d:%02d" %(hr,min,sec,milli)
    
    TIME = time.strftime("%H:%M:%S")
    print TIME ,"      ", display , "      {}V".format(pot_volts),"         {}C".format(temperature),"         {}%".format(percent)
    print"_____________________________________________________________________"

    time.sleep(delay)

print"_____________________________________________________________________"
print"Time            Timer             Pot            Temp          Light"
print"_____________________________________________________________________"

def callback1(reset_button):
   global milli
   global sec
   global min
   global hr
   milli = 0
   sec = 0
   min = 0
   hr = 0
   unused_variable = os.system("clear")
   print"_____________________________________________________________________"
   print"Time            Timer             Pot            Temp          Light"
   print"_____________________________________________________________________"


def callback2(frequency_button):
    global delay_freq

    if delay_freq == 0.5:
       delay_freq = 1
    elif delay_freq == 1:
       delay_freq = 2
    else:
       delay_freq = 0.5
    print "delay_freq is now ",delay_freq

def callback3(stop_button):
   global monitor
   global x
   if monitor == True:
      monitor = False
   elif monitor == False:
      monitor = True
      read_sensors()

def callback4(display_button):
   global display
   global count
   global k
   timer()
   display = "%02d:%02d:%02d:%02d" %(hr,min,sec,milli)
   TIME = time.strftime("%H:%M:%S")

   
   for i in range(5):
      #nt TIME ,"      ", display , "      {}V".format(values.popleft()[0])   {}C".format(values.popleft))," 
      arr =  values.popleft()
      print(arr[0])
      print(arr[1])
      print(arr[2])
   count = 0

   

   time.sleep(delay)


GPIO.add_event_detect(reset_button, GPIO.FALLING, callback=callback1, bouncetime=200)
GPIO.add_event_detect(frequency_button, GPIO.FALLING, callback=callback2, bouncetime=200)
GPIO.add_event_detect(stop_button, GPIO.FALLING, callback=callback3, bouncetime=200)
GPIO.add_event_detect(display_button, GPIO.FALLING, callback=callback4, bouncetime=200)


try:

   while(1):

      light_sensor = ReadChannel(LDR_channel)
      light_volts = ConvertVolts(light_sensor, 2)
      percent = int((light_volts/3.3)*100)

      temp_sensor = ReadChannel(temp_channel)
      temp_volts = ConvertVolts(temp_sensor, 2)
      temperature       = ConvertTemp(temp_volts, 2)
      if temperature == 0:
         temperature ="0.00"

      pot_turn = ReadChannel(Pot_channel)
      pot_volts = ConvertVolts(pot_turn, 2)

      if delay_freq == 0.5:
         milli = milli + 5
      if milli >= 100:
         milli = 0
         sec = sec + 1
         if sec >= 60:
            sec = 0
            min = min + 1
            if min >= 60:
               min = 0
               hr = hr + 1
               if hr >= 24:
                  hr = 0 
      if delay_freq != 0.5:
         sec = sec + delay_freq
          
      if count < 5:
         values.append([pot_volts, temperature, percent])
	  
         count = count + 1
      else:
         values.popleft()
         values.append([pot_volts, temperature, percent])
	
       
   
      if monitor != False:
         display = "%02d:%02d:%02d:%02d" %(hr,min,sec,milli)
    
         TIME = time.strftime("%H:%M:%S")
         print TIME ,"      ", display , "      {}V".format(pot_volts),"         {}C".format(temperature),"         {}%".format(percent)
         print"_____________________________________________________________________"


      time.sleep(delay_freq)

except KeyboardInterrupt:

      GPIO.cleanup()

