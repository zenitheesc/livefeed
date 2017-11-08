#!/usr/bin/env python3

""" A simple continuous receiver class. """

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


from time import sleep
import time
import smtplib
import mimetypes
import email
import email.mime.application
import sys
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD
import io
from PIL import Image
from array import array

BOARD.setup()

parser = LoRaArgumentParser("Continous LoRa receiver.")


class LoRaRcvCont(LoRa):

    receiver_buffer = []
    first_packet = 1
    millis = 0
    recv = 0
    var = 0

    def __init__(self, verbose=False):

        super(LoRaRcvCont, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)

    def re_init(self):
	self.receiver_buffer = []
    	self.first_packet = 1
    	self.millis = 0
    	self.recv = 0
	self.var = 0

    def on_rx_done(self):
	if self.first_packet == 1:
	    self.first_packet = 0
	    self.millis = int(round(time.time() * 1000))
	self.recv = int(round(time.time() * 1000))
        BOARD.led_on()
        #print("\nRxDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        #print(bytes(payload).decode())

	self.receiver_buffer += payload
	print "Recebi o %d" % self.var
	self.var = self.var + 1
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        BOARD.led_off()
        self.set_mode(MODE.RXCONT)

    def on_tx_done(self):
        print("\nTxDone")
        print(self.get_irq_flags())

    #def on_cad_done(self):
        #print("\non_CadDone")
        #print(self.get_irq_flags())

    #def on_rx_timeout(self):
        #print("\non_RxTimeout")
        #print(self.get_irq_flags())

    #def on_valid_header(self):
        #print("\non_ValidHeader")
        #print(self.get_irq_flags())

    #def on_payload_crc_error(self):
        #print("\non_PayloadCrcError")
        #print(self.get_irq_flags())

    #def on_fhss_change_channel(self):
        #print("\non_FhssChangeChannel")
        #print(self.get_irq_flags())

    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
	a = 1	
	print "Running!"
        while True:
            rssi_value = self.get_rssi_value()
            status = self.get_modem_status()
            sys.stdout.flush()
            sys.stdout.write("\r%d %d %d" % (rssi_value, status['rx_ongoing'], status['modem_clear']))
	    if  int(round(time.time() * 1000)) - self.recv >= 5000 and self.first_packet == 0:
		#a = 0
		#print type(self.millis)
		print "ESSA PORRA DUROU::::"
		print int(round(time.time() * 1000)) - self.millis
		print "TAMANHO DESSA PORRA %d" % sys.getsizeof(bytearray(self.receiver_buffer))
		image = Image.open(io.BytesIO(bytearray(self.receiver_buffer)))
        	image.save("pybrocado.png")
		msg = email.mime.Multipart.MIMEMultipart()
		msg['Subject'] = 'First Live Photo'
		msg['From'] = 'zenith.eesc@gmail.com'
		msg['To'] = 'zenith.eesc@gmail.com'

		directory = 'pybrocado.png'
		 
		# Split de directory into fields separated by / to substract filename
		 
		spl_dir=directory.split('/')
		 
		# We attach the name of the file to filename by taking the last
		# position of the fragmented string, which is, indeed, the name
		# of the file we've selected
		 
		filename=spl_dir[len(spl_dir)-1]
		 
		# We'll do the same but this time to extract the file format (pdf, epub, docx...)
		 
		spl_type=directory.split('.')
		 
		type=spl_type[len(spl_type)-1]
		 
		fp=open(directory,'rb')
		att = email.mime.application.MIMEApplication(fp.read(),_subtype=type)
		fp.close()
		att.add_header('Content-Disposition','attachment',filename=filename)
		msg.attach(att)
		 
		# send via Gmail server
		# NOTE: my ISP, Centurylink, seems to be automatically rewriting
		# port 25 packets to be port 587 and it is trashing port 587 packets.
		# So, I use the default port 25, but I authenticate.
		s = smtplib.SMTP('smtp.gmail.com:587')
		s.starttls()
		s.login('zenith.eesc@gmail.com','zenith2016')
		s.sendmail('zenith.eesc@gmail.com','zenith.eesc@gmail.com', msg.as_string())
		s.quit()
		self.re_init()


lora = LoRaRcvCont(verbose=False)
args = parser.parse_args(lora)

lora.set_mode(MODE.STDBY)
lora.set_pa_config(pa_select=1)
#lora.set_rx_crc(True)
#lora.set_coding_rate(CODING_RATE.CR4_6)
#lora.set_pa_config(max_power=0, output_power=0)
#lora.set_lna_gain(GAIN.G1)
#lora.set_implicit_header_mode(False)
#lora.set_low_data_rate_optim(True)
#lora.set_pa_ramp(PA_RAMP.RAMP_50_us)
#lora.set_agc_auto_on(True)

#print(lora)
assert(lora.get_agc_auto_on() == 1)

try:
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print("")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("")
    lora.set_mode(MODE.SLEEP)
    #print(lora)
    BOARD.teardown()
