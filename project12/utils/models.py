from django.db import models

class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间") # 创建时会生成时间
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间") # 每次修改是都会更改时间

    class Meta:
        abstract = True
