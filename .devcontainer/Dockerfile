FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
RUN echo 'APT::Install-Suggests "0";' >> /etc/apt/apt.conf.d/00-docker
RUN echo 'APT::Install-Recommends "0";' >> /etc/apt/apt.conf.d/00-docker
RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common gpg-agent && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get purge -y --autoremove software-properties-common gpg-agent && \
    apt-get install -y --no-install-recommends python3.11 python3-pip python3.11-dev python3.11-venv gcc g++ wget git bash systemd ffmpeg espeak libespeak-dev npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN useradd -ms /bin/bashr ova
USER ova