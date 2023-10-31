#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import ctypes
import os
import platform
import psutil
import subprocess


def get_free_space_GiB(folder):
    """ Return folder/drive free space (in Giga Bytes)
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value / 1024 / 1024 // 1024
    else:
        st = os.statvfs(folder)
        return st.f_bavail * st.f_frsize / 1024 / 1024 // 1024


def checkprocess(processname):
    """ 检查某个进程是否存在
    """
    try:
        for proc in psutil.process_iter():
            if proc.name() == processname:
                return True
        else:
            return False
    except (psutil.ZombieProcess, psutil.NoSuchProcess):
        return False
    except:
        return False


def runProcess(commands):
    p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    while True:
        # returns None while subprocess is running
        retcode = p.poll()
        line = p.stdout.readline()
        yield line
        if retcode is not None:
            break
    p.stdout.close()
