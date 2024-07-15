FROM python:3.12-slim-bullseye as dev

ENV PYTHONUNBUFFERED 1 \  BIND_PORT=8000
ARG APP_HOME=/app/src
WORKDIR ${APP_HOME}

COPY ./backend ./poetry.lock ./pyproject.toml  ${APP_HOME}/

RUN apt-get update &&  \
    apt install netcat libreadline-dev -y && \
    apt-get autoremove && \
    apt-get autoclean && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/tmp/* && \
    pip install --upgrade pip && \
    pip install poetry --only main &&  \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev

COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
