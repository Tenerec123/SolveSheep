from .views import *
from django.urls import path

urlpatterns = [
    path('', Training_search, name="Training"),
    path("bundle/<int:bund_id>/", Open_bundle, name="Bundle"),
    path("like_bundle/<int:bund_id>/", Like_Unlike_Bundle, name="Like_Bundle"),
    # path('base', Base, name="Base"),
]
