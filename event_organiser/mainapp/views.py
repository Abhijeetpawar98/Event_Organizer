# views.py
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from event_organiser.utils import get_tokens_for_user
from .models import Event
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from datetime import datetime  # Import datetime from the datetime module
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils.dateformat import DateFormat
from django.utils.formats import date_format

def index(request):
    return render(request, 'index.html')

def success_view(request):
    print('request.user',request.user)
    return render(request, 'esting.html', {'user': request.user})  # Render the success page

# def dashboard(request):
#     if 'username' in request.session:
#         username = request.session['username']
#         print('username',username)
#     context={'username':username}
#     return render(request, 'dashboard.html', context)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['GET'])
@permission_classes([AllowAny])
def protected_route(request):
    return Response({"message": "This is a protected view!"})


def register(request):
    if request.method == 'POST':
        username = request.POST.get('txt')
        email = request.POST.get('email')  # Get the email from the request
        password1 = request.POST.get('pswd1')
        password2 = request.POST.get('pswd2')
        first_name = request.POST.get('first_name')  # Get the first name from the request

        # Validate the email format
        try:
            email = email.strip()  # Remove any leading/trailing whitespace
            validate_email(email)
        except ValidationError:
            return JsonResponse({'error': 'Invalid email address!'}, status=400)

        # Check if the user already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'User already registered!'}, status=400)

        if password1 == password2:
            try:
                subject = 'Registration Successful'  # Title of the email
                message = f'Hello {username},\n\nYou have successfully registered in the Event Organizer app! Make sure to join the event.\n\nBest Regards,\nThe Event Organizer Team'  # Body of the email
                from_email = settings.EMAIL_HOST_USER  # Sender's email from settings
                recipient_list = [email]  # List of recipient emails

                # Send the email
                send_mail(
                    subject,
                    message,
                    from_email,
                    recipient_list,
                    fail_silently=False
                )
                # Create user with the first_name and email
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.first_name = first_name  # Set the first_name field
                user.save()  # Save the user with the updated first name

                # Get JWT tokens for the user
                tokens = get_tokens_for_user(user)
 
                
                return JsonResponse({
                    'message': 'Registered successfully! You can now log in.',
                    'tokens': tokens,
                }, status=201)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            return JsonResponse({'error': 'Passwords do not match!'}, status=400)

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('text')
        password = request.POST.get('pswd')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session['username'] = username

            # Fetch signed-up events for the user
            signed_up_events = list(user.signed_up_events.values_list('id', flat=True))  # Get list of signed up event IDs
            
            # Create tokens
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
                'message': 'Login successful',
                'username': username,
                'signed_up_events': signed_up_events  # Include signed up events in response
            }, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def submit_data(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        date_str = request.POST.get('date')  # Get the date as a string
        time_str = request.POST.get('time')  # Get the time as a string
        max_attendees = request.POST.get('max_attendees')

        if 'username' in request.session:
            username = request.session['username']
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User does not exist'}, status=400)

            try:
                # Convert string date to a datetime object
                date = datetime.strptime(date_str, '%Y-%m-%d').date()  # Adjust the format if necessary
                time = datetime.strptime(time_str, '%H:%M').time()  # Adjust the format if necessary

                # Create a new Event object and save it
                new_event = Event.objects.create(
                    title=title,
                    description=description,
                    location=location,
                    date=date,
                    time=time,
                    max_attendees=max_attendees,
                    created_by=user
                )
                return JsonResponse({
                    'title': new_event.title,
                    'description': new_event.description,
                    'location': new_event.location,
                    'date': new_event.date.isoformat(),
                    'time': new_event.time.strftime("%H:%M"),
                    'max_attendees': new_event.max_attendees,
                    'created_by': user.username,
                })
            except Exception as e:
                print(f"Error returning response: {e}")  # Log error
                return JsonResponse({'error': 'Failed to return response'}, status=500)
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def fetch_data(request):
    username = request.session.get('username')
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=400)

    # Get events the user hasn't signed up for
    if user.first_name.lower() == 'organizer':
        events = Event.objects.filter(created_by=user)
    else:
        # Filter out events the user has already signed up for
        events = Event.objects.exclude(attendees=user)

    # Paginate data
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 5)
    paginator = Paginator(events, per_page)
    paginated_data = paginator.get_page(page)

    # Prepare JSON response data
    data = list(paginated_data.object_list.values('id', 'title', 'description', 'location', 'date', 'time', 'max_attendees'))
    response = {
        'data': data,
        'page': paginated_data.number,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
        'has_next': paginated_data.has_next(),
        'has_previous': paginated_data.has_previous(),
    }

    return JsonResponse(response)



