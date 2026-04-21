import uuid
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.db.models import Q
from .models import ChatbotConversation, ChatMessage, HealthTopic, ChatbotFeedback
from .forms import ChatMessageForm, ChatbotFeedbackForm, QuickSymptomCheckForm


def get_or_create_session(request):
    """Get or create a session ID for the user"""
    if 'chatbot_session_id' not in request.session:
        request.session['chatbot_session_id'] = str(uuid.uuid4())
    return request.session['chatbot_session_id']


def get_chatbot_conversation(request):
    """Get or create a ChatbotConversation for the current user/session"""
    session_id = get_or_create_session(request)
    
    try:
        conversation = ChatbotConversation.objects.get(session_id=session_id)
    except ChatbotConversation.DoesNotExist:
        conversation = ChatbotConversation.objects.create(
            session_id=session_id,
            user=request.user if request.user.is_authenticated else None
        )
    
    return conversation


def detect_urgency(user_message):
    """
    Detect urgency level from user message
    Returns: 'emergency', 'high', 'medium', or 'low'
    """
    emergency_keywords = [
        'chest pain', 'difficulty breathing', 'shortness of breath', 'choking',
        'severe bleeding', 'loss of consciousness', 'sudden severe',
        'stroke', 'heart attack', 'can\'t breathe', 'unconscious',
        'severe allergic', 'poison', 'overdose', 'suicide',
    ]
    
    high_keywords = [
        'severe fever', 'high fever', 'severe headache', 'severe pain',
        'persistent vomiting', 'confusion', 'uncontrolled bleeding',
        'severe dizziness', 'fainting',
    ]
    
    message_lower = user_message.lower()
    
    for keyword in emergency_keywords:
        if keyword in message_lower:
            return 'emergency'
    
    for keyword in high_keywords:
        if keyword in message_lower:
            return 'high'
    
    if any(word in message_lower for word in ['severe', 'critical', 'urgent', 'emergency']):
        return 'high'
    
    if any(word in message_lower for word in ['pain', 'hurt', 'ache', 'discomfort']):
        return 'medium'
    
    return 'low'


def extract_symptoms(user_message):
    """Extract mentioned symptoms from user message"""
    symptom_keywords = {
        'fever': ['fever', 'high temperature', 'temp', 'pyrexia'],
        'cough': ['cough', 'coughing', 'dry cough', 'wet cough'],
        'sore_throat': ['sore throat', 'throat pain', 'throat ache', 'redness in throat'],
        'headache': ['headache', 'head pain', 'migraine', 'head ache'],
        'fatigue': ['fatigue', 'tiredness', 'exhaustion', 'weak', 'weakness'],
        'nausea': ['nausea', 'nauseous', 'vomit', 'vomiting', 'gastric'],
        'body_aches': ['body aches', 'muscle pain', 'joint pain', 'aching', 'soreness'],
        'difficulty_breathing': ['difficulty breathing', 'shortness of breath', 'can\'t breathe', 'breathless'],
        'chest_pain': ['chest pain', 'chest discomfort', 'chest ache'],
        'dizziness': ['dizziness', 'vertigo', 'dizzy', 'lightheaded'],
    }
    
    detected_symptoms = []
    message_lower = user_message.lower()
    
    for symptom, keywords in symptom_keywords.items():
        for keyword in keywords:
            if keyword in message_lower:
                detected_symptoms.append(symptom)
                break
    
    return detected_symptoms


def generate_chatbot_response(user_message, detected_symptoms, urgency_level):
    """
    Generate a response based on user message and symptoms
    Follows healthcare chatbot guidelines: informational only, no diagnosis/prescription
    """
    
    # Emergency protocol
    if urgency_level == 'emergency':
        return {
            'response': (
                "🚨 **EMERGENCY DETECTED** 🚨\n\n"
                "**Please seek IMMEDIATE medical attention:**\n\n"
                "1. **Call Emergency Services (911 in the US)** or your local emergency number\n"
                "2. **Go to the nearest Emergency Room** if you can safely travel\n"
                "3. **Do not delay seeking professional help**\n\n"
                "This chatbot is for informational purposes only and cannot provide emergency care.\n\n"
                "**If you're in a developing country, call your local emergency service immediately.**"
            ),
            'requires_escalation': True,
            'show_resources': True,
        }
    
    # Check Health Topics database first
    matching_topics = HealthTopic.objects.filter(
        is_active=True
    ).filter(
        Q(keywords__icontains=user_message[:30]) |
        Q(title__icontains=user_message[:20])
    )[:1]
    
    if matching_topics.exists():
        topic = matching_topics.first()
        response = topic.response
    else:
        # Generate contextual response based on detected symptoms
        if detected_symptoms:
            symptoms_str = ', '.join(detected_symptoms)
            response = generate_symptom_response(symptoms_str, urgency_level)
        else:
            # General wellness response
            response = generate_general_response(user_message)
    
    return {
        'response': response,
        'requires_escalation': urgency_level in ['high', 'emergency'],
        'show_resources': urgency_level in ['high', 'emergency'],
    }


