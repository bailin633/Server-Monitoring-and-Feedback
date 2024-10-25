# 邮件发送系统
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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


def send_alert_email(body, subject, to_email, email, password):
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
        print("Alert email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
