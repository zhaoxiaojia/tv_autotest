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

from tool.test_result import TestResult
from tool.yaml_tool import YamlTool
from third_party_equipment import ThirdPartyEqupment


def pytest_sessionstart(session):
	# parse configutration file
	pytest.config_yaml = YamlTool(os.getcwd() + '/config/config.yaml')
	pytest.repeat_count = pytest.config_yaml.get_note('repeat_test')
	# init third party equiment
	third_equipment = ThirdPartyEqupment()
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
		wildcard = pytest.config_yaml.get_note("connect_type")[pytest.connect_type]['wildcard']
		pytest.executer = TelnetTool(telnet_ip, wildcard)
		logging.info("telnet connected %s" % telnet_ip)
	elif pytest.connect_type == None:
		pytest.executer = ''
		logging.info("Don't need adb or telnet control")
	else:
		raise EnvironmentError("Not support connect type %s" % pytest.connect_type)

	# create a folder based on the current time to save logs
	# result_path = os.path.join(os.getcwd(), 'results/' + session.config.getoption("--resultpath"))
	# os.mkdir(result_path)
	# pytest.testResult = TestResult(result_path)
	# pytest.result_data = collections.defaultdict(list)
	# create test results if not exist
	# if not os.path.exists('results'):
	# 	os.mkdir('results')


def pytest_addoption(parser):
	parser.addoption(
		"--resultpath", action="store", default=None, help="Test result path"
	)

# @pytest.fixture()
# def resultpath(request):
# 	logging.info(f'resultpath {time.asctime()}')
# 	pytest.resultpath_timestamp = request.config.getoption("--resultpath")
# 	return pytest.resultpath_timestamp


# @pytest.fixture(autouse=True)
# def setup():
#
# 	pytest.kpi_result = 0
# 	yield
# 	time.sleep(10)


# def pytest_sessionfinish(session):
# 	pytest.testResult.write_data(pytest.result_data)
# 	shutil.copy("pytest.log", "debug.log")
# 	shutil.move("debug.log", pytest.testResult.logDir)
# 	shutil.copy("report.html", "debug.html")
# 	shutil.move("debug.html", pytest.testResult.logDir)
#
# 	if os.path.exists("report.html"):
# 		os.remove("report.html")


# @pytest.hookimpl(tryfirst=True)
# def pytest_runtest_makereport(item, call):
# 	if hasattr(item, 'execution_count'):
# 		pytest.reruns_count = item.execution_count
