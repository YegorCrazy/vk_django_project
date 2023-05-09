# Generated by Django 4.2.1 on 2023-05-09 10:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('friends', '0002_alter_user_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendshipRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_requests', to='friends.user')),
                ('Sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outcoming_requests', to='friends.user')),
            ],
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Friend1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendships', to='friends.user')),
                ('Friend2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='friends.user')),
            ],
        ),
    ]