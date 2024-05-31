# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File        : video_checkpoint.py
# @Time       : 2024/5/15 15:27
# @Author     : chao.li
# @Software   : PyCharm
"""
import threading
import time

import threadpool

LOCK = threading.Lock()


class VideoPlayerChecker:
	def __init__(self):
		self.abnormal_observer_list = []
		with LOCK:
			self.check_tag = False

	def get_abnormal_observer(self):
		if self.abnormal_observer_list:
			self.exitcode = 1  # if thread abnormal exit, set 1
			return True
		else:
			return False

	def check_common_status(self, func, timeout=60):
		start_time = time.time()
		while time.time() - start_time < timeout:
			time.sleep(3)
			eval(func)
			if self.get_abnormal_observer():
				break

	def check_threadpool_on(self):
		common_func_list = ["self.check_v4lvideo_count()", "self.checkFrame()", "self.checkHWDecodePlayback()"]
		common_task_pool = threadpool.ThreadPool(6)
		requests = threadpool.makeRequests(self.check_common_status, common_func_list)
		[common_task_pool.putRequest(req) for req in requests]
		common_task_pool.wait()
