# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/18 10:22
# @Author  : chao.li
# @File    : __init__.py.py
# @Project : kpi_test
# @Software: PyCharm


import os

import pytest

from dut_control.xiaomi_ir import XiaomiIr
from tool.yaml_tool import YamlTool


class xiaomi_adb:
    def __init__(self):
        ...

    def home(self):
        pytest.executer.home()
        pytest.executer.wait_and_tap("我的", 'text')

    def yunshiting_jiguang(self):
        self.home()
        pytest.executer.wait_and_tap("我的应用", 'text')
        pytest.executer.enter()
        pytest.executer.wait_and_tap("云视听极光", 'text')



xiaomi_lux = YamlTool(os.getcwd() + '/config/xiaomi/xiaomi.yaml')
xiaomi_ir = XiaomiIr()
xiaomi_adb = xiaomi_adb()
# xiaomi_serial = serial_crt(xiaomi_lux.get_note('serial_crt')['port'], xiaomi_lux.get_note('serial_crt')['baud'])
