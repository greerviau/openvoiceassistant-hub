#!/bin/bash

apt install -y python3-pip python3-dev python3-venv nginx wget git bash systemd ffmpeg espeak libespeak-dev sed npm

CWD=$(pwd)

echo $CWD

#BACKEND INSTALL

python3 -m venv $CWD/env

source $CWD/env/bin/activate

python3 -m pip install --upgrade pip

python3 -m pip install --upgrade wheel

python -m pip install -r requirements_full.txt

python -m spacy download en_core_web_sm

python -m nltk.downloader stopwords

cp $CWD/scripts/ova_hub_backend.service.sample /etc/systemd/system/ova_hub_backend.service
sed -i -e "s|OVAPATH|$CWD|g" /etc/systemd/system/ova_hub_backend.service
sed -i -e "s|USER|${USER}|g" /etc/systemd/system/ova_hub_backend.service

#FRONTEND INSTALL

cd frontend

npm install

cd $CWD

cp $CWD/scripts/ova_hub_frontend.service.sample /etc/systemd/system/ova_hub_frontend.service
sed -i -e "s|OVAPATH|$CWD|g" /etc/systemd/system/ova_hub_frontend.service
sed -i -e "s|USER|${USER}|g" /etc/systemd/system/ova_hub_frontend.service

systemctl enable ova_hub_backend.service
systemctl enable ova_hub_frontend.service
systemctl start ova_hub_backend.service
systemctl start ova_hub_frontend.service