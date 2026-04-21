"""
Chatbot Logic Module
Handles all core chatbot functionality including:
- Session management
- Urgency detection
- Symptom extraction
- Response generation
- Message processing
"""

import uuid
import re
from django.db.models import Q
from django.utils.timezone import now
from .models import ChatbotConversation, ChatMessage, HealthTopic, ChatbotFeedback


# ============================================================================
# SYMPTOM MAPPINGS & CONSTANTS
# ============================================================================

SYMPTOMS = {
    "fever": ["fever", "high temperature", "body heat", "hot", "pyrexia"],
    "cold": ["cold", "cough", "runny nose", "congestion", "sniffle"],
    "pain": ["pain", "ache", "hurt", "soreness", "aching"],
    "cough": ["cough", "coughing", "dry cough", "wet cough", "hacking"],
    "headache": ["headache", "head pain", "migraine", "head ache", "throbbing head"],
    "nausea": ["nausea", "nauseous", "vomit", "vomiting", "queasy"],
    "fatigue": ["fatigue", "tiredness", "exhaustion", "weak", "weakness"],
    "sore_throat": ["sore throat", "throat pain", "throat ache", "pharyngitis"],
    "chest_pain": ["chest pain", "chest hurt", "chest ache", "chest discomfort"],
    "dizziness": ["dizziness", "dizzy", "vertigo", "lightheaded", "spinning"]
}

INTENTS = {
    "greeting": ["hello", "hi", "hey"],
    "symptom": ["pain", "fever", "cough"],
    "emergency": ["chest pain", "cant breathe", "unconscious"]
}

RESPONSES = {
    "fever": {
        "advice": "Stay hydrated by drinking water and warm fluids. Get plenty of rest. You can use over-the-counter fever reducers if needed.",
        "warning": "Consult a doctor if fever persists for more than 2-3 days or exceeds 103°F (39.4°C).",
        "general": "Fever is often a sign that your body is fighting an infection."
    },
    "cold": {
        "advice": "Stay hydrated, get rest, and use saline nasal drops. Warm liquids like tea with honey can help soothe your throat.",
        "warning": "Seek medical attention if you develop difficulty breathing or severe symptoms.",
        "general": "A cold typically resolves on its own within 7-10 days."
    },
    "pain": {
        "advice": "Rest the affected area, apply ice or heat therapy, and take over-the-counter pain relievers if needed.",
        "warning": "Consult a doctor if pain is severe, persistent, or limits your daily activities.",
        "general": "Pain can result from many causes and usually improves with rest and care."
    },
    "cough": {
        "advice": "Stay hydrated, use honey and lemon in warm water, and get adequate rest. Avoid irritants like smoke.",
        "warning": "Consult a doctor if cough persists for more than 3 weeks or brings up blood.",
        "general": "A mild cough is often your body's way of clearing the airways."
    },
    "headache": {
        "advice": "Rest in a dark, quiet room, stay hydrated, and manage stress. Over-the-counter pain relievers may help.",
        "warning": "Seek immediate care if headache is severe, sudden, or accompanied by vision changes, stiffness, or confusion.",
        "general": "Headaches can be triggered by stress, dehydration, or muscle tension."
    },
    "nausea": {
        "advice": "Eat light, bland foods, stay hydrated with small sips of water, and rest. Ginger tea may help ease nausea.",
        "warning": "Seek medical attention if nausea lasts more than a few hours or is accompanied by severe symptoms.",
        "general": "Nausea can result from various causes including dietary or medication issues."
    },
    "fatigue": {
        "advice": "Get adequate sleep (7-9 hours), maintain a balanced diet, stay hydrated, and engage in light exercise.",
        "warning": "Consult a doctor if fatigue persists for weeks or is accompanied by other symptoms.",
        "general": "Fatigue is your body's signal that it needs rest and recovery."
    },
    "sore_throat": {
        "advice": "Gargle with salt water, drink warm liquids, use throat lozenges, and rest your voice.",
        "warning": "See a doctor if sore throat is severe, persists for more than a week, or is accompanied by high fever.",
        "general": "Sore throat often improves on its own within a few days."
    },
    "chest_pain": {
        "advice": "Stop all activities immediately and sit down. Stay calm. Do not drive yourself.",
        "warning": "SEEK EMERGENCY CARE IMMEDIATELY. Call 911 or emergency services. Do not wait.",
        "general": "Chest pain can be a sign of serious medical conditions and requires urgent evaluation."
    },
    "dizziness": {
        "advice": "Sit or lie down immediately. Stay in a safe position. Avoid sudden movements. Stay hydrated.",
        "warning": "Seek medical attention if dizziness is severe, persistent, or accompanied by other symptoms like vision loss or chest pain.",
        "general": "Dizziness can result from dehydration, blood pressure changes, or inner ear issues."
    }
}

