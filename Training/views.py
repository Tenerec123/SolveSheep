from django.shortcuts import render, get_object_or_404, redirect
from MainApp.models import (
    Bundle,
    Problem,
    ProblemAttempt,
    ProblemProgress,
    TypeTag,
)
from MainApp.templatetags.problem_areas import get_problem_area_tags
from django.http import JsonResponse
from django.db import transaction
from django.db.models import F
import random


# T4/S4: the random picker keeps only the current pick in the Django
# session. It is session-scoped state, never long-term profile history
# and never an accuracy record.
_TRAINING_PICK_SESSION_KEY = "training_pick"
_PICK_PENDING = "pending"
_PICK_SOLVED = "solved"
_PICK_GIVEN_UP = "given_up"


def _training_pick_session_key(request):
    """Separate anonymous browser state from each authenticated account."""
    user = getattr(request, "user", None)
    user_id = user.pk if user and user.is_authenticated else "anonymous"
    return f"{_TRAINING_PICK_SESSION_KEY}_{user_id}"


def _stored_pick(request):
    """Return the current identity's session pick only while its problem exists."""
    key = _training_pick_session_key(request)
    pick = request.session.get(key)
    if not pick or not Problem.objects.filter(pk=pick.get("problem")).exists():
        if pick:
            request.session.pop(key, None)
        return None
    return pick


def _area_tag_groups(problem):
    area_tags = get_problem_area_tags(problem)
    return [
        {
            "kind": "mathematical",
            "label": "Mathematical areas",
            "tags": area_tags["mathematical"],
        },
        {
            "kind": "cognitive",
            "label": "Cognitive areas",
            "tags": area_tags["cognitive"],
        },
    ]


def _training_context(request):
    active_pick = _stored_pick(request)
    if active_pick:
        active_pick = dict(active_pick)
        problem = Problem.objects.get(pk=active_pick["problem"])
        active_pick["problem_obj"] = problem
        active_pick["area_tag_groups"] = _area_tag_groups(problem)
    return {
        "active_pick": active_pick,
        "picker_no_problems": Problem.objects.count() == 0,
        "can_pick": not active_pick or active_pick.get("status") != _PICK_PENDING,
    }


def _handle_training_pick(request):
    active_pick = _stored_pick(request)
    if active_pick and active_pick.get("status") == _PICK_PENDING:
        # An active problem remains pending until it is explicitly solved or abandoned.
        return redirect("Training")

    problem_ids = list(Problem.objects.values_list("pk", flat=True))
    if not problem_ids:
        # Truthful empty state: nothing can be picked, nothing is stored.
        return render(request, 'training.html', {
            "Card_objs": Bundle.objects.all(),
            "practice_sets": [],
            "active_pick": None,
            "picker_no_problems": True,
        })
    problem_id = random.choice(problem_ids)
    pick = {"problem": problem_id, "status": _PICK_PENDING}
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        with transaction.atomic():
            attempt = ProblemAttempt.objects.create(
                user=user,
                problem_id=problem_id,
                outcome=ProblemAttempt.Outcome.PENDING,
            )
            ProblemProgress.objects.update_or_create(
                user=user,
                problem_id=problem_id,
                defaults={"status": ProblemProgress.Status.PENDING},
            )
        pick["attempt"] = attempt.pk

    request.session[_training_pick_session_key(request)] = pick
    return redirect("Training")


def _set_pick_status(request, status):
    pick = _stored_pick(request)
    if pick and pick.get("status") == _PICK_PENDING:
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            with transaction.atomic():
                attempt = None
                attempt_id = pick.get("attempt")
                if attempt_id:
                    attempt = ProblemAttempt.objects.filter(
                        pk=attempt_id,
                        user=user,
                        problem_id=pick["problem"],
                        outcome=ProblemAttempt.Outcome.PENDING,
                    ).first()
                else:
                    # Preserve a pending session created before account
                    # persistence was deployed, without trusting its owner.
                    attempt = ProblemAttempt.objects.create(
                        user=user,
                        problem_id=pick["problem"],
                        outcome=ProblemAttempt.Outcome.PENDING,
                    )

                if attempt:
                    attempt.outcome = status
                    attempt.save(update_fields=["outcome"])
                    latest_attempt_id = ProblemAttempt.objects.filter(
                        user=user, problem_id=pick["problem"]
                    ).order_by("-attempted_at", "-pk").values_list("pk", flat=True).first()
                    if latest_attempt_id == attempt.pk:
                        ProblemProgress.objects.update_or_create(
                            user=user,
                            problem_id=pick["problem"],
                            defaults={"status": status},
                        )
                    pick["status"] = status
            if not pick.get("attempt") and attempt:
                pick["attempt"] = attempt.pk
        else:
            pick["status"] = status

        request.session[_training_pick_session_key(request)] = pick
    return redirect("Training")


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
    # T4/S4: POST actions stay on this same route (no new URLs),
    # CSRF-protected through the training template forms, and always
    # answer with a normal redirect back to the Training page.
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "pick":
            return _handle_training_pick(request)
        if action == "solved":
            return _set_pick_status(request, _PICK_SOLVED)
        if action == "give_up":
            return _set_pick_status(request, _PICK_GIVEN_UP)
        return redirect("Training")

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
    context = {
        "Card_objs":Bundle.objects.all(),
        "practice_sets": practice_sets,
        **_training_context(request),
    }
    return render(request, 'training.html', context)

def Open_bundle(request, bundle_slug):

    # for prob in Problem.objects.all():
    #     prob.likes_count = 0
    #     prob.save(update_fields=['likes_count'])
    bund = get_object_or_404(Bundle, slug=bundle_slug)
    return render(request, 'bundle_interface.html', {
        'bund':bund,
        'Card_objs':bund.problems.all().order_by("dif_tag", "title").prefetch_related(
            "area_weights__area"
        )
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
