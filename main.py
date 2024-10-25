import time
import os
import keyboard
from termcolor import colored
from function import user_time_sleep
from windows_info import get_os_info, get_windows_version_info, get_cpu_usage, get_memory_usage
from clear_console import clear_console, get_user_clear_time
from check_file import check_and_create_file, check_and_create_folder, check_and_copy_or_none
from config import read_config_main
from send_email import send_alert_email
from index import open_html

check_and_copy_or_none()

print(colored("Ctrl+m查看使用文档", 'red'))
print(colored("!!!---第一次运行请不要选择加载配置文件---!!!\n", 'red'))
keyboard.add_hotkey('ctrl+m', lambda: (open_html()))

# 获取系统版本号
os_name, os_version = get_os_info()
print(colored(f"Operating System: {os_name} {os_version}", 'green'))

# 获取Windows的版本信息
version_info = get_windows_version_info()
print(colored(f"Windows Version Info: {version_info}\n",'green'))
# 调用检测文件夹和文件的函数
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


# 调用主函数
email, password, target_email = read_config_main()

last_user_time = user_time_sleep()


############################################################################################
############################################################
############################################################################################
######################################################################
########################################################


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
            send_alert_email(body, subject, to_email, email, password)

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
                        background: linear-gradient(135deg, #00ffff, #0000ff);
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
            send_alert_email(body, subject, to_email, email, password)

        time.sleep(last_user_time)  # 等待用户指定的时间间隔


if __name__ == "__main__":
    monitor_system()
