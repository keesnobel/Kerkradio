#!/usr/bin/python
##
# Kerkradio versie 3.0
# Kees Nobel
# Twitter: @keesnobel

import time
import RPi.GPIO as GPIO
import os
import threading
from time import sleep
import lcd_display
lcd = lcd_display.lcd()
from urllib2 import urlopen
import commands
from datetime import datetime
import pyspeedtest
import psutil

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

def LedBlink(numTimes,speed):
	for i in range(0,numTimes):
		GPIO.output(LED,True)
		time.sleep(speed)
		GPIO.output(LED,False)
		time.sleep(speed)
iterations = 10
speed = 0.1

def test():
	count=0
	qry=''
	ul=0.00
	dl=0.00
	t0 = time.time()
	upload = psutil.net_io_counters(pernic=True)['wlan0'][0]
	download = psutil.net_io_counters(pernic=True)['wlan0'][1]
	up_down = (upload,download)

	while True:
		sleep(0.3)
		if((GPIO.input(OP)==False)):
			return
		if((GPIO.input(NEER)==False)):
			return
		last_up_down = up_down
		upload=psutil.net_io_counters(pernic=True)['wlan0'][0]
		download=psutil.net_io_counters(pernic=True)['wlan0'][1]
		t1 = time.time()
		up_down = (upload,download)
		try:
			ul, dl = [(now - last) / (t1 - t0) / 1024.0
				for now,last in zip(up_down, last_up_down)]             
			t0 = time.time()
		except:
			pass
		if dl>0.1 or ul>=0.1:
			time.sleep(0.75) 
			lcd.display_string(('UL= {:0.2f} kB/s'.format(ul)), 1)
			lcd.display_string(('DL= {:0.2f} kB/s'.format(dl)), 2)	

def laden_mpc():
	os.system("sudo /usr/bin/tvservice -o")
	os.system("sudo modprobe snd_bcm2835")
	os.system("sudo mpc")
	os.system("sudo mpc clear")
	os.system("sudo mpc volume 0")
	os.system("mpc add http://stream.hervormdoudewater.nl:8010/hekendorp")	# Hekendorp
	os.system("mpc add http://62.45.72.16:8000")				# Oudewater
	os.system("mpc add http://62.45.72.15:8000")				# Hekendorp 2
	os.system("mpc add http://grootnieuwsradio.streampartner.nl:8000/live")	# Grootnieuws radio
	os.system("mpc add http://media01.streampartner.nl:8003/live")		# Reformatorische omroep

def Afsluiten():
	LedBlink(int(iterations),float(speed))
	os.system("sudo /usr/bin/tvservice -p")
	GPIO.output(RELAIS, 0)
	lcd.display_string("", 1)
	lcd.display_string("", 2)
	lcd.backlight_off()
	os.system("sudo mpc clear")
	os.system("sudo mpc volume 0")
	print("Alles afgesloten. EINDE")
	GPIO.cleanup()

def power():
	power_closed = False
	led_aan = False
	op_dicht = False
	neer_dicht = False
	rechts_dicht = False
	links_dicht = False
	menu_aan = False
	uit_zetten = False
	cpu_aan = False
	cpu_loop = False
	echt_uit = False
	menu1 = False
	menu2 = False
	menu3 = False
	menu4 = False
	menu5 = False
	menu6 = False
	menu7 = False
	menu8 = False
	menu9 = False
	test_aan = False
	Max_Gebouw = 5
	Gebouw = ['               ', 'Hekendorp       ', 'Oudewater       ', 'Hekendorp 2    ', 'Grootnieuws    ', 'RO 1           '];
	currentChannel = 1
	Volume = 10
	TIJD = datetime.now().strftime("%H:%M:%S")
	DT = datetime.now().strftime("%d-%m-%Y")
	lcd.display_string("Welkom ", 1)
	lcd.display_string("standby", 2)
	LedBlink(int(iterations),float(speed))
	GPIO.output(LED, 0)
	GPIO.output(RELAIS, 0)
	sleep(2)
	lcd.display_string("", 1)
	lcd.display_string("", 2)
	lcd.backlight_off()

	while (True):

#### Power menu ###############################################################################

