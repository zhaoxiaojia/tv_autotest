# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/20 15:08
# @Author  : chao.li
# @File    : __init__.py.py
# @Project : kpi_test
# @Software: PyCharm

import logging
import os

import pytest

from command.roku.roku_command import RokuCommand
from dut_control.roku_ctrl import RokuCtrl
from tool.dut_control.serial_ctrl import SerialCtrl
from tool.pil_tool import PilTool
from tool.signal_generator.master_8100s import Master_8100s
from tool.yaml_tool import YamlTool
import time
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
command = RokuCommand()
pytest.executer.execute_cmd('echo 6 > /proc/sys/kernel/printk')

info = pytest.executer.checkoutput('[ -e /nvram/debug_overlay/etc/autostart ] && echo "yes" || echo "no"')
logging.info(f'check info {info}')
pytest.executer.execute_cmd('mkdir -p /nvram/debug_overlay/etc')
pytest.executer.execute_cmd('cp /media/ext1\:/roku_usb/autostart /nvram/debug_overlay/etc')
# roku_ctl.ser.write('\x1A')
# roku_ctl.ser.write('bg')
pil = PilTool()
# roku_serial = serial_crt(roku_lux.get_note('serial_crt')['port'], roku_lux.get_note('serial_crt')['baud'])

# 将排序方式 设置成short
roku_ctl.enter_media_player()
roku_ctl.ir_enter('Audio', roku_ctl.layout_media_player_home)
assert roku_ctl.check_udisk(), "No USB flash drive detected"
roku_ctl.wait_for_element("Search", timeout=5)
roku_ctl.select(time=1)
roku_ctl.ir_enter('roku_usb', roku_ctl.get_u_disk_file_distribution())
time.sleep(1)
roku_ctl.info(time=1)
if 'Row Style - [Short]' not in roku_ctl._get_screen_xml():
	for _ in range(7):
		if 'Row Style' not in roku_ctl.get_ir_focus(secret=True):
			roku_ctl.down(time=1)

	for _ in range(5):
		if 'Short' not in roku_ctl.get_ir_focus(secret=True):
			roku_ctl.select(time=1)

	roku_ctl.down(time=1)
	roku_ctl.select(time=1)
	roku_ctl.back(time=1)
	roku_ctl.back(time=1)
roku_ctl.home(time=1)

