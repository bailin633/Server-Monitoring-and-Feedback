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
    current_time = time.time()

    # 发送频率限制 (30秒)
    if current_time - last_sent_time < 30:
        return {"success": False, "error": "发送频率限制：30秒内只能发送一封邮件。"}

    domain = email.split("@")[-1]
    server_config = EMAIL_SERVERS.get(domain)

    if not server_config:
        return {"success": False, "error": f"未找到域 '{domain}' 对应的SMTP服务器配置。"}

    smtp_server = server_config["smtp_server"]
    smtp_port = server_config["smtp_port"]
    
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(email, password)
        server.sendmail(email, to_email, msg.as_string())
        server.quit()
        last_sent_time = current_time
        return {"success": True, "message": "邮件已成功发送！"}
    except Exception as e:
        return {"success": False, "error": f"邮件发送失败: {str(e)}"}
