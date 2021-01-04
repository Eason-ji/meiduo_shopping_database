from ronglian_sms_sdk import SmsSDK

accId = '8aaf0708762cb1cf0176c6078ef235ad'
accToken = '298971fec81f4d0ea1cd2ff2667b8b29'
appId = '8aaf0708762cb1cf0176c6078fb735b4'

def send_message():
    sdk = SmsSDK(accId,accToken,appId)
    tid = "1"
    mobile = "18742067032"
    datas = ("666999",5)      # 您的验证码为{1},请于{2}分钟内输入

    sdk.sendMessage(tid,mobile,datas)

send_message()
