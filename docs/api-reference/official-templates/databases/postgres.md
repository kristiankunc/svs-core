# PostgreSQL Template

A template for the [PostgreSQL](https://www.postgresql.org/) database server, a powerful open-source relational database.

## What is PostgreSQL?

PostgreSQL is an advanced, open-source relational database management system known for its reliability, feature robustness, and performance. It's perfect for web applications, data warehousing, and complex queries.

## Quick Start Guide

Follow the **[Common Deployment Steps](../../../guides/common-steps.md)** to deploy your PostgreSQL database:

1. **[Find the template](../../../guides/common-steps.md#find-a-template)** - Look for `postgres-database`
2. **[Create the service](../../../guides/common-steps.md#create-a-service)** - Configure required environment variables (see below)
3. **[Start the service](../../../guides/common-steps.md#start-a-service)** - Start your database
4. **Connect to your database** - From applications or external clients (see below)

## Configuration

### Required Environment Variables

When [creating the service](../../../guides/common-steps.md#configure-environment-variables), configure these environment variables:

- **`POSTGRES_USER`**: Username for the PostgreSQL user to be created (required)
- **`POSTGRES_PASSWORD`**: Password for the user specified in `POSTGRES_USER` (required)
- **`POSTGRES_DB`**: Name of the database to be created on first start (required)

**Example:**
```bash
sudo svs service create my-postgres <template_id> \
  --env POSTGRES_USER=myuser \
  --env POSTGRES_PASSWORD=mypassword \
  --env POSTGRES_DB=mydatabase
```

### Default Settings

- **Port:** Container port 5432 (PostgreSQL default) is exposed
- **Volume:** `/var/lib/postgresql/data` stores database files persistently
- **User:** Runs as the postgres user inside the container

### Optional Configuration

You can customize PostgreSQL behavior with additional environment variables:

- **`POSTGRES_INITDB_ARGS`**: Additional arguments for `initdb`
- **`POSTGRES_HOST_AUTH_METHOD`**: Authentication method (default: password-based)
- **`PGDATA`**: Custom data directory path

See the [PostgreSQL Docker image documentation](https://hub.docker.com/_/postgres) for all available options.

## Common Operations

### View Database Logs

[Check PostgreSQL logs](../../../guides/common-steps.md#view-service-logs) for errors or connection issues.

### Backup Database

Connect to your database and use `pg_dump`:

```bash
pg_dump -h your-server-ip -p <host_port> -U myuser mydatabase > backup.sql
```

### Restore Database

Restore from a backup file:

```bash
psql -h your-server-ip -p <host_port> -U myuser mydatabase < backup.sql
```

## Connecting from Applications

### Python (psycopg2)

```python
import psycopg2

conn = psycopg2.connect(
    host="my-postgres",  # Use service name for internal connections
    port=5432,            # Container port
    database="mydatabase",
    user="myuser",
    password="mypassword"
)
```

### Node.js (pg)

```javascript
const { Client } = require('pg');

const client = new Client({
  host: 'my-postgres',
  port: 5432,
  database: 'mydatabase',
  user: 'myuser',
  password: 'mypassword'
});

await client.connect();
```

### Django (Python)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydatabase',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'my-postgres',
        'PORT': '5432',
    }
}
```

## Troubleshooting

### Can't Connect to Database

1. **Check service status:** Verify the service is running with `svs service get <service_id>`
2. **Check credentials:** Ensure you're using the correct username and password
3. **Check port:** Verify you're using the correct host port for external connections or container port for internal connections
4. **View logs:** Check for errors with `svs service logs <service_id>`

### Database Not Persisting Data

Ensure the service has a [volume configured](../../../guides/common-steps.md#configure-volumes) at `/var/lib/postgresql/data`.

## Security Best Practices

- **Use strong passwords:** Generate random, complex passwords for database users
- **Limit access:** Don't expose the database port publicly if not needed
- **Regular backups:** Set up automated backups of your databases
- **Update regularly:** Keep PostgreSQL updated to get security patches

## Additional Resources

- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Common Deployment Steps](../../../guides/common-steps.md)

## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/postgres.json"
    ```
