import socket
import os
import thread
import sys
import urllib
from dotstar import Adafruit_DotStar
import time
import random
from PIL import Image

HOST = '' #localhost address
PORT = 5005 #communication port

#LED STRIP SETUP

numpixels = 30 # Number of LEDs in strip

# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24
strip     = Adafruit_DotStar(numpixels, datapin, clockpin)

level = 64
strip.begin()           # Initialize pins for output
strip.setBrightness(level) # Limit brightness to ~1/4 duty cycle

#END LED STRIP SETUP


#GLOBAL VARIABLES AND STRINGS
bindSuccess = False
frameBufferCommand = "fbi -a -T 1 -d /dev/fb0 -noverbose  "
moviePosterLocation = "/home/pi/movieposters/"
openBlackImage = "/home/pi/movieposters/special/black.jpg"
killFrameBuffer = "sudo killall fbi"


#SOCKET STUFF
crestronSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Crestron Socket Created")

try:
    crestronSocket.bind((HOST, PORT))
    os.system(frameBufferCommand + openBlackImage)
    print("Socket Bind Completed")
    bindSuccess = True
    print("bindSuccess Variable State: " + str(bindSuccess))    
    
except socket.error as msg:
    os.system(killFrameBuffer)
    bindSuccess = False
    print("bindSuccess State: " + str(bindSuccess) + " --- " + "Bind failed. Error Code : " + str(msg[0]) + " Message " + msg[1])
    sys.exit()


#SOCKET STARTS LISTENING
crestronSocket.listen(2)
print("Crestron Socket Listening")

#DEFINE FUNCTIONS

def splitString(input):
    
    stringList = input.split("/x00/") 
    return stringList

def setStripColor(numpixels, red, green, blue):
    level = 64
    levelRGB = [red, green, blue]
    for i in range(numpixels):
        strip.setPixelColor(i, red, green, blue)
        print("Pixel #" + str(i) + " to " + str(levelRGB))
    strip.show()    

def genreColor(socketInput):
    
    
    level = 64
    
    if socketInput == "Action": 
        RedValue = 255
        GreenValue = 0
        BlueValue = 0
        movieColor = "Changing RGB Level to Red"
        
        setStripColor(numpixels, RedValue, GreenValue, BlueValue)
        
    elif socketInput == "Adventure":
        RedValue = 255
        GreenValue = 106
        BlueValue = 0
        movieColor = "Changing RGB Level to Orange"
        
        setStripColor(numpixels, RedValue, GreenValue, BlueValue)
        
    elif socketInput == "Animation":
        RedValue = 0
        GreenValue = 157
        BlueValue = 255
        movieColor = "Changing RGB Level to Blue"
        
        setStripColor(numpixels, RedValue, GreenValue, BlueValue)
            
    elif socketInput == "Fantasy":
        RedValue = 0
        GreenValue = 242
        BlueValue = 255
        movieColor = "Changing RGB Level to Teal"
        
        setStripColor(numpixels, RedValue, GreenValue, BlueValue)
            
    elif socketInput == "Science Fiction":
        RedValue = 0
        GreenValue = 255
        BlueValue = 0
        movieColor = "Changing RGB Level to Green"
        
        setStripColor(numpixels, RedValue, GreenValue, BlueValue)
            
    elif socketInput == "Horror":
        RedValue = 183
        GreenValue = 0
        BlueValue = 255
        movieColor = "Changing RGB Level to Purple"
        
        setStripColor(numpixels, RedValue, GreenValue, BlueValue)
                
    elif socketInput == "Thriller":
        RedValue = 140
        GreenValue = 0
        BlueValue = 255
        movieColor = "Changing RGB Level to Indigo"
        
        setStripColor(numpixels, RedValue, GreenValue, BlueValue)
            
    elif socketInput == "Comedy":
        RedValue = 246
        GreenValue = 255
        BlueValue = 0
        movieColor = "Changing RGB Level to Yellow"
        
        setStripColor(numpixels, RedValue, GreenValue, BlueValue)            
            
    else:
        RedValue = random.randint(0, 255)
        GreenValue = random.randint(0, 255)
        BlueValue = random.randint(0, 255)
        movieColor = "Changing RGB Level to Randomly Generated Color"
        
        setStripColor(numpixels, RedValue, GreenValue, BlueValue)
        
    return movieColor





