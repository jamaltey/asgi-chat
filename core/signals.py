from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Chat

@receiver(m2m_changed, sender=Chat.members.through)
def update_chat_name(sender, instance, **kwargs):
    if not instance.name or instance.name.isspace():
        instance.name = ', '.join([member.username for member in instance.members.all()])
        instance.save(update_fields=['name'])
