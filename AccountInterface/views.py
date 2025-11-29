from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from MainApp.models import Problem
# Create your views here.

def User_Interface(request, username):
    user = User.objects.get(username=username)
    problems = Problem.objects.filter(author=user)
    return render(request,"Acc_display.html", {
        "user":user,
        "Problems":problems
    })