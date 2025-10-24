## Prerequisites

Before you begin, ensure you meet the following prerequisites:

### Linux distribution

A Debian based distribution (e.g., Debian, Ubuntu, etc.) is required. Other distributions might work, but are not officially supported.

### Docker

Ensure Docker is installed on your system. You can install Docker by following the official [Docker installation guide](https://docs.docker.com/engine/install/).

### Docker Compose

Ensure Docker Compose is installed. You can install it by following the official [Docker Compose installation guide](https://docs.docker.com/compose/install/).

### Build packages

Depending on your distribution, you may need the following build packages:
- libpq-dev
- python3-dev
- build-essential

Install via
```bash
$ apt install -y libpq-dev python3-dev build-essential
```

## Backend services

The following backend services are required to be configured and running:
 - PostgreSQL
 - Caddy

Caddy must be ran via docker, as it relies on recognising docker labels for reverse proxying. PostgreSQL can be ran natively but docker is recommended for ease of setup.

You can use the example compose file to set up these services. Make sure to configure the environment variables in the `.env` file accordingly.

??? note "Example docker-compose.yml"
    ```yaml
    name: "svs-core"

    services:
        db:
            image: postgres:latest
            restart: unless-stopped
            container_name: svs-db
            env_file:
                - .env
            ports:
                - "5432:5432"
            volumes:
                - pgdata:/var/lib/postgresql

        caddy:
            image: lucaslorentz/caddy-docker-proxy:latest
            container_name: caddy
            restart: unless-stopped
            ports:
                - "80:80"
                - "443:443"
            volumes:
                - /var/run/docker.sock:/var/run/docker.sock
                - caddy_data:/data
                - caddy_config:/config
            environment:
                - CADDY_INGRESS_NETWORK=caddy
            networks:
                - caddy

    volumes:
        pgdata:
        caddy_data:
        caddy_config:

    networks:
        caddy:
            driver: bridge
    ```

??? note "Example docker-compose .env file"
    ```env
    POSTGRES_USER=
    POSTGRES_PASSWORD=
    POSTGRES_DB=
    POSTGRES_HOST=localhost
    PGPORT=5432
    ```

## Application setup

### Install pipx

Install `pipx` to safely install the CLI globally without affecting system packages. Follow the official [pipx installation guide](https://pipx.pypa.io/stable/) to install pipx.

### Install the CLI globally

```bash
$ sudo PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install svs_core
```

Following that, you need to force the PIPX_HOME and PIPX_BIN_DIR ENV variables for all users by appendng it to `etc/environment`

```bash
$ printf '%s\n' 'PIPX_HOME="/opt/pipx"' 'PIPX_BIN_DIR="/usr/local/bin"' | sudo tee -a /etc/environment
```

To verify the installation, run:

```bash
$ which svs
```

This should output `/usr/local/bin/svs`.

### Run setup script
Run the setup script to initialze the configuration. Requires sudo privileges to create necessary directories and set permissions.

Download the setup script from [https://github.com/kristiankunc/svs-core/blob/main/install.sh](https://github.com/kristiankunc/svs-core/blob/setup-migrations/install.sh)


```bash
$ sudo bash install.sh
```

### Configure environment variables
The install script wll create a `.env` for svs which requires configuration. Edit the file to set the necessary environment variables.

??? note "Example svs .env file"
    ```env
    DATABASE_URL=postgres://<user>:<password>@<host>:<port>/<database>
    ```

After configuring it, re-run the install script. You will be prompted to create a first admin user. Using a brand new, SVS-only system user is recommended but not enforced.

To run a hello world service, check out [hello-world](hello-world.md)

That's it. Head over to the [cli documentation](../cli.md) to get started with using the CLI.
