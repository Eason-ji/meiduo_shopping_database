from django.urls import converters

class UserNameConverter:
    # 正则判断
    regex = '[a-zA-Z0-9_-]{5,20}'

    def to_python(self,value):
        # value 验证成功后的数据
        return value