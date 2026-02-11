# Adminer Template

A template for the [Adminer](https://www.adminer.org/) database management tool, a full-featured database management interface in a single PHP file.

## What is Adminer?

Adminer (formerly phpMinAdmin) is a lightweight database management tool that supports MySQL, PostgreSQL, SQLite, MS SQL, Oracle, and MongoDB. It provides a user-friendly web interface for managing your databases, running queries, and viewing data.

## Quick Start Guide

Follow the **[Common Deployment Steps](../../../guides/common-steps.md)** to deploy Adminer:

1. **[Find the template](../../../guides/common-steps.md#find-a-template)** - Look for `adminer`
2. **[Create the service](../../../guides/common-steps.md#create-a-service)** - Optionally add a domain: `--domain adminer.example.com`
3. **[Start the service](../../../guides/common-steps.md#start-a-service)** - Start Adminer
4. **Access Adminer** - Via your configured domain or assigned port
5. **Connect to databases** - Use service names to connect to your SVS databases (see below)

## Using Adminer

### Connecting to Databases

On the Adminer login page, you'll see fields for:

1. **System:** Select your database type (MySQL, PostgreSQL, etc.)
2. **Server:** Enter your database service name (for services in SVS) or hostname
3. **Username:** Your database username
4. **Password:** Your database password
5. **Database:** (Optional) Specific database name

#### Connecting to SVS Database Services

To connect to a database service running in SVS, use [Docker's internal DNS](../../../guides/common-steps.md#access-services-via-dns):

1. **Server:** Use the service name (e.g., `my-postgres` or `my-mysql`)
2. **Port:** Leave empty (Adminer will use the default port) or specify the container port
3. **Username/Password:** Use the credentials configured in your database service

Example for PostgreSQL service named `my-postgres`:
- System: PostgreSQL
- Server: `my-postgres`
- Username: `myuser`
- Password: `mypassword`
- Database: `mydatabase`

For more details on database service names, see [Access Services via DNS](../../../guides/common-steps.md#access-services-via-dns).

Adminer provides many features including:

- **Browse tables:** View and edit table data
- **Run SQL queries:** Execute custom SQL queries
- **Import/Export:** Import and export databases in various formats
- **Table management:** Create, modify, and drop tables
- **User management:** Manage database users and permissions
- **Search:** Full-text search across tables

## Configuration

### Default Settings

- **Port:** Container port 8080 is exposed for the web interface
- **No authentication required:** Adminer itself has no login; you authenticate to your databases
- **Supports multiple databases:** Can connect to any database accessible from the container

### Customization

Adminer supports plugins and themes. To customize Adminer:

1. Upload custom Adminer files to the service volume
2. Restart the service to apply changes

## Security Considerations

!!! warning "Security Best Practices"
    Adminer provides direct access to your databases. Follow these security practices:
    
    - **Use strong domain restrictions:** Don't expose Adminer publicly without proper access controls
    - **Use strong database passwords:** Ensure all database services use strong passwords
    - **Limit access:** Consider using a VPN or restricting access by IP
    - **Monitor access:** Regularly check logs for unauthorized access attempts

### Recommended Security Setup

1. **Use a non-obvious domain:** Don't use obvious names like `adminer.example.com`
2. **Add authentication:** Consider putting Adminer behind a reverse proxy with HTTP authentication
3. **Restrict network access:** Use firewall rules to limit who can access the Adminer port

## Common Use Cases

- **Database Administration:** Manage multiple database servers from one interface
- **Development:** Quickly inspect and modify database during development
- **Quick Queries:** Run ad-hoc SQL queries without a desktop client
- **Database Exploration:** Browse table structures and relationships
- **Data Import/Export:** Transfer data between databases

## Troubleshooting

### Can't Connect to Database Service

1. **Check service name:** Ensure you're using the correct service name (not the container ID)
2. **Verify database is running:** Check that your database service is running with `svs service get <db_service_id>`
3. **Check credentials:** Verify username and password are correct
4. **Check network:** Ensure both services are in the same Docker network

### Adminer Interface Not Loading

1. **[Check service status](../../../guides/common-steps.md#view-service-details):** Verify Adminer is running
2. **[Check logs](../../../guides/common-steps.md#view-service-logs):** View Adminer logs
3. **Verify port:** Ensure you're accessing the correct host port

## Alternatives

If Adminer doesn't meet your needs, consider these alternatives:

- **phpMyAdmin:** More feature-rich for MySQL databases specifically
- **pgAdmin:** Specifically designed for PostgreSQL
- **DBeaver:** Desktop application with extensive database support

## Additional Resources

- [Adminer Official Website](https://www.adminer.org/)
- [Adminer Documentation](https://www.adminer.org/en/)
- [Adminer Docker Image](https://hub.docker.com/_/adminer)
- [Common Deployment Steps](../../../guides/common-steps.md)


## Definition

??? note "Source"
    ```json
    --8<-- "service_templates/adminer.json"
    ```
