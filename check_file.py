import os
import shutil
from termcolor import colored


# 检测路径是否存在，如果不存在,创建，如果存在，不创建
def check_and_create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"文件夹'{path}'已创建")


# 检测文件是否存在，若不存在，创建
def check_and_create_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:  # 创建一个空文件
            pass
        print(f"文件'{file_path}'已创建")


def check_and_copy_or_none():
    # 获取项目根目录下的 index.html 文件路径
    project_index_path = os.path.join(os.path.dirname(__file__), 'index.html')  # 当前文件所在目录
    # C 盘根目录下的 index.html 文件路径
    c_index_path = r'C:\Server_Data'

    # 检查 C 盘根目录下是否存在 index.html
    if os.path.isfile(c_index_path):
        print(colored("200-OK\n", 'green'))
    else:
        # 复制文件
        if os.path.isfile(project_index_path):  # 确保源文件存在
            shutil.copy(project_index_path, c_index_path)
            print(colored("200-OK\n", 'green'))
        else:
            print(f"未找到项目目录下的 index.html 文件: {project_index_path}")
