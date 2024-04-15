# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : third_party_equipment.py
# @Time       : 2024/4/1 9:31
# @Author     : chao.li
# @Software   : PyCharm
"""
import logging

import pytest
from tool.yaml_tool import YamlTool
import os
from tool.phidgets_sensor.light_sensor import lightSensor
from tool.pdusnmp import PowerCtrl
from tool.signal_generator.master_8100s import Master_8100s


class ThirdPartyEqupment:

	def __init__(self):
		pytest.light_sensor = ''
		pytest.power_crt = ''
		pytest.pattern_gener = ''
		# init lightsensor
		if self.get_status('light_sensor'):
			pytest.light_sensor = lightSensor()

		# init power crt
		if self.get_status('power_crt'):
			pytest.power_crt = PowerCtrl(pytest.config_yaml.get_note("power_crt")['ip'])

		# init
		if self.get_status('pattern_generator'):
			pytest.pattern_gener = Master_8100s()

	def get_status(self, device_name):
		return pytest.config_yaml.get_note(device_name)['status']
