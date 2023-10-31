#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import logging  # 引入logging模块
import os.path
import time


class Logger:
    def __init__(self,loggername):

        # 创建一个logger
        self.logger = logging.getLogger(loggername)
        self.logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件
        # log_path = os.path.dirname(getcwd.get_cwd())+"/logs/" # 指定文件输出路径
        log_path = os.path.dirname(__file__) + "/logs/"  # 指定文件输出路径
        # print("log_path=" + log_path)
        date_str = time.strftime('%Y%m%d', time.localtime(time.time()))
        log_file_name = log_path + 'plot' + date_str + '.log'  # 指定输出的日志文件名
        fh = logging.FileHandler(log_file_name, encoding='utf-8')  # 指定utf-8格式编码，避免输出的日志文本乱码
        fh.setLevel(logging.DEBUG)
        # print("log_file_name=" + log_file_name)
        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
        fh.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)

    # 定义一个函数，回调logger实例
    def get_logger(self):
        return self.logger


if __name__ == '__main__':
    t = Logger("hmk").get_log().debug("User %s is loging")
