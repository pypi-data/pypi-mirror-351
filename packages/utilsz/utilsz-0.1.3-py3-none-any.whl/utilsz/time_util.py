# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2024-10-24 15:11:56
import random
import time
from datetime import datetime


def get_cur_datetime_str(str_format='%Y-%m-%d %H:%M:%S'):
    return datetime.now().strftime(str_format)


def sleep_ms(ms):
    time.sleep(ms * 0.001)
    pass


def sleep_random_ms(min_ms, max_ms):
    # 生成一个0到1之间的随机浮点数
    x = random.random()
    s = (min_ms + x * (max_ms - min_ms)) * 0.001
    time.sleep(s)
    return int(s * 1000)


def format_time_interval(start_time_s, end_time_s):
    """
    格式化时间间隔
    :param start_time_s:
    :param end_time_s:
    :return:
    """
    total_seconds = (end_time_s - start_time_s)
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    years, days = divmod(days, 365)
    months, days = divmod(days, 30)
    if int(years) > 0:
        return f"{int(years)}年{int(months)}月{int(days)}天{int(hours)}时{int(minutes)}分{int(seconds)}秒"
    elif int(months) > 0:
        return f"{int(months)}月{int(days)}日{int(hours)}时{int(minutes)}分{int(seconds)}秒"
    elif int(days) > 0:
        return f"{int(days)}日{int(hours)}时{int(minutes)}分{int(seconds)}秒"
    elif int(hours) > 0:
        return f"{int(hours)}时{int(minutes)}分{int(seconds)}秒"
    elif int(minutes) > 0:
        return f"{int(minutes)}分{int(seconds)}秒"
    else:
        return f"{int(seconds)}秒"


def get_cur_time_ms():
    # 获取当前时间戳（以秒为单位）
    timestamp = time.time()
    # 将时间戳转换为毫秒
    millisecond = int(timestamp * 1000)
    return millisecond


def ms_to_datetime(ms, str_format='%Y-%m-%d %H:%M:%S'):
    # 将毫秒数转换为秒数
    seconds = ms / 1000
    # 将秒数转换为 datetime 对象
    dt = datetime.fromtimestamp(seconds)
    # 格式化 datetime 对象为年月日时分秒的字符串
    formatted_time = dt.strftime(str_format)
    # %f是微秒，取前3位表示毫秒
    if '%f' in str_format:
        return formatted_time[:-3]
    else:
        return formatted_time


def test_sleep_random_ms():
    ms = sleep_random_ms(1000, 5000)
    print(f'test_sleep_random_ms: 已延迟{ms}ms')
    ms = sleep_random_ms(1000, 5000)
    print(f'test_sleep_random_ms: 已延迟{ms}ms')
    ms = sleep_random_ms(1000, 5000)
    print(f'test_sleep_random_ms: 已延迟{ms}ms')


def test_format_time_interval():
    start_time_s = time.time()
    time.sleep(1)
    print(f'test_format_time_interval: 已延迟 {format_time_interval(start_time_s, time.time())}')
    start_time_s = time.time()
    time.sleep(2)
    print(f'test_format_time_interval: 已延迟 {format_time_interval(start_time_s, time.time())}')
    time.sleep(3)
    print(f'test_format_time_interval: 已延迟 {format_time_interval(start_time_s, time.time())}')


if __name__ == '__main__':
    # test_sleep_random_ms()
    test_format_time_interval()
