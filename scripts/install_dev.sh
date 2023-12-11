#!/bin/bash

apt install -y python3-pip python3.11-dev python3.11-venv python3.11-dev nginx wget git bash systemd ffmpeg espeak libespeak-dev sed npm

CWD=$(pwd)

echo $CWD

python3.11 -m venv $CWD/env

source $CWD/env/bin/activate

python -m pip install -r requirements.txt

python -m spacy download en_core_web_sm

python -m nltk.downloader stopwords