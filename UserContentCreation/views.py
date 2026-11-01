from django.shortcuts import render, redirect
import threading
from django.conf import settings
import resend
from MainApp.models import Problem, Solution
from django.http import HttpResponse

resend.api_key = settings.RESEND_API_KEY


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



def SendSolutionToVerificate(request, prob_id):
    if request.method == "GET":
        return render(request, "send_solution.html", {"prob_id":prob_id})
    prob = Problem.objects.get(id=prob_id)
    thread = threading.Thread(target=lambda:send_email_and_save_solution(prob_id,request.POST.get("solution", "ERROR"), request.user))
    thread.start()

    return redirect('Problem', problem_slug=prob.slug)