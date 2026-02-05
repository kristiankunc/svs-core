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

```bash
git clone https://github.com/kristiankunc/svs-core && cd svs-core/web
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

## Security recommendations

For production use:

1. Set `DEBUG=False` in your `.env` file
2. Configure HTTPS using a reverse proxy (Caddy or nginx)
3. Ensure the `logs/` directory exists and is writable
4. Review security logs regularly: `tail -f web/logs/security.log`
5. Use firewall rules or VPN to restrict access to trusted IPs only
