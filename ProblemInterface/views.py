from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from MainApp.models import Problem, Solution
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json

def Open_problem(request, problem_slug):

    # for prob in Problem.objects.all():
    #     prob.likes_count = 0
    #     prob.save(update_fields=['likes_count'])
    prob = get_object_or_404(Problem, slug=problem_slug)
    return render(request, 'interface.html', {
        'prob':prob,
        'solutions':Solution.objects.filter(problem=prob, accepted=True),
    })

@csrf_exempt
def Like_Unlike_Problem(request, problem_slug):

    prob = Problem.objects.get(slug=problem_slug)

    if not request.user.is_authenticated:
        return JsonResponse({
        "likes_count": prob.likes_count,
        'liked':False
    })

    liked = True
    if request.user in prob.likes.all():
        liked = False
        print("Dislike")
        prob.likes.remove(request.user)
        prob.likes_count -= 1
    else:
        print("Like")
        prob.likes.add(request.user)
        prob.likes_count += 1
    prob.save(update_fields=['likes_count'])
    return JsonResponse({
        "likes_count": prob.likes_count,
        'liked':liked
    })
@csrf_exempt
def toggle_solutions(request, problem_slug):
    if request.method == "POST":
        prob = get_object_or_404(Problem, slug=problem_slug)
        data = json.loads(request.body)
        show = data.get("show", False)

        print(show)
        # Aquí puedes registrar la acción en tu modelo o en otro registro
        # Ejemplo: prob.last_viewed = request.user
        # prob.solutions_visible = show
        # prob.save()
        return JsonResponse({"ok": True, "show": show})
    return JsonResponse({"ok": False}, status=400)

