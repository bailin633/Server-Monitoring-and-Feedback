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
        self.geometry("800x700") # 进一步增大窗口以适应更清晰的布局

        # --- Modern Dark Theme Styling ---
        self.style = ttk.Style(self)
        # self.style.theme_use('default') # Start from a basic theme if overriding heavily

        # Colors
        dark_bg = "#2e2e2e" # Dark gray background
        medium_bg = "#3c3c3c" # Slightly lighter for elements
        light_fg = "#e0e0e0" # Light gray for text
        accent_color = "#009688" # Teal accent
        value_ok_color = "#4CAF50" # Green for OK status
        value_alert_color = "#F44336" # Red for alert status
        entry_bg = "#4a4a4a"

        self.configure(bg=dark_bg) # Root window background

        # Fonts
        base_font_family = 'Calibri' # Or 'Segoe UI' on Windows
        font_normal = (base_font_family, 11)
        font_bold = (base_font_family, 11, 'bold')
        font_large_bold = (base_font_family, 14, 'bold')
        font_log = ('Consolas', 10)

        # General widget styling
        self.style.configure('.',
                             background=dark_bg,
                             foreground=light_fg,
                             font=font_normal,
                             borderwidth=0,
                             relief=tk.FLAT)

        self.style.configure('TFrame', background=dark_bg)
        self.style.configure('TLabelframe',
                             background=dark_bg,
                             foreground=light_fg,
                             font=font_bold,
                             padding=10,
                             relief=tk.SOLID, # Give labelframes a subtle border
                             bordercolor=medium_bg,
                             borderwidth=1)
        self.style.configure('TLabelframe.Label',
                             background=dark_bg,
                             foreground=accent_color, # Make labelframe titles stand out
                             font=font_bold,
                             padding=(0, 5)) # Padding for labelframe title

        self.style.configure('TLabel', background=dark_bg, foreground=light_fg, font=font_normal, padding=(5,3))
        self.style.configure('Value.TLabel', background=dark_bg, font=font_large_bold) # Color set dynamically
        
        self.style.configure('TEntry',
                             font=font_normal,
                             padding=6,
                             fieldbackground=entry_bg,
                             foreground=light_fg,
                             insertcolor=light_fg, # Cursor color
                             borderwidth=1,
                             relief=tk.SOLID,
                             bordercolor=medium_bg)
        self.style.map('TEntry', bordercolor=[('focus', accent_color)])


        self.style.configure('TButton',
                             background=medium_bg,
                             foreground=light_fg,
                             font=font_bold,
                             padding=(10, 6),
                             relief=tk.FLAT,
                             borderwidth=1,
                             bordercolor=medium_bg)
        self.style.map('TButton',
                       background=[('active', accent_color), ('pressed', accent_color)],
                       foreground=[('active', dark_bg), ('pressed', dark_bg)],
                       relief=[('pressed', tk.SUNKEN), ('!pressed', tk.FLAT)],
                       bordercolor=[('focus', accent_color)])

        self.style.configure('Start.TButton', background="#28a745", foreground=dark_bg) # Greenish
        self.style.map('Start.TButton', background=[('active', "#218838"), ('pressed', "#1e7e34")])
        
        self.style.configure('Stop.TButton', background="#dc3545", foreground=dark_bg) # Reddish
        self.style.map('Stop.TButton', background=[('active', "#c82333"), ('pressed', "#bd2130")])

        self.style.configure('Vertical.TScrollbar',
                             background=medium_bg,
                             troughcolor=dark_bg,
                             bordercolor=dark_bg,
                             arrowcolor=light_fg,
                             relief=tk.FLAT,
                             gripcount=0)
        self.style.map('Vertical.TScrollbar',
                       background=[('active', accent_color)])


        self.monitoring_active = False
        self.monitor_thread = None

        # 初始化系统信息 (部分信息在启动时获取一次)
        self.os_name, self.os_version = get_os_info()
        self.version_info = get_windows_version_info()
        self.cpu_cores, self.cpu_cores_more = get_cpu_core_count()
        self.mem_info = get_mem_info()
        self.int_mem_info = int(self.mem_info)
        
        # 设置窗口图标
        try:
            self.iconbitmap('icon.ico') # 假设 icon.ico 在同级目录
        except tk.TclError:
            print("未能加载icon.ico，请确保文件存在且格式正确。")

        # 从配置文件加载初始值
        loaded_sender_email = "your_email@example.com"
        loaded_sender_password = "your_password"
        loaded_receiver_email = "recipient_email@example.com"
        loaded_check_interval_minutes = 1.0

        try:
            config_data = read_config_main()
            if config_data and None not in config_data[:3]: # 确保邮件信息存在
                loaded_sender_email = config_data[0]
                loaded_sender_password = config_data[1]
                loaded_receiver_email = config_data[2]
                loaded_check_interval_minutes = float(config_data[3])
            else:
                 messagebox.showwarning("配置提示", "未能从配置文件加载完整的邮件信息，请检查或填写配置。")
        except Exception as e:
            messagebox.showerror("配置错误", f"加载配置文件失败: {e}\n将使用默认值或提示输入。")
        
        self.sender_email = loaded_sender_email
        self.sender_password = loaded_sender_password
        self.receiver_email = loaded_receiver_email
        self.check_interval_minutes = loaded_check_interval_minutes

        self.cpu_threshold_var = tk.StringVar(value="90")
        self.memory_threshold_var = tk.StringVar(value="80")
        self.check_interval_var = tk.StringVar(value=str(self.check_interval_minutes))

        self.sender_email_var = tk.StringVar(value=self.sender_email)
        self.sender_password_var = tk.StringVar(value=self.sender_password) # 初始密码不显示在UI上，但变量需要
        self.receiver_email_var = tk.StringVar(value=self.receiver_email)

        self.create_widgets()
        self.update_static_info() # 更新一次静态系统信息

    def create_widgets(self):
        # 使用 self.style 中定义的字体
        # Retrieve styled font and colors
        font_log = self.style.lookup('.', 'font', default=('Consolas', 10)) # Get styled log font
        value_ok_color = "#4CAF50"
        value_alert_color = "#F44336"
        dark_bg = self.style.lookup('.', 'background', default="#2e2e2e")
        light_fg = self.style.lookup('.', 'foreground', default="#e0e0e0")
        entry_bg = self.style.lookup('TEntry', 'fieldbackground', default="#4a4a4a")


        main_frame = ttk.Frame(self, padding="15", style='TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # --- 实时数据展示区 ---
        data_frame = ttk.LabelFrame(main_frame, text="实时监控数据", padding=(10,5), style='TLabelframe')
        data_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0,15), padx=10)
        data_frame.columnconfigure(1, weight=1)

        ttk.Label(data_frame, text="CPU 使用率:", style='TLabel').grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.cpu_usage_label = ttk.Label(data_frame, text="N/A", style='Value.TLabel', foreground=value_ok_color)
        self.cpu_usage_label.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

        ttk.Label(data_frame, text="内存 使用率:", style='TLabel').grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.memory_usage_label = ttk.Label(data_frame, text="N/A", style='Value.TLabel', foreground=value_ok_color)
        self.memory_usage_label.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(data_frame, text="操作系统:", style='TLabel').grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.os_label = ttk.Label(data_frame, text="N/A", style='TLabel')
        self.os_label.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)

        ttk.Label(data_frame, text="Windows 版本:", style='TLabel').grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.win_ver_label = ttk.Label(data_frame, text="N/A", style='TLabel')
        self.win_ver_label.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)

        ttk.Label(data_frame, text="CPU 核心数:", style='TLabel').grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        self.cpu_cores_label = ttk.Label(data_frame, text="N/A", style='TLabel')
        self.cpu_cores_label.grid(row=4, column=1, sticky=tk.W, padx=10, pady=5)

        ttk.Label(data_frame, text="总物理内存:", style='TLabel').grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        self.total_mem_label = ttk.Label(data_frame, text="N/A", style='TLabel')
        self.total_mem_label.grid(row=5, column=1, sticky=tk.W, padx=10, pady=5)

        # --- 设置与配置框架 ---
        settings_and_config_frame = ttk.Frame(main_frame, style='TFrame')
        settings_and_config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10, padx=10)
        settings_and_config_frame.columnconfigure(0, weight=1)
        settings_and_config_frame.columnconfigure(1, weight=1)

        # --- 监控设置区 ---
        settings_frame = ttk.LabelFrame(settings_and_config_frame, text="监控参数设置", padding=(10,5), style='TLabelframe')
        settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=0, padx=(0,10))
        settings_frame.columnconfigure(1, weight=1)

        ttk.Label(settings_frame, text="CPU 阈值 (%):", style='TLabel').grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(settings_frame, textvariable=self.cpu_threshold_var, width=12, style='TEntry').grid(row=0, column=1, sticky=tk.EW, padx=10, pady=5)

        ttk.Label(settings_frame, text="内存 阈值 (%):", style='TLabel').grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(settings_frame, textvariable=self.memory_threshold_var, width=12, style='TEntry').grid(row=1, column=1, sticky=tk.EW, padx=10, pady=5)

        ttk.Label(settings_frame, text="检测间隔 (分钟):", style='TLabel').grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(settings_frame, textvariable=self.check_interval_var, width=12, style='TEntry').grid(row=2, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # --- 邮箱配置区 ---
        email_frame = ttk.LabelFrame(settings_and_config_frame, text="邮件警报配置", padding=(10,5), style='TLabelframe')
        email_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=0, padx=(10,0))
        email_frame.columnconfigure(1, weight=1)

        ttk.Label(email_frame, text="发件人邮箱:", style='TLabel').grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(email_frame, textvariable=self.sender_email_var, width=35, style='TEntry').grid(row=0, column=1, sticky=tk.EW, padx=10, pady=5)
        
        ttk.Label(email_frame, text="发件人密码:", style='TLabel').grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(email_frame, textvariable=self.sender_password_var, width=35, show="*", style='TEntry').grid(row=1, column=1, sticky=tk.EW, padx=10, pady=5)

        ttk.Label(email_frame, text="收件人邮箱:", style='TLabel').grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(email_frame, textvariable=self.receiver_email_var, width=35, style='TEntry').grid(row=2, column=1, sticky=tk.EW, padx=10, pady=5)

        self.save_config_button = ttk.Button(email_frame, text="保存邮件配置", command=self.save_email_config, style='TButton')
        self.save_config_button.grid(row=3, column=0, columnspan=2, pady=(15,5), padx=10, sticky=tk.EW)

        # --- 控制区 ---
        control_frame = ttk.Frame(main_frame, style='TFrame', padding=(0,10))
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15,10))
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=0)
        control_frame.columnconfigure(2, weight=0)
        control_frame.columnconfigure(3, weight=1)

        self.start_button = ttk.Button(control_frame, text="▶ 启动监控", command=self.start_monitoring, style='Start.TButton', width=15)
        self.start_button.grid(row=0, column=1, padx=15)

        self.stop_button = ttk.Button(control_frame, text="■ 停止监控", command=self.stop_monitoring, state=tk.DISABLED, style='Stop.TButton', width=15)
        self.stop_button.grid(row=0, column=2, padx=15)
        
        # --- 状态/日志区 ---
        log_frame = ttk.LabelFrame(main_frame, text="状态与日志", padding=(10,5), style='TLabelframe')
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10, padx=10)
        main_frame.rowconfigure(3, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, height=10, width=80, state=tk.DISABLED,
                                font=font_log, relief=tk.FLAT, borderwidth=0,
                                bg=entry_bg, fg=light_fg, wrap=tk.WORD,
                                insertbackground=light_fg, selectbackground=accent_color)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview, style='Vertical.TScrollbar')
        self.log_text['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # --- Status Bar ---
        self.status_bar = ttk.Label(main_frame, text="就绪", relief=tk.FLAT, anchor=tk.W, style='TLabel', padding=(5,3))
        self.status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5,0), padx=10)


    def log_message(self, message):
        if self.status_bar:
             self.status_bar.config(text=f"{time.strftime('%H:%M:%S')}: {message}")
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
            value_ok_color = self.style.lookup('TButton', 'background', default="#4CAF50") # Fallback
            value_alert_color = self.style.lookup('Stop.TButton', 'background', default="#F44336") # Fallback
            
            # Ensure thresholds are available before using them for color coding
            cpu_thresh = self.current_cpu_threshold if hasattr(self, 'current_cpu_threshold') else 101
            mem_thresh = self.current_memory_threshold if hasattr(self, 'current_memory_threshold') else 101

            self.cpu_usage_label.config(text=f"{cpu_usage:.2f}%", foreground=value_ok_color if cpu_usage < cpu_thresh else value_alert_color)
            self.memory_usage_label.config(text=f"{memory_usage:.2f}%", foreground=value_ok_color if memory_usage < mem_thresh else value_alert_color)
        except Exception as e:
            self.log_message(f"获取系统数据错误: {e}")
            value_alert_color = self.style.lookup('Stop.TButton', 'background', default="#F44336")
            self.cpu_usage_label.config(text="Error", foreground=value_alert_color)
            self.memory_usage_label.config(text="Error", foreground=value_alert_color)
        
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
        if self.status_bar: self.status_bar.config(text="监控运行中...")
        
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
            if self.status_bar: self.status_bar.config(text="监控已停止。")
            # 停止后，界面上的动态数据将不再更新
            default_fg_color = self.style.lookup('TLabel', 'foreground', default="#e0e0e0")
            self.cpu_usage_label.config(text="N/A (已停止)", foreground=default_fg_color)
            self.memory_usage_label.config(text="N/A (已停止)", foreground=default_fg_color)


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