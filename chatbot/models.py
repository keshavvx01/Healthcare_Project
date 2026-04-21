from django.db import models
from django.contrib.auth.models import User


class ChatbotConversation(models.Model):
    """Model to store chatbot conversations with tracking metadata"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        user_info = self.user.username if self.user else f"Guest ({self.session_id})"
        return f"Conversation - {user_info} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    def get_last_message(self):
        """Safely get the last message in the conversation"""
        return self.messages.last()

    class Meta:
        ordering = ['-created_at']


class ChatMessage(models.Model):
    """Model to store individual chat messages in a conversation"""
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('assistant', 'Assistant Response'),
        ('system', 'System Message'),
    ]

    conversation = models.ForeignKey(ChatbotConversation, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='user')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # For tracking context and response quality
    symptom_mentioned = models.CharField(max_length=200, blank=True, null=True)
    urgency_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('emergency', 'Emergency'),
        ],
        default='low',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.get_message_type_display()} - {self.conversation.id} - {self.timestamp.strftime('%H:%M:%S')}"

    class Meta:
        ordering = ['timestamp']


class HealthTopic(models.Model):
    """Model for frequently asked health topics and responses"""
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    keywords = models.TextField(help_text="Comma-separated keywords for matching user queries")
    response = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class ChatbotFeedback(models.Model):
    """Model to collect user feedback on chatbot responses"""
    RATING_CHOICES = [
        (1, 'Very Unhelpful'),
        (2, 'Unhelpful'),
        (3, 'Neutral'),
        (4, 'Helpful'),
        (5, 'Very Helpful'),
    ]

    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    feedback_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback - {self.get_rating_display()} - {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-created_at']
