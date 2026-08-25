FROM mariopique/imarina-load:latest

COPY ./tests /app

ENTRYPOINT ["make", "test"]