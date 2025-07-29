# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2024-10-10 10:11:26
import logging
import sys

# 定义一个新的日志级别，比DEBUG更低
PURE_LEVEL = logging.CRITICAL + 100
PURE_NAME = 'PURE'


def init(level=logging.INFO):
    # stream=sys.stdout：logging默认输出到stderr，导致所有日志都是红色的
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(funcName)s(): %(message)s',
                        level=level, stream=sys.stdout)


def pure(msg):
    """
    指定logging的所有handler忽略formatter，输出纯粹的消息
    使用场景：程序只有命令行没有界面时，交互的命令使用纯输出比较合适
    :return:
    """
    # 使用setlevel和remove的方式都会影响上下文，导致还原后日志输出不连续，所以采用setformatter方式
    # 需要实现2个：1. 设置不受level控制，始终输出日志；2. 设置日志不受foramtter影响

    # 1.设置不受level控制，始终输出日志
    # 将新的日志级别添加到logging模块中
    logging.addLevelName(PURE_LEVEL, PURE_NAME)

    # 2.设置日志不受foramtter影响
    logger = logging.getLogger()
    org_formatters = []
    for handler in logger.handlers:
        org_formatters.append(handler.formatter)
        handler.setFormatter(None)

    logger.log(PURE_LEVEL, msg)

    # 3. 还原formatter
    for index, handler in enumerate(logger.handlers):
        if index < len(org_formatters):
            handler.setFormatter(org_formatters[index])
