from django.urls import path
from .views import *

urlpatterns = [
    path("toggle_solutions/<slug:problem_slug>/", toggle_solutions, name="toggle_solutions"),
    path("like/<slug:problem_slug>/", Like_Unlike_Problem, name="Like"),
    path("problem/<slug:problem_slug>/", Open_problem, name="Problem"),
]
