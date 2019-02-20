FROM python:3.7-alpine

EXPOSE 8000
VOLUME /images


RUN mkdir /app
WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN apk add --no-cache --virtual .build-deps --update \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && pip3 install --no-cache-dir pipenv \
    && pipenv install --deploy --system \
    && apk del --no-cache .build-deps \
    && apk add --no-cache libpq

COPY bag .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
