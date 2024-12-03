FROM python:3.10.12 AS base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apt-get install curl

WORKDIR /src

COPY ./requirements ./requirements
RUN  pip install -r requirements/dev.txt

FROM base AS base_with_req

RUN mkdir -p ./logs

COPY . .

CMD ["python", "-m", "app.main"]
