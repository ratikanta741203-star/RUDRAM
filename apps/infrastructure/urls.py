from django.urls import path
from apps.infrastructure import views

urlpatterns = [
    path('api/infrastructure/', views.InfrastructureListAPIView.as_view(), name='api_infrastructure'),
    path('api/infrastructure/water-bodies/', views.WaterBodiesAPIView.as_view(), name='api_water_bodies'),
]
