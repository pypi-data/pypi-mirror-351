# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2024-09-26 19:00:42

def find_num_from_str(string, find_reserver=False, count='one',
                      return_int=False):
    """
    查找字符串中的数字，并返回数字字符串
    :param string:
    :param find_reserver: True=从前往后找；False=从后往前找
    :param count: one/all
    :param return_int:True=返回int；False=返回str
    :return: num str or ''
    """
    num_str = ''
    if not string:
        return num_str

    for char in string:
        if '0' <= char <= '9':
            num_str += char
        else:
            break

    if return_int:
        return int(num_str)
    else:
        return num_str


def find_key_strings(key_strs, source_str, separator=None):
    found_str = ''
    if not key_strs or not source_str:
        return found_str
    key_strs_split = key_strs.split(separator)
    for key_str in key_strs_split:
        key_str = key_str.strip()
        if key_str in source_str:
            found_str += key_str + separator

    found_str = found_str[:-1] if found_str.endswith(separator) else found_str
    return found_str


def join_str(str1, str2, separator=','):
    if (str1 is None or str1 == '' or
            str2 is None or str2 == ''):
        return str1 or str2
    if separator is None:
        return str1 + str2
    return f"{str1}{separator}{str2}"


def get_size(string, encoding_type='utf-8'):
    if string is None:
        return 0
    return len(string.encode(encoding_type))


def len2(string):
    if string is None:
        return 0
    return len(string)


def truncate_str_to_size(s, byte_size, encoding_type='utf-8'):
    """
    按字节大小（非字符个数）进行截取
    :param s:
    :param byte_size:
    :param encoding_type:
    :return:
    """
    if s is None:
        return None
    if byte_size < 0:
        return s
    encoded = s.encode(encoding_type)
    while len(encoded) > byte_size:
        s = s[:-1]
        encoded = s.encode(encoding_type)
    return s
