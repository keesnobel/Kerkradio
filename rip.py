#!/usr/bin/env python
#
# ### internetradio - een internet radio programma voor de Raspberry Pi
# De Pi LCD moet erop aanwezig zijn
#
# Daniel Kropveld - okt 2015
#
# # Declaraties

import time
import os
import RPi.GPIO as GPIO
import subprocess

# # setup variables
# init state of 4 buttons
up       = False
down     = False
left     = False
right    = False
hostName = 'localhost'	#host where mpd is running

# Switches from left to right
SW1      = 9 		# Next station
SW2      = 4		# Previous station
SW3      = 23
SW4      = 10
INPUTS   = [SW1,SW2,SW3,SW4]

#OUTPUTS: map GPIO to LCD lines
LCD_RS   =  7      # GPIO7 = Pi pin 26
LCD_E    =  8      # GPIO8 = Pi pin 24
LCD_D4   = 17      # GPIO17 = Pi pin 11
LCD_D5   = 18      # GPIO18 = Pi pin 12
LCD_D6   = 27      # GPIO21 = Pi pin 13
LCD_D7   = 22      # GPIO22 = Pi pin 15
OUTPUTS  = [LCD_RS,LCD_E,LCD_D4,LCD_D5,LCD_D6,LCD_D7]

CLEARDISPLAY = 0x01
SETCURSOR    = 0x80
LINE         = [0x00,0x40]

# ## Functions

def InitIO():
  #Sets GPIO pins to input & output, as required by LCD board
  GPIO.setmode(GPIO.BCM)
  GPIO.setwarnings(False)
  for lcdLine in OUTPUTS:
    GPIO.setup(lcdLine, GPIO.OUT)
  for switch in INPUTS:
    GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Een knop staat op True, als ingedrukt is hij False
def CheckSwitches():
  val1 = not GPIO.input(SW1)
  val2 = not GPIO.input(SW2)
  val3 = not GPIO.input(SW3)
  val4 = not GPIO.input(SW4)
  return (val1,val2,val3,val4)

def PulseEnableLine():
  #Pulse the LCD Enable line; used for clocking in data
  mSec = 0.0005                   #use half-millisecond delay
  time.sleep(mSec)                #give time for inputs to settle
  GPIO.output(LCD_E, GPIO.HIGH)   #pulse E high
  time.sleep(mSec)
  GPIO.output(LCD_E, GPIO.LOW)    #return E low
  time.sleep(mSec)                #wait before doing anything else

def SendNibble(data):
  #sends upper 4 bits of data byte to LCD data pins D4-D7
  GPIO.output(LCD_D4,bool(data & 0x10))
  GPIO.output(LCD_D5,bool(data & 0x20))
  GPIO.output(LCD_D6,bool(data & 0x40))
  GPIO.output(LCD_D7,bool(data & 0x80))

def SendByte(data,charMode=False):
  #send one byte to LCD controller
  GPIO.output(LCD_RS,charMode)    #set mode: command vs. char
  SendNibble(data)                #send upper bits first
  PulseEnableLine()               #pulse the enable line
  data = (data & 0x0F)<< 4        #shift 4 bits to left
  SendNibble(data)                #send lower bits now
  PulseEnableLine()               #pulse the enable line

def InitLCD():
  #initialize the LCD controller & clear display
  SendByte(0x33)          #initialize
  SendByte(0x32)          #set to 4-bit mode
  SendByte(0x28)          #2 line, 5x7 matrix
  SendByte(0x0C)          #turn cursor off (0x0E to enable)
  SendByte(0x06)          #shift cursor right
  SendByte(CLEARDISPLAY)  #remove any stray characters on display

def SendChar(ch):
  SendByte(ord(ch),True)

def ShowMessage(string):
  #Send string of characters to display at current cursor position
  for character in string:
    SendChar(character)

def GotoLine(row):
  #Moves cursor to the given row
  #Expects row values 0-1 for 16x2 display; 0-3 for 20x4 display
  addr = LINE[row]
  SendByte(SETCURSOR+addr)

def ClearDisplay():
  SendByte(CLEARDISPLAY)

def WriteDisplay(string):
# Place string on both lines of the LCD display
  ClearDisplay()
  GotoLine(0)
  ShowMessage(message[0:16])
  GotoLine(1)
  ShowMessage(message[16:32])


