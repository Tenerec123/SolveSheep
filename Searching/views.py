from django.shortcuts import render
from django.db.models import Q
from MainApp.models import DifTag, TypeTag, Problem, Bundle
from pgvector.django import CosineDistance
from sentence_transformers import SentenceTransformer
from itertools import chain

_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    return _embedding_model

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

        probs = Problem.objects.filter(Combined_search)
        bunds = Bundle.objects.filter(problems__in=probs).distinct()

        if Text:
            direct_probs = probs.filter(
                Q(title__icontains = Text) |
                Q(text__icontains = Text)
            )[:5]
            direct_bunds = bunds.filter(
                Q(title__icontains = Text) |
                Q(description__icontains = Text)
            )[:5]

            model = get_embedding_model()
            query_vector = model.encode(Text).tolist()
            remaining_probs = probs.exclude(pk__in=direct_probs.values('pk')).order_by(
                CosineDistance('embedding', query_vector)
            )[:45]
            remaining_bunds = bunds.exclude(pk__in=direct_bunds.values('pk')).order_by(
                CosineDistance('embedding', query_vector)
            )[:45]

            probs = list(direct_probs) + list(remaining_probs)
            bunds = list(direct_bunds) + list(remaining_bunds)
        else:
            probs = probs[:50]
            bunds = bunds[:50]

        card_objs = list(chain(probs, bunds))

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