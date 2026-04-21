from django.contrib import admin
from .models import ChatbotConversation, ChatMessage, HealthTopic, ChatbotFeedback


@admin.register(HealthTopic)
class HealthTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'keywords', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Topic Information', {
            'fields': ('title', 'description')
        }),
        ('Search & Keywords', {
            'fields': ('keywords',),
            'description': 'Enter comma-separated keywords for matching user queries'
        }),
        ('Response', {
            'fields': ('response',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ChatbotConversation)
class ChatbotConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_info', 'created_at', 'is_active', 'message_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'session_id')
    readonly_fields = ('session_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Conversation Details', {
            'fields': ('session_id', 'user', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def user_info(self, obj):
        return obj.user.username if obj.user else f"Guest ({obj.session_id[:8]}...)"
    user_info.short_description = 'User'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'message_type', 'urgency_level', 'timestamp', 'content_preview')
    list_filter = ('message_type', 'urgency_level', 'timestamp')
    search_fields = ('content', 'conversation__session_id', 'conversation__user__username')
    readonly_fields = ('timestamp', 'content')
    
    fieldsets = (
        ('Message Details', {
            'fields': ('conversation', 'message_type', 'content')
        }),
        ('Medical Context', {
            'fields': ('symptom_mentioned', 'urgency_level'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(ChatbotFeedback)
class ChatbotFeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'rating_display', 'user_info', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('feedback_text', 'user__username', 'message__conversation__session_id')
    readonly_fields = ('created_at', 'feedback_text')
    
    fieldsets = (
        ('Feedback Details', {
            'fields': ('message', 'user', 'rating')
        }),
        ('Comment', {
            'fields': ('feedback_text',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def rating_display(self, obj):
        return f"{obj.get_rating_display()} ({obj.rating}/5)"
    rating_display.short_description = 'Rating'
    
    def user_info(self, obj):
        return obj.user.username if obj.user else 'Anonymous'
    user_info.short_description = 'User'
