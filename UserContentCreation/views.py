from django.shortcuts import render, redirect
import threading
from django.conf import settings
import resend
from MainApp.models import Problem, Solution
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

resend.api_key = settings.RESEND_API_KEY

# Simple in-process counter; swapping CACHES to redis makes it shared
SOLUTION_RATE_LIMIT = 5
SOLUTION_RATE_WINDOW = 3600  # seconds


def _rate_limit_ok(user_id):
    key = f"solution_rate_{user_id}"
    # add() only succeeds for the first call inside the window: the stored
    # value starts at 1 so incr() afterwards counts total attempts exactly.
    if not cache.add(key, 1, SOLUTION_RATE_WINDOW):
        try:
            count = cache.incr(key)
        except ValueError:
            cache.set(key, 1, SOLUTION_RATE_WINDOW)
            count = 1
    else:
        count = 1
    return count <= SOLUTION_RATE_LIMIT


def send_email_and_save_solution(prob_id, msg, author):
    p=Problem.objects.get(id=prob_id)
    s = Solution.objects.create(
        text=msg,
        problem=p,
        author=author,
    )
    # Notification only: accept/reject happens in the Django admin
    # (Admin > Solutions). Email preview clients auto-follow GET links,
    # so emailed URLs must never perform actions.
    html_content = f"""
        <h3>New proposed solution for problem {prob_id}: {p.title}</h3>
        <p>{p.text}</p>
        <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #ccc;">
            {msg}
        </div>
        <br>
        <p>Review and accept/reject it in the Django admin (Solutions).</p>
    """

    # Send notification with Resend
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "solvesheep@gmail.com",
        "subject": f"Moderación: Solución #{s.id}",
        "html": html_content
    })



@login_required
def SendSolutionToVerificate(request, prob_id):
    if request.method == "GET":
        return render(request, "send_solution.html", {"prob_id":prob_id})

    solution_text = request.POST.get("solution", "").strip()
    if not solution_text:
        return render(request, "send_solution.html", {
            "prob_id": prob_id,
            "error": "The solution text cannot be empty.",
        })
    if len(solution_text) > 1000:
        return render(request, "send_solution.html", {
            "prob_id": prob_id,
            "error": "Solutions are limited to 1000 characters.",
        })

    if not _rate_limit_ok(request.user.pk):
        return HttpResponse("Too many solutions submitted. Try again later.", status=429)

    prob = Problem.objects.get(id=prob_id)
    thread = threading.Thread(target=lambda:send_email_and_save_solution(prob_id, solution_text, request.user))
    thread.start()

    return redirect('Problem', problem_slug=prob.slug)