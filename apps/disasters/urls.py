from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.disasters import views

router = DefaultRouter()
router.register(r'disasters', views.DisasterViewSet, basename='disaster')

urlpatterns = [
    path('drone-view/', views.drone_view, name='drone_view'),
    path('disasters/', views.disasters_list_view, name='disasters_list'),
    path('disasters/<int:pk>/', views.disaster_detail_view, name='disaster_detail'),
    path('api/', include(router.urls)),
]
