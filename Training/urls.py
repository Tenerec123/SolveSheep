from .views import *
from django.urls import path

urlpatterns = [
    path('', Training_search, name="Training"),
    path("bundle/<int:bund_id>/", Open_bundle, name="Bundle"),
    path("like_bundle/<int:bund_id>/", Like_Unlike_Bundle, name="Like_Bundle"),
    path("create_problem/<int:bund_id>/", Create_AI_Problem, name="Create_Problem"),
    path("bundle_status/<int:bund_id>/", Ready_Check, name="check_bundle_status"),
    # path('base', Base, name="Base"),
]
