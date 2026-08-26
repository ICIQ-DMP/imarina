FROM aleixmt/imarina-load-researchers:latest

COPY ./tests /app

ENTRYPOINT ["make", "test"]