from .views import *
from django.urls import path

urlpatterns = [
    path('', Main, name="Main"),
    path('difficulties/', Difs, name="Difs"),
    path("ads.txt", ads_txt),
]
