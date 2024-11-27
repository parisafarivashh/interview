from datetime import datetime
from celery.signals import task_postrun
from report_flow.medium import get_medium
from report_flow.models import NotificationSchema
from zibal_project.celery import celery_app
from bson.objectid import ObjectId

from zibal_project.utils import create_connection_db


@celery_app.task(name='send_notification')
def send_notification(notification_id: str):
    notification = NotificationSchema.get_by_id(notification_id)

    medium = get_medium(notification.medium)
    if medium:
        medium.send('notification')


@task_postrun.connect
def signal_to_create_log(
        sender=None,
        task_id=None,
        task=None,
        args=None,
        kwargs=None,
        retval=None,
        state=None,
        **extra
):
    if sender.name == 'send_notification':
        retries = task.request.retries if task and hasattr(task, 'request') else 0

        notification_id = args[0]
        create_log_notification.apply_async((
            notification_id,
            state,
            retries,
        ))


@celery_app.task()
def create_log_notification(
    notification_id: str,
    status: str,
    retries=0
):
    db = create_connection_db()
    log = {
        "status": status,
        "sendAt": datetime.now(),
        "retries": retries,
    }
    db.notifications.update_one(
        {"_id": ObjectId(notification_id)},
        {"$set": log}
    )


@celery_app.task(name='send_transaction_reports')
def send_transaction_reports():
    db = create_connection_db()
    mediums = ['sms', 'email']

    today = datetime.now()
    start_of_today = datetime(today.year, today.month, today.day, 0, 0, 0, 0)

    merchants = db.transaction.distinct("merchantId")
    for merchant in merchants:
        pipeline = [
            {"$match": {"merchant_id": merchant, "createdAt": {"$gte": start_of_today}}},
            {"$group": {"_id": "$amount", "count": {"$sum": 1}}}
        ]
        results = db.transaction.aggregate(pipeline)
        summary_lines = [
            f"Amount: {result['_id']} - Count: {result['count']}" for result in results
        ]
        summary = "\n".join(summary_lines)

        for medium in mediums:
            notification = {
                "body": summary,
                "recipient": 'user phone or email',
                "medium": medium,
                "merchant_id": merchant,
            }
            result = NotificationSchema.create(notification)
            notification_id = result.id
            send_notification.apply_async((str(notification_id),))

