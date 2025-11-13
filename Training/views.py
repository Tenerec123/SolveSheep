from django.shortcuts import render
from MainApp.models import Bundle
# Create your views here.

def Training_search(request):
    return render(request, 'training.html',{
        "Bundles":Bundle.objects.all()
    })