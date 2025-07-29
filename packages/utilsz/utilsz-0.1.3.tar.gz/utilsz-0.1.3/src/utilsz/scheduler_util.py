# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2024-10-06 20:16:21
import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger


def scheduler_demo():
    """
    伪代码，供参考
    BlockingScheduler 周期性执行时，首次执行总是在第一个周期后，以下是立即执行后再周期性执行的伪代码
    :return:
    """
    # # 设置调度器日志级别为 WARNING，避免过多打印干扰
    # logging.getLogger('apscheduler').setLevel(logging.WARNING)
    # scheduler = BlockingScheduler()
    # # 立即运行一次，之后周期性执行
    # trigger = OrTrigger([DateTrigger(run_date=datetime.now()), IntervalTrigger(minutes=1)])
    # scheduler.add_job(function, trigger)
    # scheduler.start()
