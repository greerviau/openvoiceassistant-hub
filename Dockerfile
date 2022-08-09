FROM nvidia/cuda:11.7.0-runtime-ubuntu20.04 as base
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip nginx wget git bash \
    systemd

COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip "setuptools<58.0.0"

RUN pip3 install -r tmp/requirements.txt --timeout 60

COPY ./scripts/install.sh /tmp/install.sh
RUN bash /tmp/install.sh

FROM base AS development

ARG username=user
ARG user_id=1000
ARG group_id=1000

RUN groupadd --gid $group_id $username \
    && useradd --uid $user_id --gid $group_id --create-home --shell /bin/bash $username

RUN usermod -aG sudo $username
RUN echo $username ALL=\(ALL\) NOPASSWD:ALL >> /etc/sudoers

FROM base as deployment

COPY ./ /app
WORKDIR /app