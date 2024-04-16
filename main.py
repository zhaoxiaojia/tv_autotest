# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/12 14:25
# @Author  : chao.li
# @File    : main.py
# @Project : kpi_test
# @Software: PyCharm

import json
import subprocess
import os
import time
import ast
import pytest
import datetime
import shutil
import logging
from dut_control.roku_ctrl import RokuCtrl

timestamp = datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
# 参数为需要运行的测试用例 可以是文件或者文件夹目录
# test_case = 'test/roku/CEA-861/test_C84431.py'
test_case = r'test/roku/VESA-Signals-PC'

allure_parent_path = test_case.replace('test', 'report')

# if os.path.isdir(test_case):
# 	allure_cmd = f'--alluredir=./results/allure/{test_case.split("test/")[1]}'
# else:
# 	allure_cmd = ''
# ./report/roku/VESA-Signals-PC/2024.04.11_16.28.56
allure_path = fr'./report/{test_case.split("test/")[1]}/{timestamp}'
allure_history_file = ''


# print(allure_path)
# print(allure_parent_path)


# 获取下一个文件夹的名称，以及最近一个趋势的数据
def get_dir():
	if allure_history_file:
		history_file = os.path.join(allure_parent_path, os.listdir(allure_parent_path)[-1],
		                            "widgets/history-trend.json")
		buildOrder = len(allure_history_file)
		# 取出最近一次执行的历史趋势的json
		with open(history_file, 'r+') as f:
			data = json.load(f)
			data[0]['buildOrder'] = buildOrder
			data[0]['reportUrl'] = 'http://todo.com'
		with open(history_file, 'w+') as f:
			json.dump(data, f)
		# 将这次生成的文件夹序号以及最新的历史趋势数据返回
		return buildOrder, data
	return 0, None


def update_file():
	dict = []
	for i in allure_history_file:
		file = os.path.join(allure_parent_path, i, "widgets", "history-trend.json")
		with open(file) as f:
			temp_data = json.load(f)
			if not dict:
				dict.append(temp_data[0])
				continue
			if temp_data[0]['buildOrder'] not in [i['buildOrder'] for i in dict]:
				dict.append(temp_data[0])
	dict.sort(key=lambda x: x['buildOrder'], reverse=True)
	latest_file = os.path.join(allure_parent_path + '/' + allure_history_file[-1] + "/widgets/history-trend.json")
	with open(latest_file, 'w') as f:
		json.dump(dict, f)


if __name__ == '__main__':

	# if allure_cmd:
	# 	cmd = ['-v', '--capture=sys', '--html=report.html', f'--resultpath={timestamp}', test_case, allure_cmd]
	# else:
	# 	cmd = ['-v', '--capture=sys', '--html=report.html', f'--resultpath={timestamp}', test_case]
	allure_cmd = f'--alluredir=./results/allure/{test_case.split("test/")[1]}'
	cmd = ['-v', '--capture=sys', '--html=report.html', f'--resultpath={timestamp}', test_case, allure_cmd]
	pytest.main(cmd)

	RokuCtrl.switch_ir('on')
	if not os.path.exists('report'):
		os.mkdir('report')
	if not os.path.exists('results'):
		os.mkdir('results')

	# if allure_cmd:
	subprocess.check_output(f'allure generate -c {allure_cmd.split("./")[1]} -o {allure_path}', shell=True)

	# allure_history_file = os.listdir(allure_parent_path)
	# get_dir()
	# update_file()

	shutil.move("kernel.log", allure_path)
	shutil.move("report.html", allure_path)
	shutil.move("pytest.log", allure_path)
	shutil.move("dmesg.log", allure_path)
