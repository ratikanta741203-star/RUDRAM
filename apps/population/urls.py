from django.urls import path
from apps.population import views

urlpatterns = [
    path('population/', views.population_view, name='population'),
    path('api/population/exposure/', views.PopulationExposureAPIView.as_view(), name='api_population_exposure'),
]
