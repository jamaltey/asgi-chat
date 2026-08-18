from rest_framework import serializers
from core.models import Message, Chat
from accounts.models import User

class MessageSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Message
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['chat'].queryset = self.context['request'].user.chats.all()

    def create(self, validated_data):
        user: User = self.context['request'].user
        user.typing_chat = None # Reset typing
        user.save()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Allow updating only message text
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance

class ChatSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(slug_field='username', many=True, queryset=User.objects.all())

    class Meta:
        model = Chat
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['members'].child_relation.queryset = self.context['request'].user.friends.all()

    def validate_members(self, members):
        user = self.context['request'].user
        if user not in members:
            members.append(user)
        if len(members) < 2:
            raise serializers.ValidationError(
                'A chat must have at least 2 members.'
            )
        return members
