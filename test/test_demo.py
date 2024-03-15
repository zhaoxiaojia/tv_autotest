# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : test_demo.py
# @Time       : 2024/1/26 10:09
# @Author     : chao.li
# @Software   : PyCharm
"""
import pytest


@pytest.fixture(autouse=True)
def setup():
	int('coco')


def test_demo():
	print({'a': 1, 'b': 2}['c'])
