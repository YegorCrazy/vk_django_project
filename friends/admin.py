from django.contrib import admin
from .models import User, FriendshipRequest, Friendship

admin.site.register(User)
admin.site.register(Friendship)
admin.site.register(FriendshipRequest)