# Urgency Levels Reference
URGENCY_LEVELS = {
    "Low": "General health questions or minor symptoms (information only needed)",
    "Medium": "Noticeable symptoms that warrant attention within 24-48 hours",
    "High": "Serious symptoms requiring same-day medical attention",
    "Emergency": "Life-threatening symptoms requiring immediate emergency services (911)"
}


# ============================================================================
# TEXT PREPROCESSING
# ============================================================================

def preprocess(text):
    """
    Preprocess user input text for NLP analysis.
    Normalizes text by converting to lowercase and removing special characters.
    
    Args:
        text (str): Raw user input text
    
    Returns:
        str: Cleaned and normalized text
    """
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text


def detect_symptom(message):
    """
    Detect a single symptom from a message using the SYMPTOMS mapping.
    Returns the first matching symptom found.
    
    Args:
        message (str): User message to analyze
    
    Returns:
        str: Symptom name if found, None otherwise
    
    Example:
        >>> detect_symptom("I have a high temperature")
        'fever'
    """
    message_processed = preprocess(message)
    
    for symptom, keywords in SYMPTOMS.items():
        for word in keywords:
            word_processed = preprocess(word)
            if word_processed in message_processed:
                return symptom
    
    return None


def detect_intent(message):
    """
    Detect user intent from message using simple keyword matching.
    Classifies user message into predefined intents without ML models.
    
    Intents:
    - 'greeting': User greeting messages
    - 'symptom': User describing health symptoms
    - 'emergency': User describing life-threatening emergency
    
    Args:
        message (str): User message to analyze
    
    Returns:
        str: Intent name if found, 'general' if no specific intent matched
    
    Example:
        >>> detect_intent("hello there")
        'greeting'
        >>> detect_intent("I have chest pain")
        'emergency'
        >>> detect_intent("what is diabetes")
        'general'
    """
    message_processed = preprocess(message)
    
    # Priority order: emergency > symptom > greeting (emergency has highest priority)
    intent_priority_order = ['emergency', 'symptom', 'greeting']
    
    for intent in intent_priority_order:
        if intent in INTENTS:
            keywords = INTENTS[intent]
            for keyword in keywords:
                keyword_processed = preprocess(keyword)
                if keyword_processed in message_processed:
                    return intent
    
    return 'general'


def detect_all_intents(message):
    """
    Detect all matching intents from a message (returns multiple if applicable).
    Useful for understanding complex user messages with multiple intents.
    
    Args:
        message (str): User message to analyze
    
    Returns:
        list: List of matching intent names, empty list if no matches
    
    Example:
        >>> detect_all_intents("Hi, I have chest pain")
        ['greeting', 'emergency']
    """
    message_processed = preprocess(message)
    detected_intents = []
    
    for intent, keywords in INTENTS.items():
        for keyword in keywords:
            keyword_processed = preprocess(keyword)
            if keyword_processed in message_processed:
                if intent not in detected_intents:
                    detected_intents.append(intent)
                break
    
    return detected_intents


def generate_symptom_response_text(symptom):
    """
    Generate a natural, structured response for a detected symptom.
    Uses the RESPONSES dictionary to create conversational advice.
    
    Args:
        symptom (str): Symptom key from RESPONSES dictionary
    
    Returns:
        str: Formatted response with general info, advice, and warnings
    
    Example:
        >>> generate_symptom_response_text("fever")
        "Fever is often a sign that your body is fighting an infection...
    """
    
    if symptom not in RESPONSES:
        return None
    
    response_data = RESPONSES[symptom]
    
    # Build conversational response
    response = f"""**Regarding {symptom.replace('_', ' ').title()}:**

{response_data['general']}

💡 **What you can do:**
{response_data['advice']}

⚠️ **When to seek help:**
{response_data['warning']}

Remember: This is general information only. For personalized medical advice, please consult with a healthcare professional."""
    
    return response


