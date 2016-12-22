#!/usr/bin/python

import os
import sys
import pygame
import time
import random
import csv
import requests
from collections import defaultdict
from cStringIO import StringIO
sys.path.append('/home/pi/r2_control/classes/')
from Adafruit_PWM_Servo_Driver import PWM

PS3_AXIS_LEFT_VERTICAL = 1
PS3_AXIS_LEFT_HORIZONTAL = 0

SERVO_DRIVE = 14
SERVO_STEER = 13

#PWM ranges
SERVO_FULL_CW = 100
SERVO_STOP = 400
SERVO_FULL_CCW = 800

baseurl = "http://localhost:5000/"
 
os.environ["SDL_VIDEODRIVER"] = "dummy"


pygame.display.init()
pygame.init()

size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
print "Framebuffer size: %d x %d" % (size[0], size[1])
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
screen.fill((0, 0, 0))        
pygame.display.update()
 
j = pygame.joystick.Joystick(0)
j.init()
buttons = j.get_numbuttons()

# Read in key combos from csv file
keys = defaultdict(list)
with open('keys.csv', mode='r') as infile:
   reader = csv.reader(infile)
   for row in reader:
      print "Row: %s | %s | %s" % (row[0], row[1], row[2])
      keys[row[0]].append(row[1])
      keys[row[0]].append(row[2])
#      keys.update({row[0]:row[1]})
#      keys[row[0]][0] = row[1]
#      keys[row[0]][1] = row[2]

keys.items()

def driveServo(channel, speed):
   #calculate PWM pulse (32 is the range between SERVO_STOP and SERVO_FULL)
   pulse = SERVO_STOP
   if speed != 0:
      pulse = (speed * 190) + SERVO_STOP

   #tell servo what to do
   pwm.setPWM(channel, 0, int(pulse))


print "Initialised... entering main loop..."

pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(50) # Set frequency to 60 Hz


# Main loop
while True:
   global previous
   events = pygame.event.get()
   for event in events:
      if event.type == pygame.JOYBUTTONDOWN:
         buf = StringIO()
         for i in range ( buttons ):
            button = j.get_button(i)
            buf.write(str(button))
         combo = buf.getvalue()
         print "Buttons pressed: %s" % combo
         try:
            print "Would run: %s" % keys[combo]
            newurl = baseurl + keys[combo][0]
            print "URL: %s" % newurl
            try:
               r = requests.get(newurl)
            except:
               print "No connection"
            print "Command done"
         except:
            print "No combo (pressed)"
         previous = combo 
      if event.type == pygame.JOYBUTTONUP:
         print "Buttons released: %s" % previous
         try:
            print "Would run: %s" % keys[previous][1]
            newurl = baseurl + keys[previous][1]
            print "URL: %s" % newurl
            try:
               r = requests.get(newurl)
            except:
               print "No connection"
            print "Command done"
         except:
            print "No combo (released)"
      if event.type == pygame.JOYAXISMOTION:
         if event.axis == PS3_AXIS_LEFT_VERTICAL:
            print "Value: %s" % event.value
            driveServo(SERVO_DRIVE, event.value)
         elif event.axis == PS3_AXIS_LEFT_HORIZONTAL:
            driveServo(SERVO_STEER, event.value)


