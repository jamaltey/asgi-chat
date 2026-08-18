from django.urls import path
from .views import ChatView, GlobalChatView
from .api.views import stream_chat_events

app_name = 'core'

urlpatterns = [
    path('', GlobalChatView.as_view(), name='home'),
    path('chat/<int:pk>/', ChatView.as_view(), name='chat'),
]
