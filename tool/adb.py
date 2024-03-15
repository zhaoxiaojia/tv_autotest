#
# Copyright 2021 Amlogic.com, Inc. or its affiliates. All rights reserved.
#
# AMLOGIC PROPRIETARY/CONFIDENTIAL
#
# You may not use this file except in compliance with the terms and conditions
# set forth in the accompanying LICENSE.TXT file.
#
# THESE MATERIALS ARE PROVIDED ON AN "AS IS" BASIS. AMLOGIC SPECIFICALLY
# DISCLAIMS, WITH RESPECT TO THESE MATERIALS, ALL WARRANTIES, EXPRESS,
# IMPLIED, OR STATUTORY, INCLUDING THE IMPLIED WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
#

import logging
import os
import re
import signal
import subprocess
import threading
import time
from collections import Counter
from xml.dom import minidom

import _io
import pytest

from tool.executer import executer
from tool.ui_tool import ui_tool


def connect_again(func):
    def inner(self, *args, **kwargs):
        if ':5555' in self.serialnumber:
            subprocess.check_output('adb connect {}'.format(self.serialnumber), shell=True)
            self.wait_devices()
        else:
            self.wait_devices()
        return func(self, *args, **kwargs)

    return inner


class adb(executer):
    """
    ADB class Provide common device control functions over the ADB bridge

    Attributes:
        serialnumber : adb number : str
        logdir : testcase result log path

    """

    ADB_S = 'adb -s '
    DUMP_FILE = '\\view.xml'
    OSD_VIDEO_LAYER = 'osd+video'

    def __init__(self, serialnumber="", logdir=""):
        super().__init__()
        self.serialnumber = serialnumber
        logging.info("get devices number %s" % serialnumber)
        self.logdir = logdir or os.path.join(os.getcwd(), 'results')
        self.timer = None
        self.live = False
        self.lock = threading.Lock()
        self.wait_devices()
        self.p_config_wifi = ''

    def set_status_on(self):
        '''
        set DUT survival condition to True
        @return: None
        '''
        if not self.live:
            self.lock.acquire()
            self.live = True
            logging.debug(f'Adb status is on')
            self.lock.release()

    def set_status_off(self):
        '''
        set DUT survival condition to True
        @return:
        '''
        if self.live:
            self.lock.acquire()
            self.live = False
            logging.debug(f'Adb status is Off')
            self.lock.release()

    # @property
    def u(self, type="u2"):
        '''
        uiautomater obj
        @return: instance
        '''
        self._u = ui_tool(self.serialnumber, type)
        return self._u

    def get_uuid(self):
        '''
        get u-disk uuid
        @return: uuid : str
        '''
        self.root()
        return self.checkoutput("ls /storage/ |awk '{print $1}' |head -n 1")

    def get_uuids(self):
        '''
        get u-disk uuid list
        @return: uuid : list [str]
        '''
        self.root()
        return self.checkoutput("ls /storage/ |awk '{print $1}'")[1].split("\n")

    def get_uuid_size(self):
        '''
        get u-disk size
        @return: size : [int]
        '''
        uuid = self.get_uuid()
        logging.info(f'uuid {uuid}')
        size = self.checkoutput(f"df -h |grep {uuid}|cut -f 3 -d ' '").strip()[:-1]
        return int(float(size))

    def get_uuid_avail_size(self):
        '''
        get u-disk avail size
        @return: size %  : [int]
        '''
        uuid = self.get_uuid()
        size = self.checkoutput(f"df -h |grep {uuid}|cut -f 7 -d ' '").strip()[:-1]
        unit = re.findall(r'[A-Za-z]', self.checkoutput(f"df -h |grep {uuid}|cut -f 7 -d ' '"))
        if len(size) == 0:
            size = self.checkoutput(f"df -h |grep {uuid}|cut -f 8 -d ' '").strip()[:-1]
            unit = re.findall(r'[A-Za-z]', self.checkoutput(f"df -h |grep {uuid}|cut -f 8 -d ' '"))
            if len(size) == 0:
                size = 0
                return size
        if unit[0] == 'G':
            size = int(float(size)) * 1024
        elif unit[0] == 'K':
            size = int(float(size)) / 1024
        return int(float(size))

    def keyevent(self, keycode):
        '''
        input keyevent keycode
        @param keycode: keyevent
        @return: None
        '''
        if isinstance(keycode, int):
            keycode = str(keycode)
        self.checkoutput_term(self.ADB_S + self.serialnumber +
                              " shell input keyevent " + keycode)

    def send_event(self, key, hold=3):
        '''
        sendevent
        :param key: key number
        :param hold: long press duration
        :return:
        '''
        # /dev/input/event5: 0004 0004 000c0045
        self.checkoutput(
            f'sendevent /dev/input/event5 4 4 786501;sendevent /dev/input/event5 1 {key} 1;sendevent  /dev/input/event5 0 0 0;')
        time.sleep(hold)
        self.checkoutput(
            f'sendevent /dev/input/event5 4 4 786501;sendevent /dev/input/event5 1 {key} 0;sendevent  /dev/input/event5 0 0 0;')

    def home(self):
        '''
        set DUT back to home over keyevent
        @return: None
        '''
        self.keyevent("KEYCODE_HOME")

    def enter(self):
        '''
        confirm button
        @return: None
        '''
        self.keyevent("KEYCODE_ENTER")

    def root(self):
        '''
        set adb root
        @return: None
        '''
        self.checkoutput_shell('root')

    def remount(self):
        '''
        set adb remount
        @return: None
        '''
        self.checkoutput_shell('remount')

    def reboot(self):
        '''
        set adb reboot
        @return:
        '''
        self.checkoutput_shell('reboot')

    def back(self):
        '''
        set DUT cancel button over keyevent
        @return:
        '''
        self.keyevent("KEYCODE_BACK")

    def app_switch(self):
        '''
        ui app switch button
        @return:
        '''
        self.keyevent("KEYCODE_APP_SWITCH")

    def app_stop(self, app_name):
        '''
        am force stop app
        if timer is setup cancel it
        @param app_name:
        @return:
        '''
        logging.info("Stop app(%s)" % app_name)
        self.checkoutput("am force-stop %s" % app_name)
        # self.kill_logcat_pid()

    def clear_app_data(self, app_name):
        '''
        clear app data
        :param app_name: package name. Such as com.google.xxx
        :return:
        '''
        self.checkoutput(f"pm clear {app_name}")

    def expand_logcat_capacity(self):
        '''
        Set the logcat cache space
        Adjust the logcat priority
        :return:
        '''
        self.checkoutput("logcat -G 40m")
        self.checkoutput("renice -n -50 `pidof logd`")

    def delete(self, times=1):
        '''
        ui del button
        @param times: click del times
        @return: None
        '''
        remain = times
        batch = 64
        while remain > 0:
            # way faster delete
            self.keyevent("67 " * batch)
            remain -= batch

    def tap(self, x, y):
        '''
        simulate screen tap
        @param x: x index
        @param y: y index
        @return: None
        '''
        self.checkoutput_term(self.ADB_S + self.serialnumber + " shell input tap " + str(x) + " " + str(y))

    def swipe(self, x_start, y_start, x_end, y_end, duration):
        '''
        simulate swipe screen
        @param x_start: x start index
        @param y_start: y start index
        @param x_end: x end index
        @param y_end: y end index
        @param duration: action time duration
        @return: None
        '''
        self.checkoutput_term(self.ADB_S + self.serialnumber + " shell input swipe " + str(x_start) +
                              " " + str(y_start) + " " + str(x_end) + " " + str(y_end) + " " + str(duration))

    def text(self, text):
        '''
        edittext input text
        @param text: text
        @return: None
        '''
        if isinstance(text, int):
            text = str(text)
        self.checkoutput_term(self.ADB_S + self.serialnumber + " shell input text " + text)

    def clear_logcat(self):
        '''
        clear logcat
        @return: None
        '''
        self.checkoutput_term(self.ADB_S + self.serialnumber + " logcat -b all -c")

    def save_logcat(self, filepath, tag=''):
        '''
        save logcat
        @param filepath: file path for logcat
        @param tag: tag for -s
        @return: log : subprocess.Popen , logcat_file : _io.TextIOWrapper
        '''
        filepath = self.logdir + '/' + filepath
        logcat_file = open(filepath, 'w')
        if tag and ("grep -E" not in tag) and ("all" not in tag):
            tag = f'-s {tag}'
            log = subprocess.Popen(f"adb -s {self.serialnumber} shell logcat -v time {tag}".split(), stdout=logcat_file,
                                   preexec_fn=os.setsid)
        else:
            log = subprocess.Popen(f"adb -s {self.serialnumber} shell logcat -v time {tag}", stdout=logcat_file,
                                   shell=True, stdin=subprocess.PIPE, preexec_fn=os.setsid)
        return log, logcat_file

    def stop_save_logcat(self, log, filepath):
        '''
        stop logcat ternimal , close logcat file
        @param log: logcat popen
        @param filepath: logcat file
        @return: None
        '''
        if not isinstance(log, subprocess.Popen):
            logging.warning('pls pass in the popen object')
            return 'pls pass in the popen object'
        if not isinstance(filepath, _io.TextIOWrapper):
            logging.warning('pls pass in the stream object')
            return 'pls pass int the stream object'
        # subprocess.Popen.send_signal(signal.SIGINT)
        self.filter_logcat_pid()
        log.terminate()
        log.send_signal(signal.SIGINT)
        # os.kill(log.pid, signal.SIGTERM)
        filepath.close()

    def filter_logcat_pid(self):
        p_lookup_logcat_thread_cmd = 'ps -e | grep logcat'
        output = self.checkoutput(p_lookup_logcat_thread_cmd)
        if 'logcat' in output:
            p_logcat_pid = re.search('(.*?) logcat', output, re.M | re.I).group(1).strip().split(" ")
            # print(f"p_logcat_pid 1: {p_logcat_pid}")
            # print(f"p_logcat_pid 1-1: {p_logcat_pid[9]}")
            if "S" in p_logcat_pid:
                for one in p_logcat_pid:
                    if re.findall(r".*\d+", one):
                        # print(f"p_logcat_pid 2: {one}")
                        self.checkoutput(f"kill -9 {one}")
                        break
        return output

    def start_activity(self, packageName, activityName, intentname=""):
        '''
        start activity over am start
        @param packageName: apk package name
        @param activityName: activity name
        @param intentname: intent name
        @return: None
        '''
        try:
            self.app_stop(packageName)
        except Exception as e:
            ...
        command = self.ADB_S + self.serialnumber + " shell am start -a " + intentname + " -n " + packageName + "/" + activityName
        logging.info(command)
        self.checkoutput_term(self.ADB_S + self.serialnumber +
                              " shell am start -a " + intentname + " -n " + packageName + "/" + activityName)

    def pull(self, filepath, destination):
        '''
        pull file from DUT to pc
        @param filepath: file path
        @param destination: target path
        @return: None
        '''
        self.checkoutput_term(self.ADB_S + self.serialnumber +
                              " pull " + filepath + " " + destination)

    def push(self, filepath, destination):
        '''
        push file from pc to DUT
        @param filepath: file path
        @param destination: target path
        @return: None
        '''
        self.checkoutput_term(self.ADB_S + self.serialnumber +
                              " push " + filepath + " " + destination)

    def shell(self, cmd):
        '''
        run adb -s xxx shell
        @param cmd: command
        @return: None
        '''
        self.checkoutput_term(self.ADB_S + self.serialnumber + " shell " + cmd)

    def ping(self, interface=None, hostname="www.baidu.com",
             interval_in_seconds=1, ping_time_in_seconds=5,
             timeout_in_seconds=10, size_in_bytes=None):
        """Can ping the given hostname without any packet loss

        Args:
            hostname (str, optional): ip or URL of the host to ping
            interval_in_seconds (float, optional): Time interval between
                                                   pings in seconds
            ping_time_in_seconds (int, optional)  : How many seconds to ping
            timeout_in_seconds (int, optional): wait time for this method to
                                                finish
            size_in_bytes (int, optional): Ping packet size in bytes

        Returns:
            dict: Keys: 'sent' and 'received', values are the packet count.
                  Empty dictionary if ping failed
        """
        ping_output = {}
        if not (hostname and isinstance(hostname, str)):
            logging.error("Must supply a hostname(non-empty str)")
            return False
        p_conf_wifi_ping_count = 5
        count = int(p_conf_wifi_ping_count / interval_in_seconds)
        timeout_in_seconds += p_conf_wifi_ping_count
        # Changing count based on the interval, so that it always finishes
        # in ping_time seconds

        p_conf_wifi_ping_pass_percentage = 0
        ping_pass_percentage = int(count * p_conf_wifi_ping_pass_percentage * 0.01)
        if interface:
            if size_in_bytes:
                cmd = "ping -i %s -I %s -c %s -s %s %s" % (
                    interval_in_seconds, interface, count, size_in_bytes, hostname)
            else:
                cmd = "ping -i %s -I %s -c %s %s" % (interval_in_seconds, interface, count, hostname)
        else:
            if size_in_bytes:
                cmd = "ping -i %s -c %s -s %s %s" % (
                    interval_in_seconds, count, size_in_bytes, hostname)
            else:
                cmd = "ping -i %s -c %s %s" % (interval_in_seconds, count, hostname)
        logging.debug("Ping command: %s" % cmd)
        try:
            output = self.checkoutput(cmd)
        except Exception as e:
            output = str(e)
        # rc, result = self.run_shell_cmd(cmd,  timeout=timeout_in_seconds)
        RE_PING_STATUS = re.compile(
            r".*(---.+ping statistics ---\s+\d+ packets transmitted, \d+ received, "
            r"(?:\+\d+ duplicates, )?(\d+)% packet loss, time.+ms\s*?rtt\s+?"
            r"min/avg/max/mdev)\s+?=\s+?(\d+(\.\d+)?)/(\d+(\.\d+)?)/(\d+(\.\d+)?)"
            r"/(\d+(\.\d+)?)\s+?ms.*?")
        match = RE_PING_STATUS.search(output)
        # logging.info(output)
        # logging.info(match)
        ping_output['duplicates'] = 0
        if match:
            stats = match.group(1).split('\n')[1].split(',')
            ping_output['transmitted'] = int(
                stats[0].split()[0].strip())
            ping_output['received'] = int(stats[1].split()[0].strip())
            if 'duplicates' in match.group(1):
                ping_output['duplicates'] = int(
                    stats[2].split()[0].strip().split('+')[1])
            ping_output['packet_loss'] = int(match.group(2))
            logging.debug("Ping Stats Dictionary:-{}".format(ping_output))
            expected_pkt_loss = int(((count - ping_pass_percentage) /
                                     count) * 100)
            if ping_output['packet_loss'] <= expected_pkt_loss:
                return True
        else:
            return False

    def check_apk_exist(self, package_name):
        '''
        check is apk exists or not
        :param package_name: package name. Such as com.google.xxx
        :return:
        '''
        return True if package_name in self.checkoutput('pm list packages') else False

    def install_apk(self, apk_path):
        '''
        install apk from pc
        @param apk_path: apk path
        @return: install status : boolean
        '''
        apk_path = os.path.join(os.getcwd(), 'res\\' + apk_path)
        cmd = f'install -r -t {apk_path}'
        logging.info(cmd)
        return self.checkoutput_shell(cmd)

    def uninstall_apk(self, apk_name):
        '''
        uninstall apk
        @param apk_name: apk name
        @return: uninstall status : boolean
        '''
        cmd = f'uninstall {apk_name}'
        logging.info(cmd)
        output = self.checkoutput_shell(cmd)
        time.sleep(5)
        logging.info(output)
        if 'Success' in output:
            logging.info('APK uninstall successful')
            return True
        else:
            logging.info('APK uninstall failed')
            return False

    def get_time(self, time=None):
        '''
        get time information from the logcat
        :param time: logcat info
        :return:
        '''
        if (":" not in time[6:8]) and (":" not in time[9:11]) and (":" not in time[12:14]) and (
                ":" not in time[15:18]) and ("." not in time[15:18]):
            th = int(time[6:8])
            # print(th)
            tm = int(time[9:11])
            # print(tm)
            ts = int(time[12:14])
            # print(ts)
            tms = int()
            if "-" not in time[15:18]:
                tms = int(time[15:18])
            # print(tms)
            # print(time)
            return (tms + ts * 1000 + tm * 60 * 1000 + th * 3600 * 1000) / 1000
        # else:
        #     return 0

    def getprop(self, key):
        '''
        Get property from device
        @param key: prop key
        @return: feedback output
        '''
        return self.checkoutput('getprop %s' % key, )

    def rm(self, flags, path):
        '''
        rm file
        @param flags: flags such as -r
        @param path: file path
        @return: None
        '''
        self.checkoutput_term(self.ADB_S + self.serialnumber + " shell rm " + flags + " " + path)

    def uiautomator_dump(self, filepath='', uiautomator_type='u2'):
        '''
        dump ui xml over uiautomator
        @param filepath: file path
        @return: None
        '''
        if not filepath:
            filepath = self.logdir
        logging.debug('doing uiautomator dump')
        if uiautomator_type == 'u2':
            xml = self.u().d2.dump_hierarchy()
        else:
            uiautomator_type = 'u1'
            xml = self.u(type=uiautomator_type).d1.dump()
        if not filepath.endswith('view.xml'):
            filepath += self.DUMP_FILE
        logging.debug(filepath)
        with open(filepath, 'w+', encoding='utf-8') as f:
            f.write(xml)
        logging.debug('uiautomator dump done')

    def get_dump_info(self):
        '''
        get ui dump info
        @return: dumo info : str
        '''
        path = self.logdir + self.DUMP_FILE if os.path.exists(
            self.logdir + self.DUMP_FILE) else self.logdir + '/view.xml'
        with open(path, 'r', encoding='utf-8') as f:
            temp = f.read()
        return temp

    def expand_notifications(self):
        '''
        expand android notification bar
        @return: None
        '''
        self.checkoutput_term(self.ADB_S + self.serialnumber + " shell cmd statusbar expand-notifications")

    def _screencap(self, filepath, layer="osd", app_level=28):
        '''
        screencap cmd get png style picture
        screencatch -m cmd get bmp style picture
        pngtest cmd get jpeg style picture layer default osd
        can set video or osd+video type
        @param filepath: file path
        @param layer: layer
        @param app_level: sdk version
        @return: None
        '''

        if layer == "osd":
            self.checkoutput_term(self.ADB_S + self.serialnumber + " shell screencap -p " + filepath)
        else:
            png_type = 1
            if layer == "video" or layer == self.OSD_VIDEO_LAYER:
                if app_level > 28:
                    self.screencatch(layer)
                else:
                    if layer == "video":
                        png_type = 0
                    cmd = "pngtest " + str(png_type)
                    self.checkoutput(cmd)
            else:
                logging.info("please check the set screen layer arg")

    def screenshot(self, destination, layer="osd", app_level=28):
        '''
        pull screen catch file to logdir
        @param destination: target path
        @param layer: screen layer type
        @param app_level: sdk version
        @return: None
        '''
        if layer == "osd":
            devicePath = "/sdcard/screen.png"
            destination = self.logdir + "/" + "screencap_" + destination + ".png"
        else:
            dirs = self.mkdir_temp()
            if app_level > 28:
                devicePath = dirs + "/1.bmp"
                destination = self.logdir + "/" + "screencatch_" + destination + ".bmp"
            else:
                devicePath = dirs + "/1.jpeg"
                destination = self.logdir + "/" + "pngtest_" + destination + ".jpeg"
        self._screencap(devicePath, layer, app_level)
        time.sleep(2)
        self.pull(devicePath, destination)
        time.sleep(2)
        if layer == "osd":
            self.rm("", devicePath)
        else:
            self.rm("-r", dirs)

    def continuous_screenshot(self, destination, layer="osd+video", app_level=30, screenshot_counter=3):
        '''
        continuous screenshot just for Android Q/R, set counter >1
        @param destination: target path
        @param layer: screen layer type
        @param app_level: sdk version
        @param screenshot_counter: screen shot times
        @return: None
        '''
        dirs = self.mkdir_temp()
        if app_level > 28 and screenshot_counter > 1 and (layer == "video" or layer == self.OSD_VIDEO_LAYER):
            self.screencatch(layer, screenshot_counter)
            time.sleep(5)
            for i in range(screenshot_counter):
                i = i + 1
                devicePath = dirs + "/" + str(i) + ".bmp"
                logging.info(devicePath)
                destination_temp = self.logdir + "/" + "screencatch_" + destination + "_" + str(i) + ".bmp"
                self.pull(devicePath, destination_temp)
                time.sleep(2)
        else:
            logging.info('you can use screenshot cmd')
        self.rm("-r", dirs)

    def screencatch(self, layer="osd+video", counter=1):
        '''
        screencatch [-p/-j/-m/-b] [-c <counter>] [-t <type>] [left  top  right  bottom  outWidth  outHeight]
            Args:
               -m  :  save as bmp file(android R not support png/jpeg)
               -c <counter> : continually save file with counter, default as 1
               -t <type> : set capture type:
                  0 -- video only
                  1 -- video+osd (default)
        @param layer: screen layer type
        @param counter: screen shot times
        @return: None
        '''

        if layer == self.OSD_VIDEO_LAYER:
            capture_type = "1"
        else:
            capture_type = "0"
        cmd = "screencatch -m " + " -t " + capture_type + " -c " + str(counter)
        logging.info(cmd)
        self.run_shell_cmd(cmd)

    def video_record(self, destination, app_level=28, record_time=30, sleep_time=30,
                     frame=30, bits=4000000, type=1):
        '''
        video record 后pull到logdir目录下 (the command maybe is not ok when record security video,
                                          example youtube/googleMovies DRM security video)
        Android R support args, Android P not support args just can use tspacktest command
        tspacktest [-h] [-f <framerate>] [-b <bitrate>] [-t <type>] [-s <second>] [<width> <height>]
            Args:
               -f <framerate>: frame per second, unit bps, default as 30
               -b <bitrate>  : bits per second, unit bit, default as 4000000
               -t <type>     : select video-only(0) or video+osd(1), default as video+osd
               -s <second>   : record times, unit second(s), default as 30
        '''
        destination = self.logdir + "/" + "video_record_" + destination + ".ts"
        dirs = self.mkdir_temp()
        if app_level <= 28:
            video_record = self.popen("shell tspacktest")
            time.sleep(sleep_time)
            os.kill(video_record.pid, signal.SIGTERM)
        else:
            cmd = "tspacktest -f " + str(frame) + " -b " + str(bits) + " -t " + str(type) + " -s " + str(record_time)
            logging.info(cmd)
            self.run_shell_cmd(cmd)
        time.sleep(2)
        video = dirs + "/video.ts"
        self.pull(video, destination)
        time.sleep(5)
        self.rm("-r", dirs)

    def mkdir_temp(self):
        '''
        mkdir temp folder , chmod 777
        @return: folder path
        '''
        self.root()
        dirs = '/data/temp'
        temp = self.checkoutput("ls /data")
        if "temp" not in temp:
            self.checkoutput("mkdir " + dirs)
        self.checkoutput("chmod 777 " + dirs)
        return dirs

    def check_adb_status(self, waitTime=100):
        '''
        check adb status
        @param waitTime: the time of detection
        @return: adb status : boolean
        '''
        i = 0
        waitCnt = waitTime / 5
        while i < waitCnt:
            command = "adb devices"
            cmd = command.split()
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            adb_devices = proc.communicate()[0].decode()
            rc = proc.returncode
            if rc == 0 and self.serialnumber in adb_devices and \
                    len(self.serialnumber) != 0:
                return True
            i = i + 1
            time.sleep(5)
            logging.debug("Still waiting..")
        return False

    def wait_and_tap(self, searchKey, attribute, times=5):
        '''
        wait for android widget then tap it , wait 5 seconds
        @param searchKey: widget key
        @param attribute: widget attr
        @return:
        '''
        for _ in range(times):
            if self.find_element(searchKey, attribute):
                self.find_and_tap(searchKey, attribute)
                return 1
            time.sleep(1)

    def wait_element(self, searchKey, attribute):
        '''
        wait for android widget , wait 5 seconds
        @param searchKey: widget key
        @param attribute: widget attr
        @return:
        '''
        for _ in range(5):
            if self.find_element(searchKey, attribute):
                return 1
            time.sleep(1)

    def find_element(self, searchKey, attribute, extractKey=None):
        '''
        find element in the ui dump info
        @param searchKey: element key
        @param attribute: element attr
        @param extractKey:
        @return:
        '''
        logging.info(f'find {searchKey}')
        filepath = os.path.join(self.logdir, self.DUMP_FILE)
        self.uiautomator_dump(filepath)
        xml_file = minidom.parse(filepath)
        itemlist = xml_file.getElementsByTagName('node')
        for item in itemlist:
            # print(item.attributes[attribute].value)
            if searchKey == item.attributes[attribute].illuminance_value:
                logging.info(
                    item.attributes[attribute].illuminance_value if extractKey is None else item.attributes[extractKey].illuminance_value)
                return item.attributes[attribute].illuminance_value if extractKey is None else item.attributes[extractKey].illuminance_value
        return None

    def find_pos(self, searchKey, attribute):
        '''
        find widget position
        @param searchKey: widget key
        @param attribute: widget attr
        @return: position x , position y : tuple
        '''
        logging.info('find_pos')
        filepath = self.logdir + self.DUMP_FILE
        self.uiautomator_dump(filepath)
        xml_file = minidom.parse(filepath)
        itemlist = xml_file.getElementsByTagName('node')
        bounds = None
        for item in itemlist:
            logging.debug(f'try to find {searchKey} - {item.attributes[attribute].illuminance_value}')
            if searchKey == item.attributes[attribute].illuminance_value:
                bounds = item.attributes['bounds'].illuminance_value
                break
        if bounds is None:
            logging.error("attr: %s not found" % attribute)
            return -1, -1
        bounds = re.findall(r'\[(\d+)\,(\d+)\]', bounds)
        # good for debugging button press coordinates
        # print(bounds)
        x_start, y_start = bounds[0]
        x_end, y_end = bounds[1]
        x_midpoint, y_midpoint = (int(x_start) + int(x_end)) / 2, (int(y_start) + int(y_end)) / 2
        logging.info(f'{x_midpoint} {y_midpoint}')
        return (x_midpoint, y_midpoint)

    def find_and_tap(self, searchKey, attribute):
        '''
        find widget and tap
        @param searchKey: widget key
        @param attribute: widget attr
        @return: position x , position y : tuple
        '''
        logging.info(f'find_and_tap {searchKey}')
        x_midpoint, y_midpoint = self.find_pos(searchKey, attribute)
        if (x_midpoint, y_midpoint) != (-1, -1):
            self.tap(x_midpoint, y_midpoint)
            # time.sleep(1)
        return x_midpoint, y_midpoint

    def text_entry(self, text, searchKey, attribute, delete=64):
        '''
        find edittext and input text
        @param text: input text
        @param searchKey: edittext key
        @param attribute: edittext attr
        @param delete: del 退格
        @return: position x , position y : tuple
        '''
        filepath = self.logdir + self.DUMP_FILE
        self.uiautomator_dump(filepath)
        xml_file = minidom.parse(filepath)
        itemlist = xml_file.getElementsByTagName('node')
        bounds = None
        for item in itemlist:
            if searchKey.upper() in item.attributes[attribute].illuminance_value.upper():
                if "EditText" in item.attributes['class'].illuminance_value:
                    bounds = item.attributes['bounds'].illuminance_value
                    break
        if bounds is None:
            return None
        bounds = re.findall(r'\[(\d+)\,(\d+)\]', bounds)
        x_start, y_start = bounds[0]
        x_end, y_end = bounds[1]
        x_midpoint, y_midpoint = (int(x_start) + int(x_end)) / 2, (int(y_start) + int(y_end)) / 2

        self.tap(x_midpoint, y_midpoint)

        # move to the end, and delete characters
        # TODO. This should be a select-all and delete but there is no easy way
        # to do this
        self.keyevent("KEYCODE_MOVE_END")
        self.delete(delete)

        # enter the text
        self.text(text)

        # hit enter
        self.keyevent("KEYCODE_ENTER")
        return x_midpoint, y_midpoint

    def wait_devices(self):
        '''
        check adb exists if not wait for one minute
        @return: None
        '''
        count = 0
        while subprocess.run(f'adb -s {self.serialnumber} shell getprop sys.boot_completed'.split(),
                             stdout=subprocess.PIPE).returncode != 0:
            flag = True
            if count % 10 == 0:
                logging.info('devices not exists')
            self.set_status_off()
            # subprocess.check_output('adb connect {}'.format(self.serialnumber), shell=True, encoding='utf-8')
            time.sleep(3)
            count += 1
            if count > 20:
                raise EnvironmentError('Lost Device')
        self.set_status_on()

    def kill_logcat_pid(self):
        '''
        kill all logcat in pc
        @return: None
        '''
        self.subprocess_run("killall logcat")

    # @connect_again
    def popen(self, command):
        '''
        run adb command over popen
        @param command: command
        @return: subprocess.Popen
        '''
        logging.debug(f"command:{self.ADB_S + self.serialnumber + ' ' + command}")
        cmd = self.ADB_S + self.serialnumber + ' ' + command
        return self.popen_term(cmd)

    def popen_term(self, command):
        return subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # preexec_fn=os.setsid)

    def checkoutput(self, command):
        '''
        run adb command over check_output
        raise error if not success
        @param command: command
        @return: feedback
        '''
        command = 'shell ' + command
        return self.checkoutput_shell(command)

    @connect_again
    def checkoutput_shell(self, command):
        command = self.ADB_S + self.serialnumber + ' ' + command
        return self.checkoutput_term(command)

    @connect_again
    def subprocess_run(self, command):
        '''
        run adb command over subporcess.run
        @param command: command
        @return: subprocess.CompletedProcess
        '''
        if not isinstance(command, list):
            command = (self.ADB_S + self.serialnumber + ' shell ' + command).split()
        return subprocess.run(command, stdout=subprocess.PIPE, encoding='utf-8').stdout

    def factory_reset_bootloader(self):
        '''
        factory reset over adb
        @return:
        '''
        self.checkoutput_term('adb reboot bootloader')
        self.set_status_off()
        for i in range(10):
            if 'fastboot' in self.checkoutput_term('fastboot devices'):
                break
            time.sleep(3)
        try:
            self.checkoutput_term('fastboot flashing unlock_critical')
            time.sleep(1)
            self.checkoutput_term('fastboot flashing unlock')
            time.sleep(1)
            self.checkoutput_term('fastboot -w')
            time.sleep(2)
        except subprocess.CalledProcessError as e:
            logging.info('Error occur')
        self.checkoutput_term('fastboot reboot')
        time.sleep(120)

    def apk_enable(self, packageName):
        '''
        apk enable
        @param packageName: apk package name
        @return: None
        '''
        output = self.checkoutput(f'pm enable {packageName}')
        return output

    def wait_for_launcher(self) -> None:
        '''
        # Wait for home launcher is available
        :return:
        '''
        log = self.popen('logcat')
        while True:
            try:
                line = log.stdout.readline()
            except UnicodeDecodeError as e:
                ...
            if 'Displayed com.google.android.tvlauncher/.MainActivity' in line:
                time.sleep(1)
                logging.info('wait for launcher')
                break
        log.terminate()
        log.send_signal(signal.SIGINT)

    def kill_setting(self) -> None:
        self.app_stop(self.SETTING_ACTIVITY_TUPLE[0])

    def kill_moresetting(self) -> None:
        for i in range(5):
            self.keyevent(4)
        self.kill_setting()
