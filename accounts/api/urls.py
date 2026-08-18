from django.urls import path, re_path
from .views import *

app_name = 'api'

urlpatterns = [
    path('accept-friend-request/', accept_friend_request, name='accept-friend-request'),
    path('reject-friend-request/', reject_friend_request, name='reject-friend-request'),
    path('unfriend/', unfriend, name='unfriend'),
    re_path(r'^set-typing-status/(?P<chat>\d+)?$', set_typing_status, name='set-typing-status'),
]
