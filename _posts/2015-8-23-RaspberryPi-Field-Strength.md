---
layout: post
title: Raspberry Pi based RTL-SDR Input Level and In-Band Fluctuation Measurement Tool
---

# Overview

* 고가의 장비를 시간율 측정을 위해서 장시간 운용하는 데서 오는 부담과 공간율 측정을 위해서 다수 위치에 설치해야 하는 비용적 부담을 해결하기 위해서, Raspberry Pi를 활용하여 Low-Cost Measurement Tool을 개발하는 데 그 목적이 있음.  
* 임의의 주파수 대역의 신호를 수신하여 Input Level을 측정
* In-Band Fluctuation을 판단하는 지표로써 ITU-R BT.0000에서의 정의하고 있는 Standard Deviation 값 측정


# Hardware

* [Raspberry Pi Model B+](https://www.raspberrypi.org/products/model-b-plus/)
* [Software Defined Radio Receiver USB Stick - RTL2832 w/R820T](https://www.adafruit.com/product/1497)
* [MCX Jack to SMA RF Cable Adapter](https://www.adafruit.com/products/1532)

# Installation 



# Implementation

```python
import time, random, os
import RPi.GPIO as io
from neopixel import *
DATA_PIN = 18 # pin connected to the NeoPixels
NUM_PIXELS = 240 # number of LEDs 240 LEDs in 4 meters
try :
io.setmode(io.BCM)
io.setwarnings(False)
except :
print"start IDLE with 'gksudo idle' from command line"
os._exit(1)
pixels = Adafruit_NeoPixel(NUM_PIXELS,DATA_PIN,800000,5,False)
bat1pin = 3
bat2pin = 2
bat1 = bat2 = 1
serve = False
ballDir = True
toServe = 0 # player to serve next
slugLength = 5
hitPoint1 = hitPoint2 = -1
lastTime = time.time()
interval = 0.1 # delay between frames
insertPlace = 0
slugCol = 5
red = [ 204, 0, 255, 255, 255, 255]
green = [ 102, 255, 0, 0, 153, 225]
blue = [ 0, 255, 255, 0, 153, 0]
ballSpeed = [ 0.005, 0.01, 0.015, 0.020, 0.025, 0.03 ]
def main() :
global lastTime, interval, ballDir, insertPlace, serve
global slugLength, hitPoint1,hitPoint2,slugCol
init()
while(True):
checkBat1()
checkBat2()
# advance the ball
if ((time.time() - lastTime) > interval) & serve:
lastTime = time.time()
if(ballDir) :
insertPlace += 1
else :
insertPlace -= 1
if (insertPlace + slugLength) < 0 : # hit the player 1 end
insertPlace = -slugLength
ballDir = not ballDir
hitPoint2 = -1 # clear the other players hit position
if hitPoint1 == -1 or hitPoint1 > slugLength : # failed or too early
endRally(0) # tidy up an wait for serve
else :
slugCol = hitPoint1 # change colour for next rally
interval = ballSpeed[slugCol]
if insertPlace > NUM_PIXELS : # hit the player 2 end
insertPlace = NUM_PIXELS-1
ballDir = not ballDir
hitPoint1 = -1 # clear other players hit position
if hitPoint2 == -1 or (NUM_PIXELS -1 - hitPoint2) > slugLength :
# failed to hit or too early
endRally(1) # tidy up an wait for serve
else :
slugCol = NUM_PIXELS -1 - hitPoint2 # change colour for next rally
interval = ballSpeed[slugCol]
if serve :
place(insertPlace) # don’t update if we have just missed the ball
```



```matlab
%% notation
def x
x = 0
x = 2 + 2
what is x
```

# Usage 

## Monitoring

* [Public channel at ThingSpeak](http://thingspeak.com/channels/35203)
