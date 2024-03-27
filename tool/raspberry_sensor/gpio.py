# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/12 10:48
# @Author  : Chao.li
# @File    : gpio.py
# @Project : kpi_test
# @Software: PyCharm
import logging
import time

import pytest
import RPi.GPIO as GPIO


class gpio:

    def callback(self, prefix, name, *args):
        method = getattr(self, prefix + name, None)
        if callable(method):
            return method(*args)
        else:
            logging.info("No such func")

    def get_do(self, num: int = 0):
        if type(num) != int:
            num = int(num)
        if not num:
            ...
        return GPIO.input(getattr(self, f'gpio_{num}'))

    def __init__(self, do_list: list = []):
        if not do_list:
            # if not specified, the configuration file is read
            self.do_list = []
            for i in pytest.config_yaml.get_note("light_sensitive_sensor"):
                for v in i.values():
                    if v['status'] == 'enable':
                        self.do_list.append(v['do'])
        # set BCM mode
        GPIO.setmode(GPIO.BCM)
        # set gpio mode into write
        GPIO.setup(self.do_list, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        for i in self.do_list:
            logging.info(f'gpio_{self.do_list.index(i)} , {i}')
            setattr(self, f'gpio_{self.do_list.index(i)}', i)

    def count_kpi(self, sensor, target={}, inflection_point=[], hold_times=5, time_out=30, sleep_time=0.05):
        def get_ao():
            nonlocal do, ao
            do = pytest.gpio.get_do(sensor)
            ao = pytest.smbus.get_ao(sensor)
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
        target_ao = target['ao']
        if len(target['ao']) == 1:
            target_ao = [target['ao'][0] - 15, target['ao'][0] + 15]
        else:
            target_ao = target['ao']
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
                    get_ao()
                    if type(i) == int:
                        inflection_target = [j for j in range(i - 15, i + 15)]
                    elif type(i) == list:
                        inflection_target = [j for j in range(*i)]
                    while not int(sum(ao_temp) / len(ao_temp)) in inflection_target:
                        get_ao()
                        logging.info("inflection do:{do} ao:{ao}".format(do={1: 'dark', 0: 'light'}[do], ao=ao))
                        if time.time() - start > time_out:
                            logging.warning(f"Can't catch the inflection data {inflection_target}")
                            return 0
                        continue
                    inflection_flag = True
                    logging.info(f'in inflection {ao_temp}')
                logging.info("Catch inflection done")
            else:
                get_ao()
            if count_temp % 10 == 0:
                logging.info("do:{do} ao:{ao}".format(do={1: 'dark', 0: 'light'}[do], ao=ao))
            if target_do != 2:
                do_compare = len(do_temp) == hold_times and sum(do_temp) == hold_times * target_do
            else:
                do_compare = True
            ao_compare = int(sum(ao_temp) / len(ao_temp)) in [i for i in range(*target_ao)]
            if do_compare and ao_compare:
                logging.info(f'ao_temp {ao_temp}')
                return round(time.time() - start, 3)
        else:
            logging.warning("Can't catch the target data")
            return 0

    def cleanup(self):
        GPIO.cleanup()
