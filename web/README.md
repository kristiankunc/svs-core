# SVS Web Interface

Django-based web interface for SVS Core with Vite frontend.

## Development Setup

### Prerequisites

- Python 3.13+
- Node.js 20+ (recommended: 25+)
- npm 10+ (recommended: 11+)

### Install Dependencies

```bash
# Install Node.js dependencies
cd frontend
npm install
```

### Development Workflow

#### Running the Dev Server

For development with Hot Module Replacement (HMR):

```bash
# Terminal 1: Start Vite dev server
cd frontend
npm run dev

# Terminal 2: Start Django dev server
cd ..
python manage.py runserver
```

The Vite dev server runs on `http://127.0.0.1:5173` and provides:
- **Hot Module Replacement (HMR)**: Changes to JS/CSS are reflected instantly without page reload
- **Fast rebuilds**: Only changed files are rebuilt
- **Source maps**: Easy debugging in browser DevTools

When `DEBUG=True` in Django settings, templates automatically load assets from the Vite dev server.

#### Building for Production

```bash
cd frontend
npm run build
```

This creates optimized, minified assets in `static/vite/`:
- JavaScript is bundled and minified with esbuild
- CSS is extracted and minified
- A manifest file is generated for Django to reference

When `DEBUG=False`, Django serves the built assets from `static/vite/`.

## How It Works

### Development Mode (`DEBUG=True`)

1. Vite dev server runs on port 5173
2. Django templates load:
   - `@vite/client` script for HMR
   - Main entry point from dev server (`http://127.0.0.1:5173/src/main.js`)
3. CSS is injected by Vite automatically (no separate `<link>` tag needed)
4. Changes to `frontend/src/` trigger HMR updates

### Production Mode (`DEBUG=False`)

1. Run `npm run build` to generate assets
2. Django templates load:
   - CSS from `static/vite/assets/main-*.css`
   - JS from `static/vite/assets/main-*.js`
3. Asset paths are resolved using `manifest.json`

## Architecture

### Frontend Stack

- **Vite 7**: Build tool and dev server
- **Bootstrap 5**: UI framework with custom primary color (#ffa724)
- **Alpine.js 3**: Lightweight JavaScript framework
- **Highlight.js**: Code syntax highlighting
- **Sass**: CSS preprocessor

### Template Tag

The `{% vite %}` template tag in `app/templatetags/vite.py` handles:
- Switching between dev and production asset URLs
- Loading the HMR client in development
- Resolving asset paths from the manifest in production

### Configuration Files

- `frontend/vite.config.js`: Vite configuration
  - Dev server settings (HMR, watch options)
  - Build optimization
  - Output directory configuration
- `frontend/package.json`: Node.js dependencies and scripts
- `project/settings.py`: Django settings (DEBUG mode, static files)

## Troubleshooting

### HMR Not Working

- Ensure Vite dev server is running (`npm run dev` in `frontend/`)
- Check that `DEBUG=True` in Django settings
- Verify browser console for connection errors

### Build Errors

- Delete `node_modules` and `package-lock.json`, then run `npm install` again
- Clear the build output: `rm -rf static/vite`

### Assets Not Loading in Production

- Run `npm run build` to generate assets
- Ensure `DEBUG=False` in Django settings
- Check that `static/vite/.vite/manifest.json` exists

## Security Features

The web interface includes several security hardening features for semi-production/testing environments:

### HTTPS/SSL Security

When `DEBUG=False`, the following security features are automatically enabled:
- **HTTPS Redirect**: All HTTP traffic is redirected to HTTPS
- **Secure Cookies**: Session and CSRF cookies are only sent over HTTPS
- **HSTS Headers**: HTTP Strict Transport Security with 1-year duration

These features require HTTPS to be configured via a reverse proxy (see deployment section below).

### Session Management

- **Signed Cookie Sessions**: Sessions are stored in cryptographically signed cookies
- Sessions persist across server restarts
- No server-side storage overhead
- Session integrity guaranteed by cryptographic signing

### Rate Limiting

Login attempts are rate-limited to prevent brute-force attacks:
- **Limit**: 5 login attempts per 15 minutes per IP address
- After exceeding the limit, users must wait before trying again
- Rate limit resets automatically after the time window

### Security Audit Logging

All security-critical events are logged to `logs/security.log`:
- Failed login attempts (username, IP, timestamp)
- Successful logins (username, IP, timestamp)
- Rate limit violations

**Log Location**: `web/logs/security.log`

Make sure the `logs/` directory exists and is writable:
```bash
mkdir -p logs
chmod 755 logs
```

### Additional Security Headers

The following security headers are set on all responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: same-origin`

## Deployment Recommendations

### HTTPS Setup with Reverse Proxy

For production deployments, use a reverse proxy like nginx or Caddy for HTTPS termination:

**Example nginx configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Example Caddy configuration:**
```caddyfile
your-domain.com {
    reverse_proxy localhost:8000
}
```

### Security Best Practices

1. **Generate a strong SECRET_KEY**:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Always set `DEBUG=False` in production** - This enables all security features

3. **Use HTTPS** - Configure a reverse proxy with valid SSL certificates (Let's Encrypt recommended)

4. **Network Isolation** - Run the web interface on an isolated network or VPN when possible

5. **Regular Updates** - Keep all dependencies up to date for security patches

6. **Monitor Logs** - Regularly review `logs/security.log` for suspicious activity

### Important Security Notes

!!! warning
    The web interface requires running as root to manage Docker containers. While this is unavoidable for the application's functionality, the security measures implemented provide defense in depth:
    
    - Rate limiting prevents brute-force attacks
    - Audit logging enables security monitoring
    - HTTPS and secure cookies protect data in transit
    - Security headers prevent common web vulnerabilities
    
    **The interface should NOT be exposed directly to the public internet.** Use a VPN, firewall rules, or network isolation to restrict access to trusted users only.
