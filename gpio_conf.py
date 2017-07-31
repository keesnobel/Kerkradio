#!/usr/bin/python
##

import RPi.GPIO as GPIO
from time import sleep
import time

#Button config
POWER  = 24
LINKS  = 18
RECHTS = 17
NEER   = 4
OP     = 10
LED    = 27
RELAIS = 23

def gpio_setup():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(POWER,GPIO.IN, pull_up_down=GPIO.PUD_UP)       	
	GPIO.setup(RECHTS,GPIO.IN, pull_up_down=GPIO.PUD_UP)	
	GPIO.setup(LINKS,GPIO.IN, pull_up_down=GPIO.PUD_UP)	
	GPIO.setup(OP,GPIO.IN, pull_up_down=GPIO.PUD_UP)			
	GPIO.setup(NEER,GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(LED, GPIO.OUT)
	GPIO.setup(RELAIS, GPIO.OUT)
	
def LedBlink():
	for i in range(0,10):
		GPIO.output(LED,True)
		time.sleep(0.1)
		GPIO.output(LED,False)
		time.sleep(0.1)