#### keuze tussen echt uit of stream gebruik.

		if(GPIO.input(POWER)==False and led_aan and echt_uit==False):
			lcd.display_string("uitschakelen ? ", 1)
			lcd.display_string("druk uit knop !", 2)					
			test_aan = True
			if (GPIO.input(POWER)==False):
				echt_uit = True
				GPIO.output(LED, 0)
				power_closed = False
				led_aan = False
				lcd.display_string("tot", 1)
				lcd.display_string("ziens", 2)
				os.system("sudo mpc clear")
				os.system("sudo mpc stop")
				time.sleep(3)
				GPIO.output(RELAIS, 0)
				lcd.display_string("", 1)
				lcd.display_string("", 2)
				lcd.backlight_off()
				echt_uit = False
				test_aan = False
#### Stream gebruik.

		elif((GPIO.input(OP)==False) and test_aan):
			lcd.display_string("netwerk", 1)
			lcd.display_string("gebruik", 2)
			test_aan = True
			echt_uit = False
			test()
			test_aan = False
			lcd.display_string(Gebouw[currentChannel],1)
			lcd.display_string(("Volume = " + str(Volume) + "     ") ,2)

###### Werkelijk aan zetten

		elif(GPIO.input(POWER)==False and power_closed==False and led_aan==False):
			GPIO.output(LED, 1)
			GPIO.output(RELAIS, 1)
			lcd.display_string("Welkom", 1)
			lcd.display_string(str(DT), 2)
			laden_mpc()
			led_aan = True
			os.system("sudo mpc play " + str(currentChannel))
			os.system("sudo mpc volume " + str(Volume))
			time.sleep(3)
			lcd.display_string(Gebouw[currentChannel],1)
			lcd.display_string(("Volume = " + str(Volume) + "     ") ,2)


###### Bediening menu ############################################################################

		elif (led_aan):

###### Volume op
			op_val = GPIO.input(OP)
			if (op_val and op_dicht):
				op_dicht = False
			elif (op_val==False and op_dicht==False and test_aan==False):
				op_dicht = True
				Volume = Volume + 5
				if(Volume > 100):
					Volume = 100
				os.system("sudo mpc volume " + str(Volume))
				lcd.display_string(("Volume = " + str(Volume) + "     ") ,2)

####### Volume neer
			neer_val = GPIO.input(NEER)
			if (neer_val and neer_dicht):
				neer_dicht = False
			elif (neer_val==False and neer_dicht==False and test_aan==False):
				neer_dicht = True
				Volume = Volume - 5
				if(Volume<10):
					Volume = 10
				os.system("sudo mpc volume " + str(Volume))
				lcd.display_string(("Volume = " + str(Volume) + "     ") ,2)

######## Links
			links_val = GPIO.input(LINKS)
			if (links_val and links_dicht):
				links_dicht = False
			elif (links_val==False and links_dicht==False and test_aan==False):
				links_dicht = True
				currentChannel = currentChannel - 1
				if(currentChannel==0):
					currentChannel = Max_Gebouw
				lcd.display_string(Gebouw[currentChannel],1)
				os.system("sudo mpc play " + str(currentChannel))
				os.system("sudo mpc volume " + str(Volume))
				lcd.display_string(("Volume = " + str(Volume) + "     ") ,2)

######## Rechts
			rechts_val = GPIO.input(RECHTS)
			if (rechts_val and rechts_dicht):
				rechts_dicht = False
			elif (rechts_val==False and rechts_dicht==False and test_aan==False):
				rechts_dicht = True
				currentChannel = currentChannel + 1
				if(currentChannel > Max_Gebouw):
					currentChannel=1
				lcd.display_string(Gebouw[currentChannel],1)
				os.system("sudo mpc play " + str(currentChannel))
				os.system("sudo mpc volume " + str(Volume))
				lcd.display_string(("Volume = " + str(Volume) + "     ") ,2)

######## Beheer Menu #########################################################################################
# met de links en rechts knop tegelijk ingedrukt kom je in het "beheer menu" zodra de led uit is

		elif (led_aan==False and test_aan==False):	
			if ((GPIO.input(LINKS)==False) and (GPIO.input(RECHTS)==False)):
				menu_aan = True
				lcd.display_string("|< exit         ", 1)
				lcd.display_string("     Volgende >|", 2)
				menu1 = True

