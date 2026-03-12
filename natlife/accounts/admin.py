from django.contrib import admin

# Register your models here.

from .models import Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Call the custom method 'display_roles' instead of the field name
    list_display = ['email', 'phone', 'display_roles', 'is_active', 'is_approved']
    search_fields = ['email', 'phone']
    list_filter = ['roles', 'is_active', 'is_approved']

    def display_roles(self, obj):
        # This joins all role names into a comma-separated string
        return ", ".join([role.name for role in obj.roles.all()])
    
    # This sets the column name in the admin UI
    display_roles.short_description = 'Roles'
