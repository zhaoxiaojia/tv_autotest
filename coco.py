# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 13:50
# @Author  : chao.li
# @File    : coco.py
# @Project : kpi_test
# @Software: PyCharm


# class MyDict(dict):
# 	def __init__(self, factory):
# 		print(f' init factory {factory}')
# 		self._factory = factory
#
# 	def __missing__(self, key):
# 		v = self._factory()
# 		print(f' missing factory {v}')
# 		print(f' missing factory {self._factory}')
# 		self[key] = v
# 		return v
#
#
# d = MyDict(list)
# d['hello'].append(1)
# print(d)