# # Main program
InitIO()
InitLCD()
#print "Raspberry Pi Radio"

# make sure the audio card is started, as well as MPD
# replace with test if mpd is running
#os.system("sudo modprobe snd_bcm2835")
#os.system("sudo mpd")
os.system("mpc -h " + hostName + " clear > /dev/null")
# Playlist is in file with name music.m3u
os.system("mpc -h " + hostName + " load stations > /dev/null")
os.system("mpc -h " + hostName + " volume 0 > /dev/null")

# determine number of radio stations in the playlist
cmd = subprocess.Popen("mpc -h " + hostName + " playlist",shell=True, stdout=subprocess.PIPE)
stations = cmd.stdout.readlines()
numberOfStations = len(stations)

#Put up a display
ShowMessage('*Internet Radio*')

# iterates through the playlist in order to get the names (instead of the URLs)
index = numberOfStations
while(index):
  os.system('mpc  -h ' + hostName + ' play ' + str(index) + ' > /dev/null')
#  print "Loading " + str(index)
  GotoLine(1)
  ShowMessage(str(index) + ' - Wacht...  ')
  index = index - 1
  time.sleep(2.0)

#print "stations loaded: " + str(numberOfStations)

# At startup play nothing
if(numberOfStations>0):
  os.system("mpc  -h " + hostName + " stop > /dev/null")
  # Status is used with button 3: play/stop
  status = ''
  currentChannel = 0
  GotoLine(1)
  ShowMessage('Klaar: druk knop')

# speakers on
os.system("mpc -h " + hostName + " volume 90 > /dev/null")

# main loop, looking for button presses
# this looks more complicated because the loop will me fast, this way 
# when you press the buttons it only move one station until you release the button
InitIO()
while(True):
  if(down==True):
# Button 1 is pressed: switch to next channel
    if(GPIO.input(SW1)==False):
#      print "BUTTON UP PRESSED, SWITCHING TO: "
      if(currentChannel<numberOfStations):
        currentChannel = currentChannel + 1
      else:
        currentChannel = 1			
      command = subprocess.Popen("mpc -h " + hostName + " play " + str(currentChannel),shell=True, stdout=subprocess.PIPE)
      message = str(currentChannel) + " " + command.stdout.readline().strip()
      status  = 'play'
      WriteDisplay(message)
  down = GPIO.input(SW1)
  if(up==True):
# Button 2 is pressed: switch to previous channel
    if(GPIO.input(SW2)==False):
#      print "BUTTON DOWN PRESSED, SWITCHING TO: "
      if(currentChannel>1):
        currentChannel = currentChannel - 1
      else:
        currentChannel = numberOfStations
      command = subprocess.Popen("mpc -h " + hostName + " play " + str(currentChannel),shell=True, stdout=subprocess.PIPE)
      message = str(currentChannel) + " " + command.stdout.readline().strip()
#      message = message[0:len(message)-1]
      status = 'play'
      WriteDisplay(message)
  up = GPIO.input(SW2)
  if(left==True):
# Button 3 is pressed, toggle 'mpc stop' and 'mpc play'
    if(GPIO.input(SW3)==False):
      if(status=='play'):
        command = subprocess.Popen("mpc -h " + hostName + " stop",shell=True, stdout=subprocess.PIPE)
        status  = 'stop'
        message = '*Internet Radio*Pause: druk knop'
        WriteDisplay(message)
      else:
        command = subprocess.Popen("mpc -h " + hostName + " play " + str(currentChannel),shell=True, stdout=subprocess.PIPE)
        message = str(currentChannel) + " " + command.stdout.readline().strip()
        status='play'
        WriteDisplay(message)
  left = GPIO.input(SW3)
  if(right==True):
# Button 4 pressed, switch back to first radio channel
    if(GPIO.input(SW4)==False):
      currentChannel=1
      command = subprocess.Popen("mpc -h " + hostName + " play " + str(currentChannel),shell=True, stdout=subprocess.PIPE)
      message = str(currentChannel) + " " + command.stdout.readline().strip()
      status = 'play'
      WriteDisplay(message)
  right = GPIO.input(SW4)
#
  time.sleep(.1)

# this is never hit, but should be here to indicate if you plan on leaving the main loop
os.system("mpc -h " + hostName + " stop > /dev/null")
ClearDisplay()
# print "done"
# eof #