### externe ip ----------------------------------
			elif (menu1 and (GPIO.input(RECHTS)==False)):	
				my_ip = urlopen('http://ip.42.pl/raw').read()
				lcd.display_string("externe ip        ", 1)
 				lcd.display_string((str(my_ip)),2)
				menu1 = False
				menu2 = True
				menu9 = False

### interne ip -----------------------------------
			elif (menu2 and (GPIO.input(RECHTS)==False)):	
				ipaddr = commands.getoutput("hostname -I")
				lcd.display_string("interne ip        ", 1)
 				lcd.display_string((str(ipaddr)),2)
				menu2 = False
				menu3 = True

### cpu gebruik -----------------------------------
			elif (menu3 and (GPIO.input(RECHTS)==False)):
				CPU_Pct=str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))
				lcd.display_string("CPU Usage", 1)
 				lcd.display_string((str(CPU_Pct)),2)
				menu3 = False
				menu4 = True

### Reboot -----------------------------------
			elif (menu4 and (GPIO.input(RECHTS)==False)):
				lcd.display_string("Reboot    = +    ", 1)
				lcd.display_string("annuleren = >|   ", 2)
				menu4 = False
				menu5 = True

			elif (menu5 and (GPIO.input(OP)==False)):
				lcd.display_string("Reboot", 1)
				lcd.display_string("tot zo", 2)
				sleep(2)
				lcd.backlight_off()
				LedBlink(int(iterations),float(speed))
				os.system("sudo reboot")

### Uitzetten -----------------------------------
			elif(menu5 and (GPIO.input(RECHTS)==False)):			
				lcd.display_string("uitzetten = +    ", 1)
				lcd.display_string("annuleren = >|   ", 2)
				menu5 = False
				menu6 = True

			elif (menu6 and (GPIO.input(OP)==False)):
				lcd.display_string("Tot", 1)
				lcd.display_string("Ziens", 2)
				sleep(2)
				lcd.backlight_off()
				LedBlink(int(iterations),float(speed))
				os.system("sudo shutdown -h now")

### HDMI aan/uit -----------------------------------
			elif (menu6 and (GPIO.input(RECHTS)==False)):
				lcd.display_string("HDMI aan = +    ", 1)
				lcd.display_string("HDMI uit = -    ", 2)
				menu6 = False
				menu7 = True
				menu8 = True

			elif (menu7 and (GPIO.input(OP)==False)):
				lcd.display_string("HDMI aan", 1)
				lcd.display_string("|< exit        ", 2)
				os.system("sudo /usr/bin/tvservice -p")
				menu8 = True

			elif (menu7 and (GPIO.input(NEER)==False)):
				lcd.display_string("HDMI uit", 1)
				lcd.display_string("|< exit         ", 2)
				os.system("sudo /usr/bin/tvservice -o")
				menu8 = True

### Speedtest -----------------------------------
			elif (menu8 and (GPIO.input(RECHTS)==False)):
				lcd.display_string("speed Up   = +    ", 1)
				lcd.display_string("Speed Down = -    ", 2)
				menu7 = False
				menu8 = False
				menu9 = True
				menu1 = True

			elif (menu9 and (GPIO.input(OP)==False)):
				lcd.display_string("Upload aan", 1)
				lcd.display_string("het testen", 2)
				st = pyspeedtest.SpeedTest()
				up = round(st.upload()/1048576,2)
				lcd.display_string("Upload", 1)
 				lcd.display_string((str(up) + " Mbps"),2)
				menu1 = True

			elif (menu9 and (GPIO.input(NEER)==False)):
				lcd.display_string("Download aan", 1)
				lcd.display_string("het testen", 2)
				st = pyspeedtest.SpeedTest()
				down = round(st.download()/1048576,2)
				lcd.display_string("Download", 1)
 				lcd.display_string((str(down) + " Mbps"),2)
				menu1 = True

### Exit menu -----------------------------------
			elif (menu_aan and (GPIO.input(LINKS)==False)):
				menu_aan = False
				lcd.display_string("Menu", 1)
				lcd.display_string("exit", 2)
				sleep(2)
				lcd.display_string("                ", 2)
				lcd.backlight_off()
		sleep(0.02)


if __name__ == '__main__':     # Program start from here		
	gpio_setup()
	try:
		power()
	except KeyboardInterrupt:
		Afsluiten()

#End
