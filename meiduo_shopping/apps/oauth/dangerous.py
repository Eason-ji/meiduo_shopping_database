"""
数据加密
1.导入
2.创建实例
3.组织数据,然后加密
"""
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature

# secret_key 秘钥
# expires_in 过期时间
s = Serializer(secret_key="123",expires_in=3600)
data = {
    "openid":"abd123"
}

s.dumps(data)

"""
数据解密
1.导入
2.创建实例
3.解密数据
"""
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
s = Serializer(secret_key="123",expires_in=3600)
s.loads("eyJhbGciOiJIUzUxMiIsImlhdCI6MTYwOTg5ODE3MywiZXhwIjoxNjA5OTAxNzczfQ.eyJvcGVuaWQiOiJhYmQxMjMifQ.0t8PKDCPUmWjMXcbrZhhc1EKMP5_zg1nSlzlsYYtMnNUWRj1fAlNQooxlM6My-D1QQ3_AHKrjb5ODKxqR0qS-w")


#############解密数据的时候可能会有异常(因为加密数据是不可修改的)############

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature
try:
    s = Serializer(secret_key="123", expires_in=3600)
    s.loads("TYwOTg5ODE3MywiZXhwIjoxNjA5OTAxNzczfQ.eyJvcGVuaWQiOiJhYmQxMjMifQ.0t8PKDCPUmWjMXcbrZhhc1EKMP5_zg1nSlzlsYYtMnNUWRj1fAlNQooxlM6My-D1QQ3_AHKrjb5ODKxqR0qS")
except BadSignature:
    print('数据被修改')
