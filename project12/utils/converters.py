from django.urls import converters

class UsernameConverter:

    regex = "[a-zA-Z0-9]{5,20}"

    def to_python(self, value):

        return value



class MobileConverter:

    regex = "1[3-9]\d{9}"

    def to_python(self, value):
        # value 就是验证成功后的数据
        return value