# SVS Core - Copilot Coding Agent Instructions

## Repository Overview

**SVS (Self-Hosted Virtual Stack)** is an open-source Python library for managing self-hosted services on Linux servers using Docker containers. The project provides a CLI tool and templates for common services, designed to be beginner-friendly while allowing advanced customization.

**Repository Statistics:**
- **Size:** ~4,400 lines of Python code
- **Language:** Python 3.13+ (tested with 3.12)
- **Primary Framework:** Django 6.0 (for database models/migrations and web interface)
- **CLI Framework:** Typer 0.21.0
- **Container Management:** Docker 7.1.0
- **Testing:** pytest with 278 tests (unit + integration + CLI)

## Technology Stack

- **Runtime:** Python ≥3.13 (required in pyproject.toml)
- **Database:** PostgreSQL (via asyncpg and psycopg2)
- **Web Framework:** Django 6.0 with Bootstrap 5.3.8 and Alpine.js
- **Web Proxy:** Caddy (for HTTP routing)
- **Container Orchestration:** Docker + Docker Compose
- **Testing:** pytest, pytest-asyncio, pytest-django, pytest-mock
- **Linting/Formatting:** ruff, black, isort, mypy, djlint
- **Documentation:** Zensical (mkdocs-based)

## Build & Validation Instructions

### Environment Setup

**ALWAYS use a virtual environment.** The project requires Python 3.13  + and PostgreSQL + Docker for full functionality.

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all dependencies (required before any other step)
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Database Setup for Testing

**ALWAYS start the database before running tests.** Tests require a running PostgreSQL instance.

```bash
# Start test database and Caddy using docker compose
cd .github/extra
docker compose up -d

# Wait for database to be ready (required step)
docker exec extra-db-1 pg_isready -U ci
# Should output: /var/run/postgresql:5432 - accepting connections

# Set required environment variables
export DATABASE_URL="postgres://ci:ci@localhost:5432/cidb"
export ENVIRONMENT=testing
export DJANGO_SETTINGS_MODULE=svs_core.db.settings
```

### Linting & Formatting

**ALWAYS run linting before committing.** The project uses pre-commit hooks that MUST pass.

```bash
# Install pre-commit hooks (one-time setup)
pre-commit install

# Run all pre-commit hooks (REQUIRED before committing)
pre-commit run --all-files

# This runs: black, isort, ruff, mypy, djlint, and other checks
# Expected time: 30-60 seconds for full run
```

**Individual linting tools:**
```bash
# Format code with black
black .

# Sort imports
isort .

# Lint with ruff (includes docstring checks)
ruff check . --fix

# Type check with mypy
mypy svs_core tests docs
```

### Running Tests

**Test execution takes 3-5 minutes.** Tests are split into unit and integration tests.

```bash
# Run all tests (requires database to be running)
pytest

# Run only unit tests (faster, ~30-60 seconds)
pytest -m unit

# Run only integration tests (requires Docker, ~2-3 minutes)
pytest -m integration

# Run with coverage
pytest --cov=. --cov-branch --cov-report=xml:coverage.xml
```

**CRITICAL:** Integration tests require Docker daemon to be running and accessible.

### Building Package

```bash
# Install build tools
pip install build

# Build distribution packages
python -m build

# Output: dist/svs_core-*.tar.gz and dist/svs_core-*.whl
```

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
zensical build
# Output: site/ directory

# Serve documentation locally (for testing)
zensical serve
# Access at http://127.0.0.1:8000
```

### Building Web Application

The web application is a Django-based interface located in the `web/` directory. Currently, it uses CDN-hosted assets (Bootstrap 5.3.8 and Alpine.js), but can be extended with a Vite-based build process for custom frontend assets.

**Running the web application in development:**

```bash
# Set required environment variables
export DJANGO_SETTINGS_MODULE=project.settings
export DATABASE_URL="postgres://ci:ci@localhost:5432/cidb"
export ENVIRONMENT=development

# Navigate to web directory
cd web

# Run Django development server
python manage.py runserver
# Access at http://127.0.0.1:8000
```

**Setting up Vite for custom frontend assets (optional):**

If you need to add custom JavaScript/CSS with a build process:

```bash
# In web/ directory, initialize npm and install Vite
cd web
npm init -y
npm install --save-dev vite

# Create vite.config.js for Django integration
# Configure to output to web/app/static/ directory

# Add build scripts to package.json:
# "dev": "vite"
# "build": "vite build"

# Run development server
npm run dev

