from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Documents(models.Model):
    title = models.CharField(max_length = 255)
    content = models.TextField()
    file = models.FileField(upload_to='documents/', null=True, blank=True)
    file_type = models.CharField(max_length = 50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, default="New Conversation")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Message(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
    )
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices= ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:30]}..." 