def generate_symptom_response(symptoms_str, urgency_level):
    """Generate a response for symptom-related queries"""
    
    response = f"""Thank you for sharing your symptoms. I understand you're experiencing: {symptoms_str.replace('_', ' ')}.

**What I can do:**
- Provide general information about these symptoms
- Suggest when to seek professional care
- Offer wellness tips

**What I CANNOT do:**
- Provide a diagnosis
- Prescribe medications
- Determine if your condition is serious

**Important Guidance:**
"""
    
    if urgency_level == 'high':
        response += """
- Your symptoms may warrant professional attention soon
- **Please contact your healthcare provider or visit urgent care if:**
  - Symptoms worsen significantly
  - Symptoms persist beyond a few days
  - You develop additional concerning symptoms
"""
    else:
        response += """
- For mild symptoms, monitor them closely
- **Consider seeing a healthcare provider if:**
  - Symptoms persist for more than a week
  - Symptoms worsen unexpectedly
  - You're concerned about your health
"""
    
    response += """

**General Wellness Tips:**
1. Stay hydrated by drinking plenty of water
2. Get adequate rest and sleep
3. Practice good hygiene to prevent spreading illness
4. Avoid stress and maintain a healthy diet
5. Monitor your symptoms and keep track of any changes

**When to Seek Immediate Care:**
- Difficulty breathing or shortness of breath
- Chest pain or pressure
- Severe or worsening symptoms
- Loss of consciousness
- Signs of severe allergic reaction
- Any symptom that feels life-threatening

**Next Steps:**
Would you like information about:
1. General wellness tips for these symptoms?
2. When to contact a healthcare provider?
3. Information about common health conditions?

Please reach out to a healthcare professional for personalized medical advice."""
    
    return response


def generate_general_response(user_message):
    """Generate a general wellness response"""
    
    return """Thank you for your question. I'm here to provide general health information and wellness guidance.

**What I can help with:**
- General information about common health topics
- Wellness and prevention advice
- Guidance on when to seek professional care
- Information about healthy lifestyles

**What I CANNOT do:**
- Diagnose medical conditions
- Prescribe medications or treatments
- Provide personalized medical advice
- Replace professional medical consultation

**How can I assist you further?**
You can ask me about:
1. General symptoms and when to see a doctor
2. Healthy lifestyle and wellness tips
3. Common health conditions (informational only)
4. When to seek emergency care

**For serious health concerns, please:**
- Contact your healthcare provider
- Visit an urgent care clinic
- Call emergency services if needed
- Consult a medical professional in person

Is there a specific health or wellness topic you'd like to know more about?"""


def chatbot_home(request):
    """Home page for the health chatbot"""
    conversation = get_chatbot_conversation(request)
    form = ChatMessageForm()
    quick_symptom_form = QuickSymptomCheckForm()
    
    context = {
        'conversation': conversation,
        'form': form,
        'quick_symptom_form': quick_symptom_form,
        'messages': conversation.messages.all(),
    }
    return render(request, 'chatbot/chatbot.html', context)


@require_http_methods(["POST"])
def send_message(request):
    """Handle sending a chat message and getting response"""
    conversation = get_chatbot_conversation(request)
    
    form = ChatMessageForm(request.POST)
    if not form.is_valid():
        return JsonResponse({
            'success': False,
            'errors': form.errors,
        }, status=400)
    
    user_message = form.cleaned_data['message']
    
    # Detect urgency and symptoms
    urgency_level = detect_urgency(user_message)
    detected_symptoms = extract_symptoms(user_message)
    symptoms_str = ', '.join(detected_symptoms) if detected_symptoms else None
    
    # Save user message
    user_msg = ChatMessage.objects.create(
        conversation=conversation,
        message_type='user',
        content=user_message,
        urgency_level=urgency_level,
        symptom_mentioned=symptoms_str,
    )
    
    # Generate response
    response_data = generate_chatbot_response(user_message, detected_symptoms, urgency_level)
    
    # Save assistant response
    assistant_msg = ChatMessage.objects.create(
        conversation=conversation,
        message_type='assistant',
        content=response_data['response'],
        urgency_level=urgency_level,
    )
    
    return JsonResponse({
        'success': True,
        'user_message': {
            'id': user_msg.id,
            'content': user_msg.content,
            'timestamp': user_msg.timestamp.strftime('%H:%M:%S'),
        },
        'assistant_message': {
            'id': assistant_msg.id,
            'content': assistant_msg.content,
            'timestamp': assistant_msg.timestamp.strftime('%H:%M:%S'),
        },
        'urgency_level': urgency_level,
        'requires_escalation': response_data['requires_escalation'],
        'show_resources': response_data['show_resources'],
    })


