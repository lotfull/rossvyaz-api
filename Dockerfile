FROM python:latest

EXPOSE 8000

RUN mkdir /project
WORKDIR /project

COPY ./requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

RUN cp -n .env_example .env

RUN python3 manage.py migrate

CMD python3 -u manage.py runserver 0.0.0.0:8001
