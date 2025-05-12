
import os


def clear_console():
    if os.name == 'nt':
        os.system('cls')  # Windows 系统
    else:
        os.system('clear')  # Linux/Mac 系统


