from django.shortcuts import render, get_object_or_404
from MainApp.models import Bundle, TypeTag
from django.http import JsonResponse
from django.db.models import F


def Ready_Check(request, bundle_slug):
    bund = Bundle.objects.get(slug=bundle_slug)
    if not bund.needs_reload:
        return JsonResponse({"ready":False, "retry":False})

    Response = bund.relodeable
    if Response:
        bund.relodeable = False
        bund.needs_reload = False
        bund.save(update_fields=["relodeable", "needs_reload"])
    return JsonResponse({"ready":Response, "retry":not Response})


def Training_search(request):
    # T4/S4: virtual practice sets derived only from existing TypeTag
    # records; every set routes to the existing Search page through its
    # current Type GET parameter (no new filters, routes, or taxonomy).
    practice_sets = [
        {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
            "count": tag.problem_set.count(),
        }
        for tag in TypeTag.objects.all().order_by("name")
    ]
    practice_sets = [practice_set for practice_set in practice_sets
                     if practice_set["count"] > 0]
    return render(request, 'training.html',{
        "Card_objs":Bundle.objects.all(),
        "practice_sets": practice_sets,
    })

def Open_bundle(request, bundle_slug):

    # for prob in Problem.objects.all():
    #     prob.likes_count = 0
    #     prob.save(update_fields=['likes_count'])
    bund = get_object_or_404(Bundle, slug=bundle_slug)
    return render(request, 'bundle_interface.html', {
        'bund':bund,
        'Card_objs':bund.problems.all().order_by("dif_tag", "title")
    })

def Like_Unlike_Bundle(request, bundle_slug):

    bund = Bundle.objects.get(slug=bundle_slug)

    if not request.user.is_authenticated:
        return JsonResponse({
        "likes_count": bund.likes_count,
        'liked':False
    })

    liked = True
    if request.user in bund.likes.all():
        liked = False
        bund.likes.remove(request.user)
        # Atomic counter update in the database.
        Bundle.objects.filter(pk=bund.pk).update(likes_count=F('likes_count') - 1)
    else:
        bund.likes.add(request.user)
        Bundle.objects.filter(pk=bund.pk).update(likes_count=F('likes_count') + 1)
    bund.refresh_from_db(fields=['likes_count'])
    return JsonResponse({
        "likes_count": bund.likes_count,
        'liked':liked
    })
