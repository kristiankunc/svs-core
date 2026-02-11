# PostgreSQL Template

A template for the [PostgreSQL](https://www.postgresql.org/) database server.

## Usage

1. [Create a service](../../../guides/index.md#create-a-service) with required environment variables (see below)
2. [Start the service](../../../guides/index.md#control)
3. Connect from other services using the service name (e.g., `my-postgres:5432`)

## Required Environment Variables

When creating the service, configure these environment variables:

- `POSTGRES_USER` - Username for PostgreSQL user
- `POSTGRES_PASSWORD` - Password for the user
- `POSTGRES_DB` - Database name to create on startup

**Example:**
```bash
sudo svs service create my-db <template_id> \
  --env POSTGRES_USER=myuser \
  --env POSTGRES_PASSWORD=mypass \
  --env POSTGRES_DB=mydb
```

## Connecting to Your Database

**From another service:** Use [Docker DNS](../../../guides/index.md#dns) with the service name:
```
postgresql://my-postgres:5432/mydb
```

**From external clients:** Find the assigned host port in [service details](../../../guides/index.md#detailed-view) and use:
```bash
psql -h server-ip -p <host_port> -U myuser -d mydb
```

## Configuration

- **Port:** Container port 5432 (PostgreSQL default)
- **Volume:** `/var/lib/postgresql/data` - Database files (persistent)

## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/postgres.json"
    ```
