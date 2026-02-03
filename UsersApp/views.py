from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, CustomUserChangeForm
from MainApp.models import *
from itertools import chain
from .models import User
import random
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
    
def Registro(request):

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
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
        form = CustomUserCreationForm()
        return render(request, 'login.html', {
            'form':form
        })
    
def User_Interface(request, username):
    user = User.objects.get(username=username)
    problems = Problem.objects.filter(author=user)
    bundles = Bundle.objects.filter(author=user)
    GENERAL =list(chain(problems.all(), bundles.all()))
    random.shuffle(GENERAL)
    return render(request,"Acc_display.html", {
        "profile_user":user,
        "Card_objs":GENERAL,
    })