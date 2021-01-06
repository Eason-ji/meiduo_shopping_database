from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature


# 加密
def generic_user_id(user_id):
    # 1.
    s = Serializer(secret_key="abc", expires_in=3600)
    data = {
        "user_id" : user_id
    }
    secret_data = s.dumps(data)
    return  secret_data





# 解密
def check_user_id(token):
    s = Serializer(secret_key="abc" , expires_in=3600)
    try:
        data = s.loads(token)

    except BadSignature:
        print("数据被修改")
        return None

    return data.get("user_id")















