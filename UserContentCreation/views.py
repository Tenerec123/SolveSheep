from django.shortcuts import render, redirect
from django.core.mail import send_mail
import threading

from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_str
import traceback

def enviar_email_async(prob_id, msg):
    print(f"==> [THREAD START] Intentando enviar correo para problema: {prob_id}")
    try:
        # Aseguramos que el mensaje sea un string limpio
        cuerpo_mensaje = force_str(msg)
        
        filas_afectadas = send_mail(
            subject=f'La solución enviada a {prob_id}',
            message=cuerpo_mensaje,
            from_email=settings.EMAIL_HOST_USER, # Usamos la config de settings
            recipient_list=['solvesheep@gmail.com'],
            fail_silently=False
        )
        
        if filas_afectadas > 0:
            print(f"==> [SUCCESS] Correo enviado con éxito para el problema {prob_id}")
        else:
            print(f"==> [WARNING] Django dice que envió el correo, pero 0 mensajes fueron aceptados.")

    except Exception as e:
        # Esto imprimirá el error exacto (Network unreachable, Authentication error, etc.)
        print(f"==> [ERROR EN HILO EMAIL]: {str(e)}")
        # Opcional: descomenta la siguiente línea si quieres ver toda la pila del error en el log
        # traceback.print_exc()

def SendSolutionToVerificate(request, prob_id):
    if request.method == "GET":
        return render(request, "send_solution.html", {"prob_id":prob_id})
    thread = threading.Thread(target=lambda:enviar_email_async(prob_id,request.POST.get("solution", "ERROR")))
    thread.start()
    return redirect('Problem', prob_id=prob_id)