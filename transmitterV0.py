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


	image_buffer = []           #list that receive the bytearray of image
	buffer_size = []            #piece of image_buffer that will be send
	iteration = 0				#number that represent the package that is being sending
	number_packets = 0
	step = 252					#the number of bytes that will be send per packet
	number_image = 0            #the number that indicate the number of the picture that is being sended
	sending = 0
	resto = 0
	first_time = 1



	def __init__(self, verbose=False):
		super(LoRaBeacon, self).__init__(verbose)
		self.set_mode(MODE.SLEEP)
		self.set_dio_mapping([1,0,0,0,0,0])


	def re_init(self):

		self.image_buffer = []
		self.buffer_size = []
		self.iteration = 0
		self.number_packets = 0
		self.step = 252
		self.sending = 0
		self.resto  = 0
		self.first_time = 1

	def semi_re_init(self):
		self.iteration = 0


	def take_pic(self):
		print "Taking Pic...."
		number_image += 1

		# raspistill command for taking pictures from Raspberry Cam
		os.system("raspistill -th none -vf -w 600 -h 400 -q 10 -o currentPicture.jpg")

		# save picture into another directory
		suport_string = "cp currentPicture.jpg Images/" + str(number_image) + ".jpg"
		os.system(suport_string)

		# Open saved picture
		with open("currentPicture.jpg","rb") as imageFile:
			f = imageFile.read()

		self.image_buffer = bytearray(f)
		self.buffer_size = sys.getsizeof(self.image_buffer)
		self.number_packets = int( self.buffer_size / self.step)

	def send_image(self):

		if self.sending == 1:

			# Normal packet
			if self.iteration < self.number_packets:

				# Appending packet number, 1 byte
				Z = bytearray([self.iteration,self.number_image])

				# Appending bytearray from picture, 253 bytes
				Z[2:] = self.image_buffer[self.iteration * self.step : self.iteration * self.step + self.step]
				print "I'm on %d" % self.iteration

				# Casting to List (needed)
				E = list(Z)

				# Increment Packet number
				self.iteration += 1

				# Init SPI transmission to radio
				self.write_payload(E)
				BOARD.led_on()
				self.set_mode(MODE.TX)

			# Last packet
			elif self.iteration == self.number_packets:

				print "Sending remaining bytes....."
				# Appending packet number, 1 byte
				Z = bytearray([self.iteration,0])
				print "Packet: %d" % self.iteration

				# Appending bytearray from picture, X remaining bytes
				Z[2:] = self.image_buffer[self.iteration * self.step:]

				# Casting to List (needed)
				E = list(Z)

				# Init SPI transmission do radio
				self.write_payload(E)
				BOARD.led_on()
				self.set_mode(MODE.TX)

				# Reset global variables
				if self.first_time == 0:
					self.re_init()
					print "Waiting for new pic..."
				else:
					self.semi_re_init()
					print "Sending picture second time..."
					self.first_time = 0

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
				print "Starting process..."

				self.sending = 1

				self.take_pic() # Take new picture

				print "Sending picture first time..."
				print "Picture size: %d bytes." % self.buffer_size
				print "Full packets: %d" % self.number_packets
				print "Last packet: %d bytes." % (self.buffer_size%self.step)

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
