FROM python:3.7-alpine

EXPOSE 8000
VOLUME /app/media/images

RUN mkdir -p /app
WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN apk add --no-cache --virtual .build-deps --update \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    build-base \
    linux-headers \
    pcre-dev \
    && pip3 install --no-cache-dir pipenv \
    && pipenv install --deploy --system \
    && apk del --no-cache .build-deps \
    && apk add --no-cache libpq pcre-dev mailcap

COPY config/uwsgi.ini .
COPY config/docker-entrypoint.sh .
COPY bag .

RUN python manage.py collectstatic --noinput

ENTRYPOINT [ "/app/docker-entrypoint.sh" ]
