FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y build-essential

RUN mkdir ml_app

COPY ../api ./ml_app/api

WORKDIR /ml_app

RUN pip install -r ./api/requirements.txt

CMD uvicorn ml.api.__main__:app --host 0.0.0.0 --port 8001
