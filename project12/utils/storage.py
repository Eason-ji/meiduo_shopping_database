from django.core.files.storage import Storage

class Qiniuyun(Storage):
    def _open(self):
        pass

    def _save(self):
        pass

    def url(self, name):

        return "http://qmllvum7m.hn-bkt.clouddn.com/"+name