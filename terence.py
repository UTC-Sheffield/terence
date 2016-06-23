#!/usr/bin/env python

import cv2, sys, time, os
from pantilt import *
import pygame
from random import randrange
            
            
samples = [
    'sounds/UTC SHEFFIELD.wav',
    'sounds/good_evening.wav',
    'sounds/UTC SHEFFIELD.wav',
    'sounds/UTC SHEFFIELD.wav',
    'sounds/thud.wav',
    'sounds/clap.wav',
    'sounds/crash.wav',
    'sounds/hat.wav',
    'sounds/smash.wav',
    'sounds/rim.wav',
    'sounds/ting.wav'
]

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()
pygame.mixer.set_num_channels(16)

sounds = []
for x in range(8):
    sounds.append(pygame.mixer.Sound(samples[x]))
    
    

# Load the BCM V4l2 driver for /dev/video0
os.system('sudo modprobe bcm2835-v4l2')
# Set the framerate ( not sure this does anything! )
os.system('v4l2-ctl -p 4')

# Frame Size. Smaller is faster, but less accurate.
# Wide and short is better, since moving your head
# vertically is kinda hard!
FRAME_W = 180
FRAME_H = 100

# Default Pan/Tilt for the camera in degrees.
# Camera range is from 0 to 180
cam_pan = 70
cam_tilt = 70

# Set up the CascadeClassifier for face tracking
#cascPath = 'haarcascade_frontalface_default.xml' # sys.argv[1]
cascPath = '/usr/share/opencv/lbpcascades/lbpcascade_frontalface.xml'
faceCascade = cv2.CascadeClassifier(cascPath)

# Set up the capture with our frame size
video_capture = cv2.VideoCapture(0)
video_capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH,  FRAME_W)
video_capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, FRAME_H)
time.sleep(2)

# Turn the camera to the default position
pan(cam_pan)
tilt(cam_tilt)

lastSeen = time.time() - 30;
scanPan = 0
scanTilt = 0
scanPanSpeed = 1.5

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    if ret == False:
      print("Error getting image")
      continue

    # Convert to greyscale for detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist( gray )

    # Do face detection
    faces = faceCascade.detectMultiScale(frame, 1.1, 3, 0, (10, 10))
   
    # Slower method 
    '''faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(20, 20),
        flags=cv2.cv.CV_HAAR_SCALE_IMAGE | cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT | cv2.cv.CV_HAAR_DO_ROUGH_SEARCH
    )'''
    
    currentTime = time.time();
    for (x, y, w, h) in faces:
        #if its been more then 30 seconds since it saw some one say hi
        if(lastSeen +30 < currentTime):
            #print("Hi");
            #sounds[0].play(loops=0)
            random_index = randrange(0,4)
            sounds[random_index].play(loops=0) 
        elif(lastSeen +5 < currentTime):
            sounds[4].play(loops=0) 
		
        lastSeen = currentTime;
        # Draw a green rectangle around the face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Track first face
        
        # Get the center of the face
        x = x + (w/2)
        y = y + (h/2)

        # Correct relative to center of image
        turn_x  = float(x - (FRAME_W/2))
        turn_y  = float(y - (FRAME_H/2))

        # Convert to percentage offset
        turn_x  /= float(FRAME_W/2)
        turn_y  /= float(FRAME_H/2)

        # Scale offset to degrees
        turn_x   *= 2.5 # VFOV
        turn_y   *= 2.5 # HFOV
        cam_pan  += -turn_x
        cam_tilt += turn_y

        # Clamp Pan/Tilt to 0 to 180 degrees
        cam_pan = max(0,min(180,cam_pan))
        cam_tilt = max(0,min(180,cam_tilt))

        # Update the servos
        pan(cam_pan)
        tilt(cam_tilt)

        break
        
        
    if(currentTime > (lastSeen + 10 )):
        #titl back to sensible angle
        #print("scan");
        cam_pan  += scanPanSpeed
        if(cam_pan > 180 or cam_pan < 0):
            scanPanSpeed = scanPanSpeed * -1
            cam_pan += scanPanSpeed
            cam_tilt += 5
            if(cam_tilt> 90):
                cam_tilt = 40
            tilt(cam_tilt)
        pan(cam_pan)
            
    frame = cv2.resize(frame, (900,500))
    frame = cv2.flip(frame, 1)
   
    # Display the image, with rectangle
    # on the Pi desktop 
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
