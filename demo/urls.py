from django.urls import path
from demo import views

urlpatterns = [
    path('api/demo/run-scenario/', views.RunDemoScenarioAPIView.as_view(), name='api_demo_run_scenario'),
    path('api/demo/reset/', views.ResetDemoAPIView.as_view(), name='api_demo_reset'),
]
