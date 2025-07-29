# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2024-09-27 10:06:16
import os
import shutil


def create_parent_directory(file_path):
    parent_directory = os.path.dirname(file_path)
    # 如果是当前目录，则parent_directory为''且makedirs抛异常FileNotFoundError
    if parent_directory and not os.path.exists(parent_directory):
        os.makedirs(parent_directory)


def get_file_list(dir_path: str, if_recursive: bool = True) -> list:
    file_list = []
    if if_recursive:
        # 递归遍历文件夹
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_list.append(file_path)
    else:
        # 遍历文件夹
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            # 判断是否为文件
            if os.path.isfile(file_path):
                file_list.append(file_path)
                print(file_path)
    return file_list


def read_file_to_string(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"文件 {file_path} 不存在。")
        return ""
    except UnicodeDecodeError:
        print("读取文件时编码错误，请确保文件编码为utf-8。")
        return ""


def copyfile(src, dest):
    create_parent_directory(dest)
    return shutil.copy(src, dest)
