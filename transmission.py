# Software from Zenith Aerospace Group.
# A simple LoRa Image Transmiter.

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
    resto = 0
  
 

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
        self.resto  = 0
    

    def take_pic(self):
    	print "Taking Pic...."

        # raspistill command for taking pictures from Raspberry Cam
    	os.system("raspistill -th none -vf -q 10 -w 640 -h 480 -o currentPicture.jpg")

        # Open saved picture
    	with open("currentPicture.jpg","rb") as imageFile:
       	    self.f = imageFile.read()

        self.b = bytearray(self.f)
        self.a = sys.getsizeof(self.b)
        self.c =  len(self.b)
        self.n = int( self.a / self.step)

    def send_image(self):     

        if self.sending == 1:

            # Normal packet  
            if self.i < self.n:

                # Appending packet number, 1 byte
                Z = bytearray([self.i,0])                

                # Appending bytearray from picture, 253 bytes
                Z[1:] = self.b[self.i * self.step : self.i * self.step + (self.step - 1)]                
                print "I'm on %d" % self.i
                print "Packet: [%d .. %d ]" % (int(self.b[self.i * self.step]), int(self.b[self.i * self.step + (self.step - 1)]))

                # Casting to List (needed)
                E = list(Z)     

                # Increment Packet number
                self.i += 1

                # Init SPI transmission to radio
                self.write_payload(E)
                BOARD.led_on()
                self.set_mode(MODE.TX)

            # Last packet
            elif self.i == self.n: 

                print "Sending remaining bytes....."           
                # Appending packet number, 1 byte
                Z = bytearray([self.i,0])
                print "Packet: "
                print self.b[self.i * self.step:] 

                # Appending bytearray from picture, X remaining bytes
                Z[1:] = self.b[self.i * self.step:]            

                # Casting to List (needed)
                E = list(Z) 

                # Init SPI transmission do radio
                self.write_payload(E)
                BOARD.led_on()
                self.set_mode(MODE.TX)

                # Reset global variables
                self.re_init()

                print "Waiting for new pic..."

    def on_tx_done(self):
        global args
        self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)
        BOARD.led_off()
        sleep(args.wait)
        if self.sending == 1:
            self.send_image()    

    # Main function
    def start(self):
        global args                
        BOARD.led_on()
	
	while True:
	    sleep(0.5) # Needed for some unknown reason.

	    if self.sending == 0: # If not sending
	    	print "Starting process"
	    	sleep(1)

	    	self.sending = 1
	    	self.take_pic() # Take new picture

	    	print "TAMANHO DA FOTO %d" % self.a 
	    	print self.n
	    	print "PACOTES CHEIOS: %d" % self.n
	    	print "RESTO: %d" % (self.a%self.step)
	    	
	    	self.send_image() # Iniciate IRQ recurssion
	    	  	

lora = LoRaBeacon(verbose=False)
args = parser.parse_args(lora)
lora.set_pa_config(pa_select=1)

assert(lora.get_agc_auto_on() == 1)

print "Beacon config: %d" % args.wait

print 

try:
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print 
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()
