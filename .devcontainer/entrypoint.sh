#!/bin/bash

# Start Docker daemon in the background
echo "🔧 Starting Docker daemon..."
sudo dockerd > /home/dev/docker.log 2>&1 &

# Wait for Docker to become available
echo "⏳ Waiting for Docker to be ready..."
until docker info > /dev/null 2>&1; do
    sleep 1
done

echo "✅ Docker is ready!"

# Start interactive shell
exec bash
