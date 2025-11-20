from django.shortcuts import render
from django.db.models import Q
from MainApp.models import DifTag, TypeTag, Problem
# Create your views here.

def Search(request):

    dif = DifTag.objects.all()
    type = TypeTag.objects.all()

    if request.GET.get('Dif'):
        probs = Problem.objects.all()

        if request.GET.get('Type') != "0":
            probs = probs.filter(type_tags = request.GET.get('Type'))
        if request.GET.get('Dif') != "0":
            probs = probs.filter(dif_tag = request.GET.get('Dif'))
        if request.GET.get('Text') != "":
            probs = probs.filter(
                Q(title__icontains = request.GET.get('Text')) | 
                Q(text__icontains = request.GET.get('Text'))

            )

        return render(request, 'search.html',{
        'dif':dif,
        'types':type,
        'dif_selected':int(request.GET.get('Dif')),
        'type_selected':int(request.GET.get('Type')),
        'text_selected':request.GET.get('Text'),
        'Problems':probs
    })

    return render(request, 'search.html',{
        'dif':dif,
        'types':type
    })