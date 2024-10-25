import os
import json

# 配置文件路径
config_file_path = 'C:/Server_Data/Data.json'


# 保存邮箱和授权码
def save_config(email, password, target_email):
    config = {
        "email": email,
        "password": password,
        "target_email": target_email,  # 接收方邮箱

    }
    with open(config_file_path, 'w') as f:
        json.dump(config, f)
    print(f"邮箱配置文件已保存到 '{config_file_path}'")


# 读取邮箱配置
def load_config():
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as f:
            config = json.load(f)
        return config["email"], config["password"], config["target_email"]
    else:
        return None, None, None


# 获取用户输入(邮箱和授权码)
def get_user_input():
    email = input("请输入您的邮箱: ")
    password = input("请输入您的授权码: ")
    target_email = input("请输入接收方邮箱")
    save_config(email, password, target_email)
    return email, password, target_email


# 主逻辑：读取配置或获取用户输入
def read_config_main():
    if os.path.exists(config_file_path):
        choice = input("检测到配置文件，是否拉取并使用 (y/n): ")
        if choice.lower() == 'y':
            email, password, target_email = load_config()  # 读取接收方邮箱
            print(f"已加载配置: 邮箱: {email}, 接收方邮箱: {target_email}")
        else:
            email, password, target_email = get_user_input()  # 获取所有输入
    else:
        email, password, target_email = get_user_input()  # 获取所有输入

    return email, password, target_email  # 返回所有值
