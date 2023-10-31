#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import configparser


class ReadConfig:
    """定义一个读取配置文件的类"""

    def __init__(self, filepath=None):
        if filepath:
            configpath = filepath
        else:
            root_dir = os.path.dirname(os.path.abspath('.'))
            configpath = os.path.join(root_dir, "autoplot.conf")
        self.cf = configparser.ConfigParser()
        self.cf.read(configpath, encoding='utf-8')

    def read_config(self, section, option):
        return self.cf.get(section, option)
