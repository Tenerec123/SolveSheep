from django.shortcuts import render
from django.db.models import Q
from MainApp.models import DifTag, TypeTag, Problem, Bundle
from itertools import chain
import random
# Create your views here.

def Search(request):

    dif = DifTag.objects.all()
    type = TypeTag.objects.all()

    if request.GET.get('Dif'):

        Type_idx = int(request.GET.get('Type'))
        Text = request.GET.get('Text')
        Dif_idx = int(request.GET.get('Dif'))
        Start_idx = int(request.GET.get('Start_Dif'))
        End_idx = int(request.GET.get('End_Dif'))
        Range = request.GET.get("Range")
        Combined_search = Q()
        if Range == "true":
            if Start_idx == 0 or End_idx == 0:
                return render(request, 'search.html',{
                    'searched':True,
                    'dif':dif,
                    'types':type,

                    'dif_selected':Dif_idx,
                    'start_dif_selected':Start_idx,
                    'end_dif_selected':End_idx,
                    
                    'type_selected':Type_idx,
                    'text_selected':Text,
                    'range_alert':True,
                    'range': Range
                })
            else:
                if Start_idx > End_idx:
                    Start_idx, End_idx = End_idx, Start_idx  
                print(Start_idx, End_idx)
                for i in range(Start_idx, End_idx+1):
                    print(i)
                    Combined_search |= Q(dif_tag = i)     
        else:
            if Dif_idx != 0:
                Combined_search &= Q(dif_tag = Dif_idx)
        
        if Type_idx != 0:
            Combined_search &= Q(type_tags = Type_idx)

        if Text != "":
            Combined_search &= Q(
                Q(title__icontains = Text) | 
                Q(text__icontains = Text)
            )
        probs = Problem.objects.all().filter(Combined_search)
        bunds = Bundle.objects.all().filter(problems__in = probs).distinct()
        card_objs =list(chain(probs, bunds))
        random.shuffle(card_objs)

        return render(request, 'search.html',{
        'searched':True,
        'dif':dif,
        'types':type,

        'dif_selected':Dif_idx,
        'start_dif_selected':Start_idx,
        'end_dif_selected':End_idx,
        
        'type_selected':Type_idx,
        'text_selected':Text,
        'Card_objs':card_objs,
        'range': Range
    })

    return render(request, 'search.html',{
        'dif':dif,
        'types':type,
        'range':False,
    })