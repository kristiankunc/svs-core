# MySQL Template

A template for the [MySQL](https://www.mysql.com/) database server.

## Usage

1. [Create a service](../../../guides/index.md#create-a-service) with required environment variables (see below)
2. [Start the service](../../../guides/index.md#control)
3. Connect from other services using the service name (e.g., `my-mysql:3306`)

## Required Environment Variables

When creating the service, configure these environment variables:

- `MYSQL_ROOT_PASSWORD` - Password for root user
- `MYSQL_DATABASE` - Database name to create on startup
- `MYSQL_USER` - Username to create
- `MYSQL_PASSWORD` - Password for the user

**Example:**
```bash
sudo svs service create my-db <template_id> \
  --env MYSQL_ROOT_PASSWORD=rootpass \
  --env MYSQL_DATABASE=mydb \
  --env MYSQL_USER=myuser \
  --env MYSQL_PASSWORD=mypass
```

## Connecting to Your Database

**From another service:** Use [Docker DNS](../../../guides/index.md#dns) with the service name:
```
mysql://my-mysql:3306/mydb
```

**From external clients:** Find the assigned host port in [service details](../../../guides/index.md#detailed-view) and use:
```bash
mysql -h server-ip -P <host_port> -u myuser -p
```

## Configuration

- **Port:** Container port 3306 (MySQL default)
- **Volume:** `/var/lib/mysql` - Database files (persistent)

## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/mysql.json"
    ```
