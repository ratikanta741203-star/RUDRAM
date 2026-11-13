from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.models import UserProfile
from apps.accounts.serializers import UserProfileSerializer

from apps.accounts.permissions import is_admin_user, is_operator

def login_view(request):
    if request.method == 'POST':
        login_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Resolve user by email or username for seamless authentication
        target_user = None
        if '@' in login_input:
            target_user = User.objects.filter(email__iexact=login_input).first()
        if not target_user:
            target_user = User.objects.filter(username__iexact=login_input).first()

        actual_username = target_user.username if target_user else login_input
        user = authenticate(request, username=actual_username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            if is_admin_user(user):
                return redirect('admin_dashboard')
            elif is_operator(user):
                return redirect('operator_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'accounts/login.html')

from django.db import transaction

def citizen_signup_view(request):
    """
    Public Citizen Sign-Up View.
    Enforces atomic database transaction safety:
    Validates all inputs BEFORE database write. If any step fails, transaction rolls back cleanly.
    Strictly assigns ROLE = CITIZEN on server-side.
    """
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        form_data = {
            'full_name': full_name,
            'email': email,
            'phone_number': phone_number
        }

        # 1. Full Name Validation
        if not full_name or len(full_name) < 2:
            messages.error(request, "Please enter a valid full name.")
            return render(request, 'accounts/signup.html', {'form_data': form_data})

        # 2. Email Validation
        if not email or '@' not in email or '.' not in email:
            messages.error(request, "Please enter a valid email address.")
            return render(request, 'accounts/signup.html', {'form_data': form_data})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email address is already registered.")
            return render(request, 'accounts/signup.html', {'form_data': form_data})

        # 3. Phone Number Validation
        if not phone_number or len(phone_number) < 7:
            messages.error(request, "Please enter a valid phone number.")
            return render(request, 'accounts/signup.html', {'form_data': form_data})

        if UserProfile.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number is already registered.")
            return render(request, 'accounts/signup.html', {'form_data': form_data})

        # 4. Password Validation
        if not password or len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, 'accounts/signup.html', {'form_data': form_data})

        if password != confirm_password:
            messages.error(request, "Passwords do not match. Please verify your password.")
            return render(request, 'accounts/signup.html', {'form_data': form_data})

        # Generate unique username from email
        import re
        base_username = email.split('@')[0]
        base_username = re.sub(r'[^a-zA-Z0-9_]', '', base_username) or 'citizen'
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Execute atomic database transaction
        try:
            with transaction.atomic():
                # Create User with Django hashed password
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=full_name
                )

                # STRICTLY ASSIGN CITIZEN ROLE SERVER-SIDE
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.role = 'CITIZEN'  # Server-side enforced CITIZEN role
                profile.phone_number = phone_number
                profile.organization = 'Citizen First Responder'
                profile.save()

            messages.success(request, f"Citizen account created successfully for {full_name}. Please log in with your credentials.")
            return redirect('login')
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Atomic account creation error: {e}")
            messages.error(request, "An error occurred while creating your account. Please try again.")
            return render(request, 'accounts/signup.html', {'form_data': form_data})

    return render(request, 'accounts/signup.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('dashboard')

def switch_role_view(request):
    """Convenient switch role for hackathon evaluation and demonstration"""
    if request.method == 'POST':
        new_role = request.POST.get('role', 'ADMIN')
        if request.user.is_authenticated:
            profile = request.user.profile
            profile.role = new_role
            profile.save()
            messages.success(request, f"Active role switched to: {profile.get_role_display()}")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

class CurrentUserAPIView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            serializer = UserProfileSerializer(request.user.profile)
            return Response({'authenticated': True, 'user': serializer.data})
        return Response({
            'authenticated': False,
            'user': {
                'username': 'Citizen Guest',
                'role': 'CITIZEN',
                'organization': 'Public User',
                'assigned_zone': 'Bhubaneswar Zone'
            }
        })
