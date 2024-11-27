import os

from celery import Celery
from celery.schedules import crontab

from zibal_project.celery.base import AppCelery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zibal_project.settings')
celery_app = Celery('zibal_project', task_cls=AppCelery)

celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.task_default_queue = 'default_queue'
celery_app.conf.task_default_exchange = 'default_exchange'
celery_app.conf.task_default_routing_key = 'default_routing_key'
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    'send_transaction_reports': {
        'task': 'send_transaction_reports',
        'schedule': crontab(hour='23', minute='0')
    },
}
