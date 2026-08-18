from django.http import HttpRequest, StreamingHttpResponse
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import MessageSerializer, ChatSerializer
from .permissions import IsAuthor
from accounts.models import User
from core.models import *

class MessageViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    API endpoint that allows messages to be created or deleted.
    """
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated, IsAuthor]

class ChatViewSet(CreateModelMixin, GenericViewSet):
    """
    API endpoint that allows chats to be created.
    """
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()
    permission_classes = [IsAuthenticated]

# Stream chat events

import asyncio, json
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user

async def stream_chat_events(request: HttpRequest, chat: int | None = None) -> StreamingHttpResponse:
    """
    Streams chat messages to the client as they are created or deleted.
    """
    user: User = await sync_to_async(get_user)(request)
    chat = await sync_to_async(user.chats.get)(id=chat) if chat else None

    async def event_stream():
        """
        Send a continuous stream of data to the connected clients.
        """
        try:
            previous_messages = await get_all_message_ids()
            previous_typing_users = await get_typing_users()
            
            events = []

            # Send initial state
            if previous_typing_users:
                events.append({'action': 'typing', 'users': list(previous_typing_users)})

            while True:
                current_messages = await get_all_message_ids()
                
                # Handle typing users
                typing_users = await get_typing_users()
                if typing_users != previous_typing_users:
                    previous_typing_users = typing_users
                    typing_users = list(typing_users)
                    events.append({'action': 'typing', 'users': typing_users})
                
                # Handle new messages
                new_message_ids = current_messages - previous_messages
                new_messages = await sync_to_async(list)(Message.objects.filter(id__in=new_message_ids))
                for message in new_messages:
                    message = await sync_to_async(dict)(message)
                    events.append({'action': 'create', 'message': message})

                # Handle deleted messages
                deleted_message_ids = previous_messages - current_messages
                for message_id in deleted_message_ids:
                    events.append({'action': 'delete', 'message_id': message_id})

                for event in events:
                    yield 'data: %s\n\n' % json.dumps(event)

                events = []

                previous_messages = current_messages
                await asyncio.sleep(0.1)  # To reduce db queries

        except asyncio.CancelledError:
            user.typing_chat = None # Stop typing
            await user.asave()
            raise asyncio.CancelledError

    async def get_all_message_ids() -> set[int]:
        messages = await sync_to_async(user.get_related_messages)()
        messages = set( message.id for message in messages )
        return messages

    async def get_typing_users() -> set[str]:
        if not chat:
            return set()
        users = await sync_to_async(set)(
            chat.typing_users.values_list('username', flat=True)
        )
        return users

    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")

