import os
import json

# 配置文件路径
config_file_path = 'C:/Server_Data/Data.json'


# 保存邮箱和授权码
def save_config(email, password, target_email, last_user_time, user_clear_time):
    config = {
        "email": email,
        "password": password,
        "target_email": target_email,  # 接收方邮箱
        "last_user_time": last_user_time,
        "user_clear_time": user_clear_time,
    }
    with open(config_file_path, 'w') as f:
        json.dump(config, f)
    print(f"邮箱配置文件已保存到 '{config_file_path}'")


# 读取邮箱配置
def load_config():
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as f:
            config = json.load(f)
        return config["email"], config["password"], config["target_email"], config["last_user_time"], config[
            "user_clear_time"]
    else:
        return None, None, None, None, None


# 获取用户输入(邮箱和授权码)
def get_user_input():
    email = input("请输入您的邮箱: ")
    password = input("请输入您的授权码: ")
    target_email = input("请输入接收方邮箱:")
    last_user_time = input("请输入检测间隔(分钟):")
    user_clear_time = input("请输入清空控制台时间间隔(秒):")
    save_config(email, password, target_email, last_user_time, user_clear_time)
    return email, password, target_email, last_user_time, user_clear_time


# 主逻辑：读取配置或获取用户输入
def read_config_main():
    # 先检查配置文件是否存在
    if os.path.exists(config_file_path):
        # 文件存在，询问用户是否使用已保存的配置
        choice = input("检测到配置文件，是否拉取并使用 (y/n): ")
        if choice.lower() == 'y':
            email, password, target_email, last_user_time, user_clear_time = load_config()  # 读取接收方邮箱
            print(f"已加载配置: 邮箱: {email}, 接收方邮箱: {target_email}")
        elif choice.lower() == 'n':
            email, password, target_email, last_user_time, user_clear_time = get_user_input()  # 获取所有输入
        else:
            print("程序已中断，回车退出重启...")
            input()  # 等待用户按回车
            return None, None, None, None, None  # 返回空值，表示程序中断
    else:
        # 文件不存在，直接获取用户输入
        print("未检测到配置文件，请输入邮箱和授权码。")
        email, password, target_email, last_user_time, user_clear_time = get_user_input()  # 获取所有输入

    return email, password, target_email, last_user_time, user_clear_time  # 返回所有值
