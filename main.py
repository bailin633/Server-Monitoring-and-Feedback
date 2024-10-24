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


# 获取用户输入的阈值
cpu_threshold, memory_threshold = get_user_thresholds()
print(f"用户设定的CPU阈值: {cpu_threshold}%")
print(f"用户设定的内存阈值: {memory_threshold}%")

# 配置文件路径
config_file_path = 'C:/Server_Data/Data.json'


# 保存邮箱和授权码
def save_config(email, password):
    config = {
        "email": email,
        "password": password
    }
    with open(config_file_path, 'w') as f:
        json.dump(config, f)
    print(f"邮箱配置文件已保存到 '{config_file_path}'")


# 读取邮箱配置
def load_config():
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as f:
            config = json.load(f)
        return config["email"], config["password"]
    else:
        return None, None


# 获取用户输入
def get_user_input():
    email = input("请输入您的邮箱: ")
    password = input("请输入您的授权码: ")
    save_config(email, password)
    return email, password


# 主逻辑：读取配置或获取用户输入
def read_config_main():
    if os.path.exists(config_file_path):
        choice = input("检测到配置文件，是否拉取并使用 (y/n): ")
        if choice.lower() == 'y':
            email, password = load_config()
            print(f"已加载配置: 邮箱: {email}")
        else:
            email, password = get_user_input()
    else:
        email, password = get_user_input()

    # 返回邮箱和密码，用于后续使用
    return email, password


# 调用主函数
email, password = read_config_main()

# 继续使用邮箱和密码
print(f"最终使用的邮箱是: {email}")


def user_time_sleep():
    while True:
        minutes = input("请输入检测时间间隔(分钟)")
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


# 邮件发送系统
def send_alert_email(body, subject, to_email):
    smtp_server = "smtp.qq.com"
    smtp_port = 465
    from_email = "2412433138@qq.com"  # 发送方邮箱
    password = "hsmxwitefteqdica"  # 授权码

    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # 添加邮件正文
    msg.attach(MIMEText(body, 'html'))

    try:
        # 使用 SMTP_SSL 连接服务器
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Alert email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


# 主程序逻辑，将系统监控和邮件系统结合
def monitor_system():
    to_email = "s2412433138@gmail.com"  # 收件人邮箱
    while True:
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
                    <h2 style="margin-bottom: 0;">⚠️ CPU占用率过高警告</h2>
                    <p style="font-size: 16px;">系统当前检测到CPU占用率已达到<strong>{cpu_usage}%</strong></p>
                </div>
                <table>
                    <tr>
                        <th>信息</th>
                        <th>值</th>
                    </tr>
                    <tr>
                        <td>当前CPU占用率</td>
                        <td>{cpu_usage}%</td>
                    </tr>
                    <tr>
                        <td>当前系统</td>
                        <td>{os_name}</td>
                    </tr>
                    <tr>
                        <td>系统版本</td>
                        <td>{os_version}</td>
                    </tr>
                    <tr>
                        <td>版本号</td>
                        <td>{version_info}</td>
                    </tr>
                    <tr>
                        <td>设触发阈值</td>
                        <td>{cpu_threshold}%</td>
                    </tr>
                </table>
                <p style="font-size: 12px; color: grey; margin-top: 20px;">由系统监控工具生成</p>
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
                        background: linear-gradient(135deg, #4b79a1, #283e51);
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
                    <h2 style="margin-bottom: 0;">⚠️ 内存占用率过高警告</h2>
                    <p style="font-size: 16px;">系统当前检测到内存占用率已达到<strong>{memory_usage}%</strong></p>
                </div>
                <table>
                    <tr>
                        <th>信息</th>
                        <th>值</th>
                    </tr>
                    <tr>
                        <td>当前内存占用率</td>
                        <td>{memory_usage}%</td>
                    </tr>
                    <tr>
                        <td>当前系统</td>
                        <td>{os_name}</td>
                    </tr>
                    <tr>
                        <td>系统版本</td>
                        <td>{os_version}</td>
                    </tr>
                    <tr>
                        <td>版本号</td>
                        <td>{version_info}</td>
                    </tr>
                    <tr>
                        <td>触发阈值</td>
                        <td>{memory_threshold}%</td>
                    </tr>
                </table>
                <p style="font-size: 12px; color: grey; margin-top: 20px;">由系统监控工具生成</p>
            </body>
            </html>
            """
            send_alert_email(body, subject, to_email)

        time.sleep(last_user_time)


if __name__ == "__main__":
    monitor_system()
    read_config_main()
