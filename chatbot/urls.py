from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Main chatbot interface
    path('', views.chatbot_home, name='chatbot_home'),
    path('send-message/', views.send_message, name='send_message'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    
    # Symptom checker tool
    path('symptom-checker/', views.symptom_checker, name='symptom_checker'),
    
    # Chat history and viewing
    path('history/', views.chat_history, name='chat_history'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    
    # Resources
    path('health-resources/', views.health_resources, name='health_resources'),
]
