from django.shortcuts import render, redirect
import threading
from django.conf import settings
import resend
from MainApp.models import Problem, Solution
from django.core.signing import Signer # Para firmar los enlaces
from django.core.signing import BadSignature
from django.http import HttpResponse

resend.api_key = settings.RESEND_API_KEY

def decide_solution(request, action, token):
    signer = Signer()
    try:
        # Verificamos que el token es auténtico
        solution_id = signer.unsign(token)
        solution = Solution.objects.get(id=solution_id)

        if action == "yes":
            solution.accepted = True # O el campo que uses para validar
            solution.save()
            return HttpResponse("✅ Solution succesfully accepted.")
        
        elif action == "no":
            solution.delete() # O marcar como rechazada
            return HttpResponse("❌ Solution succesfully deleted.")

    except (BadSignature, Solution.DoesNotExist):
        return HttpResponse("⚠️ El enlace no es válido o ya ha expirado.", status=403)
    

def send_email_and_save_solution(prob_id, msg, author):
    p=Problem.objects.get(id=prob_id)
    s = Solution.objects.create(
        text=msg,
        problem=p,
        author=author,
    )
       # 2. Creamos el token de seguridad para ESTA solución
    signer = Signer()
    token = signer.sign(s.id)

    base_url = settings.MAIN_URL #"https://solvesheep.com" 
    url_aceptar = f"{base_url}/creation/decide/yes/{token}/"
    url_rechazar = f"{base_url}/creation/decide/no/{token}/"

     # 4. Diseñamos el HTML del email con botones
    html_content = f"""
        <h3>Nueva propuesta para el problema {prob_id}:{p.title}</h3>
        <p>{p.text}</p>
        <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #ccc;">
            {msg}
        </div>
        <br>
        <p>¿Qué quieres hacer con esta solución?</p>
        <a href="{url_aceptar}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">ACEPTAR</a>
        <a href="{url_rechazar}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">RECHAZAR</a>
    """

    # 5. Enviamos con Resend
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "solvesheep@gmail.com",
        "subject": f"Moderación: Solución #{s.id}",
        "html": html_content
    })



def SendSolutionToVerificate(request, prob_id):
    if request.method == "GET":
        return render(request, "send_solution.html", {"prob_id":prob_id})
    thread = threading.Thread(target=lambda:send_email_and_save_solution(prob_id,request.POST.get("solution", "ERROR"), request.user))
    thread.start()

    return redirect('Problem', prob_id=prob_id)