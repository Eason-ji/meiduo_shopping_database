"""
celery
生产者
消息队列
消费者
    通过指令来消费(执行)任务
    在虚拟环境下celery -A celery实例对象的文件路径 worker [-l INFO]  后两表示能在终端中显示
"""

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
app.autodiscover_tasks(["celery_tasks.sms"])
