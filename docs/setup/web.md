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

### Security Configuration

For semi-production/testing deployments, ensure proper security configuration:

1. **Generate a strong SECRET_KEY**:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Add this to your `.env` file as `DJANGO_SECRET_KEY`.

2. **Set DEBUG=False** in production to enable:
   - HTTPS redirects
   - Secure cookies (session and CSRF)
   - HSTS headers
   - Additional security protections

3. **Configure ALLOWED_HOSTS** with your actual domain/IP:
   ```bash
   DJANGO_ALLOWED_HOSTS=yourdomain.com,192.168.1.100
   ```

### HTTPS Setup with Reverse Proxy

The web interface requires HTTPS for production use. Use a reverse proxy like nginx or Caddy:

**Caddy (recommended for simplicity):**
```caddyfile
yourdomain.com {
    reverse_proxy localhost:8000
}
```

Caddy automatically handles HTTPS certificates via Let's Encrypt.

**nginx:**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Security Features

The web interface includes:

- **Rate Limiting**: Login attempts limited to 5 per 15 minutes per IP
- **Audit Logging**: Security events logged to `web/logs/security.log`
- **Signed Cookie Sessions**: Cryptographically secure session storage
- **Security Headers**: XSS protection, clickjacking prevention, content type sniffing protection
- **HTTPS Enforcement**: Automatic redirect when `DEBUG=False`

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

!!! note "Production Deployment"

    For production use:
    1. Set `DEBUG=False` in your `.env` file
    2. Configure HTTPS using a reverse proxy (Caddy or nginx)
    3. Ensure the `logs/` directory exists and is writable
    4. Review security logs regularly: `tail -f web/logs/security.log`
    5. Use firewall rules or VPN to restrict access to trusted IPs only
