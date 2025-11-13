from django.shortcuts import render
from MainApp.models import Problem
# Create your views here.

# def Display(request):
#     PF = ProblemForm()
#     if request.method == "POST":
#         PF = ProblemForm(request.POST)
#         if PF.is_valid():
#             Problem.objects.create(
#                 title = request.POST['Title'],
#                 text = request.POST['Text'],
#                 image = request.POST['Image'])
#             return redirect('/?valid')
        
#     return render(request, 'landing.html',{
#         'ProblemForm':PF
#     })

def Base(request):
    return render(request, 'base.html')