def displayDownloadedPosters(dataInput):
    
    
    fileCount = next(os.walk(moviePosterLocation))[2] #get the number of available posters
    print('Current Posters in Directory: ' + str(len(fileCount))) 
    
    for index in enumerate(fileCount):
        
        image = Image.open(moviePosterLocation + index[1]) #open the current image
        
        width, height = image.size
        
        if width > height: 
            
            print("We Think This Not A Movie Poster (Width > Height) -- Skipping This Image")
        
        else:
        
            try:
                conn.send("Displaying Poster # " + str(index))
        
            except socket.error as msg:
                print(msg)
                break
                
            print("Displaying Poster # " + str(index[0]))
            os.system(frameBufferCommand + moviePosterLocation + index[1])
                
            time.sleep(60)


#MAIN THREADING FUNCTION

def clientthread(conn): #create new thread to handle clients
    try: 
        conn.send('Connected to Raspberry Pi')

    except socket.error as msg:
        print(msg)
    
    
    while bindSuccess == True: #socket bound successfully, do things based on input strings       
        
        crestronDataReceived = conn.recv(1024)
        reply = 'OK   '
        
        try:
            conn.sendall(reply + crestronDataReceived)
            
        except socket.error as msg:
            print(msg)
            break
            
            
        try: 
            crestronRXSplit = splitString(crestronDataReceived)
            
            if "x01" in crestronRXSplit[0]: # x01 as first byte - system is off /x01/x00/SOURCE/x00/RED/x00/GREEN/x00/BLUE/x00/GENRE/x00/THUMBNAIL
                print("System Is Off")#turn monitor output off
                try:
                    os.system(frameBufferCommand + openBlackImage)
                    os.system('sudo /opt/vc/bin/tvservice -o')
                except OSError as msg:
                    print('error occured')
                    
                
            elif "x02" in crestronRXSplit[0]: # x02 as first byte - system is on /x02/x00/SOURCE/x00/RED/x00/GREEN/x00/BLUE/x00/GENRE/x00/THUMBNAIL
                #turn monitor output on
                os.system('sudo /opt/vc/bin/tvservice -p')
                #add timeout start
                
                incomingData = splitString(crestronDataReceived)
                print(incomingData)
                
                if "x01" in incomingData[1]: #APPLETV                
                    os.system(frameBufferCommand + moviePosterLocation + 'special/appletv.jpg')
                    
                    try: 
                        appleRed = incomingData[2]
                        appleGreen = incomingData[3]
                        appleBlue = incomingData[4]
                        
                        levelRGB = [appleRed, appleGreen, appleBlue]
                        
                        try:
                            conn.send("Current LED State " + str(levelRGB))                         
                        
                        except socket.error as msg:
                            print(msg)
                            print("State Change Update Not Sent To" + addr[0])                            
                            break
                            
                        
                        print("Current LED State " + str(levelRGB))
                        setStripColor(numpixels, int(appleRed), int(appleGreen), int(appleBlue))                    
                        
                                             
                        
                    except IndexError as msg:
                        print("Missing an RGB Level Index")
                    
                                   
                    
                elif "x02" in incomingData[1]: #PS2
                    os.system(frameBufferCommand + moviePosterLocation + 'special/playstation.jpg')
                    edgeRGB = [51, 64, 189]
                    middleRGB = [0, 171, 169]
                    centerRGB = [255, 255, 255]
                    for i in range(0, 5):
                        print('Setting Left Edge - Pixel #' + str(i) + " to RGB Level" + str(edgeRGB))
                        strip.setPixelColor(i, edgeRGB[0], edgeRGB[1], edgeRGB[2]) #set left edge
                    for i in range(6, 11):
                        print('Setting Left Middle - Pixel #' + str(i) + " to RGB Level" + str(middleRGB))
                        strip.setPixelColor(i, middleRGB[0], middleRGB[1], middleRGB[2]) #set leftmiddle
                    for i in range(12, 17):
                        print('Setting Center - Pixel #' + str(i) + " to RGB Level" + str(centerRGB))
                        strip.setPixelColor(i, centerRGB[0], centerRGB[1], centerRGB[2]) #set center
                    for i in range(18, 23):
                        print('Setting Right Middle - Pixel #' + str(i) + " to RGB Level" + str(edgeRGB))
                        strip.setPixelColor(i, middleRGB[0], middleRGB[1], middleRGB[2]) #set rightmiddle
                    for i in range(24, 30):
                        print('Setting Right Edge - Pixel #' + str(i) + " to RGB Level" + str(edgeRGB))
                        strip.setPixelColor(i, edgeRGB[0], edgeRGB[1], edgeRGB[2]) #set right edge
                
                elif "x03" in incomingData[1]: #XBMC
                    print("Changing LED Strip Color Based On Genre")
                    
                    try: #try to assign movieGenre from incomingData[5]
                    
                        movieGenre = incomingData[5]
                    
                    except IndexError as msg: #error encountered
                        print("Genre Not Available!")
                                
                    print(movieGenre)
                
                    currentLEDStripColor = genreColor(movieGenre)
                
                    print(currentLEDStripColor + " Genre: " + movieGenre)
                
                    try: #try to notify crestron 
                        conn.send(currentLEDStripColor + " Genre: " + movieGenre)  
                
                    except socket.error as msg: #error encountered
                        print(msg)
                        break
                    
                
                    try:
                        conn.send("XBMC Movie Poster Downloading")
                        
                    except socket.error as msg:
                        print(msg)
                        break
                    
                    try:    
                        moviePosterURL = incomingData[6]
                    
                        splitPosterURL = moviePosterURL.split("%")
                    
                        moviePosterFilename = splitPosterURL[7]
                        
                        urllib.urlretrieve(moviePosterURL, moviePosterLocation + moviePosterFilename)
                        
                        print("Movie Poster saved as: " + moviePosterLocation + moviePosterFilename)
                    
                        try:
                            conn.send("Movie Poster saved as: " + moviePosterLocation + moviePosterFilename)
                    
                        except socket.error as msg:
                            print(msg)
                            break
                    
                        try:
                            os.system(frameBufferCommand + moviePosterLocation + moviePosterFilename)
                            print('Opening Downloaded Poster')
                    
                        except OSError as msg:
                            print(str(msg[0]) + str(msg[1]))
                        
                        
                    except IndexError as msg:
                        print("IncomingData[6] did not contain a Poster URL")
                        print("AND/OR splitPosterURL[7] did not contain a string")
                        print('Movie Not Playing - Poster Not Downloaded')
                        try:
                            conn.send('Movie Not Playing - Poster Not Downloaded')
                        
                        except socket.error as msg:
                            print(msg)
                            break
                        
                        displayDownloadedPosters(incomingData[1])                                                                                    
                                                                                                                        
                elif "x04" in incomingData[1]: #XBOX
                    os.system(frameBufferCommand + moviePosterLocation + 'special/xbox.jpg')
                    
                    redColor = 0
                    greenColor = 255
                    blueColor = 0
                    
                    setStripColor(numpixels, redColor, greenColor, blueColor)
                        
                    #print("Starting xBox LED Function")
                    #conn.send("xBox LED Function Started")                    
                    
                    #while True:
                            #for i in range(0, 255):                            
                                #if level < 255:
                                    #level += 1
                                    #strip.setBrightness(level)
                                    #print(level)
                                #else:
                                    #break
                    
                                #time.sleep(0.25)
                    
                            ##fade down
                            #for i in range(0, 255):                                                  
                                #level -= 1
                                #strip.setBrightness(level)
                                #print(level)                           
                        
                                #time.sleep(0.25)
                                                                        
                else: #source integer out of range
                    print(incomingData[1])
                    print("incomingData Integer Out Of Range")
                    try:
                        conn.send("Active Source Integer Out Of Range")
                    except socket.error as msg:
                        print(msg)
                        break
                    
            else: #no other strings formats matched
                print("Unrecognized String")
                
                try:
                    conn.send(" Unrecognized String")
                
                except socket.error as msg:
                    print(msg)
                    break
                    
                    
        except IndexError as msg:
            print("encountered an index error")
            
            
                        
            

    
#WAIT FOR ANOTHER CONNECTION

while 1:
    #wait to accept a connection - blocking call
    conn, addr = crestronSocket.accept()
    print('Connected with Client: ' + addr[0] + ':' + str(addr[1]))
        
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    thread.start_new_thread(clientthread ,(conn,))
        
crestronSocket.close()        