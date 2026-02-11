# Django Template

A template for the [Django](https://www.djangoproject.com/) web framework. This template builds your Django application on-demand from source.

## Usage

1. Prepare your Django project (see below)
2. [Create a service](../../../guides/index.md#create-a-service) with required environment variables
3. [Upload your code](../../../guides/index.md#uploading-files) via GIT or SSH to the service volume
4. [Build and start](../../../guides/index.md#building-services) the service

For detailed information about the build process, see [Building services](../../../guides/index.md#building-services).

## Preparation

Your project must have:
- `requirements.txt` - Python dependencies including Django
- `manage.py` - Django management script
- Your Django project directory with `settings.py` and `wsgi.py`

Configure `settings.py` to read from environment variables:
```python
import os

DEBUG = os.environ.get('DEBUG', 'True') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-default-key')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
```

## Required Environment Variables

- `APP_NAME` - Your Django project name (directory containing `wsgi.py`) - **Required**

**Example:**
```bash
sudo svs service create my-app <template_id> \
  --env APP_NAME=myproject \
  --env DEBUG=False \
  --env SECRET_KEY=your-secret \
  --env ALLOWED_HOSTS=myapp.example.com
```

## Configuration

- **Port:** Container port 8000 (Django default)
- **Volume:** `/app` - Application code
- **Runtime:** Python with Gunicorn WSGI server
- **Migrations:** Automatically run on container start

## Connecting to Databases

For PostgreSQL, add these environment variables and configure `settings.py`:
```bash
--env DB_HOST=svs-{postgres_service_id} \
--env DB_NAME=mydb \
--env DB_USER=myuser \
--env DB_PASSWORD=mypass
```

Replace `{postgres_service_id}` with your database service's ID. See [DNS](../../../guides/index.md#dns) for more details on service naming.

## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/django.json"
    ```

??? note "Dockerfile"
    ```dockerfile
    --8<-- "service_templates/django.Dockerfile"
    ```
