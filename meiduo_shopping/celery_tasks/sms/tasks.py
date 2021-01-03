# 文件名必须是tasks,因为celery会自动检测tasks文件
from celery_tasks.main import app
# 写任务
# 人物必须要celery实例对象装饰器task装饰
# 任务包的任务需要celery调用自检检查函数(在mian文件中写)

@app.task
def celery_send_sms_code(mobile, sms_code):
    from ronglian_sms_sdk import SmsSDK

    accId = '8aaf0708762cb1cf0176c6078ef235ad'
    accToken = '298971fec81f4d0ea1cd2ff2667b8b29'
    appId = '8aaf0708762cb1cf0176c6078fb735b4'

    # 9.1 创建容联云实例
    sdk = SmsSDK(accId, accToken, appId)
    tid = '1'  # 暂时只能选1
    mobile = "%s" % mobile  # 给那些手机发送验证码，只能是测试用户
    datas = (sms_code, '2')  # 涉及到模板的变量
    # 您的验证码为【1】，请于【2】分钟内输入

    # 9.2 发送短信
    sdk.sendMessage(tid, mobile, datas)
