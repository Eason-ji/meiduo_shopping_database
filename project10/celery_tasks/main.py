from celery import Celery

app=Celery(main="meiduo")

# 加载配置信息
app.config_from_object("celery_tasks.config")

app.autodiscover_tasks(["celery_tasks.sms"])