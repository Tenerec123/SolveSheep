from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from MainApp.models import Problem, Bundle
import random
from itertools import chain
# Create your views here.

def User_Interface(request, username):
    user = User.objects.get(username=username)
    problems = Problem.objects.filter(author=user)
    bundles = Bundle.objects.filter(author=user)
    GENERAL =list(chain(problems.all(), bundles.all()))
    random.shuffle(GENERAL)
    return render(request,"Acc_display.html", {
        "user":user,
        "Card_objs":GENERAL,
    })