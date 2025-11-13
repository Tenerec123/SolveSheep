from .views import *
from django.urls import path

urlpatterns = [
    path('', Main, name="Main"),
    # path('base', Base, name="Base"),
]