@require_http_methods(["POST"])
def submit_feedback(request):
    """Handle feedback submission for chatbot responses"""
    message_id = request.POST.get('message_id')
    
    try:
        message = ChatMessage.objects.get(id=message_id)
    except ChatMessage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found'}, status=404)
    
    form = ChatbotFeedbackForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    feedback = form.save(commit=False)
    feedback.message = message
    feedback.user = request.user if request.user.is_authenticated else None
    feedback.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Thank you for your feedback!'
    })


def symptom_checker(request):
    """Quick symptom checker tool"""
    form = QuickSymptomCheckForm()
    context = {
        'form': form,
    }
    
    if request.method == 'POST':
        form = QuickSymptomCheckForm(request.POST)
        if form.is_valid():
            symptom = form.cleaned_data['symptom']
            duration = form.cleaned_data['duration']
            severity = form.cleaned_data['severity']
            other_symptoms = form.cleaned_data['other_symptoms']
            
            # Generate advice based on symptom
            advice = generate_symptom_advice(symptom, duration, severity, other_symptoms)
            context['advice'] = advice
            context['form'] = form
    
    return render(request, 'chatbot/symptom_checker.html', context)


def generate_symptom_advice(symptom, duration, severity, other_details):
    """Generate general advice for specific symptoms"""
    
    symptom_info = {
        'fever': {
            'description': 'Elevated body temperature',
            'general_advice': [
                'Keep hydrated with water, warm tea, or electrolyte drinks',
                'Rest in a cool environment',
                'Use light clothing and bedding',
                'Monitor temperature regularly',
            ],
            'see_doctor_if': [
                'Temperature exceeds 103°F (39.4°C) in adults',
                'Temperature exceeds 101°F (38.3°C) in children',
                'Fever lasts more than 3 days',
                'Accompanied by severe symptoms',
            ],
        },
        'cough': {
            'description': 'Persistent or new onset cough',
            'general_advice': [
                'Stay hydrated to help loosen mucus',
                'Use honey (for adults and children over 1 year)',
                'Try saline nasal drops or spray',
                'Rest your voice if possible',
                'Keep air moist with a humidifier',
            ],
            'see_doctor_if': [
                'Cough lasts more than a week',
                'Producing blood or yellow/green mucus',
                'Difficulty breathing',
                'Accompanied by chest pain',
            ],
        },
        'sore_throat': {
            'description': 'Throat pain or irritation',
            'general_advice': [
                'Gargle with warm salt water (1/2 teaspoon salt in 8 oz water)',
                'Drink warm (not hot) liquids',
                'Use honey to soothe throat',
                'Avoid irritants like smoke and cold air',
                'Take lozenges or hard candies',
            ],
            'see_doctor_if': [
                'Severe difficulty swallowing',
                'Difficulty breathing',
                'White or yellow patches in throat',
                'Fever above 101°F (38.3°C)',
            ],
        },
        'headache': {
            'description': 'Head pain or discomfort',
            'general_advice': [
                'Rest in a quiet, dark room',
                'Apply cold or warm compress to forehead or neck',
                'Stay hydrated',
                'Practice relaxation or deep breathing',
                'Maintain regular sleep patterns',
            ],
            'see_doctor_if': [
                'Sudden severe headache (worst of your life)',
                'Accompanied by fever, stiff neck, or confusion',
                'Confused vision or difficulty speaking',
                'Headaches becoming more frequent or severe',
            ],
        },
        'fatigue': {
            'description': 'Persistent tiredness or low energy',
            'general_advice': [
                'Ensure adequate sleep (7-9 hours per night)',
                'Eat balanced meals with adequate iron and B vitamins',
                'Stay hydrated throughout the day',
                'Exercise regularly but don\'t overexert',
                'Manage stress with meditation or relaxation techniques',
            ],
            'see_doctor_if': [
                'Fatigue is severe or debilitating',
                'Unexplained and persistent (more than 2 weeks)',
                'Accompanied by weight loss or other symptoms',
                'Interfering with daily activities',
            ],
        },
        'nausea': {
            'description': 'Feeling of sickness or need to vomit',
            'general_advice': [
                'Eat small, frequent meals',
                'Avoid strong smells and greasy foods',
                'Drink ginger tea or peppermint tea',
                'Stay hydrated with small sips of water',
                'Rest and avoid sudden movements',
            ],
            'see_doctor_if': [
                'Vomiting for more than a few hours',
                'Unable to keep liquids down',
                'Signs of dehydration (dry mouth, no urination)',
                'Persistent with other severe symptoms',
            ],
        },
        'body_aches': {
            'description': 'Muscle or joint pain throughout the body',
            'general_advice': [
                'Rest and elevate affected areas when possible',
                'Apply warm compress for muscle aches',
                'Keep moving with gentle stretching',
                'Maintain good posture',
                'Stay active but avoid overexertion',
            ],
            'see_doctor_if': [
                'Pain is severe or unbearable',
                'Accompanied by swelling or redness',
                'Limited range of motion',
                'Persists for more than a week without improvement',
            ],
        },
        'difficulty_breathing': {
            'description': 'Shortness of breath or labored breathing',
            'general_advice': [
                '**This may require urgent care - consult a professional soon**',
                'Sit upright to aid breathing',
                'Use breathing exercises (slow, deep breaths)',
                'Avoid allergens and irritants',
                'Keep air clean and humid',
            ],
            'see_doctor_if': [
                'Difficulty breathing at rest',
                'Chest pain during breathing',
                'High heart rate',
                'Blue lips or nails',
                '**Any severe difficulty breathing requires immediate medical attention**',
            ],
        },
        'chest_pain': {
            'description': 'Pain or discomfort in the chest area',
            'general_advice': [
                '**This may be serious and requires professional evaluation**',
                'Rest and avoid strenuous activity',
                'Try to remain calm',
                'Note when pain occurs and what makes it better/worse',
            ],
            'see_doctor_if': [
                '**Any persistent or new chest pain requires medical attention**',
                'Severe crushing pain',
                'Pain radiating to arm, neck, or jaw',
                '**If severe, call emergency services immediately**',
            ],
        },
        'dizziness': {
            'description': 'Feeling lightheaded or unbalanced',
            'general_advice': [
                'Sit or lie down immediately',
                'Stay hydrated',
                'Avoid sudden position changes',
                'Move slowly and carefully',
                'Avoid alcohol and certain medications',
            ],
            'see_doctor_if': [
                'Accompanied by chest pain or difficulty breathing',
                'Sudden or severe dizziness',
                'Persistent for days',
                'With confusion or vision changes',
            ],
        },
    }
    
    if symptom not in symptom_info:
        return {
            'symptom': symptom,
            'description': 'Symptom information not available in quick checker',
            'advice': ['Please describe your specific symptoms in the main chatbot for personalized guidance'],
            'when_to_see_doctor': ['Consult a healthcare provider for accurate evaluation'],
        }
    
    info = symptom_info[symptom]
    
    advice = {
        'symptom': ' '.join(word.capitalize() for word in symptom.split('_')),
        'description': info['description'],
        'duration': duration,
        'severity': severity,
        'advice': info['general_advice'],
        'when_to_see_doctor': info['see_doctor_if'],
        'additional_details': other_details,
    }
    
    return advice


