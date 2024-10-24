import psutil
import smtplib
import time
import platform
import winreg
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# 获取系统资源状态
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def get_memory_usage():
    memory_info = psutil.virtual_memory()
    return memory_info.percent


def get_os_info():
    return platform.system(), platform.release()


# 获取系统版本号
os_name, os_version = get_os_info()
print(f"Operating System: {os_name} {os_version}")


def get_windows_version_info():
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")

        # 获取 DisplayVersion
        try:
            display_version, _ = winreg.QueryValueEx(registry_key, "DisplayVersion")
        except FileNotFoundError:
            display_version = "N/A"

        # 获取 ReleaseId
        try:
            release_id, _ = winreg.QueryValueEx(registry_key, "ReleaseId")
        except FileNotFoundError:
            release_id = "N/A"

        # 获取 CurrentBuild
        current_build, _ = winreg.QueryValueEx(registry_key, "CurrentBuild")

        winreg.CloseKey(registry_key)

        return {
            "显示版本": display_version,
            "ID": release_id,
            "构建版本号": current_build
        }
    except Exception as e:
        return f"Error retrieving Windows version info: {e}"


# 获取Windows的版本信息
version_info = get_windows_version_info()
print(f"Windows Version Info: {version_info}")


# 检测路径是否存在，如果不存在,创建，如果存在，不创建
def check_and_create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"文件夹'{path}'已创建")
    else:
        print(f"文件夹'{path}已存在'")


# 检测文件是否存在，若不存在，创建
def check_and_create_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:  # 创建一个空文件
            pass
        print(f"文件'{file_path}'已创建")
    else:
        print(f"文件'{file_path}'已存在")


folder_path = 'C:/Server_Data'
file_path = os.path.join(folder_path, 'Data.json')
check_and_create_folder(folder_path)
check_and_create_file(file_path)


# 获取用户输入的阈值
def get_user_thresholds():
    try:
        cpu_threshold = int(input("请输入CPU占用触发率阈值 (例如: 90): "))
        memory_threshold = int(input("请输入内存占用出发率阈值 (例如: 80): "))
    except ValueError:
        print("输入无效，请输入整数值。")
        return get_user_thresholds()  # 重新获取用户输入

    return cpu_threshold, memory_threshold


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


# 调用主函数
email, password, target_email = read_config_main()


def user_time_sleep():
    while True:
        minutes = input("请输入检测时间间隔(分钟): ")
        # 检测输入是否是数字或者小数点
        if minutes.replace('.', '', 1).isdigit() or '.' in minutes:
            try:
                user_time = float(minutes) * 60  # 转换为秒
                return user_time
            except ValueError:
                print("输入无效，请重新输入。")
        else:
            print("输入无效，请重新输入。")


last_user_time = user_time_sleep()


def clear_console():
    if os.name == 'nt':
        os.system('cls')  # Windows 系统
    else:
        os.system('clear')  # Linux/Mac 系统


def get_user_clear_time():
    user_clear_time = int(input("请输入间隔多久清空控制台"))
    return user_clear_time


############################################################################################
############################################################
############################################################################################
######################################################################
########################################################

