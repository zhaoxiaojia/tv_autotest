# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 13:36
# @Author  : chao.li
# @File    : serial_crt.py
# @Project : kpi_test
# @Software: PyCharm


import logging
import re
import signal
import time

import pytest
import serial


class SerialCtrl:
    '''
    serial command control
    Attributes:
        serial_port : serial port
        baud : baud
        ser : serial.Serial instance
        ethernet_ip : ip address
        status : serial statuc
    '''

    def __init__(self, serial_port='', baud=''):
        self.serial_port = serial_port or pytest.config['serial_port']
        self.baud = baud or pytest.config['baudrate']
        logging.info(f"self.serial_port: {self.serial_port},self.baud: {self.baud}")
        self.ser = ''
        self.ethernet_ip = ''
        self.uboot_time = 0
        try:
            self.ser = serial.Serial(self.serial_port, self.baud)
            # self.ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
            # self.ser.parity = serial.PARITY_NONE  # set parity check: no parity
            # self.ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
            # self.ser.timeout = 1  # non-block read - timeout block read
            # self.ser.xonxoff = False  # disable software flow control
            # self.ser.rtscts = False  # disable hardware (RTS/CTS) flow control
            # self.ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
            # self.ser.writeTimeout = 2  # timeout for write
            logging.info('the serial port %s-%s is opened' % (self.serial_port, self.baud))
        except serial.serialutil.SerialException as e:
            logging.info(f'not found serial:{e}')
        if isinstance(self.ser, serial.Serial):
            self.status = self.ser.isOpen()
        else:
            self.status = False
        if self.ethernet_ip:
            logging.info('get ip ：%s' % self.ethernet_ip)
        logging.info('the status of serial port is {}'.format(self.status))

    def get_ip_address(self, inet='ipv4'):
        '''
        get ip address
        @param inet: inet type ipv4 or ipv6
        @return:
        '''
        ip, eth0Ip, wlanIp, ppp0Ip = '', '', '', ''
        logging.info('getting ip info through the serial port')
        self.write('ifconfig')
        time.sleep(2)
        ipInfo = ''.join([i.decode('utf-8') for i in self.ser.readlines()]).split('TX bytes:')
        logging.info(ipInfo)
        if ipInfo == ['']:
            logging.info('no ip')
            return None
        for i in ipInfo:
            if 'eth0' in i:
                if inet == 'ipv4':
                    eth0Ip = re.findall(r'inet addr:(.*?)  Bcast', i, re.S)
                if inet == 'ipv6':
                    eth0Ip = re.findall(r'inet6 addr:(.*?)  Bcast', i, re.S)
                return eth0Ip[0]
            if 'wlan0' in i:
                wlanIp = re.findall(r'inet addr:(.*?)  Bcast', i, re.S)
                return wlanIp[0]
            if 'ppp0' in i:
                ppp0Ip = re.findall(r'inet addr:(.*?)  P-t-P', i, re.S)
                return ppp0Ip[0]
        logging.info('Devices no ip info')
        return None

    def write_pipe(self, command):
        '''
        execute the command , get feecback
        @param command: command
        @return: feedback
        '''
        self.ser.write(bytes(command + '\r', encoding='utf-8'))
        logging.info(f'=> {command}')
        time.sleep(0.1)
        data = self.recv()
        logging.debug(data.strip())
        return data

    def enter_uboot(self):
        '''
        enter in uboot
        @return: uboot status : boolean
        '''
        self.write('reboot')
        start = time.time()
        info = ''
        while time.time() - start < 30:
            logging.debug(f'uboot {self.ser.read(100)}')
            try:
                info = self.ser.read(100).decode('utf-8')
                logging.info(info)
            except UnicodeDecodeError as e:
                logging.warning(e)
            # Todo
        logging.info('no uboot info printed,please confirm manually')

    def enter_kernel(self):
        '''
        enter in kernel
        @return: kernel status : boolean
        '''
        self.write('reset')
        self.ser.readlines()
        time.sleep(2)
        start = time.time()
        info = ''
        while time.time() - start < 60:
            try:
                info = self.ser.read(10000).decode('utf-8')
                logging.info(info)
            except UnicodeDecodeError as e:
                logging.warning(e)
            # Todo
        logging.info('no kernel message captured,please confirm manually')

    def write(self, command):
        '''
        enter in kernel
        @param command: command
        @return:
        '''
        self.ser.write(bytes(command + '\r', encoding='utf-8'))
        logging.info(f'=> {command}')
        time.sleep(1)

    def recv(self):
        '''
        get feedback from buffer
        @return: feedback
        '''
        while True:
            data = self.ser.read_all()
            if data == '':
                continue
            else:
                break
            time.sleep(0.02)
        return data.decode('utf-8')

    def recv_until_pattern(self, pattern=b'', timeout=60):
        '''
        keep get feedback from buffer until pattern has been catched
        @param pattern: pattern
        @param timeout: timeout
        @return: contains the printing of keywords
        '''
        start = time.time()
        result = []
        while True:
            if time.time() - start > timeout:
                if pattern:
                    raise TimeoutError('Time Out')
                return result
            try:
                log = self.ser.readline()
            except Exception:
                log = ''
            if not log:
                continue
            # logging.info(log)
            result.append(log)
            if pattern and pattern in log:
                return result

    def receive_file_via_serial(self, output_file):
        try:
            with open(output_file, 'wb') as file:
                while True:
                    data = self.ser.read(1024)
                    if not data:
                        break
                    file.write(data)
            print("file transfer complete")
        except serial.SerialException as e:
            print("serial port connection error:", str(e))
        except Exception as e:
            print("Warning :", str(e))

    def kill_app(self, app_name):
        for _ in range(5):
            pid = 0
            time.sleep(10)
            self.write(f'ps -ef|grep -v root|grep {app_name}')
            info = self.recv()
            logging.info(info)
            pid = re.findall(rf'{app_name}\s+(\d+)\s+', info, re.S)
            if pid:
                logging.info(f'pid  {pid}')
                self.write(f'kill -9 {pid[0]}')
            else:
                break

    def __del__(self):
        if type(self.ser) == serial.Serial:
            self.ser.close()

# ser = SerialCtrl('/dev/cu.usbserial-gggggggg1', 115200)
# ser.write('\x1A')
# ser.write('bg')
# ser.write('cat /sys/class/hdmirx/hdmirx0/info')
# print(ser.recv())
