#!/bin/bash

apt install -y python3-pip python3.9-dev python3.9-venv nginx wget git bash systemd ffmpeg espeak libespeak-dev sed npm

CWD=$(pwd)

echo $CWD

python3.9 -m venv $CWD/env

source $CWD/env/bin/activate

python -m pip install -r requirements.txt

cd $CWD/backend/components/synthesizer/gradtts/grad_tts/model/monotonic_align/

python setup.py build_ext --inplace

cd $CWD

python -m spacy download en_core_web_sm

python -m nltk.downloader stopwords

cp $CWD/scripts/ova_hub_backend.service.sample /etc/systemd/system/ova_hub_backend.service
sed -i -e "s|OVAPATH|$CWD|g" /etc/systemd/system/ova_hub_backend.service
sed -i -e "s|USER|${USER}|g" /etc/systemd/system/ova_hub_backend.service

systemctl enable ova_hub_backend.service
systemctl start ova_hub_backend.service