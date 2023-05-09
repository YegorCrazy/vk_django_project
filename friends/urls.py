from django.urls import path

from .views import CreateUser, GetUser

urlpatterns = [
    path("user/", CreateUser),
    path("user/<int:user_id>/", GetUser),
]
