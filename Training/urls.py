from .views import *
from django.urls import path

urlpatterns = [
    path('', Training_search, name="Training"),
    path("bundle/<slug:bundle_slug>/", Open_bundle, name="Bundle"),
    path("like_bundle/<slug:bundle_slug>/", Like_Unlike_Bundle, name="Like_Bundle"),
    path("create_problem/<slug:bundle_slug>/", Create_AI_Problem, name="Create_Problem"),
    path("bundle_status/<slug:bundle_slug>/", Ready_Check, name="check_bundle_status"),
    # path('base', Base, name="Base"),
]
