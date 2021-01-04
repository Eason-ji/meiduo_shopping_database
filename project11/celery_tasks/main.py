from celery import Celery
# 创建celery实例
app = Celery(main="meiduo")


# 加载配置信息
app.config_from_object("celery_tasks.config")

# 自动注册celery任务
app.autodiscover_tasks(["celery_tasks.sms"])