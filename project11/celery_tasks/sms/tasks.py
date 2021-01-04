from celery_tasks.main import app

@app.task
def celery_send_sms_code(mobile,sms_code):
    from ronglian_sms_sdk import SmsSDK
    accId = '8aaf0708762cb1cf0176c6078ef235ad'
    accToken = '298971fec81f4d0ea1cd2ff2667b8b29'
    appId = '8aaf0708762cb1cf0176c6078fb735b4'

    sdk = SmsSDK(accId, accToken, appId)
    tid = "1"
    mobile = "%s" % mobile
    datas = (sms_code, 2)  # 您的验证码为{1},请于{2}分钟内输入
    # 发送验证码
    sdk.sendMessage(tid, mobile, datas)