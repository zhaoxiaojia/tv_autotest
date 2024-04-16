# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : open_allure.py
# @Time       : 2024/4/16 17:17
# @Author     : chao.li
# @Software   : PyCharm
"""


import os

allure_report = os.listdir('report')

print(allure_report[-1])
os.system(f'allure serve ./allure')