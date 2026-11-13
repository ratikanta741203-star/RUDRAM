from django.urls import path
from apps.risk import views

urlpatterns = [
    path('risk/', views.risk_prediction_view, name='risk_prediction'),
    path('api/risk/predict/', views.RiskPredictAPIView.as_view(), name='api_risk_predict'),
    path('api/risk/zones/', views.RiskZoneListAPIView.as_view(), name='api_risk_zones'),
]
