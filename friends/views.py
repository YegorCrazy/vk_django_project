from rest_framework.decorators import api_view
import json
from django.http import JsonResponse
from friends.models import User


@api_view(['POST'])
def CreateUser(request):
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

    new_user = User(Username=username, TrueName=true_name)

    try:
        new_user.save()
    except Exception:
        return JsonResponse({'code': 78,
                             'payload': 'can\'t save user'},
                            status=400)

    data = {'id': new_user.ID,
            'username': new_user.Username,
            'true_name': new_user.TrueName}
    return JsonResponse(data, status=200)


@api_view(['GET'])
def GetUser(request, user_id):
    try:
        user = User.objects.get(ID=user_id)
    except Exception:
        return JsonResponse({'code': 79,
                             'payload': 'user not found'},
                            status=404)

    data = {'id': user.ID,
            'username': user.Username,
            'true_name': user.TrueName}
    return JsonResponse(data, status=200)
