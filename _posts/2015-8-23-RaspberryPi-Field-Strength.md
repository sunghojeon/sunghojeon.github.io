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
#--- Sungho JEON --- 2014/12/23  2015/03/16    2015/04/23
# Sensor Networks Example Raspberry Pi ThingSpeak Cloud Storage

import os

from rtlsdr import * # ADC USB 기기 불러옴

from gps import * # USB GPS 기기 불러옴
import threading

import time
from datetime import datetime

import sys
import httplib, urllib

import numpy as np
import math

###############################################################################

gpsd = None #seting the global variable

###############################################################################

class GpsPoller(threading.Thread): #GPS 연동을 위한 부분
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true

  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

###############################################################################

def record_samples_to_ThingSpeak(input1): #측정 데이터를 서버에 업로드 하는 부분

    print "Uploading to ThingSpeak ..."

    # use your API key generated in the thingspeak channels for the value of 'key'
    params = urllib.urlencode({'field1': input1, 'field2': sdr.center_freq, 'field3': gpsd.fix.latitude, 'field4': gpsd.fix.longitude, 'field5': gpsd.fix.altitude, 'key':'0D1VWX5IXVK7OKB0'})

    # temp is the data you will be sending to the thingspeak channel for plotting the graph.
    # You can add more than one channel and plot more graphs
    headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")
    try:
        conn.request("POST", "/update", params, headers)
        response = conn.getresponse()
        print response.status, response.reason
        data = response.read()
        conn.close()
        print "done."
    except:
        print "connection failed"

###############################################################################

def get_inband_level_std(): #수신전계레벨[dBm], 대역내주파수응답 표준편차

    num_of_time_samples = pow(2,17)
    fft_size = pow(2,8)

    # initialize the variables
    AvgInbandLevel = 0.
    ChannelStdDev = 0.
    Pxx = np.zeros((Nfft,1),dtype=float)

    freq_center = sdr.center_freq

    # Lower Side Band (LSB) sample
    sdr.reset_buffer()
    sdr.center_freq = freq_center - sdr.sample_rate/2 - 0.005e6
    samples_time1 = sdr.read_samples(num_of_time_samples)*pow(10,-sdr.gain/20)

    # Upper Side Band (USB) sample
    sdr.reset_buffer()
    sdr.center_freq = freq_center + sdr.sample_rate/2 + 0.005e6
    samples_time2 = sdr.read_samples(num_of_time_samples)*pow(10,-sdr.gain/20)

    #========= Received Field Strength in dBm
    samples_time = np.concatenate((samples_time1,samples_time2),axis=0)
    AvgInbandLevel = 10*np.log10(pow(abs(samples_time),2).mean(axis=0))

    #========= In-band fluctuation in dtandard deviation
    # calculating the averaged in-band fluctuation
    samples_freq1 = np.fft.fft(samples_time1,fft_size)/fft_size
    samples_freq2 = np.fft.fft(samples_time2,fft_size)/fft_size
    samples_freq = np.concatenate((samples_freq1,samples_freq2),axis=0)

    # Power Spectral Density over frequency
    Pxx = 20*np.log10(abs(samples_freq))

    # calculating the in-band fluctuation in terms of stadnard deviation [dB]
#    WindowsSize = 5
#    Pxx = np.convolve( Pxx, np.ones((WindowsSize,),)/WindowsSize, mode='valid')
#    Pxx = Pxx[ WindowsSize: , ]
#    Pxx = Pxx[ -WindowsSize: , ]
    ChannelStdDev = Pxx.std(axis=0)

    del Pxx

    return AvgInbandLevel, ChannelStdDev

###############################################################################

def main():

    print "Start!!"

    measuredata = open("Lab201_151123_dipole_707MHz.csv", 'a')

    global sdr
    sdr = RtlSdr()
    sdr.sample_rate = 2.800e6   # in MHz, reliably sampling at a rate up to 2.8 MHz

    sdr.gain = 40.   # in dB, gain of RF amplifier at the receiver front-end

    sdr.center_freq = 701.000e6   # DVB-T2 center frequency [Hz] 701. MBC
#    sdr.center_freq = 707.000e6   # DVB-T2 center frequency [Hz] 707. SBS
#    sdr.center_freq = 761.000e6   # DVB-T2 center frequency [Hz] 761. KBS

    while True:

        AvgInbandLevel,ChannelStdDev = get_inband_level_std()
        record_samples_to_ThingSpeak(AvgInbandLevel,ChannelStdDev)

        print datetime.today(), AvgInbandLevel, ChannelStdDev, sdr.center_freq/1.0e6, sdr.gain
        print "..................", gpsd.fix.latitude, gpsd.fix.longitude, gpsd.fix.altitude

        # write_samples into txt file
        measuredata.write(datetime.today().strftime("%Y%m%d%H%M%S, \t"))
        measuredata.write("%f, \t" % AvgInbandLevel)
        measuredata.write("%f, \t" % sdr.center_freq)
        measuredata.write("%f, \t" % sdr.gain)
        measuredata.write("%f, \t" % gpsd.fix.latitude)
        measuredata.write("%f, \t" % gpsd.fix.longitude)
        measuredata.write("%f, \t" % gpsd.fix.altitude)
        measuredata.write("\n")

    sdr.close()
    measuredata.close()

if __name__ == '__main__':

    gpsp = GpsPoller()

    try:
         gpsp.start() # start it up

         args = sys.argv[1:]
         main(*args)
    except IOError:
         KeyboardInterrupt
    finally:
         main(*args)

# Usage 

## Monitoring

* [Public channel at ThingSpeak](http://thingspeak.com/channels/35203)
