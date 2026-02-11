# Official Templates

SVS provides a set of official [templates](../../index.md#template) that can be used to create common services.

All templates follow the **[Common Deployment Steps](../../guides/common-steps.md)** workflow. Each template page provides specific configuration details and examples for that particular technology.

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

## Getting Started

1. **Choose a template** - Select the template that matches your application type
2. **Review template documentation** - Each template page provides specific setup instructions
3. **Follow common steps** - All templates use the same deployment workflow documented in [Common Deployment Steps](../../guides/common-steps.md)

## Customization

As a general rule, SVS does not interfere with the image configuration. To customize a service's behavior:

- **Image-based templates** (NGINX, PostgreSQL, MySQL, Adminer): Refer to the official image documentation on [Docker Hub](https://hub.docker.com/)
- **Build templates** (Django, Python, PHP, SvelteKit): Modify your application code and configuration files as needed

All templates support [environment variables](../../guides/common-steps.md#configure-environment-variables) for runtime configuration.
