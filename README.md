**Django-сервис друзей**

Для запуска необходимы модули Django и djangorestframework.

**Запуск сервиса:**

```
python3 manage.py migrate
python3 manage.py runserver
```

Спецификация API в формате .yaml содержится в файле spec.yaml.

**Примеры использования API:**

Здесь и далее предполагаем, что сервис слушает на localhost:8000.

1) Создание пользователя:
   `curl --request POST  
   --url http://localhost:8000/friends/user/  
   --header 'Content-Type: application/json'  
   --data '{
    "username": "brightnkov",
    "true_name": "yegor britenkov"
   }'`
   Ответ:
   `{
       "id": 1,
       "username": "brightnkov",
       "true_name": "yegor britenkov"
   }`

2) Получение данных о пользователе:
   `curl --request GET \
     --url http://localhost:8000/friends/user/1/`
   Ответ:
   `{
    "id": 1,
    "username": "brightnkov",
    "true_name": "yegor britenkov"
   }`

3) Получение данных обо всех пользователях:
   `curl --request GET \
     --url http://localhost:8000/friends/user/`
   Ответ:
   `{
       "users": [
           {
               "id": 1,
               "username": "brightnkov",
               "true_name": "yegor britenkov"
           },
           {
               "id": 2,
               "username": "risha",
               "true_name": "arina rodionova"
           }
       ]
   }`

4) Отправление запроса дружбы:
   `curl --request POST \
     --url http://localhost:8000/friends/request/ \
     --header 'Content-Type: application/json' \
     --data '{
       "auth_info": {
           "id": 1
       },
       "user_id": 2
   }'`
   Ответ:
   `{
       "id": 1,
       "sender_id": 1,
       "receiver_id": 2
   }`

5) Получение информации о входящих/исходящих запросах дружбы:
   `curl --request GET \
     --url 'http://localhost:8000/friends/request/?request_type=incoming&user_id=2'`
   Ответ:
   `{
       "requests": [
           {
               "id": 1,
               "sender_id": 1,
               "receiver_id": 2
           }
       ]
   }`

6) Ответ на запрос дружбы:
   `curl --request POST \
     --url http://localhost:8000/friends/answer_request/ \
     --header 'Content-Type: application/json' \
     --data '{
       "auth_info": {
           "id": 2
       },
       "request_id": 1,
       "action": "accept"
   }'`
   В ответе приходит только код 200.

7) Получение списка друзей:
   `curl --request GET \
     --url http://localhost:8000/friends/friends/1/`
   Ответ:
   `{
       "friends": [
           2
       ]
   }`

8) Удаление друга:
   `curl --request DELETE \
     --url http://localhost:8000/friends/friends/ \
     --header 'Content-Type: application/json' \
     --data '{
       "auth_info": {
           "id": 2
       },
       "user_id": 1
   }'`
   В ответе приходит только код 200.

9) Получение статуса дружбы с другим пользователем (есть входящая/исходящая заявка, уже друзья или ничего из вышеперечисленного):
   `curl --request GET \
     --url 'http://localhost:8000/friends/status/?id=1&user_id=2'`
   Ответ:
   `{
       "status": "none"
   }`


