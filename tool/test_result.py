# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/12 17:15
# @Author  : chao.li
# @File    : test_result.py
# @Project : kpi_test
# @Software: PyCharm

import logging
import os
import time


class TestResult:
    def __init__(self, logDir):
        self.logDir = logDir
        # if not hasattr(self, 'logFile'):
        #     self.log_file = os.path.join(self.logDir,
        #                                  'Kpi' + time.asctime().replace(' ', '_').replace(':', '_') + '.csv')
        # with open(self.log_file, 'a', encoding='utf-8') as f:
        #     title = 'TestCase Min Max Avg'
        #     logging.info(title.split())
        #     f.write(','.join(title.split()))
        #     f.write('\n')

    def write_data(self, data: dict):
        logging.info('statisticis in progress')
        for k, v in data.items():
            avg = round(sum(v) / len([i for i in v if i]), 3)
            logging.info(f'{k},{min([i for i in v if i])},{max(v)},{avg},{",".join([str(j) for j in v])}')
            with open(self.log_file, 'a') as f:
                f.write(f'{k},{min([i for i in v if i])},{max(v)},{avg},{",".join([str(j) for j in v])}')
                f.write('\n')
