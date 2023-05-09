FROM python:3.10

ENV PYTHONUNBUFFERED 1

WORKDIR /parsing/

COPY . /parsing/

RUN pip install -r req.txt