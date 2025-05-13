# Server-Monitoring-and-Feedback

Real-time monitoring of server CPU and memory status, with automated email feedback.

实时监控服务器 CPU 与内存状态，并通过电子邮件提供反馈。

---

## 📌 Features | 功能特性

- ⏱️ Real-time monitoring of server CPU and memory usage  
- 📧 Sends feedback and alerts via email  
- ⚙️ Easy configuration and setup  
- 🪛 No manual dependencies installation required (auto install via `.bat`)

---

## 🛠️ Installation | 安装方式

Before running the program, please make sure to install the required Python libraries.  
在运行程序之前，请确保已安装所需的 Python 库。

📁 **Quick install method | 快速安装方法：**  
Double-click `install_libs.bat` to automatically install all required dependencies.  
双击运行 `install_libs.bat` 文件，即可自动安装所有依赖项。

---

## ⚙️ Configuration | 配置说明

All configuration files are stored in the following directory:  
所有配置文件存储于以下路径：

C:\Server_Data

You can adjust email settings, monitoring thresholds, and other parameters inside this folder.  
您可以在该目录中修改邮箱设置、监控阈值等参数。

---

## 📧 Email Feedback | 邮件反馈机制

The system periodically checks the server's CPU and memory usage.  
If usage exceeds a predefined threshold, an automatic email alert will be sent to the configured address.

系统会周期性检查服务器的 CPU 和内存使用情况。  
若超出预设阈值，将自动向指定邮箱发送警报邮件。

---

## 📂 File Structure | 文件结构

├── install_libs.bat # One-click dependency installer
├── main.py # Main monitoring script
├── config_template.json # Example config file (copy to C:\Server_Data)
└── README.md # Project documentation

---

## 📄 License | 许可证



---

## 👨‍💻 Author | 作者

Developed by bailin
