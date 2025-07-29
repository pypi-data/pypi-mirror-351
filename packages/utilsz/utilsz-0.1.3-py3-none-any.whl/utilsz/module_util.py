# encoding: utf-8
# desc: 
# auth: Jack Jiang
# date: 2024-11-19 16:34:52
import importlib.util


def load_module(module_name, file_path):
    """
    动态加载python文件
    :param module_name: 加载后的名字
    :param file_path: py文件路径
    :return: 该模块对象，可直接访问属性、方法等
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def format_obj(obj):
    for attr_name in dir(obj):
        attr_value = getattr(obj, attr_name, None)
        print(f"{attr_name}: {attr_value}")