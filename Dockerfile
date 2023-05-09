FROM python:3.10

WORKDIR /parsers/

COPY . /parsers/


RUN pip install -r req.txt