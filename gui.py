import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading # 用于在后台运行监控任务

# 假设这些模块中的函数可以被导入和使用
from windows_info import get_cpu_usage, get_memory_usage, get_os_info, get_windows_version_info, get_cpu_core_count, get_virtual_memory_usage, get_running_process_count, get_mem_info
from config import read_config_main, save_config # 修改此处
from send_email import send_alert_email
from main import run_initial_setup # 添加导入
# from clear_console import clear_console # GUI中不需要清空控制台
# from check_file import check_and_create_file, check_and_create_folder, check_and_copy_or_none # 初始化由 main.run_initial_setup() 处理

class SystemMonitorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("系统资源监控")
        self.geometry("700x550")

        self.monitoring_active = False
        self.monitor_thread = None

        # 初始化系统信息 (部分信息在启动时获取一次)
        self.os_name, self.os_version = get_os_info()
        self.version_info = get_windows_version_info()
        self.cpu_cores, self.cpu_cores_more = get_cpu_core_count()
        self.mem_info = get_mem_info()
        self.int_mem_info = int(self.mem_info)
        
        # 从配置文件加载初始值
        try:
            self.email_config = read_config_main()
            self.sender_email = self.email_config[0]
            self.sender_password = self.email_config[1]
            self.receiver_email = self.email_config[2]
            self.check_interval_minutes = float(self.email_config[3])
            # self.clear_interval_seconds = float(self.email_config[4]) # GUI不需要控制台清空
        except Exception as e:
            messagebox.showerror("配置错误", f"加载配置文件失败: {e}\n将使用默认值。")
            self.sender_email = "your_email@example.com"
            self.sender_password = "your_password"
            self.receiver_email = "recipient_email@example.com"
            self.check_interval_minutes = 1.0
            # self.clear_interval_seconds = 3600.0


        self.cpu_threshold_var = tk.StringVar(value="90")
        self.memory_threshold_var = tk.StringVar(value="80")
        self.check_interval_var = tk.StringVar(value=str(self.check_interval_minutes))

        self.sender_email_var = tk.StringVar(value=self.sender_email)
        self.sender_password_var = tk.StringVar(value=self.sender_password)
        self.receiver_email_var = tk.StringVar(value=self.receiver_email)

        self.create_widgets()
        self.update_static_info() # 更新一次静态系统信息

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # --- 实时数据展示区 ---
        data_frame = ttk.LabelFrame(main_frame, text="实时监控数据", padding="10")
        data_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        ttk.Label(data_frame, text="CPU 使用率:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.cpu_usage_label = ttk.Label(data_frame, text="N/A", font=("Arial", 12, "bold"))
        self.cpu_usage_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(data_frame, text="内存 使用率:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.memory_usage_label = ttk.Label(data_frame, text="N/A", font=("Arial", 12, "bold"))
        self.memory_usage_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(data_frame, text="操作系统:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.os_label = ttk.Label(data_frame, text="N/A")
        self.os_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(data_frame, text="Windows 版本:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.win_ver_label = ttk.Label(data_frame, text="N/A")
        self.win_ver_label.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(data_frame, text="CPU 核心数:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.cpu_cores_label = ttk.Label(data_frame, text="N/A")
        self.cpu_cores_label.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(data_frame, text="总物理内存:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.total_mem_label = ttk.Label(data_frame, text="N/A")
        self.total_mem_label.grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)


        # --- 设置区 ---
        settings_frame = ttk.LabelFrame(main_frame, text="监控设置", padding="10")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        ttk.Label(settings_frame, text="CPU 阈值 (%):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(settings_frame, textvariable=self.cpu_threshold_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(settings_frame, text="内存 阈值 (%):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(settings_frame, textvariable=self.memory_threshold_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(settings_frame, text="检测间隔 (分钟):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(settings_frame, textvariable=self.check_interval_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # --- 邮箱配置区 ---
        email_frame = ttk.LabelFrame(main_frame, text="邮件警报配置", padding="10")
        email_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)

        ttk.Label(email_frame, text="发件人邮箱:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(email_frame, textvariable=self.sender_email_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(email_frame, text="发件人密码/授权码:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(email_frame, textvariable=self.sender_password_var, width=30, show="*").grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(email_frame, text="收件人邮箱:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(email_frame, textvariable=self.receiver_email_var, width=30).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        self.save_config_button = ttk.Button(email_frame, text="保存邮件配置", command=self.save_email_config)
        self.save_config_button.grid(row=3, column=0, columnspan=2, pady=10)


        # --- 控制区 ---
        control_frame = ttk.Frame(main_frame, padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        self.start_button = ttk.Button(control_frame, text="启动监控", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(control_frame, text="停止监控", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # --- 状态/日志区 ---
        log_frame = ttk.LabelFrame(main_frame, text="状态与日志", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(3, weight=1) # 让日志区可以扩展

        self.log_text = tk.Text(log_frame, height=8, width=80, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text['yscrollcommand'] = scrollbar.set
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def update_static_info(self):
        self.os_label.config(text=f"{self.os_name} {self.os_version}")
        self.win_ver_label.config(text=self.version_info)
        self.cpu_cores_label.config(text=f"{self.cpu_cores} (逻辑核心: {self.cpu_cores_more})")
        self.total_mem_label.config(text=f"{self.int_mem_info} GB")

    def update_dynamic_info(self):
        if not self.monitoring_active: # 如果监控未激活，则不更新动态数据
            # 可以选择清空或显示上次的值
            # self.cpu_usage_label.config(text="N/A")
            # self.memory_usage_label.config(text="N/A")
            return

        try:
            cpu_usage = get_cpu_usage()
            memory_usage = get_memory_usage()
            self.cpu_usage_label.config(text=f"{cpu_usage:.2f}%")
            self.memory_usage_label.config(text=f"{memory_usage:.2f}%")
        except Exception as e:
            self.log_message(f"获取系统数据错误: {e}")
            self.cpu_usage_label.config(text="Error")
            self.memory_usage_label.config(text="Error")
        
        # 安排下一次更新 (仅当监控激活时)
        if self.monitoring_active:
            self.after(1000, self.update_dynamic_info) # 每秒更新一次界面显示

    def save_email_config(self):
        try:
            sender_email = self.sender_email_var.get()
            sender_password = self.sender_password_var.get()
            receiver_email = self.receiver_email_var.get()
            
            current_check_interval_minutes = self.check_interval_var.get()

            # 从旧配置中获取 user_clear_time，或者使用默认值
            # read_config_main() 返回 (email, password, target_email, last_user_time, user_clear_time)
            # 我们只需要最后一个元素作为旧的 clear_time，如果存在的话。
            _config_tuple = read_config_main()
            old_user_clear_time = _config_tuple[4] if _config_tuple and len(_config_tuple) == 5 and _config_tuple[4] is not None else "3600"

            if save_config(sender_email, sender_password, receiver_email, current_check_interval_minutes, old_user_clear_time):
                self.log_message("邮件配置已保存。")
                # config.py 中的 config_file_path 是 'C:/Server_Data/Data.json'
                messagebox.showinfo("成功", "邮件配置已保存到 C:/Server_Data/Data.json")
            else:
                self.log_message("保存邮件配置失败。")
                messagebox.showerror("错误", "保存邮件配置失败。")
        except Exception as e:
            self.log_message(f"保存邮件配置时发生意外错误: {e}")
            messagebox.showerror("错误", f"保存邮件配置时发生意外错误: {e}")


    def start_monitoring(self):
        if self.monitoring_active:
            messagebox.showinfo("提示", "监控已经在运行中。")
            return

        try:
            self.current_cpu_threshold = int(self.cpu_threshold_var.get())
            self.current_memory_threshold = int(self.memory_threshold_var.get())
            self.current_check_interval_seconds = float(self.check_interval_var.get()) * 60

            if not (0 < self.current_cpu_threshold <= 100 and 0 < self.current_memory_threshold <= 100):
                messagebox.showerror("错误", "阈值必须在 1-100 之间。")
                return
            if self.current_check_interval_seconds <= 0:
                messagebox.showerror("错误", "检测间隔必须大于0。")
                return

        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字作为阈值和检测间隔。")
            return
        
        self.sender_email = self.sender_email_var.get()
        self.sender_password = self.sender_password_var.get()
        self.receiver_email = self.receiver_email_var.get()

        if not self.sender_email or not self.sender_password or not self.receiver_email:
            messagebox.showerror("错误", "请填写完整的邮件配置信息。")
            return

        self.monitoring_active = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.log_message("监控已启动。")
        
        # 启动动态信息更新循环
        self.update_dynamic_info() 

        # 在新线程中运行监控逻辑
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        if self.monitoring_active:
            self.monitoring_active = False
            if self.monitor_thread and self.monitor_thread.is_alive():
                # 对于线程的优雅停止，通常需要线程内部配合检查 self.monitoring_active
                # 这里简单设置标志位，循环会在下一次迭代时退出
                pass
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log_message("监控已停止。")
            # 停止后，界面上的动态数据将不再更新
            self.cpu_usage_label.config(text="N/A (已停止)")
            self.memory_usage_label.config(text="N/A (已停止)")


    def monitoring_loop(self):
        """核心监控循环，将在后台线程运行"""
        while self.monitoring_active:
            try:
                cpu_usage = get_cpu_usage()
                memory_usage = get_memory_usage()
                
                # 更新GUI上的实时数据 (通过主线程调度，避免Tkinter线程问题)
                # self.after(0, lambda: self.cpu_usage_label.config(text=f"{cpu_usage:.2f}%"))
                # self.after(0, lambda: self.memory_usage_label.config(text=f"{memory_usage:.2f}%"))
                # update_dynamic_info 已经处理了GUI更新

                # 获取最新的系统信息，用于邮件内容
                virtual_mem = get_virtual_memory_usage()
                process_ids = get_running_process_count()

                alert_triggered = False
                subject = ""
                body_content = []


                if cpu_usage > self.current_cpu_threshold:
                    alert_triggered = True
                    subject = "CPU Usage Alert"
                    body_content.append(f"<h2>警报：CPU使用率超过阈值！</h2><p>当前CPU使用率: <strong>{cpu_usage:.2f}%</strong></p><p>设定的阈值: <strong>{self.current_cpu_threshold}%</strong></p>")
                    self.log_message(f"警告: CPU 使用率 {cpu_usage:.2f}% 超过阈值 {self.current_cpu_threshold}%")

                if memory_usage > self.current_memory_threshold:
                    alert_triggered = True
                    if not subject: # 如果CPU没有触发，则设置内存的subject
                        subject = "Memory Usage Alert"
                    else: # 如果CPU也触发了，追加到subject
                        subject += " & Memory Usage Alert"
                    body_content.append(f"<h2>警报：内存使用率超过阈值！</h2><p>当前内存使用率: <strong>{memory_usage:.2f}%</strong></p><p>设定的阈值: <strong>{self.current_memory_threshold}%</strong></p>")
                    self.log_message(f"警告: 内存使用率 {memory_usage:.2f}% 超过阈值 {self.current_memory_threshold}%")

                if alert_triggered:
                    html_body = f"""
                    <html><head><style>
                        body {{font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333; margin: 0; padding: 20px;}}
                        .container {{background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1);}}
                        h2 {{color: #d9534f;}}
                        table {{width: 100%; margin-top: 20px; border-collapse: collapse;}}
                        th, td {{padding: 10px; text-align: left; border-bottom: 1px solid #ddd;}}
                        th {{background-color: #f0f0f0;}}
                    </style></head><body><div class="container">
                        {''.join(body_content)}
                        <h3>系统快照：</h3>
                        <table>
                            <tr><th>监控项</th><th>值</th><th>更多信息</th></tr>
                            <tr><td>CPU使用率</td><td>{cpu_usage:.2f}%</td><td>核心数量: {self.cpu_cores}/{self.cpu_cores_more}</td></tr>
                            <tr><td>内存使用率</td><td>{memory_usage:.2f}%</td><td>虚拟内存: {virtual_mem}</td></tr>
                            <tr><td>操作系统</td><td>{self.os_name}</td><td>总内存: {self.int_mem_info}GB</td></tr>
                            <tr><td>版本</td><td>{self.os_version}</td><td></td></tr>
                            <tr><td>详细信息</td><td>{self.version_info}</td><td>系统进程数量: {process_ids}</td></tr>
                        </table>
                    </div></body></html>
                    """
                    try:
                        send_alert_email(html_body, subject, self.receiver_email, self.sender_email, self.sender_password)
                        self.log_message(f"警报邮件已发送至 {self.receiver_email}。主题: {subject}")
                    except Exception as e:
                        self.log_message(f"发送邮件失败: {e}")
            
            except Exception as e:
                self.log_message(f"监控循环中发生错误: {e}")

            # 等待指定的时间间隔
            # 为了能及时响应停止信号，这里使用多次短时sleep
            for _ in range(int(self.current_check_interval_seconds)):
                if not self.monitoring_active:
                    break
                time.sleep(1)
            if not self.monitoring_active:
                break
        
        self.log_message("监控线程已结束。")


if __name__ == "__main__":
    # 执行一次性文件和文件夹检查
    try:
        run_initial_setup()
    except Exception as e:
        # 如果初始设置失败，最好能通知用户，但GUI尚未启动
        # 打印到控制台可能是目前最好的方式
        print(f"错误：初始化设置失败 - {e}")
        # 可以选择在这里退出，或者让GUI尝试启动，但可能会遇到因缺少文件/文件夹导致的问题
        # import sys
        # sys.exit(1)

    app = SystemMonitorGUI()
    app.mainloop()