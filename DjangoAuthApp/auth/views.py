import django
import email
from email import message
from email.message import EmailMessage
from tokenize import generate_tokens
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
from gfg import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator 
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.utils.encoding import force_str
django.utils.encoding.force_text = force_str


def home(request):
    return render(request, "auth/index.html")

def signup(request):

    if request.method == "POST":
        # username = request.POST.get('username')
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username = username):
            messages.error(request, "Username already exist! Please have some other username")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request,"Email already registered!")
            return redirect('home')

        if len(username)>10:
            messages.error(request, "Username must be under 10 characters")

        if pass1 != pass2:
            messages.error(request, "Passwords didn't match!")

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!")
            return redirect('home')


        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()

        messages.success(request,"Your Account has been successfully created.We have also sent you a confirmation email, please confirm your email address in order to activate your account.")

        #Welcome Email

        subject = "Welcome to Authentication App!"
        message = "Hello, " + myuser.first_name + "!! \n" + "Welcome to Authentication App! \n Thank you for vising our website \n We have also sent you a confirmation email, please confirm your email address in order to activate your account. \n\n Thanking You \n Parul Rathva"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        #Email Address Confirmation Email

        current_site = get_current_site(request)
        email_subject = "Confirm your email @ Authentication App!"
        message2 = render_to_string('email_confirmation.html',{
            'name' : myuser.first_name,
            'domain' : current_site.domain,
            'uid' : urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token' : default_token_generator.make_token(myuser)
        })
  
        email = EmailMessage( email_subject, message2, settings.EMAIL_HOST_USER, (myuser.email),)
        email.fail_silently = True
        email.send()

        return redirect('signin')
 
    return render(request, "auth/signup.html")

    
def signin(request):

    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname=user.first_name
            messages.success(request, "You are successfully logged in!")
            return render(request, "auth/index.html", {'fname':fname})
        else:
            messages.error(request, "Please enter valid Credentials")
            return redirect('home')

def signout(request):
    logout(request)
    messages.success(request, "You are successfully logged out!")
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError):
        myuser = None

    if myuser is not None and default_token_generator.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')
