"""
对openid进行加密和解密操作
"""
from itsdangerous import TimedJSONWebSignatureSerializer,BadSignature
# 加密
def generic_openid(openid):
    # 创建一个实例对象
    s = TimedJSONWebSignatureSerializer(secret_key="123", expires_in=3600)
    # 组织数据,加密数据
    data = {
        "openid":openid
    }
    secret_data = s.dumps(data)
    # 返回加密数据
    return secret_data.dacode()


def check_token(openid):

    s = TimedJSONWebSignatureSerializer(secret_key="123", expires_in=3600)
    try:
        data = s.loads(openid)

    except BadSignature:
        print('数据被修改')
        return None

    return data.get("openid")