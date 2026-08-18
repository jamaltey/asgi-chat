from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.http import Http404, HttpResponse
from core.models import *

class ChatView(LoginRequiredMixin, DetailView):
    model = Chat
    template_name = 'chat.html'
    context_object_name = 'chat'

    def get_queryset(self):
        return self.request.user.chats.all()

    def dispatch(self, request, *args, **kwargs):
        try: return super().dispatch(request, *args, **kwargs)
        except Http404: return redirect('core:home')

class GlobalChatView(ChatView):
    def get_object(self, queryset=None):
        return {
            'id': 0,
            'name': 'Global Chat',
            'messages': Message.objects.filter(chat__isnull=True),
        }
