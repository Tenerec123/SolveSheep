from .views import *
from django.urls import path

urlpatterns = [
    path('', Main, name="Main"),
    path('difficulties/', Difs, name="Difs"),
    path('json/', Add_JSON_probs, name = "Json"),
    path("ads.txt", ads_txt),
]
