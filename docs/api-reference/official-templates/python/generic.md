# Generic Python Template

A template for deploying Python applications - web apps (Flask, FastAPI), scripts, workers, or APIs.

## Usage

1. Prepare your application (see below)
2. [Create a service](../../../guides/index.md#create-a-service)
3. [Upload your code](../../../guides/index.md#uploading-files) via GIT or SSH
4. [Start the service](../../../guides/index.md#control)

## Preparation

Your project should have:
- `main.py` - Entry point (default)
- `requirements.txt` - Python dependencies (optional)

**Example `main.py` for Flask:**
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

## Configuration

- **Runtime:** Python 3.14
- **Working Directory:** `/app`
- **Default Command:** `python main.py` (customize with `--start-cmd`)
- **Volume:** `/app` - Application code
- **User:** Non-root user `appuser`

**Custom entry point:**
```bash
--start-cmd "python app.py"
--start-cmd "uvicorn main:app --host 0.0.0.0 --port 8000"
```

## Environment Variables & Ports

Configure as needed:
```bash
--env DATABASE_URL=postgresql://my-db:5432/mydb \
--port :8000
```

## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/python.json"
    ```

??? note "Dockerfile"
    ```dockerfile
    --8<-- "service_templates/python.Dockerfile"
    ```
