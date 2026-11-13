from django.urls import path
from apps.fire import views

urlpatterns = [
    path('api/fire/hotspots/', views.FireHotspotsAPIView.as_view(), name='api_fire_hotspots'),
]
