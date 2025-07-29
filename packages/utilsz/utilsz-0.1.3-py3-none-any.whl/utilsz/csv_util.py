# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2024-09-27 08:48:47
import os

import pandas

from . import file_util


def read_csv_file(file_path, has_head=True, encoding='utf-8-sig'):
    """
    读取csv文件并返回列表，元素为map，表头为map的key
    :param file_path:
    :param has_head: True=第一行作为key；False=列名作为key
    :param encoding: 默认值；utf-8-sig
    :return:元素为map的list
    """
    if not os.path.exists(file_path):
        return None

    df = pandas.read_csv(file_path, sep=',', header=None, encoding=encoding)
    read_list = []
    if not has_head:
        header_list = df.columns.tolist()
    else:
        header_list = None

    for index, row in df.iterrows():
        if index == 0 and has_head:
            # cvs的第一行作为map的key
            header_list = row.tolist()
            continue
        data_dict = dict(zip(header_list, row.tolist()))
        read_list.append(data_dict)
    return read_list


def write_csv_file(file_path, list_map, encoding='utf-8-sig'):
    file_util.create_parent_directory(file_path)
    df = pandas.DataFrame(list_map)
    # 将数据保存为 CSV 文件，注意编码格式为utf-8-sig提高utf-8兼容性；该sig会添加bom开头，否则在某些系统比如windows的excel程序打开会乱码
    df.to_csv(file_path, index=False, encoding=encoding)
    return True
