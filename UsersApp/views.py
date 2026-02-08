from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, CustomUserChangeForm
from MainApp.models import *
from itertools import chain
from .models import User
import random
import resend
from django.core.signing import Signer # Para firmar los enlaces
resend.api_key = settings.RESEND_API_KEY
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
            user.is_active = False  # Bloqueamos al usuario
            user.save() # Ahora sí tiene ID

            signer = Signer()
            token = signer.sign(user.id)

            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": "solvesheep@gmail.com",
                "subject": f"Account creation check",
                "html":"Someone has logged in with your mail. Are you that one?",
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



def User_Interface_Problems(request, username):
    user = User.objects.get(username=username)
    problems = Problem.objects.filter(author=user)
    
    return render(request,"account_display.html", {
        "profile_user":user,
        "Card_objs":problems,
    })

def User_Interface_Bundles(request, username):
    user = User.objects.get(username=username)
    bundles = Bundle.objects.filter(author=user)
    
    return render(request,"account_display.html", {
        "profile_user":user,
        "Card_objs":bundles,
    })

def User_Interface_Solutions(request, username):
    user = User.objects.get(username=username)
    solutions = Solution.objects.filter(author=user)
    
    return render(request,"account_display.html", {
        "profile_user":user,
        "Card_objs":solutions,
    })

def User_Interface_Likes(request, username):
    user = User.objects.get(username=username)
    liked_problems = user.liked_problems.all()
    
    return render(request,"account_display.html", {
        "profile_user":user,
        "Card_objs":liked_problems,
    })