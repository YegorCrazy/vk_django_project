import json
from rest_framework.decorators import api_view
from django.http import JsonResponse
from friends.models import User, FriendshipRequest, Friendship
from django.views import View
from .auth import AuthUser


class UserView(View):

    def post(self, request):
        # create a new user
        try:
            body = json.loads(request.body)
        except Exception:
            return JsonResponse({'code': 76,
                                 'payload': 'can\'t parse body'},
                                status=400)

        username = body.get('username')
        true_name = body.get('true_name')
        if username is None or true_name is None:
            return JsonResponse({'code': 77,
                                 'payload': 'some of fields are missing'},
                                status=400)

        if len(User.objects.filter(Username=username)) > 0:
            return JsonResponse({'code': 86,
                                 'payload': 'username occupied'},
                                status=400)

        new_user = User(Username=username, TrueName=true_name)

        try:
            new_user.save()
        except Exception:
            return JsonResponse({'code': 78,
                                 'payload': 'can\'t save user'},
                                status=400)

        return JsonResponse(new_user.ToDict(), status=200)

    def get(self, request):
        # get all users
        return JsonResponse({'users': [user.ToDict() for user
                                       in User.objects.all()]})


@api_view(['GET'])
def GetUser(request, user_id):
    try:
        user = User.objects.get(ID=user_id)
    except Exception:
        return JsonResponse({'code': 79,
                             'payload': 'user not found'},
                            status=404)

    return JsonResponse(user.ToDict(), status=200)


class FriendshipRequestView(View):

    def post(self, request):
        try:
            sender = AuthUser(request)
        except Exception as ex:
            return JsonResponse({'code': 80,
                                 'payload': 'auth failed: ' + str(ex)},
                                status=400)
        try:
            body = json.loads(request.body)
        except Exception:
            return JsonResponse({'code': 76,
                                 'payload': 'can\'t parse body'},
                                status=400)

        receiver_id = body.get('user_id')
        if receiver_id is None:
            return JsonResponse({'code': 77,
                                 'payload': 'some of fields are missing'},
                                status=400)

        try:
            receiver = User.objects.get(ID=receiver_id)
        except Exception:
            return JsonResponse({'code': 79,
                                 'payload': 'user not found'},
                                status=404)

        if sender == receiver:
            return JsonResponse({'code': 87,
                                 'payload': 'request to same user'},
                                status=404)

        friendships = (Friendship.objects.filter(Friend1=sender)
                       .filter(Friend2=receiver))
        if len(friendships) > 0:
            return JsonResponse({'code': 81,
                                 'payload': 'friends already'},
                                status=400)

        requests = (FriendshipRequest.objects.filter(Sender=sender)
                    .filter(Receiver=receiver))
        if len(requests) > 0:
            # request already exists
            return JsonResponse(requests[0].ToDict(), status=200)

        reverse_requests = (FriendshipRequest.objects.filter(Sender=receiver)
                            .filter(Receiver=sender))
        if len(reverse_requests) > 0:
            for friendship_request in reverse_requests:
                friendship_request.delete()
            new_friendship1 = Friendship(Friend1=sender, Friend2=receiver)
            new_friendship1.save()
            new_friendship2 = Friendship(Friend1=receiver, Friend2=sender)
            new_friendship2.save()
            return JsonResponse({}, status=200)

        new_request = FriendshipRequest(Sender=sender, Receiver=receiver)
        new_request.save()

        return JsonResponse(new_request.ToDict(), status=200)

    def get(self, request):
        user_id = request.GET.get('user_id')
        request_type = request.GET.get('request_type')

        if user_id is None or request_type is None:
            return JsonResponse({'code': 77,
                                 'payload': 'some of fields are missing'},
                                status=400)

        if request_type not in ['incoming', 'outcoming']:
            return JsonResponse({'code': 82,
                                 'payload': 'wrong request type'},
                                status=400)

        try:
            user = User.objects.get(ID=user_id)
        except Exception:
            return JsonResponse({'code': 79,
                                 'payload': 'user not found'},
                                status=404)

        if request_type == 'incoming':
            req_set = FriendshipRequest.objects.filter(Receiver=user)
        else:
            req_set = FriendshipRequest.objects.filter(Sender=user)

        return JsonResponse({'requests': [req.ToDict() for req in req_set]},
                            status=200)


