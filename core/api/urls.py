from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import *

app_name = 'api'

router = DefaultRouter()
router.register(r'chats', ChatViewSet, basename='chats')
router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = router.urls + [
    re_path(r'^stream-chat-events/(?P<chat>\d+)?$', stream_chat_events, name='stream-chat-events'),
]