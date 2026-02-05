from .views import *
from django.urls import path

urlpatterns = [
    path('logout/', Logout, name="Logout"),
    path('register/',Register, name="Register"),
    path('login/',Login, name="Login"),
    path('user/<str:username>/', User_Interface, name="UserInterface"),
    path('edit/', Edit, name="EditUser"),
]
