from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from .forms import ProblemForm
from .models import Problem, DifTag, TypeTag
import os
import random
import json

# Create your views here.

def ads_txt(request):
    return HttpResponse("google.com, pub-1229341265329797, DIRECT, f08c47fec0942fa0", content_type="text/plain")

def Main(request):
    Problems = list(Problem.objects.all())
    random.shuffle(Problems)
    return render(request,"landing.html", {
        'Card_objs':Problems
    })

def Difs(request):
    return render(request, 'difficulties.html')

def Add_JSON_probs(request):
    with open(r'C:\Users\siste\Documentos\Codigo\Python\Django\MathWeb\MainApp\ZZ_newprobs.json', 'r', encoding='utf-8') as archivo:
        objeto = json.load(archivo)
        for prob in objeto:
            # Usamos update_or_create con title como criterio
            new_problem, created = Problem.objects.update_or_create(
                title=prob['title'],  # <-- criterio de búsqueda
                defaults={
                    'text': prob['text'],
                    'video': prob['video'],
                    'author': User.objects.get(username=prob['author']),
                    'dif_tag': DifTag.objects.get(name=prob['dif_tag']),
                }
            )

            # Limpiamos los type_tags actuales y añadimos los nuevos
            new_problem.type_tags.set([TypeTag.objects.get(name=tt) for tt in prob['type_tags']])

    return redirect("Main")
