from django.contrib import admin
from .models import Event  # Updated import for the Event model
from django.contrib.auth.models import User

# Custom User admin to display specific fields
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'email')  # Added last_name and email for better visibility

admin.site.unregister(User)  # Unregister the default User admin
admin.site.register(User, UserAdmin)  # Register the customized User admin

# Admin configuration for the Event model
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'date', 'time', 'max_attendees', 'created_by')  # Updated columns to display
    search_fields = ('title', 'description', 'location')  # Enable search by these fields

admin.site.register(Event, EventAdmin)  # Register the updated Event model
