# Web setup

A web UI is provided for controlling SVS and provides a more user-friendly way to organise your system.

!!! danger

    The web interface is considered insecure and experimental. Exposing to the internet is not recommended.
    This is because it requires running as `root` before changes are made to the core library.

## Prerequisites

The web interface requires the core SVS library to be installed. Please follow the [quickstart guide](../setup/quickstart.md) to install the core library first.
After you have installed the library and verified it is working, you can continue with the web setup.

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

## Configuration

### Environment variables

Edit the provided `.env.example` file and save it as `.env`

```bash
cp .env.example .env
```

All the required environment variables are documented in the `.env.example` file.

## Running

To start the web interface, simply run:

```bash
sudo -E .venv/bin/gunicorn project.wsgi --bind 0.0.0.0:8000 # sudo warning mentioned at the top of this page
```

After starting, you can access the web interface in your browser at `http://<your-server-ip>:8000`
