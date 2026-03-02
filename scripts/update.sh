#!/bin/bash
set -e

PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx upgrade svs-core

svs utils django-shell migrate

SVS_VERSION=$(svs --version | awk '{print $3}')

echo "svs-core updated to version $SVS_VERSION, update the web interface if present!"
