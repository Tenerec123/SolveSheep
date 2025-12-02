from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import ProblemForm
from .models import Problem, DifTag, TypeTag
import os
import random
import json

# Create your views here.

def Main(request):
    Problems = list(Problem.objects.all())
    random.shuffle(Problems)
    return render(request,"landing.html", {
        'Card_objs':Problems
    })

def Difs(request):
    return render(request, 'difficulties.html')

def Add_JSON_probs(request):
    with open(r'C:\Users\siste\Documentos\Codigo\Python\Django\MathWeb\MainApp\ZZ_newprobs.json', 'r' , encoding='utf-8') as archivo:
        objeto = json.load(archivo)
        for prob in objeto:
            if len(Problem.objects.filter(title = prob['title'])) != 0:
                continue
            
            dif_tag = DifTag.objects.get(name = prob['dif_tag'])
            
            new_problem = Problem.objects.create(
                title = prob['title'],
                text = prob['text'],
                video = prob['video'],
                author = User.objects.get(username = prob['author']),
                dif_tag = dif_tag,
            )
            for type_tag_str in prob['type_tags']:
                type_tag = TypeTag.objects.get(name = type_tag_str)
                new_problem.type_tags.add(type_tag)
    return redirect("Main")