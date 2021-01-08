from django.db import models
"""
我们想以后的表,每个表中都2个字段跟别是create_time,和update_time
可以采用继承实现
定义一个基类,基类于这个两个字段
子类继承我们的基类
"""

class BaseModel(models.Model):

    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True,verbose_name="更新时间")

    class Meta:
        abstract = True