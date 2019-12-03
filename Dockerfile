FROM python:latest

EXPOSE 8000

RUN mkdir /project
WORKDIR /project

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

RUN cp -n .env_example .env
