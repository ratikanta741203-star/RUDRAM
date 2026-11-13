from django.contrib import admin
from apps.accounts.models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'organization', 'assigned_zone', 'phone_number')
    list_filter = ('role', 'organization')
    search_fields = ('user__username', 'user__email', 'organization', 'assigned_zone')
