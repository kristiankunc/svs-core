#!/bin/bash
# Start Docker daemon in background
start-docker.sh

while ! docker info >/dev/null 2>&1; do
    echo "Waiting for Docker daemon..."
    sleep 1
done

echo "Docker daemon ready."

if [ ! -f /etc/svs/.env ]; then
    echo ""
    echo "============================================"
    echo "  Running first-time SVS initialization..."
    echo "============================================"
    echo ""

    bash /root/install.sh --yes --scope system

    PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin \
        svs init --yes --skip-completions

    echo ""
    echo "============================================"
    echo "  SVS sandbox ready!"
    echo "  Check output above for admin credentials."
    echo "  Run 'svs user list' to verify."
    echo "============================================"
else
    echo "SVS already initialized."
fi

exec tail -f /dev/null