def generate_multi_symptom_response(symptoms):
    """
    Generate a response for multiple detected symptoms.
    Provides comprehensive guidance when user mentions multiple issues.
    
    Args:
        symptoms (list): List of symptom keys
    
    Returns:
        str: Combined response addressing all symptoms
    
    Example:
        >>> generate_multi_symptom_response(['fever', 'cough'])
        "I notice you may be experiencing multiple symptoms..."
    """
    
    if not symptoms:
        return None
    
    # Get valid responses for each symptom
    valid_responses = {s: RESPONSES.get(s) for s in symptoms if s in RESPONSES}
    
    if not valid_responses:
        return None
    
    # Build header
    symptoms_str = ', '.join([s.replace('_', ' ').title() for s in valid_responses.keys()])
    response = f"""**Regarding your symptoms: {symptoms_str}**

I notice you may be experiencing multiple symptoms. Here's guidance for each:

"""
    
    # Add each symptom's info
    for symptom, data in valid_responses.items():
        response += f"""**{symptom.replace('_', ' ').title()}:**
• {data['general']}
• Advice: {data['advice']}
• Warning: {data['warning']}

"""
    
    response += """**General Recommendations:**
1. Get plenty of rest and stay hydrated
2. Monitor all symptoms closely
3. Contact a healthcare provider if symptoms worsen or persist
4. Seek emergency care for severe symptoms

This is general information only. For personalized guidance, consult a healthcare professional."""
    
    return response


def generate_quick_response(symptom):
    """
    Generate a quick, concise response for rapid assessment.
    Perfect for immediate feedback during conversation.
    
    Args:
        symptom (str): Symptom key
    
    Returns:
        str: Brief, actionable response
    
    Example:
        >>> generate_quick_response("fever")
        "You may have a fever. Stay hydrated and rest..."
    """
    
    if symptom not in RESPONSES:
        return "Please consult a healthcare professional for personalized advice."
    
    data = RESPONSES[symptom]
    
    return f"""You may be experiencing {symptom.replace('_', ' ')}.

**Action:** {data['advice'].split('.')[0]}.

**Important:** {data['warning']}"""


def get_response_for_symptom(symptom, response_type='full'):
    """
    Get response for a symptom with customizable detail level.
    
    Args:
        symptom (str): Symptom key
        response_type (str): 'full', 'quick', or 'advice'
    
    Returns:
        str: Response text based on type
    """
    
    if symptom not in RESPONSES:
        return None
    
    data = RESPONSES[symptom]
    
    if response_type == 'quick':
        return generate_quick_response(symptom)
    elif response_type == 'advice':
        return data['advice']
    elif response_type == 'warning':
        return data['warning']
    else:  # 'full'
        return generate_symptom_response_text(symptom)


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def get_or_create_session(request):
    """
    Get or create a unique session ID for the user.
    
    Args:
        request: Django request object
    
    Returns:
        str: Session ID (UUID)
    """
    if 'chatbot_session_id' not in request.session:
        request.session['chatbot_session_id'] = str(uuid.uuid4())
    return request.session['chatbot_session_id']


def get_chatbot_conversation(request):
    """
    Get or create a ChatbotConversation for the current user/session.
    Associates authenticated users with their conversation, creates anonymous sessions for guests.
    
    Args:
        request: Django request object
    
    Returns:
        ChatbotConversation: The conversation object for this user/session
    """
    session_id = get_or_create_session(request)
    
    try:
        conversation = ChatbotConversation.objects.get(session_id=session_id)
    except ChatbotConversation.DoesNotExist:
        conversation = ChatbotConversation.objects.create(
            session_id=session_id,
            user=request.user if request.user.is_authenticated else None
        )
    
    return conversation


# ============================================================================
# URGENCY DETECTION
# ============================================================================

