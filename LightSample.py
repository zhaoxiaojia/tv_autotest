# -*- coding: utf-8 -*-

import datetime
import time
import traceback
from collections import defaultdict

from Phidget22.Devices.LightSensor import *
from Phidget22.Devices.Log import *
from Phidget22.Devices.SoundSensor import *
from Phidget22.LogLevel import *
from Phidget22.Phidget import *

ch1 = LightSensor()
ch2 = SoundSensor()

ch1.openWaitForAttachment(3000)
ch2.openWaitForAttachment(3000)

def onAttach(self):
    print("Attached!")

def onDetach(self):
    print("Detached!")

# Get LightSensor data interval range
# minDataInterval1 = ch1.getMinDataInterval()
# maxDataInterval1 = ch1.getMaxDataInterval()
# print("LightSensor DataInterval Range: [ {} - {} ]".format(str(minDataInterval1), str(maxDataInterval1)))

# Get SoundSensor data interval range
# minDataInterval2 = ch2.getMinDataInterval()
# maxDataInterval2 = ch2.getMaxDataInterval()
# print("SoundSensor DataInterval Range: [ {} - {} ]".format(str(minDataInterval2), str(maxDataInterval2)))

# Set data interval
ch1.setDataInterval(125)
ch2.setDataInterval(100)

# Get data interval
dataInterval1 = ch1.getDataInterval()
print("LightSensor Current DataInterval: " + str(dataInterval1))
dataInterval2 = ch2.getDataInterval()
print("SounudSensor Current DataInterval: " + str(dataInterval2))


# Get illuminance range
minIlluminance = ch1.getMinIlluminance()
maxIlluminance = ch1.getMaxIlluminance()
print("Illuminance Support Range: [ {} - {} ]".format(str(minIlluminance), str(maxIlluminance)))

# Get illuminance change trigger range
# minIlluminanceChangeTrigger = ch1.getMinIlluminanceChangeTrigger()
# maxIlluminanceChangeTrigger = ch1.getMaxIlluminanceChangeTrigger()
# print("Illuminance Change Trigger Range: [ {} - {} ]".format(str(minIlluminanceChangeTrigger), str(maxIlluminanceChangeTrigger)))

# Set illuminance Change Trigger
ch1.setIlluminanceChangeTrigger(3.0)

# Get illuminance Change Trigger
illuminanceChangeTrigger = ch1.getIlluminanceChangeTrigger()
print("Illuminance Current Change Trigger: " + str(illuminanceChangeTrigger))

'''
When selecting a range, first decide how sensitive you want the microphone to be. 
Select a smaller range when you want more sensitivity from the microphone.
If a Saturation event occurrs, increase the range.
'''
ch2.setSPLRange(1)
SPLRange = ch2.getSPLRange()
print("SPLRange: {}. eg: 0x1: 102dB; 0x2: 82dB".format(str(SPLRange)))

# minSPLChangeTrigger = ch2.getMinSPLChangeTrigger()
# maxSPLChangeTrigger = ch2.getMaxSPLChangeTrigger()
# print("SPLChangeTriggerRange: [ {} - {} ]".format(str(minSPLChangeTrigger), str(maxSPLChangeTrigger)))

ch2.setSPLChangeTrigger(1.0)
SPLChangeTrigger = ch2.getSPLChangeTrigger()
print("SPLChangeTrigger: " + str(SPLChangeTrigger))

# noiseFloor = ch2.getNoiseFloor()
# print("NoiseFloor: " + str(noiseFloor))

# octaves = ch2.getOctaves()
# print("Octaves[7] - 4KHz:" + str(octaves[5]))


def onError(self, code, description):
    print("Code: " + ErrorEventCode.getName(code))
    print("Description: " + str(description))
    print("----------")

avGroup = defaultdict(list)

def onIlluminanceChange(self, illuminance):
    if illuminance > 3:
        # avGroup['video'].append(datetime.datetime.now())
        print("{} - Illuminance: {}".format(datetime.datetime.now(), str(illuminance)))
#
def onSPLChange(self, dB, dBA, dBC, octaves):
    # if abs(dB - octaves[7]) < 5:
    if dB:
        pass
        # avGroup['audio'].append(datetime.datetime.now())
        print("{} - DB: {}, {}, {}, Octaves: {}".format(datetime.datetime.now(), str(dB), str(dBA), str(dBC), str(octaves[7])))

# def avsyncHandler():
#     try:
#         # if len(avGroup['video']) == len(avGroup['audio']) and len(avGroup['audio']) > 0 and len(avGroup['video']) > 0:
#         if len(avGroup['video']) == 1 and len(avGroup['audio']) == 1:
#             print(avGroup)
#             diff = (avGroup['audio'][-1] - avGroup['video'][-1]).total_seconds() * 1000
#             print("diff: {}".format(diff))
#             if diff > 0:
#                 print('{} - video later than audio: -{}ms'.format(datetime.datetime.now(), abs(diff)))
#             else:
#                 print('{} - audio later than video: +{}ms'.format(datetime.datetime.now(), abs(diff)))
#     finally:
#         avGroup['video'] = []
#         avGroup['audio'] = []

# Register for event before calling open
ch1.setOnIlluminanceChangeHandler(onIlluminanceChange)
# ch2.setOnSPLChangeHandler(onSPLChange)

while True:
    # dB = ch2.getdB()
    # dBA = ch2.getdBA()
    # dBC = ch2.getdBC()
    # illu = ch1.getIlluminance()
    # if dB > 55:
    #     print("{}: dB, dBA, dBC: {}, {}, {}".format(datetime.datetime.now(), dB, dBA, dBC))
    # if illu > 20:
    #     print("{}: illuminance: {}".format(datetime.datetime.now(), illu))
    # avsyncHandler()
    time.sleep(0.1)
