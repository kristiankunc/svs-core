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

cd /root

cat <<EOF > .env
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=$POSTGRES_DB
EOF


docker-compose up -d

while ! docker ps --format '{{.Names}}' | grep -qE 'svs-db|caddy'; do
    echo "Waiting for svs-db and caddy containers to start..."
    sleep 2
done

bash /root/install.sh -y


echo "DATABASE_URL=postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:5432/$POSTGRES_DB" > /etc/svs/.env

exec tail -f /dev/null
