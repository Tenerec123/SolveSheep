from .views import *
from django.urls import path

urlpatterns = [
    path('', Training_search, name="Training"),
    # path('base', Base, name="Base"),
]
