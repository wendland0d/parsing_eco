FROM python:3.10

ENV PYTHONUNBUFFERED 1

WORKDIR /bot/

COPY . /bot/
COPY requirements.txt /bot/

RUN pip install -r /bot/requirements.txt
