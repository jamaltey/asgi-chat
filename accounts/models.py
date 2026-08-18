from django.contrib.auth.models import AbstractUser
from core.models import *

class User(AbstractUser):
    first_name = None
    last_name = None
    display_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=False, unique=True, max_length=254)
    bio = models.TextField(max_length=190, blank=True)
    profile_pic = models.ImageField(upload_to='images', null=True, blank=True)
    friends = models.ManyToManyField('self', blank=True)
    typing_chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='typing_users', blank=True, null=True)

    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        if not self.display_name or self.display_name.isspace():
            self.display_name = self.username
        super().save(*args, **kwargs)

    @property
    def pfp(self): # profile picture
        return self.profile_pic.url if self.profile_pic else '/static/icons/profile.png'
    
    def get_related_messages(self):
        messages = [i.messages.all() for i in self.chats.all()]
        messages = [i for sublist in messages for i in sublist] # flatten
        messages.extend(Message.objects.filter(chat__isnull=True)) # add global messages
        return messages

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        existing_request = FriendRequest.objects.filter(from_user=self.to_user, to_user=self.from_user)
        if existing_request.exists():
            existing_request[0].accept()
            self.delete()

    def accept(self):
        self.from_user.friends.add(self.to_user)
        self.delete()

    def reject(self):
        self.delete()

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"from {self.from_user} to {self.to_user}"
