from rest_framework import permissions
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def is_strict_admin(user):
    """Checks if a Django user has strict Admin / Disaster Commander privileges."""
    if not user or not user.is_authenticated:
        return False

    # Priority Check: If user profile explicitly states EMERGENCY_OPERATOR, CITIZEN, or ANALYST, they are NOT Admin unless is_superuser
    try:
        from apps.accounts.models import UserProfile
        profile = UserProfile.objects.filter(user=user).first()
        if profile:
            if profile.role == 'ADMIN':
                return True
            if profile.role in ['EMERGENCY_OPERATOR', 'CITIZEN', 'ANALYST']:
                if getattr(user, 'is_superuser', False):
                    return True
                return False
    except Exception:
        pass

    if getattr(user, 'is_superuser', False):
        return True
    if hasattr(user, 'role') and str(user.role).upper() == 'ADMIN':
        return True
    return False

def is_operator(user):
    """Checks if a Django user has Emergency Operator privileges."""
    if not user or not user.is_authenticated:
        return False
    if hasattr(user, 'profile') and user.profile.role == 'EMERGENCY_OPERATOR':
        return True
    return False

def is_admin_or_operator(user):
    """Checks if a Django user is an Admin or Emergency Operator."""
    return is_strict_admin(user) or is_operator(user)

def is_admin_user(user):
    """Alias for is_strict_admin to enforce Admin-only access."""
    return is_strict_admin(user)

class IsAdminUserOrCommander(permissions.BasePermission):
    """
    Custom DRF Permission Class.
    Requires authenticated user with strict ADMIN role.
    """
    def has_permission(self, request, view):
        return is_strict_admin(request.user)

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom DRF Permission Class allowing GET/HEAD/OPTIONS to all, requiring Admin for write operations.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return is_strict_admin(request.user)

class IsAdminOrOperatorOrReadOnly(permissions.BasePermission):
    """
    Custom DRF Permission Class allowing GET to all, requiring Admin or Operator for write operations.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return is_admin_or_operator(request.user)

def admin_required(view_func):
    """
    Decorator for Django HTML views to enforce strict Admin role access.
    Returns 403 Forbidden for Emergency Operators and Citizens.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in with administrative credentials to access the Admin Dashboard.")
            return redirect('login')
        if not is_strict_admin(request.user):
            if is_operator(request.user):
                messages.warning(request, "Access Denied: Administrative privileges required. Redirected to Operator Dashboard.")
                return redirect('operator_dashboard')
            raise PermissionDenied("Access Denied: Administrative privileges required.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def operator_required(view_func):
    """
    Decorator for Django HTML views to enforce Emergency Operator access.
    Admins are also permitted, but Citizens are denied.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in with Emergency Operator credentials.")
            return redirect('login')
        if not is_admin_or_operator(request.user):
            raise PermissionDenied("Access Denied: Emergency Operator privileges required.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

