import os
import json

# 配置文件路径
config_file_path = 'C:/Server_Data/Data.json'


# 保存邮箱和授权码 (GUI将调用此函数)
# 在gui.py中，我将其视为 write_config_main，但实际上就是这个 save_config
def save_config(email, password, target_email, last_user_time, user_clear_time, cpu_threshold, memory_threshold, email_cooldown):
    config = {
        "email": email,
        "password": password,
        "target_email": target_email,
        "last_user_time": str(last_user_time), # 确保保存为字符串
        "user_clear_time": str(user_clear_time), # 确保保存为字符串
        "cpu_threshold": str(cpu_threshold), # 新增
        "memory_threshold": str(memory_threshold), # 新增
        "email_cooldown": str(email_cooldown), # 新增邮件冷却时间
    }
    try:
        with open(config_file_path, 'w') as f:
            json.dump(config, f, indent=4)
        # print(f"邮箱配置文件已保存到 '{config_file_path}'") # GUI会处理消息
        return True
    except Exception as e:
        # print(f"保存配置文件失败: {e}") # GUI会处理消息
        return False


# 读取邮箱配置 (供 read_config_main 调用)
def load_config():
    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'r') as f:
                config = json.load(f)
            # 提供默认值以防某些键丢失
            return (
                config.get("email"),
                config.get("password"),
                config.get("target_email"),
                config.get("last_user_time", "1.0"), # 默认1分钟
                config.get("user_clear_time", "3600"), # 默认3600秒
                config.get("cpu_threshold", "80"), # 新增，默认80%
                config.get("memory_threshold", "80"), # 新增，默认80%
                config.get("email_cooldown", "600") # 新增，默认600秒
            )
        except json.JSONDecodeError:
            # print(f"配置文件 '{config_file_path}' 格式错误.") # GUI会处理
            return None, None, None, None, None, None, None, None # 调整返回数量
        except Exception as e:
            # print(f"读取配置文件时发生错误: {e}") # GUI会处理
            return None, None, None, None, None, None, None, None # 调整返回数量
    else:
        return None, None, None, None, None, None, None, None # 调整返回数量


# 获取用户输入(邮箱和授权码) - 此函数将不再被GUI版本直接使用
# def get_user_input():
#     email = input("请输入您的邮箱: ")
#     password = input("请输入您的授权码: ")
#     target_email = input("请输入接收方邮箱:")
#     last_user_time = input("请输入检测间隔(分钟):")
#     user_clear_time = input("请输入清空控制台时间间隔(秒):")
#     save_config(email, password, target_email, last_user_time, user_clear_time)
#     return email, password, target_email, last_user_time, user_clear_time


# 主逻辑：读取配置 (供GUI调用，无交互)
def read_config_main():
    email, password, target_email, last_user_time, user_clear_time, cpu_threshold, memory_threshold, email_cooldown = load_config()
    if email is not None:
        # print(f"已加载配置: 邮箱: {email}, 接收方邮箱: {target_email}") # GUI会处理消息
        return email, password, target_email, last_user_time, user_clear_time, cpu_threshold, memory_threshold, email_cooldown
    else:
        # print("未检测到配置文件或配置文件损坏。GUI将使用默认值或提示输入。") # GUI会处理消息
        # 返回一组默认值或None，让GUI知道需要初始化
        return None, None, None, "1.0", "3600", "80", "80", "600" # 默认值

# 为了兼容旧的 main.py（如果它仍然尝试独立运行并调用 get_user_input）
# 我们可以保留 get_user_input，但理想情况下它不应该再被调用
def get_user_input_fallback():
    print("警告: get_user_input_fallback 被调用。这通常不应在GUI模式下发生。")
    email = "fallback_email@example.com"
    password = "fallback_password"
    target_email = "fallback_recipient@example.com"
    last_user_time = "5"
    user_clear_time = "60"
    cpu_threshold = "90" # Fallback
    memory_threshold = "90" # Fallback
    email_cooldown = "600" # Fallback
    # save_config(email, password, target_email, last_user_time, user_clear_time, cpu_threshold, memory_threshold, email_cooldown) # 通常不应在fallback中保存
    return email, password, target_email, last_user_time, user_clear_time, cpu_threshold, memory_threshold, email_cooldown
