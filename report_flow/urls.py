from report_flow.views import TransactionV1View, TransactionV2View, \
    NotificationView
from django.urls import path


urlpatterns = [
    path('v1/report', TransactionV1View.as_view(), name='get_report'),
    path('v2/report', TransactionV2View.as_view(), name='get_report'),
    path('notif', NotificationView.as_view(), name='send_notif'),
]