def chat_history(request):
    """View chat history for authenticated users"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    conversations = ChatbotConversation.objects.filter(
        user=request.user
    ).prefetch_related('messages')
    
    context = {
        'conversations': conversations,
    }
    return render(request, 'chatbot/chat_history.html', context)


def conversation_detail(request, conversation_id):
    """View detailed conversation"""
    conversation = get_object_or_404(ChatbotConversation, id=conversation_id)
    
    # Security check - ensure user can only view their own conversations
    if conversation.user != request.user and not request.user.is_staff:
        return redirect('chatbot:chatbot_home')
    
    messages = conversation.messages.all()
    
    context = {
        'conversation': conversation,
        'messages': messages,
    }
    return render(request, 'chatbot/conversation_detail.html', context)


def health_resources(request):
    """Page with health resources and emergency contacts"""
    context = {
        'emergency_numbers': {
            'US': '911',
            'UK': '999',
            'India': '102 or 100 + medical service number',
            'Australia': '000',
            'Canada': '911',
        },
        'hotlines': [
            {'name': 'Mental Health Crisis Line', 'number': '988 (US)', 'description': 'Suicide and Crisis Lifeline'},
            {'name': 'Poison Control', 'number': '1-800-222-1222 (US)', 'description': 'Poison emergency'},
            {'name': 'Domestic Violence Hotline', 'number': '1-800-799-7233 (US)', 'description': '24/7 support'},
        ],
        'resources': [
            {'title': 'When to Seek Urgent Care', 'description': 'Guidelines for urgent vs. emergency symptoms'},
            {'title': 'Wellness Tips', 'description': 'General health and wellness advice'},
            {'title': 'Medication Safety', 'description': 'Important information about medications'},
        ]
    }
    return render(request, 'chatbot/health_resources.html', context)
