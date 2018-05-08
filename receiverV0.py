# Software from Zenith Aerospace Group.
# A simple LoRa Image Receiver.

import io
import sys
import os

from time import sleep
import time

import smtplib
import mimetypes
import email
import email.mime.application

from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD

from PIL import Image, ImageFile
from array import array
from random import randint

from math import ceil



BOARD.setup()

parser = LoRaArgumentParser("Continous LoRa receiver.")


class LoRaRcvCont(LoRa):

    receiver_buffer0 = []                           # lista com os pacotes recebidos na primeira tentativa de envio (0)
    receiver_buffer1 = []                           # lista com os pacotes recebidos na segunda tentativa de envio (1)
    first_packet = 1
    millis = 0
    recv = 0
    var = 0                                         # índice do pacote esperado a ser recebido
    image_number = 0                                # índice da imagem esperada a ser recebida
    missed_packets0 = []                            # lista com os pacotes perdidos na tentativa de envio 0
    missed_packets1 = []                            # lista com os pacotes perdidos na tentativa de envio 1
    missed_packets_number = 0
    attempt = 0                                     # variável para indicar qual a tentavia de envio
    step = 252                                      # tamanho do pacote
    image_test = 1
    time_reference = 0                              # tempo no qual um pacote foi recebido
    variation_time = 0                              # variação do tempo entre as recepções
    savingbuffer = []                               # lista com os pacotes que serão salvos em um arquivo de imagem

    def __init__(self, verbose=False):

        super(LoRaRcvCont, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)

    def re_init(self):
        # Todas as listas e variáveis para armazenamento de pacotes são resetadas
        self.receiver_buffer0 = []
        self.receiver_buffer1 = []
    	self.first_packet = 1
    	self.millis = 0
    	self.recv = 0
        self.var = 0
       	self.missed_packets0 = []
        self.missed_packets1 = []
        self.attempt = 0
        self.time_reference = 0
        self.variation_time = 0
        self.savingbuffer = []

    def bufferlencheck (self):
    """ bufferlen recebe a quantidade de pacotes armazenados em receiver_buffer
    """
        bufferlen = 0
        if self.attempt == 0:
            bufferlen = int(len(self.receiver_buffer0)/self.step)
        elif self.attempt == 1:
            bufferlen = int(len(self.receiver_buffer1)/self.step)

        return bufferlen
    #end of bufferlencheck function

    def payloadAnalyser (self, pack):
    """ Parâmetros:
            pack: payload
        Possíveis retornos:
            0: o pacote recebido era o esperado
            1: houve perda de pacotes
            2: houve uma possível interferência
    """
        # O índice da imagem é o esperado
        if pack[1] == self.image_number:

            # O pacote esperado foi recebido
            if pack[0] == self.var:
                self.var += 1                       # var recebe o índice do próximo pacote a ser recebido
                return 0

            # Houve perdas de pacote em uma variação de tempo considerável
            elif pack[0] > self.var and self.variation_time > 500:
                if self.var == -1:
                    self.var = self.bufferlencheck()
                    return 2
                else:
                    self.missed_packets_number = pack[0] - self.var         # missed_packets_number recebe a quantidade de pacotes perdidos entre as recepções
                    self.var = pack[0] + 1
                    print("Missed %d packets"% self.missed_packets_number)
                    return 1

            # A imagem está sendo enviada pela segunda vez
            elif pack[0] < self.var:
                if pack[0] == -1:
                    return 2
                else:
                    self.attempt = 1
                    self.var = 0
                    if pack[0] == self.var:
                        self.var += 1
                        return 0
                    elif pack[0] > self.var:
                        self.missed_packets_number = pack[0] - self.var
                        self.var = pack[0] + 1
                        return 1

        elif self.variation_time < 2000:
            # Em uma pequena variação de tempo, foi lida uma grande diferença entre os valores esperados e os recebidos, ou seja, possivelmente houve interferência
            if pack[1] != self.image_number or (abs(self.var) - abs(pack[0])) > 10:
                self.variation_time = 0
                self.time_reference = 0
                return 2

        # Uma imagem diferente está sendo recebida
        elif pack[1] > self.image_number:
            self.image_number = pack[1]
            self.attempt = 0
            self.var = 0

            # O pacote recebido é o primeiro do envio
            if pack[0] == self.var:
                self.var += 1
                return 0

            # Houve perda de pacotes
            elif pack[0] > self.var:
                self.missed_packets_number = pack[0] - self.var
                self.var = pack[0] + 1
                return 1
    #end of payloadAnalyser function

    def incrementBuffer(self, missed_number, pack, rbuffer):
        """ A função salva o pacote em receiver_buffer
            Parametros:
                missed_number: quantia de pacotes perdidos
                pack: valores significativos de payload
                rbuffer: buffer em que o pacote será armazenado
        """
        if missed_number != 0:
            # Para cada pacote perdido, uma lista de 0 é concatenada ao buffer
            for i in xrange(0, missed_number):
                for j in xrange(0, self.step):
                    rbuffer.append(0)
                print("Packet blacked-out!")

        # buffer e payload são concatenados
        rbuffer += pack
    #end of incrementBuffer function

    def on_rx_done(self):
        # Get time of first packet received
        if self.first_packet == 1:
            self.first_packet = 0
            self.millis = int(round(time.time() * 1000))

        # Get the variaton of time between the current and the last received packet
        self.variation_time = abs(int(round(time.time() * 1000)) - self.time_reference)
        self.time_reference = int(round(time.time() * 1000))

        # Reset timeout
        self.recv = int(round(time.time() * 1000))

        BOARD.led_on()
        self.clear_irq_flags(RxDone=1)

        # payload is read
        payload = self.read_payload(nocheck=True)

        answer = self.payloadAnalyser(payload)

        #Reference info, could be commented
        print("----------------------------------------------")
        print("Packet Info:")
        print("    Image Number: %d    Packet Number: %d" %(payload[1], payload[0]))
        print("    Var:          %d    Attempt:       %d" %(self.var - 1, self.attempt))       #Here, self.var is subtracted because it was incremented into this function

        if self.missed_packets_number != 0:
            print("    Packets missed: %d" % self.missed_packets_number)

        if answer == 2:
            print("INTERFERENCE")   # O pacote é ignorado

        # Primeira recepção da imagem
        elif self.attempt == 0:
            if answer == 0:
                self.incrementBuffer(0, payload[2:], self.receiver_buffer0)

            elif answer == 1:
                self.incrementBuffer(self.missed_packets_number, payload[2:], self.receiver_buffer0)
                for i in xrange(payload[0] - self.missed_packets_number, payload[0]):
                    self.missed_packets0.append(i)
                print self.missed_packets0

        # Segunda recepção da imagem
        elif self.attempt == 1:
            if answer == 0:
               self.incrementBuffer(0, payload[2:], self.receiver_buffer1)

            elif answer == 1:
                self.incrementBuffer(self.missed_packets_number, payload[2:], self.receiver_buffer1)
                for i in xrange(payload[0] - self.missed_packets_number, payload[0]):
                    self.missed_packets1.append(i)
                print self.missed_packets1

        self.missed_packets_number = 0

        # LoRa stuff
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        BOARD.led_off()
        self.set_mode(MODE.RXCONT)

    #end of on_rx_done function

    def check_finished(self):
        # É verificado se o envio da imagem foi realizado completamente
        if int(round(time.time() * 1000)) - self.recv >= 3500 and self.first_packet == 0:
            self.image_test += 1
            return True
        else:
            return False

        #end of check_finished function

    def print_summary(self):
        # Informações sobre o envio são printadas
        print("")
        print("-----------  Sumary  -----------")
        print("")
        print "Total duration: %.2f seconds" % float((int(round(time.time() * 1000)) - self.millis)/1000)
        print "Total size of image: %d bytes" % int(sys.getsizeof(bytearray(self.savingbuffer)))
        print("")
        print("--------------------------------")
        print("")

        #end of print_summary function

    def save_image(self, savingindex):
        """ Os pacotes armazenados no buffer são lidos como um bytearray e salvos posteriormente
            Parâmetros:
                savindindex: índice indicando se os envios foram mesclados
        """
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        print("SAVE DA MLKADA")
        try:
            image = Image.open(io.BytesIO(bytearray(self.savingbuffer)))
            image.save("LivePicture.jpg")
            print("ENTROU NO SAVE MEMO")
            #Saving picture into another diretory
            temp_string = "cp LivePicture.jpg Images/" + str(self.image_number) + str(savingindex) +".jpg"
            os.system(temp_string)
        finally:
            print "Image saved!!"
        #end of save_image function

    def compare_buffer(self):
        """ A função verifica qual a tentativa de envio com menor perda de pacotes
            Possíveis retornos:
                00: tentativa 0 não perdeu pacotes
                10: tentativa 1 não perdeu pacotes
                01: tentativa 0 perdeu menos pacotes que 1
                11: tentativa 1 perdeu menos pacotes que 0
        """
        if len(self.missed_packets1) == 0:
            return 10

        elif len(self.missed_packets0) ==  0:
            return 00

        elif len(self.missed_packets0) < len(self.missed_packets1): # 1st attempt have more packets than 2nd attempt
            for i in set(self.missed_packets0).intersection(self.missed_packets1):
                    self.missed_packets0.remove(i)
            return 01

        else:
            for i in set(self.missed_packets1).intersection(self.missed_packets0):
                    self.missed_packets1.remove(i)
            return 11

        #end of compare_buffer function

    def merge_image(self, rbuffer, stbuffer, missednumbers):
        """ Os pacotes que faltam em um buffer são recebidos de outro.
            Parâmetros:
                rbuffer: buffer da tentativa de envio com menor perda de pacotes
                stbuffer: buffer da tentativa com maior perda
                missednumbers: lista com todos os índices dos pacotes que faltam em rbuffer
        """
        auxbuffer = []
        for i in missednumbers:
            mindex = i*self.step
            mindex2 = (i+1)*self.step
            rbuffer = rbuffer[:mindex] + stbuffer[mindex:mindex2] + rbuffer[mindex2:]

            print("Packet %d merged " %i)

            auxbuffer = rbuffer[:]

        self.savingbuffer = []
        self.savingbuffer = auxbuffer[:]

        #end of merge_image function

    def bufferAnalyser(self):
        # É analisado se é necessário mesclar as tentativas de envio para salvar a imagem
        answer = self.compare_buffer()

        if answer == 00:
            self.savingbuffer = self.receiver_buffer0[:]
            self.save_image(0)

        elif answer == 10:
            self.savingbuffer = self.receiver_buffer1[:]
            self.save_image(0)

        elif answer == 01:
            self.savingbuffer = self.receiver_buffer0[:]
            self.save_image(0)

            self.merge_image(self.receiver_buffer0, self.receiver_buffer1, self.missed_packets0)
            self.save_image(1)

        elif answer == 11:
            self.savingbuffer = self.receiver_buffer1[:]
            self.save_image(0)

            self.merge_image(self.receiver_buffer1, self.receiver_buffer0, self.missed_packets1)
            self.save_image(1)

        #end of bufferAnalyser function

    def start(self):

        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
    	print "Running!"
        while True:

            sleep(0.1)

            if self.check_finished():

                try:
                    self.bufferAnalyser()
                    self.print_sumary()
                except:
                    pass
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
