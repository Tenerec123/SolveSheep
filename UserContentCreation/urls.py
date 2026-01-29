from .views import *
from django.urls import path

urlpatterns = [
    path('solution/<int:prob_id>/', SendSolutionToVerificate, name = "SendSolution"),
    path('decide/<str:action>/<str:token>/', decide_solution, name = "DecideSolution")
]