def detect_urgency(message):
    """
    Detect urgency level from user message with intelligent keyword matching.
    Uses priority-based detection for accurate emergency classification.
    
    Urgency Levels:
    - 'Emergency': Life-threatening symptoms requiring immediate 911/emergency services
    - 'High': Serious symptoms requiring same-day medical attention
    - 'Medium': Concerning symptoms that should be addressed within 24-48 hours
    - 'Low': Minor health concerns or general information requests
    
    Args:
        message (str): User's message text
    
    Returns:
        str: Urgency level ('Emergency', 'High', 'Medium', or 'Low')
    
    Example:
        >>> detect_urgency("I have chest pain")
        'Emergency'
        >>> detect_urgency("I have high fever")
        'High'
    """
    
    # Preprocess message for cleaner matching
    message_processed = preprocess(message)
    
    # EMERGENCY PRIORITY (Level 1) - Life-threatening symptoms
    emergency_keywords = [
        "chest pain", "chest discomfort", "chest tightness",
        "breathing problem", "difficulty breathing", "shortness of breath", "cant breathe",
        "severe bleeding", "uncontrolled bleeding",
        "loss of consciousness", "unconscious",
        "stroke", "heart attack", "cardiac", "seizure",
        "severe allergic", "anaphylaxis",
        "poison", "overdose", "toxin",
        "severe trauma", "severe accident",
        "choking", "respiratory failure",
    ]
    
    # HIGH PRIORITY (Level 2) - Requires same-day attention
    high_keywords = [
        "high fever", "severe fever", "elevated temperature",
        "severe pain", "severe headache", "severe ache",
        "persistent vomiting", "uncontrolled vomiting", "continuous vomiting",
        "confusion", "altered consciousness", "disorientation",
        "severe dizziness", "severe vertigo", "fainting",
        "severe weakness", "unable to move",
        "severe allergic reaction", "hives", "swelling",
        "high blood pressure", "very high blood pressure",
        "severe dehydration", "severe weakness",
        "abdominal pain", "severe abdominal",
        "blurred vision", "vision loss", "eye pain",
    ]
    
    # MEDIUM PRIORITY (Level 3) - Address within 24-48 hours
    medium_keywords = [
        "mild fever", "temperature", "slight fever",
        "pain", "ache", "hurt", "discomfort",
        "sore", "soreness", "tender",
        "vomiting", "nausea", "nauseous", "queasy",
        "dizziness", "dizzy", "lightheaded",
        "weakness", "weak", "tired",
        "headache", "head pain", "migraine",
        "cough", "dry cough", "persistent cough",
        "sore throat", "throat pain",
        "rash", "skin irritation", "itchy",
    ]
    
    # Check Emergency keywords first (highest priority)
    for keyword in emergency_keywords:
        keyword_processed = preprocess(keyword)
        if keyword_processed in message_processed:
            return "Emergency"
    
    # Check High urgency keywords
    for keyword in high_keywords:
        keyword_processed = preprocess(keyword)
        if keyword_processed in message_processed:
            return "High"
    
    # Check Medium urgency keywords
    for keyword in medium_keywords:
        keyword_processed = preprocess(keyword)
        if keyword_processed in message_processed:
            return "Medium"
    
    # Check for severity intensifiers (augment urgency)
    severity_intensifiers = ["severe", "critical", "urgent", "emergency", "acute", "worse", "worsening"]
    for intensifier in severity_intensifiers:
        intensifier_processed = preprocess(intensifier)
        if intensifier_processed in message_processed:
            # If found with intensifier, bump up from low to medium
            return "Medium"
    
    # Default to Low urgency for general inquiries
    return "Low"


# ============================================================================
# SYMPTOM EXTRACTION
# ============================================================================

