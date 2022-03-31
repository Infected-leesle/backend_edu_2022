FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /django-gunicorn-nginx-docker/app

WORKDIR /

RUN touch /django-gunicorn-nginx-docker/__init__.py

WORKDIR /django-gunicorn-nginx-docker/app

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./app /app
