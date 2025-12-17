# Django Template

A template for the [Django](https://www.djangoproject.com/) web framework.

## Usage

This image is built in demand. By default it will run in `Debug` mode. To run it in `Production` mode, you need to set the environment variable `DEBUG` to `False`.

In order for your project to respect these settings such as `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, you need to make sure your Django project `settings.py` file reads these values from environment variables. For example:

```python
import os

Debug = os.environ.get('DEBUG', 'True') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
```

Additionally, you need to set `APP_NAME` environment variable to match your Django project name so that the template can correctly point to your `wsgi` module. For example, if your project is named `myproject`, set `APP_NAME` to `myproject`.


## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/django.json"
    ```

??? note "Dockerfile"
    ```dockerfile
    --8<-- "service_templates/django.Dockerfile"
    ```
