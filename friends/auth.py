import json
from .models import User


def AuthUser(request):

    """
    This is a function to understand what user does the action.
    Authorization is a complex process and we can't use cookie
    because we don't have web interface, that's why we just get
    user id from request. However, we can use anything we want
    later and implement it in this function (for example,
    session manage).
    """

    try:
        body = json.loads(request.body)
    except Exception:
        raise Exception('can\'t parse body')

    user_id = body.get('auth_info').get('id')
    if user_id is None:
        raise Exception('no auth info')

    try:
        user = User.objects.get(ID=int(user_id))
    except Exception:
        raise Exception('user not found')

    return user
