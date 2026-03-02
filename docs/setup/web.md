# Web setup

A web UI is provided for controlling SVS and provides a more user-friendly way to organise your system.

!!! danger "Security Notice"

    The web interface requires running as `root` to manage Docker containers. While security hardening features are implemented (rate limiting, HTTPS, audit logging), the interface should **NOT be exposed directly to the public internet**.

    **Recommended deployment:**
    - Use within an isolated network or VPN
    - Configure firewall rules to restrict access
    - Always use HTTPS with a reverse proxy
    - Enable all security features by setting `DEBUG=False`

**Keep in mind that the web interface is strictly tied to the core library and missmatching versions may cause issues. Always use the same repository at the tag as your
installed version. Use the [svs --version](../cli-documentation/index.md#svs) command to check your installed version.**

## Prerequisites

The web interface requires the core SVS library to be installed. Please follow the [quickstart guide](../setup/quickstart.md) to install the core library first.
After you have installed the library and verified it is working, you can continue with the web setup.

### Node.js and npm

Since the web interface uses some frontend dependencies, you need to have Node.js and npm installed.
You can install them using your system's package manager or by following the instructions on the [official Node.js website](https://nodejs.org/).

Alternatively, you can use services like [nodesource](https://deb.nodesource.com/) or [nvm](https://github.com/nvm-sh/nvm). **Using latest LTS (`v24`) is recommended.**

## Installation

The web interface is provided in the root repository under the `web/` directory.

### Clone the repository

Clone the latest release of the repository and navigate to the `web/` directory:


```bash
git clone https://github.com/kristiankunc/svs-core
cd svs-core/web
```

### Install script

The web directory includes an update/install script called `update.sh` that can be used to install the web interface. It will pull the latest changes from the repository, install dependencies, and build the frontend.

```bash
sudo bash update.sh
```

## Configuration

### Environment variables

Edit the provided `.env.example` file and save it as `.env`

```bash
cp .env.example .env
```

All the required environment variables are documented in the `.env.example` file.

## Running

To start the web interface, simply run:

```bash
sudo -E .venv/bin/gunicorn project.wsgi --bind 0.0.0.0:8000 # sudo warning mentioned at the top of this page
```

After starting, you can access the web interface in your browser at `http://<your-server-ip>:8000`

## Updating

Use the same `update.sh` script to update the web interface to the latest version. It will pull the latest changes from the repository, install any new dependencies, and rebuild the frontend.

```bash
sudo bash update.sh
```


## Security recommendations

For production use:

1. Set `DEBUG=False` in your `.env` file
2. Configure HTTPS using a reverse proxy (Caddy or nginx)
3. Ensure the `logs/` directory exists and is writable
4. Review security logs regularly: `tail -f web/logs/security.log`
5. Use firewall rules or VPN to restrict access to trusted IPs only

## Background service

Best way to run the web interface in production is to set it up as a systemd service. Create a new file at `/etc/systemd/system/svs-web.service` with the following content:

```ini
[Unit]
Description=SVS Web Interface
After=network.target
[Service]
User=root
WorkingDirectory=/path/to/svs-core/web
ExecStart=/path/to/svs-core/web/.venv/bin/gunicorn project.wsgi --bind 0.0.0.0:8000 --workers 3
Restart=always
[Install]
WantedBy=multi-user.target
```

Replace all the variables and paths with the appropriate values for your system. After creating the service file, reload systemd and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable svs-web
sudo systemctl start svs-web
```

## Domain configuration

**As mentioned above, exposing publically is not recommended, but is supported**.

Modify `/etc/svs/docker/docker-compose.yml` and append the following to the `caddy` service definition to mount the Caddyfile and tell Caddy to use it:

```yaml
caddy:
    ...
    volumes:
      ...
      - ./web.Caddyfile:/etc/caddy/web.Caddyfile:ro # Mount the Caddyfile
    environment:
      ...
      - CADDY_DOCKER_CADDYFILE_PATH=/etc/caddy/web.Caddyfile # Tell Caddy to use the mounted Caddyfile
    extra_hosts:
      - "host.docker.internal:host-gateway" # Allow Caddy to access the host network
```

Then create the `web.Caddyfile` in the root repository with the following content:

```caddy
example.com {
    reverse_proxy host.docker.internal:8000
}
```

This is a minimal config, you can extend it with additional security features like rate limiting, IP allowlisting, etc. For more details, refer to the [Caddy documentation](https://caddyserver.com/docs/caddyfile).

Restart the SVS services to apply the changes:

```bash
(cd /etc/svs/docker && docker compose down && docker compose up -d)
```
