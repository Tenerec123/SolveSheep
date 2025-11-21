from django.shortcuts import render, redirect
from .forms import ProblemForm
from .models import Problem
# Create your views here.

def Main(request):
    Problems = Problem.objects.all()
    return render(request,"landing.html", {
        'Problems':Problems
    })

def Difs(request):
    return render(request, 'difficulties.html')