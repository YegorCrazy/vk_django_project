from django.test import TestCase, Client
from .models import User, FriendshipRequest, Friendship

client = Client()


def CreateUser(username, true_name):
    return client.post('/friends/user/', {'username': username,
                                          'true_name': true_name},
                       content_type='application/json')


def GetUserInfo(user_id=None):
    url = '/friends/user/' + (str(user_id) + '/' if user_id is not None
                              else '')
    return client.get(url)


def CreateFriendshipRequest(id_from, id_to):
    return client.post('/friends/request/', {
        'auth_info': {
            'id': id_from,
            },
        'user_id': id_to
        }, content_type='application/json')


def GetRequestsInfo(user_id, request_type):
    assert request_type in ['incoming', 'outcoming']
    return client.get('/friends/request/', {'request_type': request_type,
                                            'user_id': user_id})


def AnswerRequest(user_id, request_id, action):
    assert action in ['accept', 'decline']
    return client.post('/friends/answer_request/', {
        'auth_info': {
            'id': user_id,
            },
        'request_id': request_id,
        'action': action
        }, content_type='application/json')


def GetFriendsList(user_id):
    return client.get('/friends/friends/' + str(user_id) + '/')


def DeleteFriend(user_id, to_delete_id):
    return client.delete('/friends/friends/', {
        'auth_info': {
            'id': user_id,
            },
        'user_id': to_delete_id
        }, content_type='application/json')


def GetFriendshipStatus(user_id, other_id):
    return client.get('/friends/status/', {'id': user_id,
                                           'user_id': other_id})


class TestAddNewUser(TestCase):

    def testCreateUser(self):
        resp = CreateUser('aaa', 'aaa bbb')
        assert resp.status_code == 200
        assert resp.json()['username'] == 'aaa'
        assert resp.json()['true_name'] == 'aaa bbb'
        user_id = resp.json()['id']
        assert len(User.objects.all()) == 1
        user = User.objects.get(ID=user_id)
        assert user.Username == 'aaa'
        assert user.TrueName == 'aaa bbb'

    def testCreateUserSameUsername(self):
        resp = CreateUser('aaa', 'aaa bbb')
        assert resp.status_code == 200
        resp = CreateUser('aaa', 'ccc ddd')
        assert resp.status_code == 400
        assert resp.json() == {'code': 86,
                               'payload': 'username occupied'}
        assert len(User.objects.all()) == 1

    def testCreateUserSameTrueName(self):
        resp = CreateUser('aaa', 'aaa bbb')
        assert resp.status_code == 200
        first_id = resp.json()['id']
        resp = CreateUser('bbb', 'aaa bbb')
        assert resp.status_code == 200
        assert len(User.objects.filter(TrueName='aaa bbb')) == 2
        assert first_id != resp.json()['id']


class TestGetUsersInfo(TestCase):

    @classmethod
    def setUpTestData(cls):
        User(ID=1, Username='aaa', TrueName='aaa').save()
        User(ID=2, Username='bbb', TrueName='bbb').save()

    def testGetAllUsers(self):
        resp = GetUserInfo()
        assert resp.status_code == 200
        assert resp.json() == {
            'users': [
                {
                    'id': 1,
                    'username': 'aaa',
                    'true_name': 'aaa'
                    },
                {
                    'id': 2,
                    'username': 'bbb',
                    'true_name': 'bbb'
                    },
                ]
            }

    def testGetOneUser(self):
        resp = GetUserInfo(2)
        assert resp.status_code == 200
        assert resp.json() == {
            'id': 2,
            'username': 'bbb',
            'true_name': 'bbb'
            }

    def testGetNotExistingUser(self):
        resp = GetUserInfo(10)
        assert resp.status_code == 404
        assert resp.json() == {'code': 79,
                               'payload': 'user not found'}


