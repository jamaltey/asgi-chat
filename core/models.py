from django.db import models

class Chat(models.Model):
    icon = models.ImageField(upload_to='images', null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, default='')
    # admins = models.ManyToManyField('accounts.User', related_name='admin_chats')
    members = models.ManyToManyField('accounts.User', related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def icon_url(self):
        if self.icon:
            return self.icon.url
        return '/static/icons/chat.svg' if self.chat_type == 'group' else self.members.first().pfp

    @property
    def chat_type(self):
        if self.members.count() == 2:
            return 'private'
        return 'group'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.members.exists() and ( not self.name or self.name.isspace() ):
            self.name = ', '.join([member.username for member in self.members.all()])
            super().save(update_fields=['name'])

    def __str__(self):
        return f'{self.chat_type.capitalize()} chat "{self.name}"'

    class Meta:
        ordering = ['-created_at']

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', blank=True, null=True)
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    text = models.TextField(max_length=2000)
    timestamp = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return {
            'id': self.id,
            'author': { 'username': self.author.username, 'display_name': self.author.display_name, 'pfp': self.author.pfp },
            'chat_id': self.chat.id if self.chat else 0,
            'text': self.text,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M'),
        }

    def __iter__(self):
        return iter(self.to_dict().items())

    def __str__(self):
        chat = self.chat.name if self.chat else 'Global Chat'
        return f'({chat}) {self.author.username}: {self.text}'

    class Meta:
        ordering = ['timestamp']
