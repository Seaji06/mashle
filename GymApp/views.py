from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash 
from django.contrib import messages
from .models import UserProfile, Message
from .forms import UserProfileForm 
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
import json

# Create your views here.


def home(request):
    return render(request, 'home.html')

@login_required(login_url='login')
def classes(request):
    return render(request, 'classes.html')

def trainers(request):
    return render(request, 'trainers.html')

def about(request):
    return render(request, 'about.html')

@login_required(login_url='login')
def contact(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        name = request.POST.get("name")

        # Send email
        send_mail(
            subject,  
            f"{message}\n\nName: {name}\nEmail: {email}", 
            'settings.EMAIL_HOST_USER',
            ["limcedricjohn@gmail.com"],  
            fail_silently=False
        )

        if request.user.is_authenticated:
            # Use the authenticated user's information
            name = f"{request.user.first_name} {request.user.last_name}"
            email = request.user.email

        # Create and save Message object
        new_message = Message(name=name, message=message, subject=subject, email=email)
        new_message.save()

    return render(request, 'contact.html')

def user_register(request):
    if request.method == 'POST':
        username = request.POST['new-username']
        email = request.POST['email']
        password = request.POST['new-password']
        confirm_password = request.POST['confirm-password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        birthday = request.POST['birthday']

        # Store entered values in case of errors
        entered_values = {
            'new_username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'birthday': birthday,
        }

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html', entered_values)

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'register.html', entered_values)

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'register.html', entered_values)

        # Check if a UserProfile already exists for this User
        user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
        user_profile, created = UserProfile.objects.get_or_create(user=user, defaults={'birthday': birthday})
        user.is_active = False
        user.save()
        # If a UserProfile was created, update the birthday
        if not created:
            user_profile.birthday = birthday
            user_profile.save()

        messages.success(request, "Your Account has been created successfully!! Please check your email to confirm your email address in order to activate your account.")
        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ MASHLE FITNESS GYM!!"
        message2 = render_to_string('email_confirmation.html', {
            'name': user.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        email.fail_silently = True
        email.send()
        return redirect('login')

    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to your home page after login
        else:
            messages.error(request, 'Username or password is incorrect')
            return render(request, 'login.html')

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return render(request, 'home.html')

def edit_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'edit_profile.html', {'form': form})

def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'profile.html', {'user_profile': user_profile})

def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, "Your account has been successfully activated!")
        else:
            messages.info(request, "Your account is already activated.")
    else:
        messages.error(request, "Invalid activation link. Please try again.")
    
    return redirect('login')

@csrf_exempt
@login_required
def update_classes(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))  # Decode the request body as UTF-8
            class_name = data.get('class_name')

            user_profile = request.user.userprofile

            # Update the user's membership based on the selected class
            if class_name == 'Novice Fitness Forge':
                user_profile.membership = 'beginner_class'
            elif class_name == 'Proactive Performance Prodigy':
                user_profile.membership = 'intermediate_class'
            elif class_name == 'Elite Fitness Fusion':
                user_profile.membership = 'master_class'

            user_profile.save()

            # Use user_profile instead of user
            current_site = get_current_site(request)
            email_subject = "Welcome to MASHLE FITNESS GYM - Get Ready to Transform!"
            message2 = render_to_string('enroll_message.html',{
                
                'name': user_profile.user.first_name,  # Change 'user' to 'user_profile'
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user_profile.user.pk)),  # Change 'user' to 'user_profile'
                'token': generate_token.make_token(user_profile.user)  # Change 'user' to 'user_profile'
            })

            email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [user_profile.user.email],  # Change 'user' to 'user_profile'
            )
            email.fail_silently = True
            email.send()


            return JsonResponse({'message': 'Classes updated successfully'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': 'Invalid JSON format'}, status=400)
    
    return JsonResponse({'message': 'Invalid request'}, status=400)

@login_required
def change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')

        if new_password == confirm_password:
            user = request.user
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Update session to avoid logout
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')  # Redirect to the same page after successful password change
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('change_password')  # Redirect to the same page if passwords do not match

    return render(request, 'change_pass.html')