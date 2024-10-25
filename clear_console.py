import os


def clear_console():
    if os.name == 'nt':
        os.system('cls')  # Windows 系统
    else:
        os.system('clear')  # Linux/Mac 系统


def get_user_clear_time():
    user_clear_time = int(input("请输入间隔多久清空控制台(秒):"))
    return user_clear_time
