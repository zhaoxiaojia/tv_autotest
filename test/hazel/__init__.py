# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/12 11:01
# @Author  : chao.li
# @File    : __init__.py.py
# @Project : kpi_test
# @Software: PyCharm


import os

from dut_control.hazel_ir import HazelIr
from tool.yaml_tool import YamlTool

hazel_lux = YamlTool(os.getcwd() + '/config/hazel/hazel.yaml')
hazel_ir = HazelIr()

# hazel_serial = serial_crt(hazel_lux.get_note('serial_crt')['port'], hazel_lux.get_note('serial_crt')['baud'])
