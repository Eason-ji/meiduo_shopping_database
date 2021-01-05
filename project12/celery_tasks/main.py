"""


celery -A review celery.mian worker -l INFO
"""




from celery import Celery

app = Celery(main="review_celery")

app.config_from_object("celery_tasks.config")

app.autodiscover_tasks("[celery_tasks.sms]")