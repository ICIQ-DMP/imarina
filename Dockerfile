
# image base python
FROM python:3.12-alpine3.20

LABEL authors="mpique"

#RUN mkdir -p /input
#RUN mkdir -p /uploads /logs

# work directory in the container
WORKDIR /app

COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# copy at the app
COPY ./src /app/src

# script python for main
#lo comento para hacer pruebas CMD ["python", "/app/src/main.py", "--imarina-input", "/input/iMarina.xlsx", "--a3-input", "/input/A3.xlsx", "--countries-dict", "/input/countries.xlsx", "--jobs-dict", "/input/Job_Descriptions.xlsx"]
ENTRYPOINT ["python", "/app/src/main.py", "--step", "build"]


