#!/bin/bash
# Start Docker daemon in background
start-docker.sh

while ! docker info >/dev/null 2>&1; do
    echo "Waiting for Docker daemon..."
    sleep 1
done

if [ -z $POSTGRES_USER ] || [ -z $POSTGRES_PASSWORD ] || [ -z $POSTGRES_DB ]; then
    echo "One or more required environment variables are not set. Exiting."
    exit 1
fi

exec tail -f /dev/null
