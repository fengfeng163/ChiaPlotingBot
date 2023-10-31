#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from logger import Logger
from readconfig import ReadConfig
from functions import *
import logger
import time
from pathlib import Path
import shlex

# ---------------------------------------------------------
# 安装说明
# pip install psutil
# 使用说明(后台启动)
# nohup python autoplot.py &
# ------------------------------- -------------------------------

logger = Logger('autoplot').get_logger()


def main():
    # TODO 禁止多重启动

    print('=============启动绘图=============')
    logger.info('=============启动绘图=============')

    # 读取数据硬盘配置文件

    plotconf = ReadConfig('autoplot.conf')
    disks = plotconf.read_config('DATA', 'path')
    needSeconds = plotconf.read_config('FORECAST', 'need_seconds')
    if len(disks) <= 0:
        logger.error('没有读取到有效输出路径,退出！')
        return

    targetdisk = {}
    total = 0
    for datadisk in disks.splitlines():
        if len(datadisk) == 0: continue

        # 检查是否为合法路径（路径是否存在）
        diskpath = Path(datadisk)
        if not diskpath.is_dir():
            logger.warning('[%s]不是有效路径！' % datadisk)
            continue

        free_space_by_GiB = get_free_space_GiB(datadisk)
        cnt = free_space_by_GiB // 101  # 注意需提高本计算的精确度
        if free_space_by_GiB <= 0:
            # 不存在的话输出警告日志
            logger.warning('[%s]不是合法的路径!' % datadisk)
            continue
        elif cnt < 1:
            logger.warning('[%s]只剩余空间%.2fGiB,无法绘新图!' % (datadisk, free_space_by_GiB))
            continue

        total += cnt
        logger.info('[%s]剩余空间为%.2fGiB, 可绘图%d张。' % (datadisk, free_space_by_GiB, cnt))

        targetdisk[datadisk] = cnt
    if total > 0:
        end_time = time.localtime(time.time() + int(needSeconds) * total)
        end_time_str = time.strftime("%Y-%m-%d %H:%M:%S", end_time)
        logger.info('目录准备完毕，本次总计可以绘图%d张,预计结束时间:%s。' % (total, end_time_str))
        startplot(targetdisk, needSeconds)
    else:
        logger.info('目录准备完毕，暂无空间可用于绘图输出。')

    # 关闭路径配置文件

    logger.info('=============启动绘图-完成=============')
    print('=============启动绘图-完成=============')


def startplot(targetdiskdic, needSeconds):
    ''' 逐个对对象路径启动绘图程序 '''
    # 启动绘图
    plotconf = ReadConfig('autoplot.conf')
    needSeconds = plotconf.read_config('FORECAST', 'need_seconds')
    thread_num = plotconf.read_config('PLOTTER', 'thread_num')
    farmer_key = plotconf.read_config('PLOTTER', 'farmer_key')
    pool_key = plotconf.read_config('PLOTTER', 'pool_key')
    temp_dir = plotconf.read_config('PLOTTER', 'temp_dir')
    temp2_dir = plotconf.read_config('PLOTTER', 'temp2_dir')
    if len(temp2_dir) == 0: temp2_dir = temp_dir

    last_start_time = 0
    last_cnt = 0
    for (disk, cnt) in targetdiskdic.items():
        logger.info('开始处理%s，预计绘图%d张' % (disk, cnt))
        # 一次只允许启动一个chia_plot实例
        while checkprocess('chia_plot'):
            # 如果存在，等候300秒再做检查
            logger.info('------前面任务尚未完成，等候5分钟-----')
            time.sleep(300)
        if last_start_time > 0:
            # 计算前一次任务平均花费时间
            spent_seconds = time.time() - last_start_time
            spent_hours = spent_seconds / 3600
            spent_minutes = spent_seconds / 60
            average_seconds = spent_seconds // last_cnt
            average_minutes = average_seconds / 60
            logger.info('>>>>>>前一次任务完成绘图%d张，共计花费%.2f小时, 每张图花费时间%d秒，约%.2f分钟<<<<<<' \
                        % (last_cnt, spent_hours, average_seconds, average_minutes))

        # 实时检测磁盘空间，如果不够绘制一张图，跳过本目录绘图（因为可能有其它进程正在向本目录输出）
        free_space_by_GiB = get_free_space_GiB(disk)
        real_cnt = free_space_by_GiB // 101  # 注意需提高本计算的精确度
        if real_cnt <= 0:
            logger.warning('%s磁盘空间仅剩%.2fGiB,无法绘制新图，自动对下一个目录进行绘制！' % (disk, free_space_by_GiB))
            continue

        # 开始启动
        last_cnt = real_cnt
        last_start_time = time.time()

        end_time = time.localtime(time.time() + int(needSeconds) * real_cnt)
        end_time_str = time.strftime("%Y-%m-%d %H:%M:%S", end_time)
        logger.info('----------启动[%s]的绘图程序---------' % disk)
        logger.info('本次绘图[%d]张，单张绘图时间[%d]秒，预计结束时间%s' % (real_cnt, int(needSeconds), end_time_str))
        date_str = time.strftime('%Y%m%d', time.localtime(time.time()))
        plot_str = f'chia_plot -n {int(real_cnt)} -r {thread_num} -t {temp_dir} -2 {temp2_dir} -d {disk} -f {farmer_key} -p {pool_key}'
        logger.info('启动[%s]的绘图程序命令。绘图详细日志参考logs/plot%s.log。' % (disk, date_str))
        logger.info('命令详细：%s' % plot_str)
        # args = shlex.split('tail -f 5.txt')
        args = shlex.split(plot_str)
        print('args%r' % args)
        for line in runProcess(args):
            logline = line.strip('\n')  # 去掉换行符
            # print(logline)
            logger.info(logline)
        logger.info('----------[%s]的绘图程序完成，共计绘图%d张。---' % (disk, real_cnt))


if __name__ == "__main__":
    main()
