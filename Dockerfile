FROM ubuntu20.04 as base
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip nginx wget git bash \
    systemd

COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip "setuptools<58.0.0"

RUN pip3 install -r tmp/requirements.txt --timeout 60

FROM base AS development

ARG username=user
ARG user_id=1000
ARG group_id=1000

RUN groupadd --gid $group_id $username \
    && useradd --uid $user_id --gid $group_id --create-home --shell /bin/bash $username

RUN usermod -aG sudo $username
RUN echo $username ALL=\(ALL\) NOPASSWD:ALL >> /etc/sudoers

COPY ./ /app
WORKDIR /app

COPY ./services/ova_hub_backend.service.sample /etc/systemd/system/ova_hub_backend.service
COPY ./services/ova_hub_frontend.service.sample /etc/systemd/system/ova_hub_frontend.service

COPY ./scripts/ /tmp
RUN bash /tmp/install.sh

RUN bash /tmp/run_hub.sh

FROM base as deployment

COPY ./ /app
WORKDIR /app

COPY ./services/ova_hub_backend.service.sample /etc/systemd/system/ova_hub_backend.service
COPY ./services/ova_hub_frontend.service.sample /etc/systemd/system/ova_hub_frontend.service

COPY ./scripts/ /tmp
RUN bash /tmp/install.sh

RUN bash /tmp/run_hub.sh

