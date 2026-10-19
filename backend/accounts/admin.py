from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('ResQ AI', {'fields': ('role', 'department', 'phone')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('ResQ AI', {'fields': ('role', 'department', 'phone')}),)
    list_display = ('username', 'email', 'role', 'department', 'is_staff')
    list_filter = ('role', 'department', 'is_staff')