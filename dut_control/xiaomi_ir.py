# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/18 10:25
# @Author  : chao.li
# @File    : xiaomiIr.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import os
import re
import time

import pytest

from dut_control.ir import Ir
from tool.yaml_tool import YamlTool

xiaomi_lux = YamlTool(os.getcwd() + '/config/xiaomi/xiaomi.yaml')


class XiaomiIr(Ir):

    def __init__(self):
        super(XiaomiIr, self).__init__()
        self.default_inputs = ['Home', 'Last Input']
        self.inputs = ['HDMI1', 'HDMI2', 'HDMI3', 'Composite', 'Antenna']
        self.apps = ['netflix', 'youtube', 'disney', 'peacock', 'primevideo', 'hulu']
        self.settings = ['Switch Profile', 'Channel Guide', 'Inputs', 'Display Mirroring', 'Apps', 'Sleep Timer',
                         'Picture', 'Sound']

    def home(self):
        logging.info('goto home')
        self.send('home')
        pytest.light_sensor.count_kpi(0, xiaomi_lux.get_note('launcher_50_40')[pytest.panel])
        time.sleep(3)
        self.send('back')

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
        pytest.light_sensor.count_kpi(2, {'do': 1, 'ao': [500, 550]})
        time.sleep(1)
        for _ in range(2):
            self.send('down')
            time.sleep(1)
        step_list = {i: self.settings.index(i) for i in self.settings}
        for _ in range(step_list[setting] + 1):
            self.send('down')
            time.sleep(1)

    def launcher_settings(self):
        self.home()
        pytest.executer.wait_and_tap('com.amazon.tv.launcher:id/nav_bar_settings', 'resource-id')
        self.send('up')
        time.sleep(1)
        pytest.executer.wait_and_tap('com.amazon.tv.launcher:id/nav_bar_settings', 'resource-id')
        # self.send('enter')
        time.sleep(1)

    def default_input(self, input):
        logging.info('goto default input setting')
        if input not in self.default_inputs:
            raise ValueError(f"Doesn't support this default input {input}")
        self.launcher_settings()
        pytest.executer.wait_and_tap('Display & Sounds', 'text')
        pytest.executer.wait_and_tap('Power Controls', 'text')
        pytest.executer.wait_and_tap('Power On', 'text')
        pytest.executer.wait_and_tap(input, 'text')

    def enter_input(self, input):
        logging.info(f'goto {input}')
        if input not in self.inputs:
            raise ValueError(f"Doesn't support this input {input}")
        self.home()
        pytest.executer.wait_and_tap("com.amazon.tv.launcher:id/nav_bar_inputs_text_icon", "resource-id")
        pytest.executer.wait_element("HDMI1", 'content-desc')
        pytest.executer.uiautomator_dump()
        self.inputs = re.findall(
            r'resource-id="" class="android.widget\.ImageView" package="com\.amazon\.tv\.launcher" content-desc="(\w+?)"',
            pytest.executer.get_dump_info())
        logging.info(f'self.inputs {self.inputs}')
        step_list = {i: self.inputs.index(i) for i in self.inputs}
        self.send('down')
        time.sleep(1)
        for _ in range(step_list[input]):
            self.send('right')
            time.sleep(1)

    def switch_input(self, input):
        logging.info(f'Switch {input}')
        if input not in self.inputs:
            raise ValueError(f"Doesn't support this input {input}")
        self.send('setting', wait_time=1)
        pytest.light_sensor.count_kpi(2, {'do': 0, 'ao': [300, 650]})
        self.send('down', wait_time=1)
        self.send('down', wait_time=1)
        self.send('enter', wait_time=1)
        pytest.executer.uiautomator_dump()
        inputs = re.findall(r'text="(\w+)" resource-id="com.amazon.tv.quicksettings.ui:id/button_one_line_title"',
                            pytest.executer.get_dump_info(), re.S)
        logging.info(f'self.inputs {inputs}')
        step_list = {i: inputs.index(i) for i in inputs}
        for _ in range(step_list[input]):
            self.send('down', wait_time=1)
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
            # shut down the dut before test
            self.send('power')
            time.sleep(10)
            if count > 5:
                raise EnvironmentError("Pls check ir control")
