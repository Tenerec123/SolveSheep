from django.shortcuts import render, redirect
from django.core.mail import send_mail
import threading
from django.core.mail import send_mail
from django.conf import settings
import resend
from MainApp.models import Problem, Solution

resend.api_key = settings.RESEND_API_KEY


def send_email_and_save_solution(prob_id, msg):
    r = resend.Emails.send({
  "from": "onboarding@resend.dev",
  "to": "solvesheep@gmail.com",
  "subject": f"Solution to problem {prob_id}",
  "html": msg
    })

    Solution.objects.create(
        text=msg,
        problem=Problem.objects.get(id=prob_id),
    )


def SendSolutionToVerificate(request, prob_id):
    if request.method == "GET":
        return render(request, "send_solution.html", {"prob_id":prob_id})
    thread = threading.Thread(target=lambda:send_email_and_save_solution(prob_id,request.POST.get("solution", "ERROR")))
    thread.start()

    return redirect('Problem', prob_id=prob_id)