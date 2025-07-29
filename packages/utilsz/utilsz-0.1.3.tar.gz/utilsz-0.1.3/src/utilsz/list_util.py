# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2024-09-27 09:32:16
import logging
import traceback


def is_dict_in_list(dict_to_check, list_of_dicts):
    """
    判断字典是否存在于列表中，判断标准时字典内容和列表中某字典内容相同
    不能直接用in操作符是因为in是判断map的地址而不是内容
    :param dict_to_check:
    :param list_of_dicts:
    :return:
    """
    # print(f'Kasper: {isinstance(dict_to_check, dict)} {type(dict_to_check)} {isinstance(list_of_dicts, list)}')
    if (not dict_to_check or not isinstance(dict_to_check, dict) or
            not list_of_dicts or not isinstance(list_of_dicts, list)):
        return False
    for d in list_of_dicts:
        # for key in dict_to_check:
        #     print(f'Kasper: key={key}, {dict_to_check[key]} ?= {d[key]}]')
        try:
            if all(dict_to_check[key] == d[key] for key in dict_to_check):
                return True
        except KeyError:
            logging.error(traceback.format_exc())
    return False