def extract_symptoms(user_message):
    """
    Extract mentioned symptoms from user message.
    Uses keyword matching to identify common health conditions and symptoms.
    
    Args:
        user_message (str): User's message text
    
    Returns:
        list: List of detected symptom keywords (e.g., ['fever', 'cough', 'headache'])
    """
    
    # Preprocess message for cleaner matching
    message_processed = preprocess(user_message)
    
    # Comprehensive symptom keyword mapping
    symptom_keywords = {
        'fever': ['fever', 'high temperature', 'temp', 'pyrexia', 'feverish', 'elevated temp'],
        'cough': ['cough', 'coughing', 'dry cough', 'wet cough', 'persistent cough', 'hacking cough'],
        'sore_throat': ['sore throat', 'throat pain', 'throat ache', 'redness in throat', 'throat irritation', 'pharyngitis'],
        'headache': ['headache', 'head pain', 'migraine', 'head ache', 'throbbing head', 'tension headache'],
        'fatigue': ['fatigue', 'tiredness', 'exhaustion', 'weak', 'weakness', 'lethargy', 'tired all day'],
        'nausea': ['nausea', 'nauseous', 'vomit', 'vomiting', 'gastric', 'feeling sick', 'queasy'],
        'body_aches': ['body aches', 'muscle pain', 'joint pain', 'aching', 'soreness', 'myalgia', 'arthralgia'],
        'difficulty_breathing': ['difficulty breathing', 'shortness of breath', 'cant breathe', 'breathless', 'dyspnea', 'labored breathing'],
        'chest_pain': ['chest pain', 'chest discomfort', 'chest ache', 'chest tightness', 'angina'],
        'dizziness': ['dizziness', 'vertigo', 'dizzy', 'lightheaded', 'giddy', 'spinning sensation'],
        'back_pain': ['back pain', 'backache', 'lower back pain', 'upper back pain', 'spine pain'],
        'abdominal_pain': ['abdominal pain', 'stomach pain', 'belly pain', 'stomach ache', 'gastric pain'],
        'diarrhea': ['diarrhea', 'diarrhoea', 'loose stool', 'frequent bowel', 'watery stool'],
        'constipation': ['constipation', 'constipated', 'difficulty bowel', 'hard stool'],
        'runny_nose': ['runny nose', 'nasal congestion', 'congestion', 'stuffy nose', 'rhinitis'],
        'skin_rash': ['rash', 'skin rash', 'hives', 'itchy skin', 'dermatitis', 'skin irritation'],
        'insomnia': ['insomnia', 'cant sleep', 'sleepless', 'sleep problems', 'difficulty sleeping'],
        'sweating': ['sweating', 'night sweats', 'excessive sweating', 'perspiration'],
        'loss_of_appetite': ['loss of appetite', 'no appetite', 'anorexia', 'decreased appetite'],
    }
    
    detected_symptoms = []
    
    # Detect symptoms by matching keywords
    for symptom, keywords in symptom_keywords.items():
        for keyword in keywords:
            # Preprocess keyword for consistent matching
            keyword_processed = preprocess(keyword)
            if keyword_processed in message_processed:
                detected_symptoms.append(symptom)
                break  # Only add each symptom once
    
    return detected_symptoms


# ============================================================================
# RESPONSE GENERATION
# ============================================================================

def generate_chatbot_response(user_message, detected_symptoms, urgency_level):
    """
    Generate a response based on user message and detected information.
    Follows healthcare chatbot guidelines: informational only, no diagnosis/prescription.
    
    Args:
        user_message (str): Original user message
        detected_symptoms (list): List of detected symptoms
        urgency_level (str): Detected urgency level
    
    Returns:
        dict: Response object with keys:
            - 'response': The main response text
            - 'requires_escalation': Boolean indicating if professional help needed
            - 'show_resources': Boolean indicating if emergency resources should be shown
            - 'symptom_detected': Boolean indicating if symptoms were found
    """
    
    # EMERGENCY PROTOCOL - Life-threatening symptoms
    if urgency_level == 'emergency':
        return {
            'response': generate_emergency_response(),
            'requires_escalation': True,
            'show_resources': True,
            'symptom_detected': len(detected_symptoms) > 0,
        }
    
    # Try to match with Health Topics database
    matching_topic = find_matching_health_topic(user_message)
    
    if matching_topic:
        response = matching_topic.response
        requires_escalation = urgency_level in ['high', 'emergency']
    else:
        # Generate contextual response based on detected symptoms
        if detected_symptoms:
            response = generate_symptom_response(detected_symptoms, urgency_level)
            requires_escalation = urgency_level in ['high', 'emergency']
        else:
            # General wellness response for non-specific queries
            response = generate_general_response(user_message)
            requires_escalation = False
    
    return {
        'response': response,
        'requires_escalation': requires_escalation,
        'show_resources': urgency_level in ['high', 'emergency'],
        'symptom_detected': len(detected_symptoms) > 0,
    }


def generate_emergency_response():
    """
    Generate emergency protocol response for life-threatening symptoms.
    
    Returns:
        str: Emergency response message with clear instructions
    """
    return (
        "🚨 **MEDICAL EMERGENCY DETECTED** 🚨\n\n"
        "**SEEK IMMEDIATE PROFESSIONAL HELP:**\n\n"
        "1. **Call Emergency Services (911 in the US)** or your local emergency number immediately\n"
        "2. **Go to the nearest Emergency Room** if you can safely travel\n"
        "3. **Do NOT wait** - seek professional medical evaluation right now\n\n"
        "---\n\n"
        "**Important:** This chatbot is for informational purposes only. It is NOT a replacement "
        "for professional medical care. Only a qualified healthcare provider can diagnose and treat "
        "serious medical conditions.\n\n"
        "**Your safety is our priority. Please contact emergency services immediately.**"
    )


