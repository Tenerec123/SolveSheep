from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.conf import settings
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from MainApp.models import *
from .models import User
import resend

resend.api_key = settings.RESEND_API_KEY

ACTIVATION_TOKEN_MAX_AGE = 60 * 60 * 48  # 48 hours
# Create your views here.

def Logout(request):
    logout(request)
    return redirect('Main')

def Login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario) 
            return redirect('Main') 
        else:
            messages.error(request, "Username and password don't match")  
            return render(request, 'login.html', {
                'form':form,
                'login':True
            })
    else:
        form = AuthenticationForm()
        return render(request, 'login.html', {
            'form':form,
            'login':True
        })
    
def Register(request):


    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():

            
            user = form.save(commit=False)
            user.is_active = False  # Bloqueamos al usuario hasta verificar el email
            user.save()

            signer = TimestampSigner()
            token = signer.sign(user.pk)
            activation_url = f"{settings.MAIN_URL}/authentication/activate/{token}/"

            resend.Emails.send({
                "from": settings.RESEND_FROM_EMAIL,
                "to": user.email,
                "subject": "Confirm your SolveSheep account",
                "html": (
                    f"<p>Someone just created an account with this email.</p>"
                    f"<p><a href='{activation_url}'>Activate my account</a></p>"
                    f"<p>This link expires in 48 hours.</p>"
                ),
            })

            return redirect('Main')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
                    print(error)
            return render(request, 'login.html', {
                'form':form,
                'register':True,
            })
    else:
        form = CustomUserCreationForm()
        return render(request, 'login.html', {
            'form':form,
            'register':True
        })
    
def Edit(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            usuario = form.save()
            return redirect('Main')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
                    print(error)
            return render(request, 'login.html', {
                'form':form
            })
    else:
        form = CustomUserChangeForm(instance=request.user)
        return render(request, 'login.html', {
            'form':form
        })



def Activate(request, token):
    signer = TimestampSigner()
    try:
        user_id = signer.unsign(token, max_age=ACTIVATION_TOKEN_MAX_AGE)
        user = User.objects.get(pk=user_id)
    except (SignatureExpired, BadSignature, User.DoesNotExist, ValueError):
        messages.error(request, "The activation link is invalid or has expired. Please register again.")
        return redirect('Register')

    if user.is_active:
        messages.info(request, "This account is already active. You can log in.")
        return redirect('Login')

    user.is_active = True
    user.save()
    login(request, user)
    messages.success(request, "Your account is now active. Welcome!")
    return redirect('Main')

def _account_profile_context(request, profile_user, card_objects):
    is_profile_owner = (
        request.user.is_authenticated and request.user.pk == profile_user.pk
    )
    context = {
        "profile_user": profile_user,
        "Card_objs": card_objects,
        "is_profile_owner": is_profile_owner,
    }
    if is_profile_owner:
        context["problem_progress"] = (
            ProblemProgress.objects.filter(user=profile_user)
            .select_related("problem")
            .order_by("-updated_at", "pk")
        )
    return context


def User_Interface_Problems(request, username):
    user = User.objects.get(username=username)
    problems = Problem.objects.filter(author=user).prefetch_related("area_weights__area")
    
    return render(request, "account_display.html", _account_profile_context(request, user, problems))

def User_Interface_Bundles(request, username):
    user = User.objects.get(username=username)
    bundles = Bundle.objects.filter(author=user)
    
    return render(request, "account_display.html", _account_profile_context(request, user, bundles))

def User_Interface_Solutions(request, username):
    user = User.objects.get(username=username)
    solutions = Solution.objects.filter(author=user)
    
    return render(request, "account_display.html", _account_profile_context(request, user, solutions))

def User_Interface_Likes(request, username):
    user = User.objects.get(username=username)
    liked_problems = user.liked_problems.prefetch_related("area_weights__area")
    
    return render(request, "account_display.html", _account_profile_context(request, user, liked_problems))