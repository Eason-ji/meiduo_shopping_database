
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_shopping.settings')
# 加载配置文件
from celery import Celery
# 1.创建celery实例
# 参数main及名字
app = Celery(main="meiduo")
# 2,加载celery配置信息
# 配置信息中指定了我们的消息队列(broker)
# 我们选择redis作为消息队列(broker)
# 我们把broker的配置单独放置一个文件中

app.config_from_object("celery_tasks.config")


# 自动检测人物
app.autodiscover_tasks(["celery_tasks.sms","celery_tasks.email"])
