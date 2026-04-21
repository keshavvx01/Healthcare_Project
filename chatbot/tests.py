from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import ChatbotConversation, ChatMessage, HealthTopic, ChatbotFeedback


class ChatbotConversationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.conversation = ChatbotConversation.objects.create(
            session_id='test-session-123',
            user=self.user
        )
    
    def test_conversation_creation(self):
        self.assertTrue(self.conversation.is_active)
        self.assertEqual(self.conversation.user, self.user)
    
    def test_conversation_str(self):
        self.assertIn('testuser', str(self.conversation))


class ChatMessageTestCase(TestCase):
    def setUp(self):
        self.conversation = ChatbotConversation.objects.create(
            session_id='test-session-456'
        )
    
    def test_create_user_message(self):
        message = ChatMessage.objects.create(
            conversation=self.conversation,
            message_type='user',
            content='I have a fever',
            urgency_level='medium'
        )
        self.assertEqual(message.message_type, 'user')
        self.assertEqual(message.content, 'I have a fever')
        self.assertEqual(message.urgency_level, 'medium')
    
    def test_create_assistant_message(self):
        message = ChatMessage.objects.create(
            conversation=self.conversation,
            message_type='assistant',
            content='Here is general information about fever...'
        )
        self.assertEqual(message.message_type, 'assistant')


class HealthTopicTestCase(TestCase):
    def setUp(self):
        self.topic = HealthTopic.objects.create(
            title='Common Cold',
            description='Information about common cold',
            keywords='cold, cough, sneezing, flu',
            response='A common cold is...'
        )
    
    def test_topic_creation(self):
        self.assertEqual(self.topic.title, 'Common Cold')
        self.assertTrue(self.topic.is_active)
    
    def test_topic_str(self):
        self.assertEqual(str(self.topic), 'Common Cold')


class ChatbotViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
    
    def test_chatbot_home_page_loads(self):
        response = self.client.get('/chatbot/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chatbot/chatbot.html')
    
    def test_symptom_checker_page_loads(self):
        response = self.client.get('/chatbot/symptom-checker/')
        self.assertEqual(response.status_code, 200)
    
    def test_health_resources_page_loads(self):
        response = self.client.get('/chatbot/health-resources/')
        self.assertEqual(response.status_code, 200)


class ChatbotFeedbackTestCase(TestCase):
    def setUp(self):
        self.conversation = ChatbotConversation.objects.create(
            session_id='test-session-789'
        )
        self.message = ChatMessage.objects.create(
            conversation=self.conversation,
            message_type='assistant',
            content='Test response'
        )
    
    def test_create_feedback(self):
        feedback = ChatbotFeedback.objects.create(
            message=self.message,
            rating=4,
            feedback_text='Very helpful response'
        )
        self.assertEqual(feedback.rating, 4)
        self.assertEqual(feedback.message, self.message)
