 #!/usr/bin/env python

""" A simple beacon transmitter class to send a 1-byte message (0x0f) in regular time intervals. """

# Copyright 2015 Mayer Analytics Ltd.
#
# This file is part of pySX127x.
#
# pySX127x is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pySX127x is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You can be released from the requirements of the license by obtaining a commercial license. Such a license is
# mandatory as soon as you develop commercial activities involving pySX127x without disclosing the source code of your
# own applications, or shipping pySX127x with a closed source product.
#
# You should have received a copy of the GNU General Public License along with pySX127.  If not, see
# <http://www.gnu.org/licenses/>.


import sys
import io
import os
from time import sleep
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD
import math
from PIL import Image

BOARD.setup()

parser = LoRaArgumentParser("A simple LoRa beacon")
parser.add_argument('--single', '-S', dest='single', default=False, action="store_true", help="Single transmission")
parser.add_argument('--wait', '-w', dest='wait', default=0.2, action="store", type=float, help="Waiting time between transmissions (default is 0s)")

class LoRaBeacon(LoRa):

    f = []
    b = []
    a = []
    c =  0
    i = 0
    last = 1
    n=0
    step = 254
    sending = 0
 

    def __init__(self, verbose=False):
        super(LoRaBeacon, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([1,0,0,0,0,0])
	

    def re_init(self):
	self.f = []
	self.b = []
	self.a = []
	self.c =  0
	self.i = 0
	self.last = 1
	self.n=0
	self.step = 254
    	self.sending = 0

    def take_pic(self):
    	print "Taking Pic...."
    	os.system("raspistill -th none -vf -q 10 -w 640 -h 480 -o seistrampando.jpg")
	with open("seistrampando.jpg","rb") as imageFile:
   	    self.f = imageFile.read()
   	self.b = bytearray(self.f)
	self.a = sys.getsizeof(self.b)
	self.c =  len(self.b)
	self.n = int( self.a / self.step)

    def send_image(self):
        if self.i == self.n:
	    print "Mandando resto..."
	    self.write_payload(list(self.b[self.i*self.step:]))
	    BOARD.led_on()
	    self.set_mode(MODE.TX)
	    print "Waiting for new pic..."
	    self.re_init()
	elif self.i < self.n:
	    #print "RANGE = %d to %d" % (self.i*self.step,self.i*self.step+self.step)
	    Z = self.b[self.i*self.step:self.i*self.step + self.step]
	    print "Estou no %d" % self.i
	    E = list(Z)
	    self.i += 1
	    self.write_payload(E)
	    BOARD.led_on()
	    self.set_mode(MODE.TX)

    def on_rx_done(self):
        print("\nRxDone")
        #print(self.get_irq_flags())
        print(map(hex, self.read_payload(nocheck=True)))
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
	#print("Bb")

    def on_tx_done(self):
        global args
	self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)
        BOARD.led_off()
        sleep(args.wait)
        if self.sending == 1:
            self.send_image()

    def on_cad_done(self):
        print("\non_CadDone")
        print(self.get_irq_flags())
	print("Ee")

    #def on_rx_timeout(self):
        ##print("\non_RxTimeout")
        #print(self.get_irq_flags())
	#print("Ff")
    def on_valid_header(self):
        print("\non_ValidHeader")
        print(self.get_irq_flags())
	print("Gg")
    def on_payload_crc_error(self):
        print("\non_PayloadCrcError")
        print(self.get_irq_flags())
	print("Hh")
    def on_fhss_change_channel(self):
        print("\non_FhssChangeChannel")
        print(self.get_irq_flags())
	print("Ii")
    def start(self):
        global args
        sys.stdout.write("\rstart")
        self.tx_counter = 0
        BOARD.led_on()
	
	while True:
	    sleep(0.5)
	    #print "SENDING: %d" % self.sending
	    if self.sending == 0:
	    	print "Starting process"
	    	sleep(15)
	    	self.sending = 1
	    	self.take_pic()
	    	print "TAMANHO DA FOTO %d" % self.a
	    	print self.n
	    	print "PACOTES CHEIOS: %d" % self.n
	    	print "RESTO: %d" % (self.a%self.step)
	    	#print "SIZE Z: %d" % len(Z)
	    	self.send_image()
	    	  	
	   	

lora = LoRaBeacon(verbose=False)
args = parser.parse_args(lora)
lora.set_pa_config(pa_select=1)

#lora.set_rx_crc(True)
#lora.set_agc_auto_on(True)
#lora.set_lna_gain(GAIN.NOT_USED)
#lora.set_coding_rate(CODING_RATE.CR4_6)
#lora.set_implicit_header_mode(False)
#lora.set_pa_config(max_power=0x04, output_power=0x0F)
#lora.set_pa_config(max_power=0x04, output_power=0b01000000)
#lora.set_low_data_rate_optim(True)
#lora.set_pa_ramp(PA_RAMP.RAMP_50_us)


#print(lora)
#assert(lora.get_lna()['lna_gain'] == GAIN.NOT_USED)
assert(lora.get_agc_auto_on() == 1)

print("Beacon config:")
print("  Wait %f s" % args.wait)
print("  Single tx = %s" % args.single)
print("")
#try: input("Press enter to start...")
#except: pass

try:
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("")
    lora.set_mode(MODE.SLEEP)
    #print(lora)
    BOARD.teardown()
