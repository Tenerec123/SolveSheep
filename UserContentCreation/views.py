from django.shortcuts import render, redirect
from django.core.mail import send_mail
import threading

def enviar_email_async(prob_id, msg):
    try:
        send_mail(
        subject=f'La solución enviada a {prob_id}',
        message=msg,
        from_email='solvesheep@gmail.com',
        recipient_list=['solvesheep@gmail.com'],
        fail_silently=False
    )
        print(f"DEBUG: Correo enviado con éxito para el problema {prob_id}")
    except Exception as e:
        # Esto saldrá en los logs de Render sin tumbar la web
        print(f"ERROR enviando correo: {e}")


def SendSolutionToVerificate(request, prob_id):
    if request.method == "GET":
        return render(request, "send_solution.html", {"prob_id":prob_id})
    thread = threading.Thread(target=lambda:enviar_email_async(prob_id,request.POST.get("solution", "ERROR")))
    thread.start()
    return redirect('Problem', prob_id=prob_id)