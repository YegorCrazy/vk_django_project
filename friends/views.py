import json
from rest_framework.decorators import api_view
from django.http import JsonResponse
from friends.models import User
from django.views import View


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
