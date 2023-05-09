from django.urls import path

from .views import *

urlpatterns = [
    path("user/", UserView.as_view()),
    path("user/<int:user_id>/", GetUser),
    path("request/", FriendshipRequestView.as_view()),
    path("answer_request/", ProcessFriendshipRequest),
    path("friends/<int:user_id>/", GetFriends),
    path("friends/", DeleteFriend),
    path("status/", GetFriendshipStatus),
]
