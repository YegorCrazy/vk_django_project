FROM python:3

ADD . /work/server
WORKDIR /work/server

ENV PYTHONUNBUFFERED=1
RUN pip install -r ./requirements.txt
RUN python manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
