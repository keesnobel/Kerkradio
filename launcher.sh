#!/bin/bash

cd /home/pi/Kerkradio
sudo python kerkradio.py
cd ~
exit

# in crontab -e 
# de volgende regel plaatsen
# @reboot sh /home/pi/Kerkradio/launcher.sh >/home/pi/logs/cronlog 2>&1
