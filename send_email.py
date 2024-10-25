# 邮件发送系统
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_alert_email(body, subject, to_email, email, password):
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