@api_view(['POST'])
def ProcessFriendshipRequest(request):
    try:
        user = AuthUser(request)
    except Exception as ex:
        return JsonResponse({'code': 80,
                             'payload': 'auth failed: ' + str(ex)},
                            status=400)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({'code': 76,
                             'payload': 'can\'t parse body'},
                            status=400)

    request_id = body.get('request_id')
    action = body.get('action')
    if request_id is None or action is None:
        return JsonResponse({'code': 77,
                             'payload': 'some of fields are missing'},
                            status=400)

    if action not in ['accept', 'decline']:
        return JsonResponse({'code': 83,
                             'payload': 'wrong action type'},
                            status=400)

    try:
        friendship_request = FriendshipRequest.objects.get(ID=request_id)
    except Exception:
        return JsonResponse({'code': 84,
                             'payload': 'friendship request not found'},
                            status=404)

    if friendship_request.Receiver != user:
        return JsonResponse({'code': 85,
                             'payload': 'request is not yours'},
                            status=400)

    if action == 'accept':
        other_user = friendship_request.Sender
        new_friendship1 = Friendship(Friend1=user, Friend2=other_user)
        new_friendship1.save()
        new_friendship2 = Friendship(Friend1=other_user, Friend2=user)
        new_friendship2.save()

    friendship_request.delete()

    return JsonResponse({}, status=200)


@api_view(['GET'])
def GetFriends(request, user_id):
    try:
        user = User.objects.get(ID=user_id)
    except Exception:
        return JsonResponse({'code': 79,
                             'payload': 'user not found'},
                            status=404)

    resp = [friendship.Friend2.ID for friendship
            in Friendship.objects.filter(Friend1=user)]
    return JsonResponse({'friends': resp}, status=200)


@api_view(['DELETE'])
def DeleteFriend(request):
    try:
        user = AuthUser(request)
    except Exception as ex:
        return JsonResponse({'code': 80,
                             'payload': 'auth failed: ' + str(ex)},
                            status=400)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({'code': 76,
                             'payload': 'can\'t parse body'},
                            status=400)

    other_user_id = body.get('user_id')
    if other_user_id is None:
        return JsonResponse({'code': 77,
                             'payload': 'some of fields are missing'},
                            status=400)

    try:
        other_user = User.objects.get(ID=other_user_id)
    except Exception:
        return JsonResponse({'code': 79,
                             'payload': 'user not found'},
                            status=404)

    friendship1 = Friendship.objects.filter(Friend1=user).filter(
        Friend2=other_user)
    friendship2 = Friendship.objects.filter(Friend2=user).filter(
        Friend1=other_user)
    for friendship in friendship1:
        friendship.delete()
    for friendship in friendship2:
        friendship.delete()
    return JsonResponse({}, status=200)


@api_view(['GET'])
def GetFriendshipStatus(request):
    user_id = request.GET.get('id')
    other_user_id = request.GET.get('user_id')

    if user_id is None or other_user_id is None:
        return JsonResponse({'code': 77,
                             'payload': 'some of fields are missing'},
                            status=400)

    try:
        user = User.objects.get(ID=user_id)
    except Exception:
        return JsonResponse({'code': 79,
                             'payload': 'user not found'},
                            status=404)

    try:
        other_user = User.objects.get(ID=other_user_id)
    except Exception:
        return JsonResponse({'code': 79,
                             'payload': 'user not found'},
                            status=404)

    friendships = Friendship.objects.filter(Friend1=user).filter(
        Friend2=other_user)
    if len(friendships) > 0:
        return JsonResponse({'status': 'friends'}, status=200)

    incoming = FriendshipRequest.objects.filter(Sender=other_user).filter(
        Receiver=user)
    if len(incoming) > 0:
        return JsonResponse({'status': 'incoming',
                             'request_id': incoming[0].ID},
                            status=200)

    outcoming = FriendshipRequest.objects.filter(Receiver=other_user).filter(
        Sender=user)
    if len(outcoming) > 0:
        return JsonResponse({'status': 'outcoming',
                             'request_id': outcoming[0].ID},
                            status=200)

    return JsonResponse({'status': 'none'}, status=200)
