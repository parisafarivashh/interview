from rest_framework import serializers


class TransactionSerializer(serializers.Serializer):
    TRANSACTION_TYPE_CHOICES = ['count', 'amount']
    MODE_CHOICES = ['daily', 'weekly', 'monthly']

    type = serializers.ChoiceField(choices=TRANSACTION_TYPE_CHOICES)
    mode = serializers.ChoiceField(choices=MODE_CHOICES)
    merchant_id = serializers.CharField(max_length=100, required=False)


class NotificationSerializer(serializers.Serializer):
    body = serializers.CharField()
    recipient = serializers.CharField(max_length=255)
    medium = serializers.CharField(max_length=50)
    metadata = serializers.JSONField(required=False)
    merchant_id = serializers.CharField(max_length=255)
