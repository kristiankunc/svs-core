#!/bin/bash

set -e

SVS_VERSION=$(svs --version | awk '{print $3}')

RUN_INITIAL_SETUP=false


read -p "Do you want to also run the initial setup? (Run only once after a fresh install) (y/n) " answer
if [ "$answer" != "y" ]; then
    echo "Skipping initial setup."
else
    RUN_INITIAL_SETUP=true
fi

cd ..
git reset --hard HEAD
git fetch origin
git pull origin main
git checkout v$SVS_VERSION

cd web


if [ "$RUN_INITIAL_SETUP" = true ]; then
    python3 -m venv .venv
    mkdir -p logs
    cp .env.example .env
    echo "Please edit the .env file with your desired configuration"
else
    echo "Skipping initial setup, only updating the web interface."
fi

source .venv/bin/activate
pip install -r requirements.txt
pip install svs_core==$SVS_VERSION

npm ci --prefix frontend
npm run build --prefix frontend

python manage.py collectstatic --noinput --clear

deactivate

echo "Web interface updated to version $SVS_VERSION, restart the svs-web service to apply the changes."
