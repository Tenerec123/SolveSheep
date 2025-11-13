from django.urls import path
from .views import *

urlpatterns = [
    path("toggle_solutions/<int:prob_id>/", toggle_solutions, name="toggle_solutions"),
    path("like/<int:prob_id>/", Like_Unlike_Problem, name="Like"),
    path("problem/<int:prob_id>/", Open_problem, name="Problem"),
]