class TestMakeFriendshipRequest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User(ID=1, Username='aaa', TrueName='aaa').save()
        User(ID=2, Username='bbb', TrueName='bbb').save()

    def testCreateNewRequest(self):
        resp = CreateFriendshipRequest(1, 2)
        assert resp.status_code == 200
        assert resp.json()['sender_id'] == 1
        assert resp.json()['receiver_id'] == 2
        request_id = resp.json()['id']
        request = FriendshipRequest.objects.get(ID=request_id)
        assert request.Sender.ID == 1
        assert request.Receiver.ID == 2

    def testCreateExistingRequest(self):
        resp = CreateFriendshipRequest(1, 2)
        assert resp.status_code == 200
        request_info = resp.json()
        resp = CreateFriendshipRequest(1, 2)
        assert resp.status_code == 200
        assert resp.json() == request_info

    def testAcceptFriendshipBySendingRequest(self):
        resp = CreateFriendshipRequest(1, 2)
        assert resp.status_code == 200
        resp = CreateFriendshipRequest(2, 1)
        assert resp.status_code == 200
        assert len(FriendshipRequest.objects.all()) == 0
        assert len(Friendship.objects.all()) == 2
        assert len(Friendship.objects.filter(Friend1__Username='aaa').filter(
            Friend2__Username='bbb')) == 1
        assert len(Friendship.objects.filter(Friend2__Username='aaa').filter(
            Friend1__Username='bbb')) == 1

    def testFriendsAlready(self):
        user1 = User.objects.get(Username='aaa')
        user2 = User.objects.get(Username='bbb')
        Friendship(Friend1=user1, Friend2=user2).save()
        Friendship(Friend1=user2, Friend2=user1).save()
        resp = CreateFriendshipRequest(1, 2)
        assert resp.status_code == 400
        assert resp.json() == {'code': 81,
                               'payload': 'friends already'}

    def testSendRequestToUnexistingUser(self):
        resp = CreateFriendshipRequest(1, 10)
        assert resp.status_code == 404
        assert resp.json() == {'code': 79,
                               'payload': 'user not found'}


class TestGetRequestsInfo(TestCase):

    @classmethod
    def setUpTestData(cls):
        User(ID=1, Username='aaa', TrueName='aaa').save()
        User(ID=2, Username='bbb', TrueName='bbb').save()
        User(ID=3, Username='ccc', TrueName='ccc').save()

    def testGetIncomingRequestsInfo(self):
        FriendshipRequest(ID=1, Sender=User.objects.get(ID=2),
                          Receiver=User.objects.get(ID=1)).save()
        FriendshipRequest(ID=2, Sender=User.objects.get(ID=3),
                          Receiver=User.objects.get(ID=1)).save()
        resp = GetRequestsInfo(1, 'incoming')
        assert resp.status_code == 200
        requests = resp.json()['requests']
        assert {
            'id': 1,
            'sender_id': 2,
            'receiver_id': 1
            } in requests
        assert {
            'id': 2,
            'sender_id': 3,
            'receiver_id': 1
            } in requests
        assert len(requests) == 2

    def testGetOutcomingRequestsInfo(self):
        FriendshipRequest(ID=1, Sender=User.objects.get(ID=1),
                          Receiver=User.objects.get(ID=2)).save()
        FriendshipRequest(ID=2, Sender=User.objects.get(ID=1),
                          Receiver=User.objects.get(ID=3)).save()
        resp = GetRequestsInfo(1, 'outcoming')
        assert resp.status_code == 200
        requests = resp.json()['requests']
        assert {
            'id': 1,
            'sender_id': 1,
            'receiver_id': 2
            } in requests
        assert {
            'id': 2,
            'sender_id': 1,
            'receiver_id': 3
            } in requests
        assert len(requests) == 2

    def testGetRequestsForUnexistingUser(self):
        resp = GetRequestsInfo(10, 'incoming')
        assert resp.status_code == 404
        assert resp.json() == {'code': 79,
                               'payload': 'user not found'}
        resp = GetRequestsInfo(10, 'outcoming')
        assert resp.status_code == 404
        assert resp.json() == {'code': 79,
                               'payload': 'user not found'}


class TestAnswerRequest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User(ID=1, Username='aaa', TrueName='aaa').save()
        User(ID=2, Username='bbb', TrueName='bbb').save()
        FriendshipRequest(ID=1, Sender=User.objects.get(ID=1),
                          Receiver=User.objects.get(ID=2)).save()

    def testAcceptRequest(self):
        resp = AnswerRequest(2, 1, 'accept')
        assert resp.status_code == 200
        assert len(FriendshipRequest.objects.all()) == 0
        assert len(Friendship.objects.all()) == 2
        assert len(Friendship.objects.filter(Friend1__Username='aaa').filter(
            Friend2__Username='bbb')) == 1
        assert len(Friendship.objects.filter(Friend2__Username='aaa').filter(
            Friend1__Username='bbb')) == 1

    def testDeclineRequest(self):
        resp = AnswerRequest(2, 1, 'decline')
        assert resp.status_code == 200
        assert len(FriendshipRequest.objects.all()) == 0
        assert len(Friendship.objects.all()) == 0

    def testUnexistingRequest(self):
        resp = AnswerRequest(2, 10, 'accept')
        assert resp.status_code == 404
        assert resp.json() == {'code': 84,
                               'payload': 'friendship request not found'}
        resp = AnswerRequest(2, 10, 'decline')
        assert resp.status_code == 404
        assert resp.json() == {'code': 84,
                               'payload': 'friendship request not found'}

    def testRequestDoesNotBelongToUser(self):
        resp = AnswerRequest(1, 1, 'accept')
        assert resp.status_code == 400
        assert resp.json() == {'code': 85,
                               'payload': 'request is not yours'}


