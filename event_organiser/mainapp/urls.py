from django.contrib import admin
from django.urls import path
from .views import index, register, user_login, success_view,protected_route, submit_data,fetch_data,update_data,delete_data,logout_user,signup_event, get_signed_up_events, get_joined_events,organizer_event_summary
from rest_framework_simplejwt.views import TokenRefreshView
app_name = 'mainapp'

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', index, name='index'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', logout_user, name='logout'),
    path('success/', success_view, name='success'), 
    path('protected-route/', protected_route, name='protected-route'),
    path('refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
    path('submit-data/',submit_data, name='submit_data'),
    path('fetch-data/', fetch_data, name='fetch_data'),
    path('update-data/',update_data, name='update_data'),
    path('delete-data/', delete_data, name='delete_data'),
    path('sign-up-event/', signup_event, name='signup_event'),
    path('get-signed-up-events/', get_signed_up_events, name='get_signed_up_events'),  # Add this line
    path('joined-events/', get_joined_events, name='joined-events'),
    path('organizer-event-summary/', organizer_event_summary, name='organizer_event_summary'),
    
]
