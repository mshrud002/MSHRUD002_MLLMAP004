#!/usr/bin/python

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

#Set the pins to pull_up and pull_down
GPIO.setup(reset_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(frequency_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(stop_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(display_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#pin definition
#SPICLK = 11
#SPIMISO = 9
#SPIMOSI = 10 
#SPICS = 8


#GPIO.setup(SPIMOSI, GPIO.OUT)
#GPIO.setup(SPIMOSI, GPIO.IN)
#GPIO.setup(SPICLK,  GPIO.OUT)
#GPIO.setup(SPICS,   GPIO.OUT)

spi = spidev.SpiDev()   # create spi object
spi.open(0,0)
#RPI has one bus(#0) and two devices (#0 & #1)

# function to read ADC data from a channel
def GetData(channel):             #channel must be an integer 0-7
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
def ConvertTemp(data,decimal_places)
    temp = ((data*330)/float(1023))-50
    temp = round(temp,decimal_places)
    return temp

#Define sensor channels
LDR_channel = 0
Temp_channel = 1
Pot_channel = 2
#Define delay between readings
delay = 0.5



try:
    
    while True:
        #Read the data from light sensor
        light_sensor = ReadChannel(LDR_channel)
        light_volts = ConvertVolts(light_sensor, 2)

        #Read the data from temperature sensor
        temp_sensor = ReadChannel(temp_channel)
        temp_voltage = ConvertVolts(temp_sensor, 2)

        #Read the data from potentiometer
        pot_turn = ReadChannel(Pot_channel)
        pot_turn = ConvertVolts(pot_turn, 2)
        
        # wait before repeating loop
        time.sleep(delay)
#except keyboardInterrupt:
    #spi.close()
         
