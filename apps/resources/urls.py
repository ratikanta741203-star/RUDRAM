from django.urls import path
from apps.resources import views

urlpatterns = [
    path('resources/', views.resources_view, name='resources'),
    path('resources/dispatch/', views.dispatch_resource_view, name='resource_dispatch'),
    path('resources/update-stock/', views.update_stock_view, name='resource_update_stock'),
    path('resources/team-status/', views.update_team_status_view, name='team_status_update'),

    path('api/resources/', views.ResourceListAPIView.as_view(), name='api_resources'),
    path('api/resources/allocate/', views.ResourceAllocateAPIView.as_view(), name='api_resources_allocate'),
    path('api/rescue-teams/', views.RescueTeamListAPIView.as_view(), name='api_rescue_teams'),
]
