FROM python:3.6-alpine

ENV PYCURL_SSL_LIBRARY=openssl
WORKDIR /usr/src/app
COPY requirements.txt requirements.txt

RUN apk add --update --virtual build-dependencies \
        build-base \
        curl-dev \
        libffi-dev \
        linux-headers \
        python3-dev \
        git \
        openssh && \
    apk add --update --no-cache \
        postgresql-dev \
        libcurl && \
    pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del build-dependencies

COPY ./src .
EXPOSE 5000

CMD ["sh", "./app_start.sh"]
