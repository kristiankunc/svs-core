# Django Template

A template for the [Django](https://www.djangoproject.com/) web framework, a high-level Python web framework that encourages rapid development.

## What is Django?

Django is a powerful Python web framework that follows the "batteries included" philosophy. It provides everything you need to build web applications: an ORM, authentication, admin interface, and more. This template builds your Django application on-demand from source.

## Quick Start Guide

Follow the **[Common Deployment Steps](../../../guides/common-steps.md)** to deploy your Django application:

1. **Prepare your Django project** - Configure for production (see below)
2. **[Find the template](../../../guides/common-steps.md#find-a-template)** - Look for `django-app`
3. **[Create the service](../../../guides/common-steps.md#create-a-service)** - Configure required environment variables (see below)
4. **[Upload your code](../../../guides/common-steps.md#upload-files)** - Via GIT or SSH
5. **[Start the service](../../../guides/common-steps.md#start-a-service)** - Your Django app will build and start
6. **Access your application** - Via your configured domain

## Prepare Your Django Project

### Required Files

Your project should have:
- `requirements.txt` - Python dependencies including Django
- `manage.py` - Django management script
- Your Django project directory with `settings.py` and `wsgi.py`

### Configure Settings for Production

Modify your `settings.py` to read configuration from [environment variables](../../../guides/common-steps.md#configure-environment-variables):

```python
import os

# Debug mode (defaults to True for development)
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Secret key
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-default-secret-key')

# Allowed hosts
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database (if using PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'mydb'),
        'USER': os.environ.get('DB_USER', 'myuser'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'mypassword'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

## Configuration

### Required Environment Variables

- **`APP_NAME`**: Your Django project name (the directory containing `wsgi.py`) - **Required**

**Example:**
```bash
sudo svs service create my-django-app <template_id> \
  --domain myapp.example.com \
  --env APP_NAME=myproject \
  --env DEBUG=False \
  --env SECRET_KEY=your-secret-key \
  --env ALLOWED_HOSTS=myapp.example.com \
  --env DB_HOST=my-postgres \
  --env DB_NAME=mydatabase \
  --env DB_USER=myuser \
  --env DB_PASSWORD=mypassword
```

**Important:** Set `APP_NAME` to match your Django project's directory name (the one containing `wsgi.py`).

### Recommended Environment Variables

- **`DEBUG`**: Set to `False` for production (default: `True`)
- **`SECRET_KEY`**: Django secret key for cryptographic signing
- **`ALLOWED_HOSTS`**: Comma-separated list of allowed hostnames
- **`DB_HOST`**: Database hostname (use service name for SVS databases - see [DNS](../../../guides/common-steps.md#access-services-via-dns))
- **`DB_NAME`**: Database name
- **`DB_USER`**: Database username
- **`DB_PASSWORD`**: Database password
- **`DB_PORT`**: Database port (default: `5432` for PostgreSQL)

For more details, see [Configure Environment Variables](../../../guides/common-steps.md#configure-environment-variables).

### Default Settings

- **Port:** Container port 8000 (Django development server) is exposed
- **Volume:** `/app` directory stores your Django application code
- **Runtime:** Python with Gunicorn WSGI server
- **Mode:** Runs in debug mode by default (set `DEBUG=False` for production)

## Running Migrations

After deploying your Django application, you may need to run database migrations. The template automatically runs migrations when the container starts. [Check the logs](../../../guides/common-steps.md#view-service-logs) to verify.
If you need to run migrations manually, you can execute commands in the running container:

```bash
docker exec <container_id> python manage.py migrate
```

Find your container ID in your [service details](../../../guides/common-steps.md#view-service-details).

## Collecting Static Files

For production deployments, collect static files:

```bash
docker exec <container_id> python manage.py collectstatic --no-input
```

Configure your `STATIC_ROOT` in `settings.py` to a persistent volume location.

## Connecting to a Database

Create a PostgreSQL service first (see [PostgreSQL template](../databases/postgres.md)), then reference it using [Docker's internal DNS](../../../guides/common-steps.md#access-services-via-dns):

```bash
--env DB_HOST=my-postgres \
--env DB_NAME=mydatabase \
--env DB_USER=myuser \
--env DB_PASSWORD=mypassword
```

## Common Operations

### View Application Logs

[Check Django application logs](../../../guides/common-steps.md#view-service-logs) for errors or debugging.

### Update Application Code

When you update your code, re-deploy from GIT or upload new files, then [restart the service](../../../guides/common-steps.md#restart-a-service).

### Create Superuser

Create a Django admin superuser:

```bash
docker exec -it <container_id> python manage.py createsuperuser
```

## Production Checklist

Before deploying to production:

- [ ] Set `DEBUG=False`
- [ ] Set a strong, random `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` correctly
- [ ] Use a production database (PostgreSQL/MySQL)
- [ ] Configure static files serving
- [ ] Set up HTTPS via domain
- [ ] Configure logging
- [ ] Run migrations
- [ ] Collect static files

## Troubleshooting

### Application Won't Start

1. **[Check logs](../../../guides/common-steps.md#view-service-logs):** View detailed error messages
2. **Verify `APP_NAME`:** Ensure it matches your project directory name
3. **Check dependencies:** Ensure `requirements.txt` includes all needed packages
4. **Verify `wsgi.py` path:** Should be at `<APP_NAME>/wsgi.py`

### Database Connection Errors

1. **Verify database is running:** Check database service status
2. **Check credentials:** Ensure environment variables match database service
3. **Check host:** Use service name (e.g., `my-postgres`) not `localhost`
4. **Check port:** Use container port (e.g., `5432`) not host port

### Static Files Not Loading

1. Configure `STATIC_ROOT` in settings
2. Run `collectstatic` command
3. Configure a reverse proxy or use WhiteNoise for static file serving

## Additional Resources

- [Django Official Documentation](https://docs.djangoproject.com/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Common Deployment Steps](../../../guides/common-steps.md)

## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/django.json"
    ```

??? note "Dockerfile"
    ```dockerfile
    --8<-- "service_templates/django.Dockerfile"
    ```