class TestGetFriends(TestCase):

    @classmethod
    def setUpTestData(cls):
        User(ID=1, Username='aaa', TrueName='aaa').save()
        User(ID=2, Username='bbb', TrueName='bbb').save()
        Friendship(Friend1=User.objects.get(ID=1),
                   Friend2=User.objects.get(ID=2)).save()
        Friendship(Friend1=User.objects.get(ID=2),
                   Friend2=User.objects.get(ID=1)).save()

    def testGetFriendsList(self):
        resp = GetFriendsList(1)
        assert resp.status_code == 200
        assert resp.json() == {
            'friends': [
                2
                ]
            }
        resp = GetFriendsList(2)
        assert resp.status_code == 200
        assert resp.json() == {
            'friends': [
                1
                ]
            }

    def testUnexistingUser(self):
        resp = GetFriendsList(10)
        assert resp.status_code == 404
        assert resp.json() == {'code': 79,
                               'payload': 'user not found'}


class TestDeleteFriend(TestCase):

    @classmethod
    def setUpTestData(cls):
        User(ID=1, Username='aaa', TrueName='aaa').save()
        User(ID=2, Username='bbb', TrueName='bbb').save()
        User(ID=3, Username='ccc', TrueName='ccc').save()
        Friendship(Friend1=User.objects.get(ID=1),
                   Friend2=User.objects.get(ID=2)).save()
        Friendship(Friend1=User.objects.get(ID=2),
                   Friend2=User.objects.get(ID=1)).save()

    def testDeleteExistingFriendship(self):
        resp = DeleteFriend(1, 2)
        assert resp.status_code == 200
        assert len(Friendship.objects.all()) == 0

    def testDeleteUnexistingFriendship(self):
        old_friendship_count = len(Friendship.objects.all())
        resp = DeleteFriend(3, 2)
        assert resp.status_code == 200
        assert len(Friendship.objects.all()) == old_friendship_count

    def testUnexistingUser(self):
        resp = DeleteFriend(1, 10)
        assert resp.status_code == 404
        assert resp.json() == {'code': 79,
                               'payload': 'user not found'}


class TestFriendshipStatus(TestCase):

    @classmethod
    def setUpTestData(cls):
        User(ID=1, Username='aaa', TrueName='aaa').save()
        User(ID=2, Username='bbb', TrueName='bbb').save()
        User(ID=3, Username='ccc', TrueName='ccc').save()
        Friendship(Friend1=User.objects.get(ID=1),
                   Friend2=User.objects.get(ID=2)).save()
        Friendship(Friend1=User.objects.get(ID=2),
                   Friend2=User.objects.get(ID=1)).save()
        FriendshipRequest(ID=1, Sender=User.objects.get(ID=3),
                          Receiver=User.objects.get(ID=2)).save()

    def testStatusFriendship(self):
        resp = GetFriendshipStatus(1, 2)
        assert resp.status_code == 200
        assert resp.json() == {'status': 'friends'}
        resp = GetFriendshipStatus(2, 1)
        assert resp.status_code == 200
        assert resp.json() == {'status': 'friends'}

    def testStatusIncoming(self):
        resp = GetFriendshipStatus(2, 3)
        assert resp.status_code == 200
        assert resp.json() == {'status': 'incoming',
                               'request_id': 1}

    def testStatusOutcoming(self):
        resp = GetFriendshipStatus(3, 2)
        assert resp.status_code == 200
        assert resp.json() == {'status': 'outcoming',
                               'request_id': 1}

    def testStatusNone(self):
        resp = GetFriendshipStatus(1, 3)
        assert resp.status_code == 200
        assert resp.json() == {'status': 'none'}

    def testUnexistingUser(self):
        resp = GetFriendshipStatus(10, 3)
        assert resp.status_code == 404
        assert resp.json() == {'code': 79,
                               'payload': 'user not found'}
        resp = GetFriendshipStatus(3, 10)
        assert resp.status_code == 404
        assert resp.json() == {'code': 79,
                               'payload': 'user not found'}
