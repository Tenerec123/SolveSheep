from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Problem
import random

# Create your views here.
def ads_txt(request):
    return HttpResponse("google.com, pub-1229341265329797, DIRECT, f08c47fec0942fa0z", content_type="text/plain")

def Main(request):
    Problems = list(Problem.objects.all())
    random.shuffle(Problems)
    return render(request,"landing.html", {
        'Card_objs':Problems
    })

def Difs(request):
    return render(request, 'difficulties.html')

