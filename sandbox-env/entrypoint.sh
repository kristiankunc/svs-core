#!/bin/bash
# Start Docker daemon in background
start-docker.sh

while ! docker info >/dev/null 2>&1; do
    echo "Waiting for Docker daemon..."
    sleep 1
done

exec tail -f /dev/null
