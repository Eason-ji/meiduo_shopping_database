"""


celery -A review celery.mian worker -l INFO
"""

from celery import Celery



app = Celery(main="meiduo")

app.config_from_object('celery_tasks.config')

app.autodiscover_tasks(["celery_tasks.sms"])