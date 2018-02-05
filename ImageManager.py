#Software for Zenith Aerospace Group.
#This software aim to help the LiveFeed project with the image division.

import os
import sys
from PIL import Image

class ImageManager () :
#{
    def __init__ (self, imageValues, blockValues, opMode):
    #{
        self.imageValues = imageValues[0], imageValues[1]
        self.blockValues = blockValues[0], blockValues[1]
        self.opMode = opMode
    #}

    def ImageAnalyzer (self):
    #{
    #opening mode:

        if self.opMode == "crop":
        #{
            self.image = Image.open("Image.jpg")
            self.imageSize = self.image.size
            self.blockSize = self.blockValues[0], self.blockValues[1]
        #}
        elif self.opMode == "construct":
        #{
            self.imageSize = self.imageValues[0], self.imageValues[1]
            self.blockSize = self.blockValues[0], self.blockValues[1]
            self.image = Image.new("RGB", self.imageSize, "rgb(0, 0, 0)")
        #}

    #parameterization:

        if self.imageSize[0] % self.blockSize[0] == 0:
        #{
            if self.imageSize[1] % self.blockSize[1] == 0:
            #{
                self.widthBlocks  = int(self.imageSize[0]/self.blockSize[0])
                self.heightBlocks = int(self.imageSize[1]/self.blockSize[1])
                self.numberBlocks = self.widthBlocks*self.heightBlocks

                print("Possible block dimensions.")
                print("Image size: %d x %d"  % (self.imageSize[0], self.imageSize[1]))
                print("Block size: %d x %d"  % (self.blockSize[0], self.blockSize[1]))
                print("Number of blocks: %d" % self.numberBlocks)
                return 1 #possible division or construction
            #}
            else:
            #{
                print("Impossible block dimensions.")
                return 0 #possible division or construction
            #}
        #}
        else:
        #{
            print("Impossible block dimensions.")
            return 0 #impossible division or construction
        #}
    #} enf of the ImageAnalyzer function

    def ImageConstructor (self):
    #{
        for i in range(self.heightBlocks):
        #{
            for j in range(self.widthBlocks):
            #{
                k = i*self.widthBlocks + j + 1
                try:
                #{
                    print("Painting block %d ... " % k)
                    line = str(i)
                    column = str(j)
                    filename = line + '_' + column + '.jpg'
                    picture = Image.open(filename)
                    self.image.paste(picture, ( j*self.blockSize[0], i*self.blockSize[1], (j+1)*self.blockSize[0], (i+1)*self.blockSize[1]))
                    picture.close()
                #}
                except IOError:
                #{
                    print("Block %d was missed..." %k)
                #}
            #}
        #}
        self.image.save("newImage.jpg")
    #} end of the ImageConstructor function

    def ImageCropper (self):
    #{
        print("Image crop process starting...")
        for i in range(self.heightBlocks):
        #{
            for j in range(self.widthBlocks):
            #{
                k = i*self.widthBlocks + j + 1
                print("We are on block %d, line %d and column %d" % (k, i, j))
                picture = self.image.crop(  ( j*self.blockSize[0]  ,  i*self.blockSize[1]  ,  (j+1)*self.blockSize[0]  ,  (i+1)*self.blockSize[1] )  )
                line = str(i)
                column = str(j)
                filename = line + '_' + column + '.jpg'
                picture.save(filename)
                del picture
            #}
        #}
    #} end of the ImageCropper function

    def ImageMain (self):
    #{
        x = self.ImageAnalyzer()
        if x == 1:
        #{
            if self.opMode == "crop":
            #{
                self.ImageCropper()
            #}
            if self.opMode == "construct":
            #{
                self.ImageConstructor()
            #}
            self.image.close()
        #}
        elif x == 0:
        #{
            print("Invalid parameters")
        #}
    #} end of the ImageMain function
#} end of ImageManager class


#just for test
pic = 600,400
block = 30,20
op = "crop" #or "construct"
photo = ImageManager(pic,block,op)
photo.ImageMain()
