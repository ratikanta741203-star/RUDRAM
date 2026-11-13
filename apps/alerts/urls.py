from django.urls import path
from apps.alerts import views

urlpatterns = [
    path('alerts/', views.alerts_view, name='alerts'),
    path('api/alerts/', views.AlertListCreateAPIView.as_view(), name='api_alerts'),
    path('api/alerts/<int:pk>/dismiss/', views.AlertDismissAPIView.as_view(), name='api_alert_dismiss'),
    path('api/alerts/request-change/', views.AlertRequestChangeAPIView.as_view(), name='api_alert_request_change'),
    path('api/admin/alert-requests/<int:pk>/review/', views.AdminAlertReviewAPIView.as_view(), name='api_admin_alert_review'),
]
