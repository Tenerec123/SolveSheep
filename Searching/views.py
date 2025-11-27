from django.shortcuts import render
from django.db.models import Q
from MainApp.models import DifTag, TypeTag, Problem
# Create your views here.

def Search(request):

    dif = DifTag.objects.all()
    type = TypeTag.objects.all()

    if request.GET.get('Dif'):
        probs = Problem.objects.all()

        Type_idx = int(request.GET.get('Type'))
        Text = request.GET.get('Text')
        Dif_idx = int(request.GET.get('Dif'))
        Start_idx = int(request.GET.get('Start_Dif'))
        End_idx = int(request.GET.get('End_Dif'))
        Range = request.GET.get("Range")

        if Range == "true":
            if Start_idx != 0 and End_idx != 0:
                if Start_idx > End_idx:
                    Start_idx, End_idx = End_idx, Start_idx
                Combined_search = Q()
                print(Start_idx, End_idx)
                for i in range(Start_idx, End_idx+1):
                    print(i)
                    Combined_search |= Q(dif_tag = i)
                probs = probs.filter(Combined_search)
            else:
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
            if Dif_idx != 0:
                probs = probs.filter(dif_tag = Dif_idx)
        
        if Type_idx != 0:
            probs = probs.filter(type_tags = Type_idx)

        if Text != "":
            probs = probs.filter(
                Q(title__icontains = Text) | 
                Q(text__icontains = Text)
            )

        return render(request, 'search.html',{
        'searched':True,
        'dif':dif,
        'types':type,

        'dif_selected':Dif_idx,
        'start_dif_selected':Start_idx,
        'end_dif_selected':End_idx,
        
        'type_selected':Type_idx,
        'text_selected':Text,
        'Problems':probs,
        'range': Range
    })

    return render(request, 'search.html',{
        'dif':dif,
        'types':type,
        'range':False,
    })