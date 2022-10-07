#!/bin/bash

apt install -y ffmpeg sed espeak

CWD=$(pwd)

echo $CWD

python3 -m venv $CWD/env/hub

source $CWD/env/hub/bin/activate

python3 -m spacy download en_core_web_sm

python3 -m nltk.downloader stopwords

cp $CWD/scripts/ova_hub_backend.service.sample /etc/systemd/system/ova_hub_backend.service
sed -i -e "s|OVAPATH|$CWD|g" /etc/systemd/system/ova_hub_backend.service
sed -i -e "s|USER|${USER}|g" /etc/systemd/system/ova_hub_backend.service

systemctl enable ova_hub_backend.service
systemctl start ova_hub_backend.service