# Build for production
npm run build
```

**Note:** The current web application uses CDN-hosted libraries and does not require a build step. Vite setup is only needed if adding custom frontend code.

## Project Structure & Key Files

### Root Directory Files
```
.github/               - GitHub workflows and CI configuration
  workflows/
    test.yml          - Main CI: lint, test, build (runs on PR/push)
    publish.yml       - PyPI publishing (runs on release)
    publish-docs.yml  - Documentation deployment
    release-please.yml - Automated releases
  extra/
    .env.ci          - CI environment variables
    docker-compose.yml - Test database configuration
.devcontainer/        - VS Code devcontainer configuration
  devcontainer.json  - Container setup with auto-install
  docker-compose.yml - Dev environment compose stack
svs_core/            - Main library source code
  __main__.py        - CLI entry point
  cli/               - CLI command implementations
    user.py          - User management commands
    template.py      - Template management commands
    service.py       - Service management commands
    state.py         - CLI state management
  db/                - Django models and migrations
    models.py        - User model
    settings.py      - Django configuration
    migrations/      - Database migration files
  docker/            - Docker management logic
    container.py     - Container operations
    image.py         - Image operations
    network.py       - Network operations
    service.py       - Service orchestration
    template.py      - Template handling
    json_properties.py - Docker JSON config classes
  users/             - User management logic
  shared/            - Shared utilities (env, logger)
tests/               - Test suite
  unit/              - Unit tests (mocked, fast)
  integration/       - Integration tests (Docker required)
  cli/               - CLI command tests
  conftest.py        - Pytest fixtures
docs/                - Zensical (mkdocs backward compatibility) documentation source
service_templates/   - JSON templates for common services
  schema.json        - Template validation schema
web/                 - Django web interface
  app/               - Main web application code
    templates/       - Django templates (Bootstrap + Alpine.js)
    views/           - View functions
    lib/             - Helper utilities (user injection, etc.)
  project/           - Django project settings
    settings.py      - Web app Django settings (uses svs_core.db.settings)
  manage.py          - Django management script
  requirements.txt   - Web-specific dependencies
```

### Configuration Files
- **pyproject.toml** - Package metadata, dependencies, tool configs (ruff, black)
- **pytest.ini** - Test configuration, markers (unit, integration, django_db)
- **mypy.ini** - Type checking configuration
- **.isort.cfg** - Import sorting configuration
- **.pre-commit-config.yaml** - Pre-commit hook definitions
- **mkdocs.yml** - Documentation configuration

## Continuous Integration Pipeline

### GitHub Actions Workflow (.github/workflows/test.yml)

The CI pipeline runs on every push and pull request with two jobs:

**1. lint-format job:**
- Sets up Python 3.13
- Creates venv and installs dev dependencies
- Runs `pre-commit run --all-files`
- Must pass before tests run

**2. test job:**
- Sets up Python 3.13 and Docker
- Starts PostgreSQL and Caddy containers via docker compose
- Installs dependencies with `pip install -e ".[dev]"`
- Runs `pytest --cov=. --cov-branch --cov-report=xml:coverage.xml`
- Uploads coverage to Codecov
- Must pass before merge

**3. build job (PR only):**
- Runs after tests pass
- Posts pipx install command as PR comment

### Running CI Checks Locally

To replicate CI checks locally before pushing:

```bash
# 1. Run linting (matches lint-format job)
source .venv/bin/activate
pre-commit run --all-files

# 2. Start database and run tests (matches test job)
cd .github/extra && docker compose up -d && cd ../..
export DATABASE_URL="postgres://ci:ci@localhost:5432/cidb"
export ENVIRONMENT=testing
export DJANGO_SETTINGS_MODULE=svs_core.db.settings
pytest --cov=. --cov-branch --cov-report=xml:coverage.xml
```

## Architecture & Dependencies

### Django Integration
Despite being primarily a CLI tool, this project uses Django for:
- Database ORM (models in `svs_core/db/models.py`)
- Database migrations (managed via `svs_core` app)
- Web interface (in `web/` directory with separate Django project)
- User model and authentication

**IMPORTANT:** Django settings MUST be configured before imports:
```python
os.environ["DJANGO_SETTINGS_MODULE"] = "svs_core.db.settings"
django.setup()
```

**Two Django configurations exist:**
1. **`svs_core.db.settings`** - Core library settings for CLI and database operations
2. **`project.settings`** - Web application settings (imports and extends `svs_core.db.settings`)

**Managing database migrations:**
```bash
# Set the Django settings module for core library
export DJANGO_SETTINGS_MODULE=svs_core.db.settings

# Create new migrations
python -m django makemigrations svs_core

# Apply migrations
python -m django migrate svs_core

