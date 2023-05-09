from django.urls import path

from .views import UserView, GetUser

urlpatterns = [
    path("user/", UserView.as_view()),
    path("user/<int:user_id>/", GetUser),
]
