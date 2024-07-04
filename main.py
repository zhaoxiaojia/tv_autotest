# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/12 14:25
# @Author  : chao.li
# @File    : main.py
# @Project : kpi_test
# @Software: PyCharm

import ast
import datetime
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import traceback

import pytest

from dut_control.roku_ctrl import RokuCtrl

timestamp = datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
# 参数为需要运行的测试用例 可以是文件或者文件夹目录
# test_case = 'test/roku/Hdmi/CEA-861/test_C84431.py'
# test_case = 'test/roku/Usb-Local/UI/Media-Player-Home-Screen/test_T825138.py'
test_case = 'test/roku/Usb-Local/FunctionalAudio/test_T825173.py'
# test_case = 'test/roku/test_demo.py'
report_parent_path = test_case.replace('test', 'report')

# if os.path.isdir(test_case):
# 	allure_cmd = f'--alluredir=./results/allure/{test_case.split("test/")[1]}'
# else:
# 	allure_cmd = ''
# ./report/roku/VESA-Signals-PC/2024.04.11_16.28.56
# allure_path = fr'./report/{test_case.split("test/")[1]}/{timestamp}'

report_path = fr'./report/{timestamp}'
allure_history_file = ''

# print(allure_path)
# print(allure_parent_path)

# 获取下一个文件夹的名称，以及最近一个趋势的数据
# def get_dir():
# 	if allure_history_file:
# 		history_file = os.path.join(report_parent_path, os.listdir(report_parent_path)[-1],
# 		                            "widgets/history-trend.json")
# 		buildOrder = len(allure_history_file)
# 		# 取出最近一次执行的历史趋势的json
# 		with open(history_file, 'r+') as f:
# 			data = json.load(f)
# 			data[0]['buildOrder'] = buildOrder
# 			data[0]['reportUrl'] = 'http://todo.com'
# 		with open(history_file, 'w+') as f:
# 			json.dump(data, f)
# 		# 将这次生成的文件夹序号以及最新的历史趋势数据返回
# 		return buildOrder, data
# 	return 0, None


# def update_file():
# 	dict = []
# 	for i in allure_history_file:
# 		file = os.path.join(report_parent_path, i, "widgets", "history-trend.j`son")
# 		with open(file) as f:
# 			temp_data = json.load(f)
# 			if not dict:
# 				dict.append(temp_data[0])
# 				continue
# 			if temp_data[0]['buildOrder'] not in [i['buildOrder'] for i in dict]:
# 				dict.append(temp_data[0])
# 	dict.sort(key=lambda x: x['buildOrder'], reverse=True)
# 	latest_file = os.path.join(report_parent_path + '/' + allure_history_file[-1] + "/widgets/history-trend.json")
# 	with open(latest_file, 'w') as f:
# 		json.dump(dict, f)


if __name__ == '__main__':

	if not os.path.exists('report'):
		os.mkdir('report')
	# if os.path.exists('allure'):
	# 	shutil.rmtree('allure')
	if not os.path.exists(report_path):
		os.mkdir(report_path)

	# allure_cmd = f'--alluredir=./allure'
	tm_cmd = f'--pytest-tmreport-name=report.html'
	# cmd = ['-v', '--capture=sys', '--html=report.html', f'--resultpath={timestamp}', test_case, allure_cmd]
	cmd = ['-v', '--capture=sys', tm_cmd, f'--resultpath={timestamp}', test_case]

	pytest.main(cmd)

	if 'roku' in test_case:
		RokuCtrl.switch_ir('on')

	# if allure_cmd:
	# subprocess.check_output(f'allure generate -c ./allure -o {allure_path}', shell=True)
	# allure_history_file = os.listdir(allure_parent_path)
	# get_dir()
	# update_file()

	if os.path.exists("kernel.log"):
		shutil.move("kernel.log", report_path)
	if os.path.exists("report.html"):
		shutil.move("report.html", report_path)
	if os.path.exists("pytest.log"):
		shutil.move("pytest.log", report_path)
	if os.path.exists("dmesg.log", ):
		shutil.move("dmesg.log", report_path)
	if os.path.exists("logcat.log", ):
		shutil.move("logcat.log", report_path)

# os.system(f'allure serve ./allure')
