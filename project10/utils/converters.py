from django.urls import converters

class UernameConverter:
    regex = "[a-zA-Z0-9_-]{5,20}"

    def to_python(self, value):
        return value



class UuidCode:
    regex = '[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}'

    def to_python(self, value):
        return value


class Mobile:
    regex = '1[3-9]\d{9}'

    def to_python(self, value):
        return value