def generate_symptom_response(symptoms, urgency_level):
    """
    Generate a response for symptom-related queries.
    Provides general information while emphasizing need for professional care.
    
    Args:
        symptoms (list): List of detected symptoms
        urgency_level (str): Urgency level classification
    
    Returns:
        str: Formatted response with symptom information and guidance
    """
    
    # Format symptom list
    symptoms_formatted = ', '.join([s.replace('_', ' ').title() for s in symptoms])
    
    response = f"""**Your Reported Symptoms:** {symptoms_formatted}\n\n"""
    
    response += (
        "**What I Can Do:**\n"
        "✓ Provide general health information\n"
        "✓ Suggest when to seek professional care\n"
        "✓ Offer self-care tips and wellness advice\n\n"
    )
    
    response += (
        "**What I CANNOT Do:**\n"
        "✗ Provide a medical diagnosis\n"
        "✗ Prescribe medications\n"
        "✗ Determine the severity of your condition\n"
        "✗ Replace professional medical evaluation\n\n"
    )
    
    # Urgency-specific guidance
    if urgency_level == 'high':
        response += (
            "⚠️ **Your symptoms may require prompt medical attention:**\n\n"
            "**Please contact a healthcare provider soon if:**\n"
            "• Symptoms worsen significantly\n"
            "• Symptoms persist beyond 24-48 hours\n"
            "• You develop new or severe symptoms\n"
            "• You're experiencing significant discomfort\n"
            "• You're unsure about your symptoms\n\n"
            "**Consider:**\n"
            "- Calling your primary care doctor for advice\n"
            "- Visiting an urgent care facility\n"
            "- Using a telehealth service for quick evaluation\n\n"
        )
    elif urgency_level == 'medium':
        response += (
            "**When to Consider Professional Care:**\n"
            "• Symptoms persist for more than a week\n"
            "• Symptoms worsen or spread\n"
            "• You have a pre-existing condition\n"
            "• You're immunocompromised or elderly\n"
            "• You have concerns about your health\n\n"
        )
    else:
        response += (
            "**General Guidance:**\n"
            "• Monitor your symptoms closely\n"
            "• Track any changes over time\n"
            "• Seek care if symptoms worsen or persist\n"
            "• Contact your healthcare provider if concerned\n\n"
        )
    
    # General wellness recommendations
    response += (
        "**Self-Care Tips:**\n"
        "1. **Hydration:** Drink plenty of water (8-10 glasses daily)\n"
        "2. **Rest:** Get adequate sleep (7-9 hours nightly)\n"
        "3. **Hygiene:** Practice good hand hygiene to prevent spread\n"
        "4. **Nutrition:** Eat balanced, nutrient-rich meals\n"
        "5. **Stress:** Manage stress through relaxation techniques\n"
        "6. **Exercise:** Light movement if you're feeling well\n\n"
    )
    
    # Emergency warning signs
    response += (
        "**🆘 Seek Immediate Care (Emergency Room) if you experience:**\n"
        "• Difficulty breathing or chest pain\n"
        "• Severe bleeding or injury\n"
        "• Loss of consciousness or confusion\n"
        "• Severe allergic reaction symptoms\n"
        "• Any symptom that feels life-threatening\n\n"
    )
    
    response += (
        "**Remember:** Only a qualified healthcare professional can provide proper diagnosis and treatment.\n"
        "When in doubt, contact your healthcare provider."
    )
    
    return response


