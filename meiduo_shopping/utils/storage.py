from django.core.files.storage import Storage
# 必须要实现_save()和_open()方法
# 我们需要实现url方法
class Qiniuyun(Storage):

    def _open(self, name, mode='rb'):

        pass
    def _save(self, name, content, max_length=None):

        pass

    def url(self,name):
        # name 其实就是数据库中图片名字
        # 我们期望的图片显示,其实就是http://七牛云外联+图片名
        # 需要到settings文件中去配置
        return "http://qmllvum7m.hn-bkt.clouddn.com/"+name

        pass



