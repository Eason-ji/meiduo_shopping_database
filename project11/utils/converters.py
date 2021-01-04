import re

class Uername():

    regex = "[a-zA-Z0-9_-]{5,20}"

    def to_python(self, value):

        return value

class Usermobile():

    regex = "1[3-9]\d{9}"

    def to_python(self, value):
        return value