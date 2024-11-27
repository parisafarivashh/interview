from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from bson import ObjectId

from zibal_project.utils import create_connection_db


class NotificationSchema(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    body: str
    recipient: str
    medium: str
    merchant_id: str
    metadat: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    sendAt: Optional[datetime] = None
    retries: Optional[int] = None

    @classmethod
    def create(cls, data: dict):
        db = create_connection_db()
        notification = cls(**data)
        notification_dict = notification.model_dump(by_alias=True, exclude={"id"})
        result = db.notifications.insert_one(notification_dict)
        notification.id = str(result.inserted_id)
        return notification

    @classmethod
    def get_by_id(cls, notification_id: str):
        try:
            db = create_connection_db()
            obj_id = ObjectId(notification_id)
            result = db.notifications.find_one({"_id": obj_id})

            if result:
                return cls(**result)
        except Exception as e:
            print(f"Notification {notification_id} not found.")
            return None


# region transaction function
def set_pipline_base_mode(pipeline: list, mode: str, include_fields: list):
    project = {
        '$project': {
            "jalaliYear": {"$subtract": [{"$year": "$createdAt"}, 621]},
            "jalaliMonth": {"$month": "$createdAt"},
            "jalaliDay": {"$dayOfMonth": "$createdAt"},
            "daily": {
                "$concat": [
                    {"$toString": {"$subtract": [{"$year": "$createdAt"}, 621]}},
                    "/",
                    {"$toString": {"$month": "$createdAt"}},
                    "/",
                    {"$toString": {"$dayOfMonth": "$createdAt"}}
                ]
            }
        }
    }

    if mode == 'weekly':
        pipeline.append(
            {
                '$addFields': {
                    'jalaliWeek': {
                        'year': {"$subtract": [{"$year": "$createdAt"}, 621]},
                        'week': {"$week": "$createdAt"}
                    }
                }
            }
        )
        project = {
            '$project': {
                'weekly': {
                    '$concat': [
                        {'$literal': 'هفته '},
                        {'$toString': {"$week": "$createdAt"}},
                        {'$literal': ' سال '},
                        {'$toString': {"$subtract": [{"$year": "$createdAt"}, 621]}}
                    ]
                }
            }
        }

    elif mode == 'monthly':
        month_names = [
            "فروردین", "اردیبهشت", "خرداد", "تیر",
            "مرداد", "شهریور", "مهر", "آبان",
            "آذر", "دی", "بهمن", "اسفند"
        ]
        pipeline.append(
            {
                '$addFields': {
                    'jalaliYear': {
                        "$subtract": [{"$year": "$createdAt"}, 621]},
                    'jalaliMonth': {"$month": "$createdAt"}
                }
            }
        )
        project = {
            '$project': {
                'monthly': {
                    '$concat': [
                        {'$arrayElemAt': [month_names, {"$subtract": ["$jalaliMonth", 1]}]},
                        ' ',
                        {'$toString': "$jalaliYear"}
                    ]
                }
            }
        }

    for field in include_fields:
        project['$project'][field] = 1

    pipeline.append(project)


def get_pipline_transaction_aggregation(
        mode: str,
        transaction_type: str,
        merchant_id: str = None,
) -> list:
    pipeline = []

    if merchant_id:
        pipeline.append({'$match': {'merchantId': ObjectId(merchant_id)}})

    set_pipline_base_mode(pipeline, mode, ['amount'])
    if transaction_type == 'count':
        pipeline.append({
            '$group': {
                '_id': f'${mode}',
                'value': {'$sum': 1}
            }
        })

    elif transaction_type == 'amount':
        pipeline.append({
            '$group': {
                '_id': f'${mode}',
                'value': {'$sum': '$amount'}
            }
        })

    pipeline.append({
        '$project': {
            '_id': 0,
            'key': '$_id',
            'value': 1,
        }
    })
    pipeline.append({'$sort': {'key': 1}})
    return pipeline

def get_pipline_transaction_from_collection(
        merchant_id: str,
        mode: str,
        transaction_type: str
) -> list:
    pipeline = []

    filtering = {"$match": {"type_mode": mode}}

    if merchant_id:
        filtering["$match"]["_id.merchantId"] = ObjectId(merchant_id)

    else:
        filtering["$match"]["_id.merchantId"] = {'$exists': False}

    pipeline.append(filtering)

    if transaction_type == 'count':
        pipeline.append({
            '$project': {
                '_id': 0,
                'key': '$_id.value_mode',
                'value': '$count',
            }
        })
    else:
        pipeline.append({
            '$project': {
                '_id': 0,
                'key': '$_id.value_mode',
                'value': '$amount',
            }
        })
    pipeline.append({'$sort': {'key': 1}})
    return pipeline
# endregion
