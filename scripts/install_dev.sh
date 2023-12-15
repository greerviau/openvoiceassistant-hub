#!/bin/bash

apt install -y python3-pip python3-dev python3-venv nginx wget git bash systemd ffmpeg espeak libespeak-dev sed npm

CWD=$(pwd)

echo $CWD

python3 -m venv $CWD/env

source $CWD/env/bin/activate

python -m pip install -r requirements.txt

python -m spacy download en_core_web_sm

python -m nltk.downloader stopwords