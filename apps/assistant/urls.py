from django.urls import path
from apps.assistant import views

urlpatterns = [
    path('assistant/', views.assistant_view, name='assistant'),
    path('api/assistant/analyze/', views.AssistantAnalyzeAPIView.as_view(), name='api_assistant_analyze'),
    path('api/assistant/chat/', views.AssistantChatAPIView.as_view(), name='api_assistant_chat'),
]
