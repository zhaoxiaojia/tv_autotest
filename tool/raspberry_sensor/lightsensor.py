# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/30 10:22
# @Author  : chao.li
# @File    : lightsensor.py
# @Project : kpi_test
# @Software: PyCharm
import logging
import subprocess
import time

from tool.lightsensor.gpio import Gpio
from tool.lightsensor.smbus import Smbus


class LightSensor:

    def __init__(self):
        if not self.raspberry_model():
            self.do = Gpio()
        self.ao = Smbus()

    def cleanup(self):
        if not self.raspberry_model():
            self.do.cleanup()

    def raspberry_model(self):
        '''
        return  true if Raspberry Pi 5
        :return:
        '''
        if 'Raspberry Pi 5' in subprocess.check_output('cat /proc/cpuinfo |grep Model', shell=True).decode():
            return True

    def check_backlight(self):
        '''
        check that the screen backlight is lit
        :return: true if light, false if not light
        '''
        logging.info(f'backlight {self.ao.get_ao(0)}')
        return self.ao.get_ao(0) < 950

    def count_kpi(self, sensor, target={}, inflection_point=[], hold_times=5, time_out=30, sleep_time=0.05):
        def get_data():
            nonlocal do, ao
            do = self.do.get_do(sensor) if not self.raspberry_model() else 1
            ao = self.ao.get_ao(sensor)
            if len(ao_temp) < hold_times:
                ao_temp.append(ao)
                do_temp.append(do)
            else:
                ao_temp.pop(0)
                do_temp.pop(0)
                ao_temp.append(ao)
                do_temp.append(do)
            if sleep_time:
                time.sleep(sleep_time)

        start = time.time()
        target_do = target['do']
        target_ao = target['ao'] if target['ao'] else []
        if len(target_ao) == 1:
            target_ao = [target_ao[0] - 15, target_ao[0] + 15]
        logging.info(f'target do {target_do} ao {target_ao}')
        logging.info(f'inflection_point {inflection_point}')
        ao_temp, do_temp = [], []
        count_temp = 0
        ao, do = '', ''
        inflection_flag = False
        while time.time() - start < time_out:
            count_temp += 1
            if inflection_point and not inflection_flag:
                # make sure ao data changes are within expectations
                logging.info(inflection_point)
                for i in inflection_point:
                    get_data()
                    if type(i) == int:
                        inflection_target = [j for j in range(i - 15, i + 15)]
                    elif type(i) == list:
                        inflection_target = [j for j in range(*i)]
                    while not int(sum(ao_temp) / len(ao_temp)) in inflection_target:
                        get_data()
                        logging.info("inflection do:{do} ao:{ao}".format(do={1: 'dark', 0: 'light'}[do], ao=ao))
                        if time.time() - start > time_out:
                            logging.warning(f"Can't catch the inflection data {inflection_target}")
                            return 0
                        continue
                    inflection_flag = True
                    logging.info(f'in inflection {ao_temp}')
                logging.info("Catch inflection done")
            else:
                get_data()
            if count_temp % 10 == 0:
                logging.info("do:{do} ao:{ao}".format(do={1: 'dark', 0: 'light'}[do], ao=ao))
            if target_do != 2 and not self.raspberry_model():
                do_compare = len(do_temp) == hold_times and sum(do_temp) == hold_times * target_do
            else:
                do_compare = True
            # logging.info(f'do_compare {do_compare}')

            if target_ao:
                ao_compare = int(sum(ao_temp) / len(ao_temp)) in [i for i in range(*target_ao)]
            else:
                ao_compare = True
            if do_compare and ao_compare:
                logging.info(f'ao_temp {ao_temp}')
                return round(time.time() - start, 3)
        else:
            logging.warning("Can't catch the target data")
            return 0
