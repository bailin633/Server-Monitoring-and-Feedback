# 邮件发送系统
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

# 邮箱配置映射
EMAIL_SERVERS = {
    "qq.com": {"smtp_server": "smtp.qq.com", "smtp_port": 465},
    "gmail.com": {"smtp_server": "smtp.gmail.com", "smtp_port": 465},
    "outlook.com": {"smtp_server": "outlook.com", "smtp_port": 587},
    "icloud.com": {"smtp_server": "icloud.com", "smtp_port": 587},
    "163.com": {"smtp_server": "smtp.163.com", "smtp_port": 465},
    "126.com": {"smtp_server": "smtp.126.com", "smtp_port": 465},
    "sina.com": {"smtp_server": "smtp.sina.com", "smtp_port": 465},
}

# 上次发送的时间
last_sent_time = 0  # 全局变量,记录上一次邮件发送的时间


def send_alert_email(body, subject, to_email, email, password):
    global last_sent_time
    # 检测是否在5分钟内
    current_time = time.time()
    if current_time - last_sent_time < 30:  # 300/60 =5/min
        print("五分钟内只能发送一封邮件")
        return
    # 获取邮箱后缀，确定服务器
    domain = email.split("@")[-1]
    server_config = EMAIL_SERVERS.get(domain)

    if not server_config:
        print(f"没有找到对应SMTP服务器地址: {domain}")
        return

    smtp_server = server_config["smtp_server"]
    smtp_port = server_config["smtp_port"]
    
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
        # 更新上次发送的时间
        last_sent_time = current_time
        print("Alert email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
