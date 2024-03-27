# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/13 10:21
# @Author  : Chao.li
# @File    : irsend.py
# @Project : kpi_test
# @Software: PyCharm
import logging
import os
import subprocess
import time

from tool.exception import *


class irsend:
    '''

Synopsis:
    irsend [options] SEND_ONCE remote code [code...]
    irsend [options] SEND_START remote code
    irsend [options] SEND_STOP remote code
    irsend [options] LIST remote
    irsend [options] SET_TRANSMITTERS remote num [num...]
    irsend [options] SIMULATE "scancode repeat keysym remote"
Options:
    -h --help                   display usage summary
    -v --version                display version
    -d --device=device          use given lircd socket [/run/lirc/lircd]
    -a --address=host[:port]    connect to lircd at this address
    -# --count=n                send command n times
    '''

    def __init__(self):
        ...


    def send(self,remote,code,option="SEND_ONCE"):
        '''
        switch the key by infrared emission
        eg: irsend SEND_ONCE rdk power

        :param remote: such as rdk
        :param code: such as power
        :param option: should be one of [SEND_ONCE,SEND_START,SEND_STOP,LIST,SET_TRANSMITTERS,SIMULATE]
        :return:
        '''
        if code not in self.get_conf(remote):
            raise KeyValueNotExistsError("This key does't exist")
        logging.info(f'irsend {option} {remote} {code}')
        return subprocess.check_output(f'irsend {option} {remote} {code}'.split())

    def get_conf(self,project):
        '''
        get lircd conf
        :param project: project name, such as rdk
        :return:
        '''
        if not os.path.exists(f'/etc/lirc/lircd.conf.d/{project}.lircd.conf'):
            raise FileNotFoundError("This file does't exist")
        return subprocess.check_output(f'cat /etc/lirc/lircd.conf.d/{project}.lircd.conf |grep name',shell=True,encoding='utf-8')


# ir = irsend()
