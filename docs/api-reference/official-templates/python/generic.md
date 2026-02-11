# Generic Python Template

A generic template for deploying Python applications, perfect for scripts, APIs, web apps, or any Python-based service.

## What is This Template?

This template provides a Python 3.14 runtime environment that can run any Python application. It's flexible and suitable for:

- Python web applications (Flask, FastAPI, etc.)
- Background workers and scripts
- API services
- Data processing applications
- Custom Python services

## Quick Start Guide

Follow the **[Common Deployment Steps](../../../guides/common-steps.md)** to deploy your Python application:

1. **Prepare your application** - Ensure you have `main.py` and `requirements.txt` (see below)
2. **[Find the template](../../../guides/common-steps.md#find-a-template)** - Look for `python-generic`
3. **[Create the service](../../../guides/common-steps.md#create-a-service)** - Configure environment variables and ports as needed
4. **[Upload your code](../../../guides/common-steps.md#upload-files)** - Via GIT or SSH
5. **[Start the service](../../../guides/common-steps.md#start-a-service)** - Your Python app will start
6. **Access your application** - Via your configured domain or port

## Prepare Your Application

### Required Files

- **`main.py`** - Your application entry point (default, can be overridden)
- **`requirements.txt`** - Python dependencies (optional but recommended)

### Example `main.py` for a Flask App

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from SVS!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

### Example `requirements.txt`

```
flask==3.0.0
requests==2.31.0
```

## Configuration

### Default Settings

- **Runtime:** Python 3.14 (slim variant)
- **Working Directory:** `/app` (all your files should be here)
- **Default Command:** `python main.py`
- **User:** Runs as non-root user `appuser`
- **Volume:** `/app` directory stores your application code
- **Dependencies:** Automatically installs from `requirements.txt` if present

### Customizing the Entry Point

To run a different file or command, override the start command when creating the service. See [Common Steps](../../../guides/common-steps.md#create-a-service) for details.

Examples:
```bash
# Run a different file
--start-cmd "python app.py"

# Run a web server
--start-cmd "uvicorn main:app --host 0.0.0.0 --port 8000"
```

### Environment Variables

[Configure your application](../../../guides/common-steps.md#configure-environment-variables) using environment variables:

```bash
--env DATABASE_URL=postgresql://user:pass@db:5432/mydb \
--env API_KEY=your-api-key \
--env DEBUG=true
```

### Port Configuration

If your application listens on a port, [configure it](../../../guides/common-steps.md#configure-ports):

```bash
--port :8000
```

## Common Use Cases

### Flask Web Application

```python
# main.py
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello World!'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
```

Create with: `--port :8000`

### FastAPI Application

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

Create with: `--port :8000 --start-cmd "uvicorn main:app --host 0.0.0.0 --port 8000"`

Don't forget to add `uvicorn` and `fastapi` to your `requirements.txt`.

### Background Worker/Script

```python
# main.py
import time

while True:
    print("Processing...")
    # Your background task logic here
    time.sleep(60)
```

No port configuration needed for background workers.

## Connecting to Databases

### PostgreSQL Example

```python
import psycopg2
import os

conn = psycopg2.connect(
    host=os.environ.get('DB_HOST', 'my-postgres'),
    port=os.environ.get('DB_PORT', '5432'),
    database=os.environ.get('DB_NAME', 'mydb'),
    user=os.environ.get('DB_USER', 'myuser'),
    password=os.environ.get('DB_PASSWORD', 'mypass')
)
```

Configure with:
```bash
--env DB_HOST=my-postgres \
--env DB_NAME=mydatabase \
--env DB_USER=myuser \
--env DB_PASSWORD=mypassword
```

For more details, see [Access Services via DNS](../../../guides/common-steps.md#access-services-via-dns).

## Troubleshooting

### Application Won't Start

1. **[Check logs](../../../guides/common-steps.md#view-service-logs):** View detailed error messages
2. **Verify entry point:** Ensure `main.py` exists or custom command is correct
3. **Check dependencies:** Verify all packages in `requirements.txt` install successfully
4. **Check Python version:** Ensure your code is compatible with Python 3.14

### Import Errors

1. **Missing dependency:** Add the package to `requirements.txt`
2. **Restart service:** After updating `requirements.txt`, [restart the service](../../../guides/common-steps.md#restart-a-service)
3. **Check package name:** Verify the exact package name on PyPI

### Permission Errors

The application runs as non-root user `appuser`. If you need to write files:
1. Write to `/app` directory (mounted volume)
2. Ensure file permissions are correct

### Port Already in Use

Ensure your application listens on `0.0.0.0` (not `localhost` or `127.0.0.1`) to be accessible from outside the container.

## Best Practices

- **Use `requirements.txt`:** Always pin dependency versions for reproducibility
- **Environment variables:** Don't hardcode sensitive data; use environment variables
- **Logging:** Use Python's `logging` module instead of `print()` for production
- **Error handling:** Implement proper error handling and graceful shutdown
- **Health checks:** For web apps, implement a `/health` endpoint

## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/python.json"
    ```

??? note "Dockerfile"
    ```dockerfile
    --8<-- "service_templates/python.Dockerfile"
    ```

## Additional Resources

- [Python Official Documentation](https://docs.python.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Common Deployment Steps](../../../guides/common-steps.md)
