from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
# Create your views here.


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None
            field.widget.attrs.update({"class": "form-control"})

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
    
