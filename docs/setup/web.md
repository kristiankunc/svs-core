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
installed version. Use the [svs --version](../cli-documentation/#svs) command to check your installed version.**

## Prerequisites

The web interface requires the core SVS library to be installed. Please follow the [quickstart guide](../setup/quickstart.md) to install the core library first.
After you have installed the library and verified it is working, you can continue with the web setup.

### Node.js and npm

Since the web interface uses some frontend dependencies, you need to have Node.js and npm installed.
You can install them using your system's package manager or by following the instructions on the [official Node.js website](https://nodejs.org/).

Alternatively, you can use services like [nodesource](https://deb.nodesource.com/) or [nvm](https://github.com/nvm-sh/nvm). **Using latest LTS (`v24`) is recommended.**

## Installation

### Quick install (recommended)

Use the `svs web init` command to set up the web interface automatically. This will clone the matching release, create a virtual environment, build the frontend, configure a `.env` file, and optionally set up a systemd service.

```bash
sudo svs web init --domain svs.example.com
```

Or without a domain (will use IP-based access):

```bash
sudo svs web init
```

**Flags:**
- `--dir /opt/svs-web` - Install directory (default: `/opt/svs-web`)
- `--domain example.com` - Domain for Caddy reverse proxy configuration (creates a `web.Caddyfile` automatically)
- `--no-systemd` - Skip systemd service creation
- `--skip-build` - Skip frontend build
- `-y` - Non-interactive mode

### Manual installation

Alternatively, you can set up the web interface manually:

```bash
git clone https://github.com/kristiankunc/svs-core
cd svs-core/web
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

### Using systemd (recommended)

If you used `sudo svs web init` without `--no-systemd`, a systemd service was created automatically. Start and enable it with:

```bash
sudo systemctl enable svs-web
sudo systemctl start svs-web
```

### Manually

To start the web interface without systemd:

```bash
sudo -E .venv/bin/python -m gunicorn project.wsgi --bind 0.0.0.0:8000
```

After starting, you can access the web interface in your browser at `http://<your-server-ip>:8000`

## Updating

To update the web interface after upgrading the core library:

```bash
# Recommended: re-run svs web init (re-generates systemd service, rebuilds frontend)
sudo svs web init

# Alternative: use the update script
sudo bash update.sh
```

## Security recommendations

For production use:

1. Set `DEBUG=False` in your `.env` file
2. Configure HTTPS using a reverse proxy (Caddy or nginx)
3. Ensure the `logs/` directory exists and is writable
4. Review security logs regularly: `tail -f logs/security.log`
5. Use firewall rules or VPN to restrict access to trusted IPs only

## Systemd service (manual)

If you skipped systemd creation with `--no-systemd` or prefer to configure it yourself, create a file at `/etc/systemd/system/svs-web.service`:

```ini
[Unit]
Description=SVS Web Interface
After=network.target

[Service]
User=root
WorkingDirectory=/opt/svs-web
ExecStart=/opt/svs-web/.venv/bin/python -m gunicorn project.wsgi --bind 0.0.0.0:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

Replace the paths with your install directory if you used a custom `--dir`. Then reload systemd and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable svs-web
sudo systemctl start svs-web
```

## Domain configuration

**As mentioned above, exposing publicly is not recommended, but is supported.**

If you used `sudo svs web init --domain example.com`, a `web.Caddyfile` was created automatically in your install directory. You still need to mount it in the Caddy container.

Edit `/etc/svs/docker/docker-compose.yml` and add the following to the `caddy` service:

```yaml
caddy:
    ...
    volumes:
      ...
      - /path/to/your/web.Caddyfile:/etc/caddy/web.Caddyfile:ro
    environment:
      ...
      - CADDY_DOCKER_CADDYFILE_PATH=/etc/caddy/web.Caddyfile
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

If you don't have a `web.Caddyfile` yet, create one in your install directory:

```caddy
example.com {
    reverse_proxy host.docker.internal:8000
}
```

Restart the SVS stack to apply the changes:

```bash
(cd /etc/svs/docker && docker compose down && docker compose up -d)
```
