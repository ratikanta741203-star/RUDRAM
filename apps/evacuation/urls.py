from django.urls import path
from apps.evacuation import views

urlpatterns = [
    path('evacuation/', views.evacuation_view, name='evacuation'),
    path('api/evacuation/route/', views.EvacuationRouteAPIView.as_view(), name='api_evacuation_route'),
]