# For the web application (uses project.settings)
cd web
export DJANGO_SETTINGS_MODULE=project.settings
python manage.py makemigrations
python manage.py migrate
```

### Docker Architecture
- All services run in Docker containers
- Uses `caddy` network for routing (created by docker compose)
- User-specific networks isolate services
- Templates define service configurations (see `service_templates/`)

### Key Entry Points
- **CLI:** `svs_core/__main__.py` → `main()` function
- **Web App:** `web/manage.py` → Django development server
- **Database:** Set via `DATABASE_URL` environment variable
- **Logging:** `svs_core/shared/logger.py`
- **Environment:** `svs_core/shared/env_manager.py`

## Common Issues & Workarounds

### Database Connection Issues
- **Problem:** Tests fail with database connection errors
- **Solution:** Ensure docker compose is running and database is ready:
  ```bash
  cd .github/extra && docker compose up -d
  docker exec extra-db-1 pg_isready -U ci
  ```

### Pre-commit Hook Failures
- **Problem:** Pre-commit hooks fail on first run
- **Solution:** Pre-commit installs environments on first use. Takes 2-3 minutes.
  ```bash
  pre-commit run --all-files  # Will install environments
  ```

### Import Errors During Testing
- **Problem:** `django.core.exceptions.ImproperlyConfigured`
- **Solution:** Ensure `DJANGO_SETTINGS_MODULE` is set before running tests:
  ```bash
  export DJANGO_SETTINGS_MODULE=svs_core.db.settings
  ```

### Docker Daemon Not Running
- **Problem:** Integration tests fail with "Cannot connect to Docker daemon"
- **Solution:** Ensure Docker service is running:
  ```bash
  sudo systemctl start docker  # Linux
  # Or start Docker Desktop on macOS/Windows
  ```

### Slow Test Execution
- **Problem:** Tests take longer than expected
- **Solution:** Run only unit tests during development:
  ```bash
  pytest -m unit  # Skips Docker-dependent integration tests
  ```

### Web Application Not Starting
- **Problem:** Django web server fails to start
- **Solution:** Ensure correct settings module and database:
  ```bash
  export DJANGO_SETTINGS_MODULE=project.settings
  export DATABASE_URL="postgres://ci:ci@localhost:5432/cidb"
  cd web && python manage.py migrate
  ```

### Wrong Django Settings Module
- **Problem:** Tests or migrations fail with configuration errors
- **Solution:** Use correct settings module for the context:
  - For CLI/library: `export DJANGO_SETTINGS_MODULE=svs_core.db.settings`
  - For web app: `export DJANGO_SETTINGS_MODULE=project.settings`
  - Tests use `svs_core.db.settings` (set in `.github/extra/.env.ci`)

## Development Workflow

### Recommended Order for Changes
1. **Setup environment:** Create venv, install dependencies
2. **Start database:** Run docker compose in `.github/extra/`
3. **Make code changes**
4. **Run linting:** `pre-commit run --all-files` (or specific tools)
5. **Run tests:** `pytest -m unit` first, then `pytest` for full suite
6. **Build package:** `python -m build` to verify packaging
7. **Commit changes:** Pre-commit hooks run automatically

### Web Development Workflow

When working on the web interface:

1. **Setup web environment:**
   ```bash
   cd web
   export DJANGO_SETTINGS_MODULE=project.settings
   export DATABASE_URL="postgres://ci:ci@localhost:5432/cidb"
   export ENVIRONMENT=development
   ```

2. **Apply migrations:**
   ```bash
   # From web/ directory
   python manage.py migrate
   ```

3. **Run development server:**
   ```bash
   # From web/ directory
   python manage.py runserver
   # Access at http://127.0.0.1:8000
   ```

4. **Testing changes:**
   - Templates are in `web/app/templates/`
   - Views are in `web/app/views/`
   - The web app uses Bootstrap 5.3.8 and Alpine.js from CDN
   - No build step required unless adding custom assets

5. **If adding custom frontend assets with Vite:**
   ```bash
   # One-time setup in web/ directory
   npm init -y
   npm install --save-dev vite
   
   # Create vite.config.js to output to app/static/
   # Add scripts to package.json: "dev" and "build"
   
   # Development with hot reload
   npm run dev
   
   # Production build
   npm run build
   ```

### Before Submitting PR
```bash
# 1. Ensure all tests pass
pytest

# 2. Ensure linting passes
pre-commit run --all-files

# 3. Verify build works
python -m build

# 4. Check types (optional but recommended)
mypy svs_core tests docs
```

## Trust These Instructions

These instructions are comprehensive and validated through actual testing of the repository. **Only search for additional information if:**
- Instructions don't cover your specific use case
- You encounter an error not documented here
- You need details about specific function implementations

For most development tasks, following these instructions will be sufficient to build, test, and validate changes successfully.
