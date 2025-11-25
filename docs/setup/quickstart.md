## Prerequisites

Before you begin, ensure you meet the following prerequisites:

### Linux distribution

A Debian based distribution (e.g., Debian, Ubuntu, etc.) is required. Other distributions might work, but are not officially supported.

### Docker

Ensure Docker is installed on your system. You can install Docker by following the official [Docker installation guide](https://docs.docker.com/engine/install/).

### Docker Compose

If you've followed the Docker installation guide, you might already have Docker Compose installed. Verify with

```bash
docker compose version
```

Otherwise uou can install it by following the official [Docker Compose installation guide](https://docs.docker.com/compose/install/).


### Build packages

Depending on your distribution, you may need the following build packages:

- libpq-dev
- python3-dev
- build-essential

Install via
```bash
apt install -y libpq-dev python3-dev build-essential
```

## Application setup

### Install pipx

Install `pipx` to safely install the CLI globally without affecting system packages. Follow the official [pipx installation guide](https://pipx.pypa.io/stable/) to install pipx.

??? question "Why PIPX?"
    Pipx allows you to install and run Python applications in isolated environments. This prevents dependency conflicts with other Python packages on your system.

### Install the CLI globally

```bash
sudo PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install svs-core
```

Following that, you need to force the PIPX_HOME and PIPX_BIN_DIR ENV variables for all users by appendng it to `etc/environment`

```bash
printf '%s\n' 'PIPX_HOME="/opt/pipx"' 'PIPX_BIN_DIR="/usr/local/bin"' | sudo tee -a /etc/environment
```

To verify the installation, run:

```bash
which svs
```

This should output `/usr/local/bin/svs`.

### Run setup script

Run the setup script to initialze the configuration. Requires sudo privileges to create necessary directories and set permissions.

Download the setup script from [https://github.com/kristiankunc/svs-core/blob/main/install.sh](https://github.com/kristiankunc/svs-core/blob/main/install.sh)


```bash
curl https://raw.githubusercontent.com/kristiankunc/svs-core/refs/heads/main/install.sh -o install.sh
sudo bash install.sh
```

This script will

1. Create a database + caddy container using Docer Compose
2. Create necessary directories with correct permissions
3. Create an in-place svs user to simplify permission management
4. Run database migrations
5. Prompt you to create an initial user (**This will also create a new system user, so you must not supply an existing one**)

### Test

**As the install script creates a new user, you need to switch to that user to test the installation.** using `su <your_admin_user>` or prefix your commands with `sudo -u <your_admin_user>`

Run
```bash
sudo svs user list
```

This should output your user.


That's it. Head over to the [cli documentation](../cli.md) to get started with using the CLI.

Or, you can follow the [hello-world guide](hello-world.md) to start your first service.