def generate_general_response(user_message):
    """
    Generate a general response for non-specific health queries.
    Encourages healthy lifestyle and professional consultation.
    
    Args:
        user_message (str): User's original message
    
    Returns:
        str: General wellness guidance
    """
    
    response = (
        "Thank you for your health question.\n\n"
        "**General Health Information:**\n\n"
    )
    
    # Check message for specific health topics
    if any(word in user_message.lower() for word in ['diet', 'nutrition', 'food', 'eat']):
        response += (
            "**Nutrition Tips:**\n"
            "• Eat a balanced diet with fruits, vegetables, and whole grains\n"
            "• Limit processed foods, sugar, and sodium\n"
            "• Stay hydrated with water\n"
            "• Eat regular, balanced meals\n\n"
        )
    
    if any(word in user_message.lower() for word in ['exercise', 'fitness', 'physical', 'workout']):
        response += (
            "**Physical Activity:**\n"
            "• Aim for 150 minutes of moderate activity weekly\n"
            "• Include both cardio and strength training\n"
            "• Start slowly if you're not active\n"
            "• Consult your doctor before starting new programs\n\n"
        )
    
    if any(word in user_message.lower() for word in ['sleep', 'rest', 'insomnia', 'tired']):
        response += (
            "**Sleep Hygiene:**\n"
            "• Maintain consistent sleep schedule\n"
            "• Aim for 7-9 hours nightly\n"
            "• Avoid screens 30 minutes before bed\n"
            "• Create a cool, dark sleeping environment\n\n"
        )
    
    if any(word in user_message.lower() for word in ['stress', 'anxiety', 'mental', 'depression']):
        response += (
            "**Mental Health:**\n"
            "• Practice mindfulness and meditation\n"
            "• Regular exercise reduces stress\n"
            "• Connect with friends and family\n"
            "• Consider professional counseling if needed\n\n"
        )
    
    # Default general response if no specific topic matched
    if not any(topic in user_message.lower() for topic in ['diet', 'exercise', 'sleep', 'stress']):
        response += (
            "**General Wellness Recommendations:**\n"
            "• Maintain regular contact with your healthcare provider\n"
            "• Follow preventive care guidelines\n"
            "• Keep immunizations current\n"
            "• Maintain healthy lifestyle habits\n"
            "• Monitor your health proactively\n\n"
        )
    
    response += (
        "**For specific health concerns:**\n"
        "Please contact your healthcare provider or a medical professional who can properly "
        "assess your individual situation and provide personalized guidance.\n\n"
        "Is there anything else I can help you with?"
    )
    
    return response


# ============================================================================
# HEALTH TOPIC MATCHING
# ============================================================================

def find_matching_health_topic(user_message):
    """
    Search for matching health topics in the database.
    Uses keyword and title matching to find relevant pre-written responses.
    
    Args:
        user_message (str): User's message text
    
    Returns:
        HealthTopic object or None: Matching topic if found, otherwise None
    """
    
    # Extract keywords from message (first 50 chars for broad matching)
    message_keywords = user_message[:50].lower()
    
    # Search for matching topics
    matching_topics = HealthTopic.objects.filter(
        is_active=True
    ).filter(
        Q(keywords__icontains=message_keywords) |
        Q(title__icontains=message_keywords)
    )[:1]
    
    if matching_topics.exists():
        return matching_topics.first()
    
    return None


def search_health_topics(query_text):
    """
    Search health topics by query text.
    Returns matching topics for user browsing.
    
    Args:
        query_text (str): Search query
    
    Returns:
        QuerySet: Matching HealthTopic objects
    """
    
    return HealthTopic.objects.filter(
        is_active=True
    ).filter(
        Q(title__icontains=query_text) |
        Q(description__icontains=query_text) |
        Q(keywords__icontains=query_text)
    ).order_by('title')


# ============================================================================
# MESSAGE PROCESSING & STORAGE
# ============================================================================

def process_user_message(request, user_message_text, conversation):
    """
    Process and store a user message in the chatbot conversation.
    Performs all NLP analysis and stores metadata.
    
    Args:
        request: Django request object
        user_message_text (str): User's message text
        conversation: ChatbotConversation object
    
    Returns:
        tuple: (ChatMessage object, response_dict)
    """
    
    # Perform NLP analysis
    urgency_level = detect_urgency(user_message_text)
    symptoms = extract_symptoms(user_message_text)
    
    # Create and store user message
    user_message = ChatMessage.objects.create(
        conversation=conversation,
        message_type='user',
        content=user_message_text,
        symptom_mentioned=', '.join(symptoms) if symptoms else None,
        urgency_level=urgency_level,
    )
    
    # Generate response
    response_data = generate_chatbot_response(
        user_message_text,
        symptoms,
        urgency_level
    )
    
    # Store assistant response
    assistant_message = ChatMessage.objects.create(
        conversation=conversation,
        message_type='assistant',
        content=response_data['response'],
        urgency_level=urgency_level,
    )
    
    return user_message, response_data, assistant_message


def get_conversation_history(conversation, limit=50):
    """
    Retrieve conversation history.
    
    Args:
        conversation: ChatbotConversation object
        limit (int): Maximum number of messages to retrieve
    
    Returns:
        list: List of ChatMessage objects ordered by timestamp
    """
    
    return ChatMessage.objects.filter(
        conversation=conversation
    ).order_by('timestamp')[:limit]


