from .views import *
from django.urls import path

urlpatterns = [
    path('', Search, name="Search"),
]
