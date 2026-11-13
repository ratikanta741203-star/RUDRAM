from django.urls import path
from apps.reports import views

urlpatterns = [
    path('reports/', views.reports_view, name='reports'),
    path('api/reports/export-csv/', views.ExportCsvAPIView.as_view(), name='api_reports_export_csv'),
    path('api/reports/export-pdf/', views.ExportPdfAPIView.as_view(), name='api_reports_export_pdf'),
]