# 邮件发送系统
def send_alert_email(body, subject, to_email):
    smtp_server = "smtp.qq.com"
    smtp_port = 465

    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = to_email
    msg['Subject'] = subject

    # 添加邮件正文
    msg.attach(MIMEText(body, 'html'))

    try:
        # 使用 SMTP_SSL 连接服务器
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(email, password)
        server.sendmail(email, to_email, msg.as_string())
        server.quit()
        print("Alert email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


# 主程序逻辑，将系统监控和邮件系统结合
def monitor_system():
    to_email = target_email  # 收件人邮箱
    cpu_threshold, memory_threshold = get_user_thresholds()  # 在监控系统中获取阈值

    clear_interval = get_user_clear_time()  # 多少时间清空一次
    last_clear_time = time.time()  # 记录上次清除的时间
    while True:
        current_time = time.time()

        # 每隔一段时间清空控制台
        if current_time - last_clear_time >= clear_interval:
            clear_console()
            last_clear_time = current_time

        # 获取系统资源使用率

        cpu_usage = get_cpu_usage()
        memory_usage = get_memory_usage()

        print(f"CPU usage: {cpu_usage}%")
        print(f"Memory usage: {memory_usage}%")

        if cpu_usage > cpu_threshold:
            subject = "CPU Usage Alert"
            body = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #0a0a0a;
                        color: #ffffff;
                    }}
                    .alert {{
                        background: linear-gradient(135deg, #ff4b2b, #ff416c);
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                        animation: pulse 1.5s infinite;
                    }}
                    @keyframes pulse {{
                        0% {{ transform: scale(1); }}
                        50% {{ transform: scale(1.05); }}
                        100% {{ transform: scale(1); }}
                    }}
                    table {{
                        width: 100%;
                        margin-top: 20px;
                        border-collapse: collapse;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                        border-radius: 10px;
                        overflow: hidden;
                    }}
                    th, td {{
                        padding: 12px;
                        text-align: left;
                        border-bottom: 1px solid #ddd;
                    }}
                    th {{
                        background-color: rgba(255, 255, 255, 0.1);
                    }}
                    tr:hover {{
                        background-color: rgba(255, 255, 255, 0.2);
                    }}
                </style>
            </head>
            <body>
                <div class="alert">
                    <h2>警报：CPU使用率超过阈值！</h2>
                    <p>当前CPU使用率: <strong>{cpu_usage}%</strong></p>
                    <p>设定的阈值: <strong>{cpu_threshold}%</strong></p>
                </div>
                <table>
                    <tr>
                        <th>监控项</th>
                        <th>使用率</th>
                    </tr>
                    <tr>
                        <td>CPU使用率</td>
                        <td>{cpu_usage}%</td>
                    </tr>
                    <tr>
                        <td>内存使用率</td>
                        <td>{memory_usage}%</td>
                    </tr>
                    <tr>
                        <td>操作系统</td>
                        <td>{os_name}</td>
                    </tr>
                     <tr>
                        <td>版本</td>
                        <td>{os_version}</td>
                    </tr>
                    <tr>
                        <td>详细信息</td>
                        <td>{version_info}</td>
                    </tr>
                </table>
            </body>
            </html>
            """
            send_alert_email(body, subject, to_email)

        if memory_usage > memory_threshold:
            subject = "Memory Usage Alert"
            body = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #0a0a0a;
                        color: #ffffff;
                    }}
                    .alert {{
                        background: linear-gradient(135deg, #ff4b2b, #ff416c);
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                        animation: pulse 1.5s infinite;
                    }}
                    @keyframes pulse {{
                        0% {{ transform: scale(1); }}
                        50% {{ transform: scale(1.05); }}
                        100% {{ transform: scale(1); }}
                    }}
                    table {{
                        width: 100%;
                        margin-top: 20px;
                        border-collapse: collapse;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                        border-radius: 10px;
                        overflow: hidden;
                    }}
                    th, td {{
                        padding: 12px;
                        text-align: left;
                        border-bottom: 1px solid #ddd;
                    }}
                    th {{
                        background-color: rgba(255, 255, 255, 0.1);
                    }}
                    tr:hover {{
                        background-color: rgba(255, 255, 255, 0.2);
                    }}
                </style>
            </head>
            <body>
                <div class="alert">
                    <h2>警报：内存使用率超过阈值！</h2>
                    <p>当前内存使用率: <strong>{memory_usage}%</strong></p>
                    <p>设定的阈值: <strong>{memory_threshold}%</strong></p>
                </div>
                <table>
                    <tr>
                        <th>监控项</th>
                        <th>使用率</th>
                    </tr>
                    <tr>
                        <td>CPU使用率</td>
                        <td>{cpu_usage}%</td>
                    </tr>
                    <tr>
                        <td>内存使用率</td>
                        <td>{memory_usage}%</td>
                    </tr>
                    <tr>
                        <td>操作系统</td>
                        <td>{os_name}</td>
                    </tr>
                     <tr>
                        <td>版本</td>
                        <td>{os_version}</td>
                    </tr>
                    <tr>
                        <td>详细信息</td>
                        <td>{version_info}</td>
                    </tr>
                </table>
            </body>
            </html>
            """
            send_alert_email(body, subject, to_email)

        time.sleep(last_user_time)  # 等待用户指定的时间间隔


if __name__ == "__main__":
    monitor_system()