# MySQL Template

A template for the [MySQL](https://www.mysql.com/) database server, one of the world's most popular open-source databases.

## What is MySQL?

MySQL is a widely-used, open-source relational database management system. It's known for its ease of use, reliability, and excellent performance for web applications. It powers many popular websites and applications.

## Quick Start Guide

Follow the **[Common Deployment Steps](../../../guides/common-steps.md)** to deploy your MySQL database:

1. **[Find the template](../../../guides/common-steps.md#find-a-template)** - Look for `mysql-database`
2. **[Create the service](../../../guides/common-steps.md#create-a-service)** - Configure required environment variables (see below)
3. **[Start the service](../../../guides/common-steps.md#start-a-service)** - Start your database
4. **Connect to your database** - From applications or external clients (see below)

## Configuration

### Required Environment Variables

When [creating the service](../../../guides/common-steps.md#configure-environment-variables), configure these environment variables:

- **`MYSQL_ROOT_PASSWORD`**: Password for the MySQL root user (required)
- **`MYSQL_DATABASE`**: Name of a database to be created on first start (required)
- **`MYSQL_USER`**: Name of a user to be created on first start (required)
- **`MYSQL_PASSWORD`**: Password for the user specified in `MYSQL_USER` (required)

**Example:**
```bash
sudo svs service create my-mysql <template_id> \
  --env MYSQL_ROOT_PASSWORD=rootpassword \
  --env MYSQL_DATABASE=mydatabase \
  --env MYSQL_USER=myuser \
  --env MYSQL_PASSWORD=mypassword
```

## Connecting to Your Database

### From Another Service

Use [Docker's internal DNS](../../../guides/common-steps.md#access-services-via-dns) with the service name and container port (3306):

```bash
mysql://myuser:mypassword@my-mysql:3306/mydatabase
```

### From External Clients

Find the assigned host port in your [service details](../../../guides/common-steps.md#view-service-details) and connect using:

```bash
mysql -h your-server-ip -P <host_port> -u myuser -p
```

Or use a connection string:
```bash
mysql://myuser:mypassword@your-server-ip:<host_port>/mydatabase
```

- **Port:** Container port 3306 (MySQL default) is exposed
- **Volume:** `/var/lib/mysql` stores database files persistently
- **User:** Runs as the mysql user inside the container

### Optional Configuration

You can customize MySQL behavior with additional environment variables:

- **`MYSQL_RANDOM_ROOT_PASSWORD`**: Set to `yes` to generate a random root password
- **`MYSQL_ALLOW_EMPTY_PASSWORD`**: Set to `yes` to allow the root user to have an empty password (not recommended)
- **`MYSQL_ROOT_HOST`**: Specify the hostname from which the root user can connect

See the [MySQL Docker image documentation](https://hub.docker.com/_/mysql) for all available options.

## Common Operations

### View Database Logs

[Check MySQL logs](../../../guides/common-steps.md#view-service-logs) for errors or connection issues.

### Backup Database

Connect to your database and use `mysqldump`:

```bash
mysqldump -h your-server-ip -P <host_port> -u myuser -p mydatabase > backup.sql
```

### Restore Database

Restore from a backup file:

```bash
mysql -h your-server-ip -P <host_port> -u myuser -p mydatabase < backup.sql
```

## Connecting from Applications

### Python (mysql-connector-python)

```python
import mysql.connector

conn = mysql.connector.connect(
    host="my-mysql",      # Use service name for internal connections
    port=3306,            # Container port
    database="mydatabase",
    user="myuser",
    password="mypassword"
)
```

### Node.js (mysql2)

```javascript
const mysql = require('mysql2');

const connection = mysql.createConnection({
  host: 'my-mysql',
  port: 3306,
  database: 'mydatabase',
  user: 'myuser',
  password: 'mypassword'
});

connection.connect();
```

### PHP

```php
<?php
$conn = new mysqli("my-mysql", "myuser", "mypassword", "mydatabase", 3306);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>
```

## Troubleshooting

### Can't Connect to Database

1. **[Check service status](../../../guides/common-steps.md#view-service-details):** Verify the service is running
2. **Check credentials:** Ensure you're using the correct username and password
3. **Check port:** Verify you're using the correct host port for external connections or container port (3306) for internal connections
4. **[View logs](../../../guides/common-steps.md#view-service-logs):** Check for errors

### Database Not Persisting Data

Ensure the service has a [volume configured](../../../guides/common-steps.md#configure-volumes) at `/var/lib/mysql`.

### Root User Login Issues

If you can't log in as root from external connections, ensure you're connecting from an allowed host. By default, root can only connect from localhost. Use the regular user created with `MYSQL_USER` for remote connections, or configure `MYSQL_ROOT_HOST`.

## Security Best Practices

- **Use strong passwords:** Generate random, complex passwords for database users
- **Limit access:** Don't expose the database port publicly if not needed
- **Regular backups:** Set up automated backups of your databases
- **Update regularly:** Keep MySQL updated to get security patches
- **Use non-root users:** Create application-specific users with limited privileges

## Additional Resources

- [MySQL Official Documentation](https://dev.mysql.com/doc/)
- [MySQL Docker Image](https://hub.docker.com/_/mysql)
- [Common Deployment Steps](../../../guides/common-steps.md)

## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/mysql.json"
    ```
