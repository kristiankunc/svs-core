# Common Deployment Steps

This page documents all common steps used when deploying services with SVS. Each template guide references these steps to provide a consistent and beginner-friendly experience.

---

## Find a Template

For every service, you need a template that defines how the service should be built and run. SVS provides official templates for common services, or you can create your own (advanced users).

Templates and services are keyed by their `IDs`. You will need to know the `ID` of the template you want to use to create a service.

### Reference

All official SVS templates have their respective documentation on the [Template Reference](../api-reference/official-templates/index.md) page.

### CLI

Use the [`svs template list`](../cli-documentation/template.md#svs-template-list) command to list all templates available on your server:

```bash
sudo svs template list
```

Example output:

| ID | Name            | Type  | Description                                              |
|----|-----------------|-------|----------------------------------------------------------|
| 4  | adminer         | image | Adminer database management tool                         |
| 5  | django-app      | build | Django application container built on-demand from source |
| 6  | mysql-database  | image | MySQL database                                           |
| 7  | nginx-webserver | image | A minimal NGINX web server with default config           |

### Web

Navigate to the _Templates_ section. There you will find a list of all templates.

---

## Create a Service

Once you have identified the appropriate template for your service, you can proceed to create the service using that template.

### CLI

Use the [`svs service create`](../cli-documentation/service.md#svs-service-create) command to create a new service based on the selected template:

```bash
sudo svs service create <your_service_name> <id_of_the_template>
```

The command allows some additional parameters. Usually the default values from templates will work, but you may want to customize:

- `--domain` - Specify the domain name for your service
- `--env` - Set environment variables (can be used multiple times)
- `--port` - Configure port mappings
- `--volume` - Configure volume mappings

Refer to the [CLI documentation](../cli-documentation/service.md#svs-service-create) for complete details.

Example with domain:

```bash
sudo svs service create my-static-site 7 --domain example.com
```

### Web

1. On the _Templates_ page, locate the template you wish to use for your service
2. Click on the _View_ button associated with that template
3. On the template's detailed view page, click _Create Service from Template_
4. Fill in the service creation form with necessary details:
   - Service name (required)
   - Domain (optional)
   - Environment variables (optional)
   - Port and volume mappings (optional, defaults provided)
5. Submit the form to create your service

If you are unsure about any of the fields, the default values provided should suffice for most cases.

---

## Start a Service

After creating a service, you need to start it to make it run.

### CLI

Use the [`svs service start`](../cli-documentation/service.md#svs-service-start) command:

```bash
sudo svs service start <service_id>
```

### Web

Navigate to the _Services_ section, find your service, click on _View_, and then click the _Start_ button.

---

## View Service Details

You can view detailed information about your service including its configuration, status, and runtime details.

### CLI - Quick Overview

List all services using the [`svs service list`](../cli-documentation/service.md#svs-service-list) command:

```bash
sudo svs service list
```

Example output:

| ID | Name  | Owner    | Status  | Template            |
|----|-------|----------|---------|---------------------|
| 4  | nginx | name (1) | running | nginx-webserver (7) |

This shows a quick overview of all your services, their `IDs`, owners, current status, and the templates they are based on.

### CLI - Detailed View

To see more details about a specific service, use the [`svs service get`](../cli-documentation/service.md#svs-service-get) command:

```bash
sudo svs service get <service_id>
```

Example output:
```bash
Service(
    id=10,
    name=nginx,
    template_id=13,
    user_id=1,
    domain=nginx.example.com,
    container_id=709b02cd2335af02e84d2031a486bbebeb46955496009744445ade6668cc0b50,
    image=lscr.io/linuxserver/nginx:latest,
    exposed_ports=['ExposedPort(65205=80)'], # Format: ExposedPort(<host_port>=<container_port>)
    env=[],
    volumes=['Volume(/config=/var/svs/volumes/1/lmrfgsboowcsmute)'], # Format: Volume(<container_path>=<host_path>)
    command=None,
    healthcheck=Healthcheck(test=['CMD', 'curl', '-f', 'http://localhost/'], interval=30, timeout=10, retries=3, start_period=5),
    labels=['Label(service_id=10)', 'Label(svs_user=name)'],
    args=[],
    status=ServiceStatus.RUNNING,
    git_sources=[]
)
```

From this output, you can see:
- Service configuration (name, domain, template)
- Container details (ID, image)
- Port mappings (format: `ExposedPort(host_port=container_port)`)
- Environment variables
- Volume mounts (format: `Volume(container_path=host_path)`)
- Health check configuration
- Current status

### Web

Navigate to the _Services_ section, find your service, and click on _View_ to see the detailed view with all service information.

---

## Stop a Service

Stop a running service to free up resources.

### CLI

Use the [`svs service stop`](../cli-documentation/service.md#svs-service-stop) command:

```bash
sudo svs service stop <service_id>
```

### Web

Navigate to the _Services_ section, find your service, click on _View_, and then click the _Stop_ button.

---

## Restart a Service

Restart a service to apply configuration changes or recover from errors.

### CLI

Use the [`svs service restart`](../cli-documentation/service.md#svs-service-restart) command:

```bash
sudo svs service restart <service_id>
```

### Web

Navigate to the _Services_ section, find your service, click on _View_, and then click the _Restart_ button.

---

## View Service Logs

View the logs from your service to troubleshoot issues or monitor activity.

### CLI

Use the [`svs service logs`](../cli-documentation/service.md#svs-service-logs) command:

```bash
sudo svs service logs <service_id>
```

Add the `-f` or `--follow` flag to stream logs in real-time:

```bash
sudo svs service logs <service_id> --follow
```

### Web

Navigate to the _Services_ section, find your service, click on _View_, and the logs will be displayed on the service details page.

---

## Delete a Service

Permanently remove a service and its associated resources.

!!! warning
    This action cannot be undone. All data in the service's volumes will be lost unless backed up separately.

### CLI

Use the [`svs service delete`](../cli-documentation/service.md#svs-service-delete) command:

```bash
sudo svs service delete <service_id>
```

### Web

Navigate to the _Services_ section, find your service, click on _View_, and then click the _Delete_ button. You will be asked to confirm the deletion.

---

## Configure Domains

To access your service via a custom domain name, you need to add a domain to it. **You can do this during service creation or modify it later.**

### How Domains Work

SVS is typically hosted under one main domain, for example, `example.com`. You can access your services via subdomains like `my-service.example.com` by configuring the domain during service creation.

If you add a domain that is not a subdomain of the main SVS domain (e.g., `anotherdomain.com`), you will need to configure the DNS records for that domain to point to your server's IP address.

### CLI

Add a domain during service creation using the `--domain` flag:

```bash
sudo svs service create my-service 7 --domain my-service.example.com
```

### Web

When creating a service through the web interface, fill in the _Domain_ field in the service creation form.

---

## Configure Environment Variables

Environment variables allow you to configure your service's runtime behavior without modifying code.

### CLI

Add environment variables during service creation using the `--env` flag (can be used multiple times):

```bash
sudo svs service create my-app 5 \
  --env DATABASE_URL=postgres://user:pass@db:5432/mydb \
  --env DEBUG=False
```

### Web

When creating a service through the web interface, use the _Environment Variables_ section in the service creation form to add key-value pairs.

### Template Defaults

Many templates come with default environment variables. Check the template's documentation to see which variables are available and required.

---

## Upload Files

Upload your application code or static files to your service.

!!! note
    Uploading files is currently supported via GIT and SSH (scp, sftp). Support for direct file uploads via the Web UI is planned for a future release.

### Via GIT

Each service can have multiple GIT sources configured. This allows you to deploy your code directly from a GIT repository. You can use any GIT provider (GitHub, GitLab, Bitbucket, etc.).

#### CLI

Use the [`svs service git-source add`](../cli-documentation/service.md) command:

```bash
sudo svs service git-source add <service_id> <git_repository_url> <branch>
```

To deploy the code from the GIT repository:

```bash
sudo svs service git-source deploy <service_id> <git_source_id>
```

#### Web

On the service details page, use the _GIT Sources_ section to add a new GIT repository, then deploy it to your service.

### Via SSH (SCP/SFTP)

You can use standard SSH file transfer tools to upload files directly to your service's volumes:

1. Identify the host path of your service's volume from the service details
2. Use `scp` or `sftp` to copy files to that location on the server

Example with `scp`:
```bash
scp -r ./my-website/* user@server:/var/svs/volumes/1/volume_id/
```

---

## Access Services via DNS

Services can communicate with each other using Docker's internal DNS.

### Service DNS Names

Each service is accessible via its service name within the Docker network. For example, if you have a database service named `postgres-db`, other services can connect to it using `postgres-db` as the hostname.

### Port Access

When connecting from one service to another, use the **container port** (not the host port). For example:

- If a PostgreSQL service has port mapping `ExposedPort(65432=5432)`
- Other services should connect to: `postgres-db:5432` (using the container port)
- External connections use: `server-ip:65432` (using the host port)

### Example: Connecting to a Database

If you have a PostgreSQL database service named `my-postgres`:

```bash
# Connection string from another service
DATABASE_URL=postgresql://user:password@my-postgres:5432/mydb
```

---

## Configure Ports

Ports allow external access to your service or communication between services.

### Port Mapping Format

SVS uses port mapping to expose container ports to the host:
- **Container Port**: The port your application listens on inside the container
- **Host Port**: The port exposed on the server (randomly assigned if not specified)

Format: `host_port:container_port`

### CLI

Configure ports during service creation using the `--port` flag:

```bash
sudo svs service create my-app 5 --port 8080:80
```

To let SVS assign a random host port, omit the host port:

```bash
sudo svs service create my-app 5 --port :80
```

### Web

When creating a service through the web interface, use the _Port Mappings_ section in the service creation form.

### Template Defaults

Most templates come with sensible default port mappings. Check the template's documentation to see the default ports.

---

## Configure Volumes

Volumes provide persistent storage for your service's data.

### Volume Mapping Format

SVS maps container paths to host paths for data persistence:
- **Container Path**: Where your application stores data inside the container
- **Host Path**: Where the data is actually stored on the server (managed by SVS if not specified)

Format: `container_path:host_path`

### CLI

Configure volumes during service creation using the `--volume` flag:

```bash
sudo svs service create my-app 5 --volume /app/data
```

To specify a custom host path:

```bash
sudo svs service create my-app 5 --volume /app/data:/custom/host/path
```

### Web

When creating a service through the web interface, use the _Volume Mappings_ section in the service creation form.

### Template Defaults

Most templates come with default volume mappings. Check the template's documentation to see which paths are mounted by default.

---

## Additional Resources

- **[Template Reference](../api-reference/official-templates/index.md)** - Documentation for all official templates
- **[CLI Documentation](../cli-documentation/service.md)** - Complete CLI command reference
- **[Support](../index.md#support-and-troubleshooting)** - Get help on GitHub Discussions
