#!/usr/bin/env python
# -*- coding: utf-8 -*- 


"""
# File       : executer.py
# Time       ：2023/7/4 15:51
# Author     ：chao.li
# version    ：python 3.9
# Description：
"""


import logging
import subprocess


class Executer():
    DMESG_COMMAND = 'dmesg -S'
    CLEAR_DMESG_COMMAND = 'dmesg -c'

    def __init__(self):
        self.serialnumber = 'executer'

    def checkoutput_term(self, command):
        logging.info(f"command:{command}")
        if not isinstance(command, list):
            command = command.split()
        return subprocess.check_output(command, encoding='gbk')
