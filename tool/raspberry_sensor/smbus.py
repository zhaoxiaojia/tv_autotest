# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/12 15:02
# @Author  : Chao.li
# @File    : smbus.py
# @Project : kpi_test
# @Software: PyCharm



from smbus2 import SMBus

import pytest
import logging

class smbus:
    def __init__(self,ao_list:list=[]):
        self.addr = pytest.config_yaml.get_note("sensor_board_addr")
        self.bus = SMBus(1)
        if not ao_list:
            # if not specified, the configuration file is read
            self.ao_list = []
            for i in pytest.config_yaml.get_note("light_sensitive_sensor"):
                for v in i.values():
                    if v['status'] == 'enable':
                        self.ao_list.append(v['ao'])
        for i in self.ao_list:
            logging.info(f'ao_{self.ao_list.index(i)} , {i}')
            setattr(self, f'ao_{self.ao_list.index(i)}',i)

    def get_ao(self,num:int=0):
        if type(num) != int:
            num = int(num)
        if not num:
            ...
        data = self.bus.read_word_data(self.addr,getattr(self,f'ao_{num}'))
        return data

    def check_backlight(self):
        '''
        check that the screen backlight is lit
        :return: true if light, false if not light
        '''
        logging.info(f'backlight {self.get_ao(0)}')
        return self.get_ao(0) < 950