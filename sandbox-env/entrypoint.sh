#!/bin/bash
# Start Docker daemon in background
start-docker.sh

while ! docker info >/dev/null 2>&1; do
    echo "Waiting for Docker daemon..."
    sleep 1
done

echo "Docker daemon ready."

# Auto-initialize SVS if not yet initialized
if [ ! -f /etc/svs/.env ]; then
    echo ""
    echo "============================================"
    echo "  Running first-time SVS initialization..."
    echo "============================================"
    echo ""

    # Run the full bootstrap with 'svs init' to set up Docker stack,
    # run migrations, import templates, and create a default admin user.
    # The sandbox image already has svs-core installed via pipx, so we
    # skip re-installation and go straight to init.
    bash /root/install.sh --yes --scope system

    PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin \
        svs init --yes --skip-completions --user admin --password admin

    echo ""
    echo "============================================"
    echo "  SVS sandbox ready!"
    echo "  Default credentials: admin / admin"
    echo "  Run 'svs user list' to verify."
    echo "============================================"
else
    echo "SVS already initialized."
fi

exec tail -f /dev/null
