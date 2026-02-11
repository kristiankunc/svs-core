# Adminer Template

A template for the [Adminer](https://www.adminer.org/) database management tool - a web-based interface for managing databases (MySQL, PostgreSQL, SQLite, and more).

## Usage

1. [Create a service](../../../guides/index.md#create-a-service) using the Adminer template
2. [Start the service](../../../guides/index.md#control)
3. Access the web interface via your configured domain or assigned port
4. Connect to your database services using their service names

## Connecting to SVS Database Services

On the Adminer login page:
- **Server:** Use the service name (e.g., `my-postgres` or `my-mysql`)
- **Username/Password:** Use credentials from your database service
- **Database:** Database name (optional)

For more on service names, see [Docker DNS](../../../guides/index.md#dns).

## Configuration

- **Port:** Container port 8080 (web interface)
- **No authentication required** - Adminer itself has no login; you authenticate to databases

## Security Note

!!! warning
    Adminer provides direct database access. Use strong passwords and consider restricting access by domain or IP.

## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/adminer.json"
    ```
