from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from zibal_project.utils import create_connection_db
from .models import get_pipline_transaction_aggregation, \
    get_pipline_transaction_from_collection
from .models import NotificationSchema
from .serializers import TransactionSerializer, NotificationSerializer
from .tasks import send_notification


class TransactionV1View(APIView):

    def get(self, request, format=None):
        db = create_connection_db()
        data = request.data

        serializer = TransactionSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        pipeline = get_pipline_transaction_aggregation(
            merchant_id=data.get('merchant_id'),
            mode=data['mode'],
            transaction_type=data['type'],
        )
        result_cursor = db.transaction.aggregate(pipeline)
        formatted_result = list(result_cursor)
        return Response(formatted_result, status=status.HTTP_200_OK)


class TransactionV2View(APIView):

    def get(self, request, format=None):
        db = create_connection_db()
        data = request.data

        serializer = TransactionSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        pipeline = get_pipline_transaction_from_collection(
            merchant_id=data.get('merchant_id'),
            mode=data['mode'],
            transaction_type=data['type'],
        )
        result_cursor = db.transaction_summary.aggregate(pipeline)
        formatted_result = list(result_cursor)
        return Response(formatted_result, status=status.HTTP_200_OK)


class NotificationView(APIView):
    def post(self, request):
        data = request.data
        serializer = NotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        notification = {
            "body": data['body'],
            "recipient": data['recipient'],
            "medium": data['medium'],
            "merchant_id": data['merchant_id'],
            "metadat": data.get('metadata')
        }
        result = NotificationSchema.create(notification)
        notification_id = result.id

        send_notification.apply_async((str(notification_id),))
        return Response({"message": "Notification queued for sending"}, status=status.HTTP_201_CREATED)

