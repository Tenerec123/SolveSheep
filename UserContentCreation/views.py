from django.shortcuts import render, redirect
from django.core.mail import send_mail
import threading
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_str
import socket
from django.core.mail import get_connection
import resend

resend.api_key = settings.RESEND_API_KEY


def enviar_email_async(prob_id, msg):
    r = resend.Emails.send({
  "from": "onboarding@resend.dev",
  "to": "solvesheep@gmail.com",
  "subject": f"Solution to problem {prob_id}",
  "html": msg
    })
def SendSolutionToVerificate(request, prob_id):
    if request.method == "GET":
        return render(request, "send_solution.html", {"prob_id":prob_id})
    thread = threading.Thread(target=lambda:enviar_email_async(prob_id,request.POST.get("solution", "ERROR")))
    thread.start()
    return redirect('Problem', prob_id=prob_id)