#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
apt-get update && \
add-apt-repository -y ppa:deadsnakes/ppa && \
apt-get install -y python3.11 python3-pip python3.11-dev python3.11-venv wget git bash systemd ffmpeg espeak libespeak-dev npm

CWD=$(pwd)
echo $CWD

rm -rf $CWD/env
python3.11 -m venv $CWD/env

source $CWD/env/bin/activate

python -m pip install --upgrade pip
python -m pip install --upgrade wheel
python -m pip install -r requirements.txt

python -m spacy download en_core_web_sm
python -m nltk.downloader stopwords

FRONTEND_DIR="$CWD/frontend"

cd "$FRONTEND_DIR" || exit 1
rm -rf build
npm install
npm run build 

cd $CWD

cat <<EOF > "/etc/systemd/system/ova_hub.service"
[Unit]
Description=openvoiceassistant HUB

[Service]
ExecStart=/bin/bash $CWD/scripts/start_hub.sh
WorkingDirectory=$CWD
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOF

systemctl enable ova_hub.service
systemctl restart ova_hub.service