@csrf_exempt  # You can remove this if CSRF protection is required and your AJAX handles it
def update_data(request):
    if request.method == 'POST':
        entry_id = request.POST.get('id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        date = request.POST.get('date')
        time = request.POST.get('time')
        max_attendees = request.POST.get('max_attendees')

        try:
            # Get the entry by ID
            entry = Event.objects.get(id=entry_id)
            
            # Update fields
            entry.title = title
            entry.description = description
            entry.location = location
            entry.date = date
            entry.time = time
            entry.max_attendees = max_attendees
            entry.save()

            return JsonResponse({'status': 'success', 'id': entry.id})
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)
        except Exception as e:
            print(f"Error updating data: {e}")  # Log error for debugging
            return JsonResponse({'error': 'Failed to update entry'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



@csrf_exempt
def delete_data(request):
    if request.method == 'POST':
        entry_id = request.POST.get('id')
        entry = get_object_or_404(Event, id=entry_id)
        entry.delete()
        return JsonResponse({'status': 'success'})

    from django.shortcuts import redirect
    
def logout_user(request):
    try:
        logout(request)
        return render(request, 'index.html')
    except Exception as e:
        print(e)
        return Response(False, status = 400)

@csrf_exempt
def signup_event(request):
    if request.method == 'POST':
        print('idharrrrrrr')
        event_id = request.POST.get('event_id')
        username = request.session.get('username')
        event = Event.objects.get(id=event_id)
        
        # Set the details in the session
        request.session['title'] = event.title
        request.session['location'] = event.location
        request.session['date'] = str(event.date)  # Convert to string
        request.session['time'] = str(event.time)  # Convert to string
        request.session['email'] = request.user.email 
        
        try:
            event = Event.objects.get(id=event_id)
            user = User.objects.get(username=username)
            event.attendees.add(user)  # Add the user to the attendees
            
            # Prepare email details
            subject = 'Event Registration Successful'  # Title of the email
            message = f'''
            Hello {username},

            Thank you for registering with the Event Organizer app! Here are the details of the event you signed up for:

            Event Title: {event.title}
            Location: {event.location}
            Date: {date_format(event.date, 'DATE_FORMAT')}
            Time: {date_format(event.time, 'TIME_FORMAT')}

            Please mark your calendar and make sure to join us for an exciting experience. We look forward to seeing you there!

            Best regards,
            The Event Organizer Team
            '''
            
            from_email = settings.EMAIL_HOST_USER  # Sender's email from settings
            recipient_list = [request.user.email]  # List of recipient emails

            # Send the email
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            # Prepare a response message
            response = {
                'status': 'success',
                'event_details': {
                    'title': event.title,
                    'location': event.location,
                    'date': str(event.date),
                    'time': str(event.time)
                }
            }

            return JsonResponse(response)
        
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=405)

def get_signed_up_events(request):
    if request.user.is_authenticated:
        try:
            # Get the authenticated user
            user = request.user

            # Retrieve all events the user has signed up for using the related name 'signed_up_events'
            signed_up_events = user.signed_up_events.all()  # Related name from Event model's 'attendees' field

            # Extract event IDs from the signed-up events
            signed_up_event_ids = [event.id for event in signed_up_events]

            # Return the event IDs as a JSON response
            return JsonResponse({'signed_up_event_ids': signed_up_event_ids}, status=200)
        except Exception as e:
            # Log the error and return a server error response
            print(f"Error fetching signed-up events: {e}")
            return JsonResponse({'error': 'Failed to fetch signed-up events'}, status=500)
    else:
        # If the user is not authenticated, return a 401 Unauthorized response
        return JsonResponse({'error': 'User not authenticated'}, status=401)

def get_joined_events(request):
    if request.user.is_authenticated:
        user = request.user
        # Get all events the user has joined
        joined_events = user.signed_up_events.all()  # Assuming ManyToMany is in the Event model
        return render(request, 'joined_events.html', {'events': joined_events})
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    
def organizer_event_summary(request):
    user = request.user
    # Fetch all events created by the logged-in organizer
    events = Event.objects.filter(created_by=user).prefetch_related('attendees')

    event_data = []
    for event in events:
        event_data.append({
            'title': event.title,
            'location': event.location,
            'date': event.date,
            'time': event.time,
            'attendees_count': event.attendees.count(),  # Count of attendees
        })

    return render(request, 'organizer_event_summary.html', {'events': event_data})