#!/usr/bin/python
##
import time
import psutil
from time import sleep
import gpio_conf

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