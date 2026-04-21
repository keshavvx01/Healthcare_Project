from django import forms
from .models import ChatMessage, ChatbotFeedback


class ChatMessageForm(forms.Form):
    """Form for user to input chat messages"""
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Type your health question or concern here...',
            'class': 'form-control',
            'required': True,
        }),
        label='Your Message',
        max_length=2000,
        min_length=5,
        error_messages={
            'required': 'Please enter a message.',
            'min_length': 'Message must be at least 5 characters long.',
            'max_length': 'Message cannot exceed 2000 characters.',
        }
    )


class ChatbotFeedbackForm(forms.ModelForm):
    """Form for users to rate chatbot responses"""
    feedback_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Tell us why you gave this rating (optional)',
            'class': 'form-control',
        }),
        label='Feedback (Optional)',
        required=False,
        max_length=500,
    )

    class Meta:
        model = ChatbotFeedback
        fields = ['rating', 'feedback_text']
        widgets = {
            'rating': forms.RadioSelect(choices=ChatbotFeedback.RATING_CHOICES),
        }


class QuickSymptomCheckForm(forms.Form):
    """Form for quick symptom checking"""
    SYMPTOM_CHOICES = [
        ('', '-- Select a symptom --'),
        ('fever', 'Fever'),
        ('cough', 'Cough'),
        ('sore_throat', 'Sore Throat'),
        ('headache', 'Headache'),
        ('fatigue', 'Fatigue'),
        ('nausea', 'Nausea/Vomiting'),
        ('body_aches', 'Body Aches'),
        ('difficulty_breathing', 'Difficulty Breathing'),
        ('chest_pain', 'Chest Pain'),
        ('dizziness', 'Dizziness'),
        ('other', 'Other (describe below)'),
    ]

    symptom = forms.ChoiceField(
        choices=SYMPTOM_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Primary Symptom',
    )

    duration = forms.ChoiceField(
        choices=[
            ('', '-- Select duration --'),
            ('less_than_24h', 'Less than 24 hours'),
            ('1_3_days', '1-3 days'),
            ('4_7_days', '4-7 days'),
            ('more_than_week', 'More than a week'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='How long have you had this symptom?',
        required=False,
    )

    severity = forms.ChoiceField(
        choices=[
            ('', '-- Select severity --'),
            ('mild', 'Mild'),
            ('moderate', 'Moderate'),
            ('severe', 'Severe'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Severity Level',
        required=False,
    )

    other_symptoms = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': 'Any other symptoms or details?',
            'class': 'form-control',
        }),
        label='Additional Details',
        required=False,
        max_length=500,
    )
