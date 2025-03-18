from rest_framework import serializers
from .models import Documents, Conversation, Message

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documents
        fields = ['id', 'title','file_type', 'created_at']
        read_only_fields = ['created_at', 'updated_at']

class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    title = serializers.CharField(required=False)
    chunk_size = serializers.IntegerField(required=False, default=1000)
    chunk_overlap = serializers.IntegerField(required=False, default=200)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'role', 'content', 'created_at']
        read_only_fields = ['created_at']

class ConversationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'user', 'title', 'created_at']
        read_only_fields = ['created_at']

class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'user', 'title',
        'created_at', 'messages']
        read_only_fields = ['created_at']