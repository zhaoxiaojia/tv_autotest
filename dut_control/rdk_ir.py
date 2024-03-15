# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/14 11:20
# @Author  : chao.li
# @File    : rdkIr.py
# @Project : kpi_test
# @Software: PyCharm

import logging
import os
import time

import pytest

from dut_control.ir import Ir
from tool.yaml_tool import YamlTool

rdk_lux = YamlTool(os.getcwd() + '/config/rdk/rdk.yaml')


class RdkIr(Ir):

    def __init__(self):
        super(RdkIr, self).__init__()
        self.ir = pytest.irsend
        self.default_inputs = ['Home', 'Last used input', 'Antenna', 'HDMI 1', 'HDMI 2 (ARC)', 'HDMI 3', 'Composite']
        self.inputs = ['HDMI1', 'HDMI2', 'HDMI3', 'Composite', 'Antenna']
        self.apps = ['netflix', 'youtube', 'disney', 'peacock', 'primevideo', 'hulu']
        self.settings = ['Network', 'Picture and sound', 'Accessibility', 'Language', 'Privacy', 'Parrental controls',
                         'Content preferences', 'Apps and subscriptions', 'Device settings', 'Antenna and inputs',
                         'Airplay and HomeKit', 'Remote', 'Screen saver', 'Help', 'Developer', 'Notices']
        self.ir_name = 'rdk'

    def home(self):
        logging.info('goto home')
        self.send('home')
        pytest.light_sensor.count_kpi(0, rdk_lux.get_note('launcher_50_40')[pytest.panel])
        time.sleep(3)

    def antenna_scan(self):
        '''
        launcher -> setting -> Antenna and input -> Antenna
        :return:
        '''
        logging.info('goto scan')
        self.home()
        self.send('setting')
        time.sleep(2)
        for i in range(12):
            self.send('down')
            time.sleep(1)
        self.send('enter')
        time.sleep(1)
        for i in range(4):
            self.send('down')
            time.sleep(1)
        self.send('enter')
        time.sleep(1)
        self.send('enter')

    def enter_antenna(self):
        logging.info('goto Antenna')
        self.home()
        self.send("down")
        time.sleep(1)
        for _ in range(4):
            self.send('right')
            time.sleep(1)
        self.send('enter')
        return pytest.light_sensor.count_kpi(0, {'do': 0, 'ao': [0, 300]})

    def app(self, app_name):
        logging.info(f'goto {app_name}')
        if app_name not in self.apps:
            raise ValueError(f"Doesn't support this app {app_name}")
        step_list = {i: self.apps.index(i) for i in self.apps}
        self.home()
        for _ in range(2):
            self.send('down')
            time.sleep(1)
        self.send('right')
        time.sleep(1)
        for _ in range(step_list[app_name]):
            self.send('right')
            time.sleep(1)

    def antenna_and_input(self):
        logging.info('goto antenna and input')
        self.enter_settings('Antenna and inputs')
        self.send('enter')
        time.sleep(2)

    def enter_settings(self, setting):
        logging.info(f'goto {setting}')
        if setting not in self.settings:
            raise ValueError(f"Doesn't support this setting {setting}")
        self.send('setting')
        pytest.light_sensor.count_kpi(2, {'do': 0, 'ao': [0, 450]}, hold_times=10)
        time.sleep(1)
        for _ in range(2):
            self.send('down')
            time.sleep(1)
        step_list = {i: self.settings.index(i) for i in self.settings}
        for _ in range(step_list[setting] + 1):
            self.send('down')
            time.sleep(1)

    def default_input(self, input):
        logging.info('goto default input setting')
        if input not in self.default_inputs:
            raise ValueError(f"Doesn't support this input {input}")
        step_list = {i: self.default_inputs.index(i) for i in self.default_inputs}
        self.antenna_and_input()
        for _ in range(7):
            self.send('down')
            time.sleep(1)
        self.send('enter')
        time.sleep(1)
        for _ in range(step_list[input]):
            self.send('down')
            time.sleep(1)
        self.send('enter')
        time.sleep(1)

    def enter_input(self, input):
        logging.info(f'goto {input}')
        if input not in self.inputs:
            raise ValueError(f"Doesn't support this input {input}")
        self.antenna_and_input()
        step_list = {i: self.inputs.index(i) for i in self.inputs}
        for _ in range(step_list[input]):
            self.send('down')
            time.sleep(1)
        self.send('enter')
        time.sleep(1)

    def shutdown(self):
        count = 0
        while pytest.light_sensor.check_backlight():
            # shut down the dut before test
            self.send('power')
            time.sleep(10)
            if count > 5:
                raise EnvironmentError("Pls check ir control")

    def wakeup(self):
        count = 0
        while not pytest.light_sensor.check_backlight():
            # wake upthe dut before test
            self.send('power')
            time.sleep(10)
            if count > 5:
                raise EnvironmentError("Pls check ir control")
