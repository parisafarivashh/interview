from celery import Task


class AppCelery(Task):
    autoretry_for = (Exception,)
    default_retry_delay = 2
    soft_time_limit = None
    needs_token = False
    max_retries = 10
    time_limit = None
    acks_late = True

