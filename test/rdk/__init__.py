# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/13 09:56
# @Author  : chao.li
# @File    : __init__.py.py
# @Project : kpi_test
# @Software: PyCharm

import os

from dut_control.rdk_ir import RdkIr
from tool.dut_control.serial_ctrl import SerialCtrl
from tool.yaml_tool import YamlTool

rdk_lux = YamlTool(os.getcwd() + '/config/rdk/rdk.yaml')
rdk_ir = RdkIr()
rdk_serial = SerialCtrl(rdk_lux.get_note('serial_crt')['port'], rdk_lux.get_note('serial_crt')['baud'])
