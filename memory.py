#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys
import signal
import time
import json
import telnetlib
import requests
import configparser
from parse import parse

class tn_session:
    def __init__ (self, ip, uname, passw):
        self.ip = ip
        self.uname = uname
        self.passw = passw

        self.instance = telnetlib.Telnet(ip)
        self.file = None
        self.json_array = []


class mem_unit:
    def __init__(self):
        self.peak = 0
        self.size = 0
        self.lck = 0
        self.hwm = 0
        self.rss = 0
        self.data = 0
        self.stk = 0
        self.exe = 0
        self.lib = 0
        self.pte = 0
        self.swap = 0

    def dump(self):
        js = '{'
        js += '"timestamp":"{}",'.format(time.strftime('%H:%M:%S'))
        js += '"peak":{},'.format(self.peak)
        js += '"size":{},'.format(self.size)
        js += '"lck":{},'.format(self.lck)
        js += '"hwm":{},'.format(self.hwm)
        js += '"rss":{},'.format(self.rss)
        js += '"data":{},'.format(self.data)
        js += '"stk":{},'.format(self.stk)
        js += '"exe":{},'.format(self.exe)
        js += '"lib":{},'.format(self.lib)
        js += '"pte":{},'.format(self.pte)
        js += '"swap":{}'.format(self.swap)
        js += '}'
        return json.loads(js)

    def parse(self, resp):
        for i in range(len(resp) - 1):
            val = parse('{}:{} kB', resp[i])
            res = int(str.strip(str(val[1])))

            if 'Peak' in val[0]:
                unit.peak = res
            elif 'Size' in val[0]:
                unit.size = res
            elif 'Lck' in val[0]:
                unit.lck = res
            elif 'HWM' in val[0]:
                unit.hwm = res
            elif 'RSS' in val[0]:
                unit.rss = res
            elif 'Data' in val[0]:
                unit.data = res
            elif 'Stk' in val[0]:
                unit.stk = res
            elif 'Exe' in val[0]:
                unit.exe = res
            elif 'Lib' in val[0]:
                unit.lib = res
            elif 'PTE' in val[0]:
                unit.pte = res
            elif 'Swap' in val[0]:
                unit.swap = res

    def append_to_file(self, js, s):
        print(json.dumps(js))

        s.file = open("{}.json".format(s.ip), "w+")

        s.json_array.append(json.dumps(js).replace('\'', ''))

        s.file.write('[')
        for line in s.json_array[:-1]:
            s.file.write('{},'.format(line))
        
        s.file.write(s.json_array[-1])
        s.file.write(']')
        s.file.close()


def telnet_login(s):
    inst = s.instance

    if s.passw != '':
        inst.read_until(b"Login: ")
        inst.write(s.uname.encode('ascii') + b"\n")
        inst.read_until(b"Password: ")
        inst.write(s.passw.encode('ascii') + b"\n")
        inst.read_until(b" > ")
        inst.write("sh".encode('ascii') + b"\n")
    else:
        inst.read_until(b"login: ")
        inst.write(s.uname.encode('ascii') + b"\n")

    inst.read_until(b"# ")
    return

def telnet_exec(s, cmd):
    inst = s.instance
    inst.write(cmd.encode('ascii') + b"\n")
    out = inst.read_until(b"# ")
    return out.decode('ascii')

def get_config(cfile):
    config = []
    try:
        parser = configparser.ConfigParser()
        parser.read(cfile)
    except configparser.ParsingError:
        print('Could not parse config')
        return None

    for elem in parser.sections():
        dev = {}
        for name, value in parser.items(elem):
            dev[name] = value
        config.append(dev)

    return config

if __name__ == '__main__':
    command = 'PID=$(pidof {}) && cat /proc/$PID/status | grep Vm'.format(sys.argv[1])
    sessions = []

    config = get_config("config.ini")

    for node in config:
        sessions.append(tn_session(
            "{}.local".format(node['mac']),
            node['user'],
            node['passw']))

    for s in sessions:
        telnet_login(s)

    while True:
        for s in sessions:
            res = telnet_exec(s, command).replace('\r', '').split('\n')
            res = res[1:-1]

            unit = mem_unit()
            unit.parse(res)
            js = unit.dump()

            unit.append_to_file(js, s)

        time.sleep(1)

    for s in sessions:
        s.instance.close()

