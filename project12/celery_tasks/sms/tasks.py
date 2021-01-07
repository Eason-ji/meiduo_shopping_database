# 任务---倍celery
from ronglian_sms_sdk import SmsSDK
from celery_tasks.main import app

@app.task
def celery_send_sms_code(sms_code):

    accId = '8aaf0708762cb1cf0176c6078ef235ad'
    accToken = '298971fec81f4d0ea1cd2ff2667b8b29'
    appId = '8aaf0708762cb1cf0176c6078fb735b4'

    # 9.1 创建容联云实例
    sdk = SmsSDK(accId, accToken, appId)
    tid = '1'  # 暂时只能选1
    mobile = "18742067032"  # 给那些手机发送验证码，只能是测试用户
    datas = (sms_code, '2')  # 涉及到模板的变量
    # 您的验证码为【1】，请于【2】分钟内输入

    # 9.2 发送短信
    sdk.sendMessage(tid, mobile, datas)
