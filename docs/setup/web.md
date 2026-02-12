# Web setup

A web UI is provided for controlling SVS and provides a more user-friendly way to organise your system.

!!! danger "Security Notice"

    The web interface requires running as `root` to manage Docker containers. While security hardening features are implemented (rate limiting, HTTPS, audit logging), the interface should **NOT be exposed directly to the public internet**.

    **Recommended deployment:**
    - Use within an isolated network or VPN
    - Configure firewall rules to restrict access
    - Always use HTTPS with a reverse proxy
    - Enable all security features by setting `DEBUG=False`

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

Clone the latest release of the repository and navigate to the `web/` directory/the one corresponding to the version you have installed:

```bash
git clone --depth 1 --branch <tag_name> <repo_url> && cd svs-core/web
```

### Create virtual environment

It is recommended to create a virtual environment for the web interface to avoid dependency conflicts.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

In addition, you also need to install `svs-core` library in the virtual environment. It is excluded from the requirements as installing the same version as the one used system-wide is recommended.
Mixing different versions may lead to unexpected behaviour.

Check your current version of `svs-core` using:

```bash
sudo svs --version
```

Then install the same version in the virtual environment:

```bash
pip install svs-core==<your_version_here>
```

Install and build frontend dependencies:

```bash
(cd frontend && npm ci && npm run build)
```

## Configuration

### Environment variables

Edit the provided `.env.example` file and save it as `.env`

```bash
cp .env.example .env
```

All the required environment variables are documented in the `.env.example` file.

## Running

Create the logs directory for security audit logging:

```bash
mkdir -p logs
```

To start the web interface, simply run:

```bash
sudo -E .venv/bin/gunicorn project.wsgi --bind 0.0.0.0:8000 # sudo warning mentioned at the top of this page
```

After starting, you can access the web interface in your browser at `http://<your-server-ip>:8000`

## Updating

???+ warning "Updating the web interface"
  SVS currently does not have a built-in update mechanism for the web interface. To update, you will need to pull the latest changes from the repository and repeat the installation steps (installing dependencies, building frontend, etc.).

1) Get the latest release tag from the [releases page](https://github.com/kristiankunc/svs-core/releases/latest) and pull the latest changes:

_Ensure this release tag matches the version of `svs-core` you have installed to avoid compatibility issues._

```bash
git pull && git checkout <latest_tag>
```

2) Run django migrations to update the database schema if needed:

```bash
sudo svs utils django-shell migrate
```

3) Rebuild frontend assets:

```bash
(cd frontend && npm ci && npm run build)
```

4) Restart the web interface to apply the changes:

```bash
sudo systemctl restart svs-web # If you set it up as a systemd service
# OR
sudo -E .venv/bin/gunicorn project.wsgi --bind 0.0.0:8000 # If you are running it manually
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
