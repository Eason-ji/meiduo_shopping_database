from celery_tasks.main import app
from django.core.mail import send_mail

@app.task
def celery_send_email(html_message):
    # 邮件主题
    subject = "主题"
    # 邮件内容
    message = "邮件内容"
    # 谁发的邮件
    from_email = "美多商城<qi_rui_hua@163.com>"
    # 支持html
    html_message = html_message
    # 收件人邮箱列表
    recipient_list = ["1054416918@qq.com"]
    send_mail(subject=subject,
              message=message,
              from_email=from_email,
              recipient_list=recipient_list,
              html_message=html_message)