# Software from Zenith Aerospace Group.
# A simple LoRa Image Receiver.

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
from PIL import Image, ImageFile
from array import array
from random import randint



BOARD.setup()

parser = LoRaArgumentParser("Continous LoRa receiver.")


class LoRaRcvCont(LoRa):

    receiver_buffer = []
    first_packet = 1
    millis = 0
    recv = 0
    var = 0
    missed_packets = []

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
        self.missed_packets = []

    def on_rx_done(self):

        # Get time of first packet received
    	if self.first_packet == 1:
    	    self.first_packet = 0
    	    self.millis = int(round(time.time() * 1000))

        # Reset timeout
        self.recv = int(round(time.time() * 1000))
        BOARD.led_on()
        
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        print "Var = %d" % self.var        
        print "Packet = %d" % payload[0]

        # If packet number is correct
        if payload[0] == self.var: 
            self.receiver_buffer += payload[1:]
            print "Correctly received the %d packet" % self.var
            self.var = self.var + 1
        elif payload[0] - self.var > 0:
            print "Missed a packet... blacking-out..."

            # Black out all missed packets
            for x in xrange(0, int(payload[0]) - self.var):     
                self.missed_packets.append(self.var + x)
                self.receiver_buffer += list([0] * 253)

            print "Missed packets: "
            print self.missed_packets
            print "Blacked-out %d packets..." % (int(payload[0]) - self.var)
            self.receiver_buffer += payload[1:]   
            self.var = payload[0] + 1;     

        # LoRa stuff
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        BOARD.led_off()
        self.set_mode(MODE.RXCONT)

    def check_finished(self):
        if int(round(time.time() * 1000)) - self.recv >= 3000 and self.first_packet == 0:
            return True
        else:
            return False

    def print_sumary(self):
        print "Total duration: %d seconds" % (int(round(time.time() * 1000)) - self.millis)
        print "Total size of image: %d bytes" % sys.getsizeof(bytearray(self.receiver_buffer))

    def save_image(self):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        try:
            image = Image.open(io.BytesIO(bytearray(self.receiver_buffer)))
            image.save("LivePicture.png")
        except Exception as e:
            print "Error opening image!!"
            print e
            raise e        
        finally:
            print "Image saved!!"

    def send_email(self):
        msg = email.mime.Multipart.MIMEMultipart()
        msg['Subject'] = 'First Live Photo'
        msg['From'] = 'zenith.eesc@gmail.com'
        msg['To'] = 'zenith.eesc@gmail.com'

        directory = 'LivePicture.png'

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
        print "Image sent to email."

    def start(self):

        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
    	print "Running!"        
        while True:

            sleep(0.1)
                        
            if self.check_finished():
                
                self.print_sumary()
                
                self.save_image()

                self.send_email()
                
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
