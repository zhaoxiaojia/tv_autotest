# encoding:utf-8
import os
import time

import RPi.GPIO as GPIO
import smbus

pin_1=22
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
ADC=smbus.SMBus(1)

try:
    # os.system('irsend SEND_ONCE rdk power')
    start = time.time()
    while True:
        status_1 = GPIO.input(pin_1)
        #ADC.write_byte(0x24,0x10)
        val1=ADC.read_word_data(0x24,0x10)
        # val2=ADC.read_word_data(0x24,0x11)
        print(f'val1 {val1} ')
        # print(f"status {status_1}")
        #time.sleep(0.01)
        # if val1 < 1000:
        #     print(f"wa 好黑 {val1}")
        # else:
        #     print(f"哇 好亮 {val1}")
        #     print(time.time()-start)
        #     break
except Exception as e:
    print(e)
    GPIO.cleanup()