def clear_old_conversations(days=30):
    """
    Clear old inactive conversations (data cleanup).
    Removes conversations inactive for specified number of days.
    
    Args:
        days (int): Days of inactivity threshold
    
    Returns:
        tuple: (count_deleted, details_dict)
    """
    
    from django.utils import timezone
    from datetime import timedelta
    
    threshold_date = timezone.now() - timedelta(days=days)
    
    old_conversations = ChatbotConversation.objects.filter(
        is_active=False,
        updated_at__lt=threshold_date
    )
    
    count = old_conversations.count()
    old_conversations.delete()
    
    return count, {'deleted_conversations': count, 'threshold_date': threshold_date}


# ============================================================================
# FEEDBACK PROCESSING
# ============================================================================

def submit_message_feedback(message_id, rating, feedback_text=None, user=None):
    """
    Record user feedback on a chatbot message.
    
    Args:
        message_id (int): ID of the ChatMessage
        rating (int): Rating score (1-5)
        feedback_text (str, optional): User's feedback comment
        user: Django User object (optional)
    
    Returns:
        ChatbotFeedback object or None if error
    """
    
    try:
        message = ChatMessage.objects.get(id=message_id)
        
        feedback = ChatbotFeedback.objects.create(
            message=message,
            user=user,
            rating=rating,
            feedback_text=feedback_text,
        )
        
        return feedback
    except ChatMessage.DoesNotExist:
        return None


def get_feedback_analytics():
    """
    Get analytics on chatbot feedback.
    
    Returns:
        dict: Analytics including average rating, feedback counts, etc.
    """
    
    from django.db.models import Avg, Count
    
    feedbacks = ChatbotFeedback.objects.all()
    
    total_feedback = feedbacks.count()
    avg_rating = feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0
    
    rating_distribution = {
        'very_helpful': feedbacks.filter(rating=5).count(),
        'helpful': feedbacks.filter(rating=4).count(),
        'neutral': feedbacks.filter(rating=3).count(),
        'unhelpful': feedbacks.filter(rating=2).count(),
        'very_unhelpful': feedbacks.filter(rating=1).count(),
    }
    
    return {
        'total_feedback': total_feedback,
        'average_rating': round(avg_rating, 2),
        'rating_distribution': rating_distribution,
    }


# ============================================================================
# ANALYTICS & REPORTING
# ============================================================================

def get_conversation_analytics(conversation):
    """
    Get analytics for a specific conversation.
    
    Args:
        conversation: ChatbotConversation object
    
    Returns:
        dict: Conversation statistics
    """
    
    messages = ChatMessage.objects.filter(conversation=conversation)
    
    user_messages = messages.filter(message_type='user')
    assistant_messages = messages.filter(message_type='assistant')
    
    # Count urgency levels
    emergency_count = messages.filter(urgency_level='emergency').count()
    high_count = messages.filter(urgency_level='high').count()
    
    return {
        'total_messages': messages.count(),
        'user_messages': user_messages.count(),
        'assistant_messages': assistant_messages.count(),
        'emergency_mentions': emergency_count,
        'high_urgency_mentions': high_count,
        'duration': (conversation.updated_at - conversation.created_at).total_seconds() / 60,  # minutes
        'last_message_time': messages.last().timestamp if messages.exists() else None,
    }


def get_system_analytics():
    """
    Get overall system analytics for all conversations.
    
    Returns:
        dict: System-wide statistics
    """
    
    from django.db.models import Count
    
    total_conversations = ChatbotConversation.objects.count()
    total_messages = ChatMessage.objects.count()
    active_conversations = ChatbotConversation.objects.filter(is_active=True).count()
    user_conversations = ChatbotConversation.objects.filter(user__isnull=False).count()
    guest_conversations = ChatbotConversation.objects.filter(user__isnull=True).count()
    
    # Emergency mentions
    emergency_mentions = ChatMessage.objects.filter(urgency_level='emergency').count()
    
    # Most mentioned symptoms
    symptoms_data = ChatMessage.objects.filter(
        symptom_mentioned__isnull=False
    ).values('symptom_mentioned').annotate(
        count=Count('symptom_mentioned')
    ).order_by('-count')[:10]
    
    return {
        'total_conversations': total_conversations,
        'total_messages': total_messages,
        'active_conversations': active_conversations,
        'user_conversations': user_conversations,
        'guest_conversations': guest_conversations,
        'emergency_mentions': emergency_mentions,
        'top_symptoms': list(symptoms_data),
    }
