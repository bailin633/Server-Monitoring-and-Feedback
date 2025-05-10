
import os

# 这些导入仍然是其他模块的基础，但main.py本身不再直接使用它们来执行逻辑
from windows_info import get_os_info, get_windows_version_info, get_cpu_usage, get_memory_usage, get_cpu_core_count, \
    get_virtual_memory_usage,get_running_process_count,get_mem_info
# from clear_console import clear_console # GUI不需要
from check_file import check_and_create_file, check_and_create_folder, check_and_copy_or_none
from config import read_config_main # GUI会直接调用
from send_email import send_alert_email # GUI会直接调用
from index import open_html # GUI可能会有帮助按钮调用此功能


def run_initial_setup():
    """
    执行程序首次运行或每次启动时可能需要的文件和文件夹检查。
    这个函数可以被 gui.py 在启动时调用。
    """
    print("执行初始文件/文件夹设置...")
    check_and_copy_or_none()
    folder_path = 'C:/Server_Data'
    file_path = os.path.join(folder_path, 'Data.json')
    check_and_create_folder(folder_path)
    check_and_create_file(file_path)
    print("初始文件/文件夹设置完成。")

