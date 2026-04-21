from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from .forms import UserRegistrationForm, UserProfileForm
from .models import UserProfile
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from pharmacy.models import Medicine


# HOME
def home(request):
    return render(request, 'base/home.html')


# REGISTER
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


# LOGIN
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


# LOGOUT
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('home')


# DASHBOARD
@login_required
def dashboard(request):
    context = {
        'total_patients': Patient.objects.count(),
        'total_doctors': Doctor.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'total_medicines': Medicine.objects.filter(is_active=True).count(),
        'recent_appointments': Appointment.objects.select_related('patient', 'doctor').order_by('-appointment_date', '-appointment_time')[:5],
        'recent_patients': Patient.objects.order_by('-created_at')[:5],
    }
    return render(request, 'base/dashboard.html', context)


# PROFILE
@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'user_profile': user_profile
    })