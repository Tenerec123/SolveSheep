from django.shortcuts import render, redirect
from django.core.mail import send_mail
import smtplib
from email.mime.text import MIMEText
def SendSolutionToVerificate(request, prob_id):
    if request.method == "GET":
        return render(request, "send_solution.html", {"prob_id":prob_id})
    
    send_mail(
        subject=f'La solución enviada a {prob_id}',
        message=request.POST.get("solution", "ERROR"),
        from_email='solvesheep@gmail.com',
        recipient_list=['solvesheep@gmail.com'],
    )
    return redirect("Main")