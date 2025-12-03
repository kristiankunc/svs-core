#!/bin/sh

mkdir -p /etc/docker

if [ ! -f /etc/docker/daemon.json ]; then
  cat <<EOF >/etc/docker/daemon.json
{
  "userns-remap": "default"
}
EOF
fi

#dockerd-entrypoint.sh
