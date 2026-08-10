FROM python:3.14-alpine3.24

LABEL authors="mpique, AleixMT"

RUN apk add --no-cache make bash

WORKDIR /app

COPY ./Makefile /app
COPY ./pyproject.toml /app
COPY src /app/src
RUN make install

ENTRYPOINT ["/app/venv/bin/python", "-m", "imarina"]
CMD []
