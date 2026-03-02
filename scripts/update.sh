#!/bin/bash
set -e

sudo PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx upgrade svs-core

sudo svs utils django-shell migrate

SVS_VERSION=$(sudo svs --version | awk '{print $3}')

echo "svs-core updated to version $SVS_VERSION, update the web interface if present!"
