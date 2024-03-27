# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/12 14:25
# @Author  : chao.li
# @File    : main.py
# @Project : kpi_test
# @Software: PyCharm


import pytest

if __name__ == '__main__':
    pytest.main(['-v', '--capture=sys',
                 # '-m full_auto',
                 '--html=report.html', 'test/roku/CEA-861']) # 参数为需要运行的测试用例 可以是文件或者文件夹目录
                 # '--html=report.html', 'test/test_demo.py'])