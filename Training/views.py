from django.shortcuts import render,get_object_or_404
from MainApp.models import Bundle, Problem
from django.http import JsonResponse
# Create your views here.

def Training_search(request):
    return render(request, 'training.html',{
        "Bundles":Bundle.objects.all(),
    })

def Open_bundle(request, bund_id):

    # for prob in Problem.objects.all():
    #     prob.likes_count = 0
    #     prob.save(update_fields=['likes_count'])
    bund = get_object_or_404(Bundle, id=bund_id)
    return render(request, 'bundle_interface.html', {
        'bund':bund,
        'Problems':bund.problems.all()
    })

def Like_Unlike_Bundle(request, bund_id):

    bund = Bundle.objects.get(id=bund_id)

    if not request.user.is_authenticated:
        return JsonResponse({
        "likes_count": bund.likes_count,
        'liked':False
    })

    liked = True
    if request.user in bund.likes.all():
        liked = False
        print("Dislike")
        bund.likes.remove(request.user)
        bund.likes_count -= 1
    else:
        print("Like")
        bund.likes.add(request.user)
        bund.likes_count += 1
    bund.save(update_fields=['likes_count'])
    return JsonResponse({
        "likes_count": bund.likes_count,
        'liked':liked
    })