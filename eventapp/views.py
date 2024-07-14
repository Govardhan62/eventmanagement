from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render,redirect
from .models import Event
from .forms import EventForm
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

User = get_user_model()

def forgot_password(request, uidb64=None, token=None):
    if uidb64 and token:
        if request.method == 'POST':
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match")
            else:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
                if default_token_generator.check_token(user, token):
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, "Password reset successful. Please log in with your new password.")
                    return redirect('login')
                else:
                    messages.error(request, "The reset link is no longer valid.")
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = request.build_absolute_uri(f"/reset/{uid}/{token}/")
                subject = "Password Reset Requested"
                html_message = render_to_string('password_reset_email.html', {
                    'user': user,
                    'reset_url': reset_url,
                })
                plain_message=strip_tags(html_message)
                from_email ='pelurigovardhan@gmail.com'
                to = user.email
                send_mail(subject, plain_message, from_email,[to], html_message=html_message)
                messages.success(request, "Password reset link has been sent to your email.")
            else:
                messages.error(request, "Email address not found.")

    return render(request, 'forgot_password.html', {'uidb64': uidb64, 'token': token})


def add_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if Event.objects.filter(name=request.POST.get('name')).exists():
            return JsonResponse({"error": "Event with this name already exists"}, status=400)

        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Successfully added event"}, status=201)
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    else:
        form = EventForm()
        return render(request, 'add_event.html', {'form': form})

def events_list(request):
    if request.method=="GET":
      events = Event.objects.all()
      events_list = [
        {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "image": event.image.url if event.image else ""
        } for event in events
    ]
    return JsonResponse({'events_list':events_list})


def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        username = request.POST.get('username')
        email = request.POST.get('email')  
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Please add a unique username; it already exists'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Please add a unique email; it already exists'}, status=400)

        user = User.objects.create_user(first_name=first_name, username=username, email=email, password=password)
        user.save()
        return JsonResponse({'status': 'success', 'message': 'User created successfully'}, status=201)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if user.is_staff and user.is_superuser:
                return JsonResponse({'status': 'success', 'message': 'Login successful', 'redirect_url': 'dashboard'}, status=200)
            elif user.is_staff:
                return JsonResponse({'status': 'success', 'message': 'Login successful', 'redirect_url': '/'}, status=200)
            else:
                return JsonResponse({'status': 'success', 'message': 'Login successful', 'redirect_url': '/'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid Credentials'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def dashboard(request):
    return render(request,'dashboard.html')
    
    
def users(request):
    users = User.objects.all()
    return render(request,'users.html',{'users':users})


def toggle_staff(request, user_id):
    if request.user.is_superuser:
        user = User.objects.get(id=user_id)
        if user != request.user:
            user.is_staff = not user.is_staff
            user.save()
            return JsonResponse({'status': 'success', 'is_staff': user.is_staff})
    return JsonResponse({'status': 'error'}, status=403)

@login_required
def toggle_superuser(request, user_id):
    if request.user.is_superuser:
        user = User.objects.get(id=user_id)
        if user != request.user:
            user.is_superuser = not user.is_superuser
            user.save()
            return JsonResponse({'status': 'success', 'is_superuser': user.is_superuser})
    return JsonResponse({'status': 'error'}, status=403)

def logout(request):
    auth.logout(request)
    return redirect('/')