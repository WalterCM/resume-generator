FROM python:3.8-alpine
MAINTAINER Walter Capa

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache jpeg-dev zlib-dev
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .build-deps \
        build-base linux-headers gcc libc-dev postgresql-dev
RUN pip install -r /requirements.txt
RUN apk del .build-deps

RUN mkdir /src
WORKDIR /src
COPY ./src /src

RUN adduser -D user
USER user
