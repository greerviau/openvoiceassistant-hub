#!/bin/bash
apt-get update && apt-get install -y python3-pip python3-dev python3-venv nginx wget git bash systemd ffmpeg espeak libespeak-dev npm

curl -fsSL https://deb.nodesource.com/setup_21.x | sudo -E bash - && sudo apt-get install -y nodejs

CWD=$(pwd)

echo $CWD

#BACKEND INSTALL

python3 -m venv $CWD/env

source $CWD/env/bin/activate

python -m pip install --upgrade pip
python -m pip install --upgrade wheel
python -m pip install -r requirements_full.txt

python -m spacy download en_core_web_sm
python -m nltk.downloader stopwords

FRONTEND_DIR="$CWD/frontend"

cd "$FRONTEND_DIR" || exit 1
rm -rf build
npm run build 

cat <<EOF > "/etc/systemd/system/ova_hub_backend.service"
[Unit]
Description=openvoiceassistant HUB backend

[Service]
ExecStart=/bin/bash $CWD/scripts/start_backend.sh
WorkingDirectory=$CWD
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOF

systemctl enable ova_hub_backend.service
systemctl restart ova_hub_backend.service

: ' MAY BE ABLE TO REMOVE
#FRONTEND INSTALL
FRONTEND_DIR="$CWD/frontend"

cd "$FRONTEND_DIR" || exit 1
rm -rf build
npm run build 

# Create and configure the nginx server block
cat <<EOF > "/etc/systemd/system/ova_hub_frontend.service"
[Unit]
Description=openvoiceassistant HUB frontend

[Service]
ExecStart=/bin/bash $CWD/scripts/start_frontend.sh
WorkingDirectory=$CWD
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOF

systemctl enable ova_hub_frontend.service
systemctl restart ova_hub_frontend.service
'
