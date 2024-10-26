from django.db import models
from django.contrib.auth.models import User

# User profile model for extending user functionality
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username  # Returns the username for easier identification


# Data entry model for events
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()  # Use TextField for potentially larger descriptions
    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    max_attendees = models.PositiveIntegerField()  # Use PositiveIntegerField for attendees
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    attendees = models.ManyToManyField(User, related_name='signed_up_events', blank=True)  # New field to track attendees

    def __str__(self):
        return f"{self.title} - {self.location} - {self.date} - {self.time} - {self.created_by.username}"
