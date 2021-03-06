FROM ubuntu:20.04 as base
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip nginx

COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip "setuptools<58.0.0"

RUN pip3 install -r tmp/requirements.txt --timeout 60

FROM base AS development

RUN apt-get update && apt-get install -y git
RUN useradd -ms /bin/bash user

FROM base as deployment

COPY ./ /app
WORKDIR /app