# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/26 16:37
# @Author  : chao.li
# @File    : webcontrol.py
# @Project : kpi_test
# @Software: PyCharm

from selenium import webdriver


class WebCtrl:
    SCROL_JS = 'arguments[0].scrollIntoView();'

    def __init__(self, path, display=False):
        self.address = path
        self.option = webdriver.ChromeOptions()
        if display == True:
            self.option.add_argument("--start-maximized")  # 窗口最大化
            self.option.add_experimental_option("detach", True)  # 不自动关闭浏览器
            # self.service = Service(executable_path=r"C:\Users\yu.zeng\ChromeWebDriver\chromedriver.exe")
            self.driver = webdriver.Chrome(options=self.option)
        else:
            self.option.add_argument(argument='headless')
            self.driver = webdriver.Chrome(options=self.option)

    def scroll_to(self, target):
        self.driver.execute_script(self.SCROL_JS, target)
