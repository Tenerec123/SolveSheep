from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from MainApp.models import Bundle, Problem, DifTag, TypeTag
from django.http import JsonResponse
from google import genai
from django.conf import settings
import threading
import json
import re
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
User = get_user_model()


def Add_Problems(bund_id,Problems_json):
    print(Problems_json)
    try:
        data = json.loads(Problems_json)
    except Exception as e:
        print(e)
        return False
    Bund= Bundle.objects.get(id=bund_id)
    for prob in data:
    # Usamos update_or_create con title como criterio
        new_problem, created = Problem.objects.update_or_create(
            title=prob['title'],  # <-- criterio de búsqueda

            defaults={
                'text': prob['text'],
                'video': prob['video'],
                'author': User.objects.get(username="SolveSheep"),
                'dif_tag': DifTag.objects.get(name=prob['dif_tag']),
                
            }
        )
        new_problem.type_tags.set([TypeTag.objects.get(name=tt) for tt in prob['type_tags']])
        Bund.problems.add(new_problem)
        Bund.relodeable = True
        Bund.save(update_fields=["relodeable"])
    return True
def Prompt(Amount, bund_id):
    Bund = Bundle.objects.get(id=bund_id)
    Bundle_description = Bund.description
    Titles = [prob.title for prob in Bund.problems.all()]
    return """
    You are a mathematical problem generator for the SolveSheep database. Produce output exactly as specified below; do NOT add anything else.
    OUTPUT FORMAT (MANDATORY)
    Output MUST be a JSON array of objects, anything else, the first character must be one [ and the last ] NO MORE
    Do NOT include any id field.
    All text MUST be written in ENGLISH.
    Do NOT add explanations, comments, or extra text outside the JSON.
    EACH OBJECT (exact fields)
    Each object must contain these fields exactly and only:
    {
    "title": "Short descriptive title (as specific as possible but not too long)"
    "text": "Full problem statement, possibly with LaTeX and \\n line breaks",
    "video": "",
    "type_tags": ["ONE to THREE allowed tags"],
    "dif_tag": "X.X",
    "author": "SolveSheep"
    }
    REQUIRED FORMATTING
    The respons must start at [ and end at ]. There must not be anything before [ or after ] 
    Mathematical expressions must use LaTeX:
    - Inline: \\( ... \\) and Display: $$ ... $$
    Line breaks inside the "text" value must be """+r"{ç}"+"""
    The field "video" must always be the empty string "".
    The field "author" must ALWAYS be exactly "SolveSheep".
    Do NOT include solutions.
    Do NOT reference or ask to see figures/images; avoid phrases like "see the figure".
    ALLOWED type_tags (use only these; 1–3 tags per problem; do not use any other)
    ["Algebra","Calculus","Number Theory","Geometry","Probability","Statistics","Combinatorics","Trigonometry","Inequalities"]
    Put for each backslash put only one literal backslash (\\)
    All double quotes inside JSON strings must be properly escaped using \" and must not use \\\".
    DIFFICULTY (dif_tag)
    Use exactly ONE decimal string (e.g. "1.0"). Choose the most appropriate:
    "1.0" basic secondary school
    "1.5" intermediate/secondary-olympiad
    "2.0" pre-contest/regional
    "2.5" low national contest (requires a trick)
    "3.0" national contest
    "3.5" IMO-easy / strong national
    "4.0" IMO-hard / advanced university
    "4.5" graduate level
    "5.0" research level
    CONTENT RULES (brief)
    Problems must be self-contained and clearly stated.
    No solutions, no diagrams, no external references.
    Titles concise and descriptive.
    Do NOT repeat identical templates with trivial changes.
    VARIABLE USER REQUEST
    """+f"Number of problems: {Amount}\nDescription: {Bundle_description}\nTitles of current problems (don't repeat): {Titles}"
def Normalize(texto: str) -> str:
    # 1. Reemplazar salto de línea real o marcador por \n literal
    texto = texto.replace("{ç}", "\\n")  # si usas marcador

    # 2. Normalizar backslashes
    def reemplazo(match):
        siguiente = match.group(2)
        if siguiente == "n":
            return "\\n"  # un backslash literal
        else:
            return "\\\\" + siguiente  # doble backslash para LaTeX/otros

    return re.sub(r"(\\+)(.)", reemplazo, texto)
def Ready_Check(request, bund_id):
    bund = Bundle.objects.get(id=bund_id)
    if not bund.needs_reload:
        return JsonResponse({"ready":False, "retry":False})

    Response = bund.relodeable
    if Response:
        bund.relodeable = False
        bund.needs_reload = False
        bund.save(update_fields=["relodeable", "needs_reload"])
    return JsonResponse({"ready":Response, "retry":not Response})
def Training_search(request):
    return render(request, 'training.html',{
        "Card_objs":Bundle.objects.all()
    })
def Open_bundle(request, bund_id):

    # for prob in Problem.objects.all():
    #     prob.likes_count = 0
    #     prob.save(update_fields=['likes_count'])
    bund = get_object_or_404(Bundle, id=bund_id)
    return render(request, 'bundle_interface.html', {
        'bund':bund,
        'Card_objs':bund.problems.all().order_by("dif_tag", "title")
    })
def Like_Unlike_Bundle(request, bund_id):

    bund = Bundle.objects.get(id=bund_id)

    if not request.user.is_authenticated:
        return JsonResponse({
        "likes_count": bund.likes_count,
        'liked':False
    })

    liked = True
    if request.user in bund.likes.all():
        liked = False
        print("Dislike")
        bund.likes.remove(request.user)
        bund.likes_count -= 1
    else:
        print("Like")
        bund.likes.add(request.user)
        bund.likes_count += 1
    bund.save(update_fields=['likes_count'])
    return JsonResponse({
        "likes_count": bund.likes_count,
        'liked':liked
    })
def call_ai_api(bund_id, num_problems):
    print("API_CALLED")
    B = Bundle.objects.get(id= bund_id)
    B.needs_reload = True
    B.save(update_fields=["needs_reload"])
    print("API_MID_1")
    client = genai.Client(api_key=settings.AI_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=Prompt(num_problems, bund_id),
    )
    print("API_MID_2")
    problems = Normalize(response.text)
    Add_Problems(bund_id, problems)
    print("API_END")
@staff_member_required
def Create_AI_Problem(request, bund_id):
    thread = threading.Thread(target=lambda:call_ai_api(bund_id, int(request.POST.get("num_problems", 1))))
    thread.start()
    return redirect(reverse("Bundle", kwargs={"bund_id": bund_id}))
        
    
