## Prerequisites

Before you begin, ensure you meet the following prerequisites:

### Linux distribution

A Debian based distribution (e.g., Debian, Ubuntu, etc.) is required. Other distributions might work, but are not officially supported.

### Docker

Ensure Docker is installed on your system. You can install Docker by following the official [Docker installation guide](https://docs.docker.com/engine/install/).

### Docker Compose

Ensure Docker Compose is installed. You can install it by following the official [Docker Compose installation guide](https://docs.docker.com/compose/install/).


## Backend services

The following backend services are required to be configured and running:
 - PostgreSQL
 - Caddy

Caddy must be ran via docker, as it relies on recognising docker labels for reverse proxying. PostgreSQL can be ran natively but docker is recommended for ease of setup.

You can use the example compose file to set up these services. Make sure to configure the environment variables in the `.env` file accordingly.

??? note "Example docker-compose.yml"
    ```yaml
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
                - pgdata:/var/lib/postgresql/data

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
    POSTGRES_HOST=
    PGPORT=
    ```

## Application setup

### Install the library

!!! note "Pre-release"
    The library is currently in pre-release. To install the latest pre-release version, use the following command:
    ```bash
    $ pip install --extra-index-url https://test.pypi.org/simple/ svs_core
    ```

```bash
$ pip install svs_core
```

### Run setup script
Run the setup script to initialze the configuration. Requires sudo privileges to create necessary directories and set permissions.


```bash
$ svs setup init
```

See also [svs setup init](../cli.md#svs-setup-init) for more information.

### Configure environment variables
The CLI wll create a `.env` for svs which requires configuration. Edit the file to set the necessary environment variables.

??? note "Example svs .env file"
    ```env
    DATABASE_URL=postgres://<user>:<password>@<host>:<port>/<database>
    ```


That's it. Head over to the [cli documentation](../cli.md) to get started with using the CLI.
