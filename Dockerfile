FROM python:3.12-alpine3.20

LABEL authors="mpique, AleixMT"

RUN apk add --no-cache make bash

WORKDIR /app

COPY ./Makefile /app
COPY ./pyproject.toml /app
COPY src /app/src
RUN make install

# script python for main
#lo comento para hacer pruebas CMD ["python", "/app/src/main.py", "--imarina-input", "/input/iMarina.xlsx", "--a3-input", "/input/A3.xlsx", "--countries-dict", "/input/countries.xlsx", "--jobs-dict", "/input/Job_Descriptions.xlsx"]
ENTRYPOINT ["./venv/bin/python", "-m", "imarina"]
CMD []
