from .views import *
from django.urls import path

urlpatterns = [
    path('logout/', Logout, name="Logout"),
    path('register/',Register, name="Register"),
    path('login/',Login, name="Login"),
    path('edit/', Edit, name="EditUser"),

    path('user/<str:username>/problems', User_Interface_Problems, name="UserInterface_problems"),
    path('user/<str:username>/bundles/', User_Interface_Bundles, name="UserInterface_bundles"),
    path('user/<str:username>/solutions/', User_Interface_Solutions, name="UserInterface_solutions"),
    path('user/<str:username>/likes', User_Interface_Likes, name="UserInterface_likes"),
]