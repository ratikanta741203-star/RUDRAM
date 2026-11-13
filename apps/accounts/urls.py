from django.urls import path
from apps.accounts import views, admin_views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('citizen/signup/', views.citizen_signup_view, name='citizen_signup'),
    path('logout/', views.logout_view, name='logout'),
    path('switch-role/', views.switch_role_view, name='switch_role'),
    path('api/current-user/', views.CurrentUserAPIView.as_view(), name='api_current_user'),

    # Admin & Operator Dashboards
    path('admin-dashboard/', admin_views.admin_dashboard_view, name='admin_dashboard'),
    path('operator-dashboard/', admin_views.operator_dashboard_view, name='operator_dashboard'),

    # Admin Shelter CRUD
    path('admin-dashboard/shelters/create/', admin_views.admin_shelter_create, name='admin_shelter_create'),
    path('admin-dashboard/shelters/<int:pk>/update/', admin_views.admin_shelter_update, name='admin_shelter_update'),
    path('admin-dashboard/shelters/<int:pk>/delete/', admin_views.admin_shelter_delete, name='admin_shelter_delete'),

    # Admin Resource CRUD
    path('admin-dashboard/resources/create/', admin_views.admin_resource_create, name='admin_resource_create'),
    path('admin-dashboard/resources/<int:pk>/update/', admin_views.admin_resource_update, name='admin_resource_update'),
    path('admin-dashboard/resources/<int:pk>/delete/', admin_views.admin_resource_delete, name='admin_resource_delete'),

    # Admin Rescue Team CRUD
    path('admin-dashboard/teams/create/', admin_views.admin_team_create, name='admin_team_create'),
    path('admin-dashboard/teams/<int:pk>/update/', admin_views.admin_team_update, name='admin_team_update'),
    path('admin-dashboard/teams/<int:pk>/delete/', admin_views.admin_team_delete, name='admin_team_delete'),

    # Admin Disaster Event CRUD
    path('admin-dashboard/disasters/create/', admin_views.admin_disaster_create, name='admin_disaster_create'),
    path('admin-dashboard/disasters/<int:pk>/update/', admin_views.admin_disaster_update, name='admin_disaster_update'),
    path('admin-dashboard/disasters/<int:pk>/delete/', admin_views.admin_disaster_delete, name='admin_disaster_delete'),

    # Admin Alert CRUD
    path('admin-dashboard/alerts/create/', admin_views.admin_alert_create, name='admin_alert_create'),
    path('admin-dashboard/alerts/<int:pk>/update/', admin_views.admin_alert_update, name='admin_alert_update'),
    path('admin-dashboard/alerts/<int:pk>/delete/', admin_views.admin_alert_delete, name='admin_alert_delete'),

    # Admin User Management
    path('admin-dashboard/users/<int:pk>/toggle-active/', admin_views.admin_user_toggle_active, name='admin_user_toggle_active'),
    path('admin-dashboard/users/<int:pk>/update-role/', admin_views.admin_user_update_role, name='admin_user_update_role'),

    # Admin Approval Workflow Handlers
    path('admin-dashboard/approvals/<int:pk>/approve/', admin_views.admin_approval_approve, name='admin_approval_approve'),
    path('admin-dashboard/approvals/<int:pk>/reject/', admin_views.admin_approval_reject, name='admin_approval_reject'),

    # Admin-Only API Health Diagnostic Endpoint
    path('api/admin/api-health/', admin_views.AdminApiHealthCheckAPIView.as_view(), name='api_admin_api_health'),
]
