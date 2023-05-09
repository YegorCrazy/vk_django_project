from django.db import models


class User(models.Model):

    ID = models.AutoField(primary_key=True, db_index=True)
    Username = models.CharField(max_length=30, unique=True)
    TrueName = models.CharField(max_length=40)

    def __str__(self):
        return self.Username


class FriendshipRequest(models.Model):

    ID = models.AutoField(primary_key=True, db_index=True)
    Sender = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='outcoming_requests',
                               db_index=True)
    Receiver = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='incoming_requests',
                                 db_index=True)

    def __str__(self):
        return self.Sender.Username + '->' + self.Receiver.Username


class Friendship(models.Model):

    """
    The idea is to store entry (1, 2) and (2, 1) for a friendship
    between users 1 and 2. The other solution is to store only (1, 2)
    and control if 1.ID < 2.ID, but SQLite doesn't provide this
    """

    Friend1 = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name='friendships',
                                db_index=True)
    Friend2 = models.ForeignKey(User, on_delete=models.CASCADE,
                                db_index=True)

    def __str__(self):
        return self.Friend1.Username + '+' + self.Friend2.Username
