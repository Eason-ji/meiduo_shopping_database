from django.urls import converters

class UernameConverter:
    regex = "[a-zA-Z0-9_-]{5,20}"

    def to_python(self, value):
        return value