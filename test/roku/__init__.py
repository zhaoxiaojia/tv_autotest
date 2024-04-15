# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/20 15:08
# @Author  : chao.li
# @File    : __init__.py.py
# @Project : kpi_test
# @Software: PyCharm

import logging
import os

from dut_control.roku_ctrl import RokuCtrl
from tool.dut_control.serial_ctrl import SerialCtrl
from tool.pil_tool import PilTool
from tool.yaml_tool import YamlTool
from tool.signal_generator.master_8100s import Master_8100s

odm = 'changhong'
mode_list = ['Low power', 'Vivid', 'Sports', 'Movie', 'Standard']
size_list = ['Direct', 'Normal', 'Stretch', 'Zoom', 'Auto']

skip_mode = False
skip_size = False
no_such_timming = True

roku_lux = YamlTool(os.getcwd() + f'/config/roku/roku_{odm}.yaml')
roku_env = YamlTool(os.getcwd() + '/config/roku/config.yaml')

hdmi = 'hdmi1'
if roku_env.get_note('pytest.pattern_generator') == 'master_8100s':
	...

roku_ctl = RokuCtrl()
# roku_ctl.ser.write('\x1A')
# roku_ctl.ser.write('bg')
pil = PilTool()
# roku_serial = serial_crt(roku_lux.get_note('serial_crt')['port'], roku_lux.get_note('serial_crt')['baud'])
