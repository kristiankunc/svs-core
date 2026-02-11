# Official Templates

SVS provides a set of official [templates](../../index.md#template) that can be used to create common services.

All templates follow the deployment workflow described in the **[Guides](../../guides/index.md)** section. Each template page provides specific configuration details for that technology.

## What do you want to host?

### Web Servers

- **[NGINX](webservers/nginx.md)** - High-performance web server for static sites and reverse proxying

### Databases

- **[PostgreSQL](databases/postgres.md)** - Advanced open-source relational database
- **[MySQL](databases/mysql.md)** - Popular open-source relational database
- **[Adminer](databases/adminer.md)** - Web-based database management tool (supports PostgreSQL, MySQL, and more)

### Python Applications

- **[Django](python/django.md)** - Full-featured Python web framework with ORM and admin interface
- **[Generic Python](python/generic.md)** - Flexible Python 3.14 runtime for any Python application (Flask, FastAPI, scripts, etc.)

### PHP Applications

- **[Generic PHP](php/generic.md)** - PHP 8.3 with Apache for websites, APIs, and frameworks (WordPress, Laravel, etc.)

### Node.js Applications

- **[SvelteKit](nodejs/svelte.md)** - Modern web framework using Svelte with SSR support

## Customization

As a general rule, SVS does not interfere with the image configuration. To customize a service's behavior:

- **Image-based templates** (NGINX, PostgreSQL, MySQL, Adminer): Refer to the official image documentation on [Docker Hub](https://hub.docker.com/)
- **Build templates** (Django, Python, PHP, SvelteKit): Modify your application code and configuration files as needed
