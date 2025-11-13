from .views import *
from django.urls import path

urlpatterns = [
    path('logout/', Logout, name="Logout"),
    path('register/',Registro, name="Register"),
    path('login',Login, name="Login")
    # path('base', Base, name="Base"),
]
