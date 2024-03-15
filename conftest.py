#!/usr/bin/python
# -*- coding: utf-8 -*-

'''

@File		:	conftest.py
@Time		:	2023-12-11 19:45:29
@Author		:	chao.li
@Desc		:	None


'''
import collections
import datetime
import logging
import os
import shutil
import time

import pytest

from tool.dut_control.adb import Adb
from tool.dut_control.irsend import Irsend
from tool.dut_control.telnet_tool import TelnetTool
# from tool.raspberry_sensor.lightsensor import LightSensor
from tool.phidgets_sensor.light_sensor import lightSensor
from tool.pdusnmp import PowerCtrl
from tool.test_result import TestResult
from tool.yaml_tool import YamlTool


def pytest_sessionstart(session):
	# parse configutration file
	pytest.config_yaml = YamlTool(os.getcwd() + '/config/config.yaml')
	pytest.repeat_count = pytest.config_yaml.get_note('repeat_test')
	# init lightsensor
	pytest.light_sensor = lightSensor()
	# init ir remote
	pytest.irsend = Irsend()
	# init power crt
	pytest.power_crt = PowerCtrl(pytest.config_yaml.get_note("power_crt"))

	# dut inch
	pytest.panel = '50inch'

	# init adb if needed
	pytest.connect_type = pytest.config_yaml.get_note('connect_type')['type']
	if pytest.connect_type == 'adb':
		# Create adb obj
		devices_num = pytest.config_yaml.get_note("connect_type")[pytest.connect_type]['device']
		pytest.executer = Adb(serialnumber=devices_num)
		logging.info("adb connected %s" % devices_num)
	elif pytest.connect_type == 'telnet':
		# Create telnet obj
		telnet_ip = pytest.config_yaml.get_note("connect_type")[pytest.connect_type]['ip']
		pytest.executer = TelnetTool(telnet_ip)
		logging.info("telnet connected %s" % telnet_ip)
	elif pytest.connect_type == None:
		pytest.executer = ''
		logging.info("Don't need adb or telnet control")
	else:
		raise EnvironmentError("Not support connect type %s" % pytest.connect_type)

	# create test results if not exist
	if not os.path.exists('results'):
		os.mkdir('results')
	# create a folder based on the current time to save logs
	result_path = os.path.join(os.getcwd(), 'results/' + datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S"))
	os.mkdir(result_path)

	# init log handler
	pytest.testResult = TestResult(result_path)
	pytest.result_data = collections.defaultdict(list)


@pytest.fixture(autouse=True)
def setup():
	pytest.kpi_result = 0
	yield
	time.sleep(10)


def pytest_sessionfinish(session):
	logging.info(pytest.result_data)
	pytest.testResult.write_data(pytest.result_data)
	shutil.copy("pytest.log", "debug.log")
	shutil.move("debug.log", pytest.testResult.logDir)
	shutil.copy("report.html", "debug.html")
	shutil.move("debug.html", pytest.testResult.logDir)
	if os.path.exists("report.html"):
		os.remove("report.html")
