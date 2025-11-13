from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
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
            for msg in form.error_messages:
                messages.error(request, form.error_messages[msg])
                print(msg)
            return render(request, 'login.html', {
                'form':form
            })
    else:
        form = AuthenticationForm()
        return render(request, 'login.html', {
            'form':form
        })
    

def Registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('Main')
        else:
            for msg in form.error_messages:
                messages.error(request, form.error_messages[msg])
            return render(request, 'login.html', {
                'form':form
            })
    else:
        form = UserCreationForm()
        return render(request, 'login.html', {
            'form':form
        })