# Guides

This section contains various guides aimed at helping you configure and deploy your projects.

**Available Guides:**

- [Static website (NGINX)](./nginx.md) - NGINX is used to deploy static (HTML, CSS, JS) websites.


## Terminology

- **Docker**: Docker is a platform that balances the ease of application deployment with the need for isolation and resource control. It uses containerization technology to package applications and their dependencies into lightweight, portable containers that can run consistently across different environments.
- **Template**: A template is a predefined configuration that outlines how to build and run a specific type of service. It includes settings such as the base image, environment variables, ports, and volumes. Templates simplify the process of deploying services by providing a standardized setup.
- **Service**: A service is an instance of a running application or process that is managed by SVS. Services are created based on templates and can be started, stopped, and configured as needed.
- **Environment Variables**: Environment variables are dynamic values that can be used to configure the behavior of applications and services. They are often used to store sensitive information, such as database credentials or API keys, and can be accessed by the application at runtime.
- **Port**: A port is a communication endpoint used by networked applications to send and receive data. In the context of SVS, ports are used to expose services to the outside world, allowing users to access web applications, databases, and other services running within containers.
- **Domain**: A domain is a human-readable address used to access websites and services on the internet. In SVS, domains can be associated with services to provide easy access via web browsers. Otherwise, services can be accessed using the server's IP address and the assigned port.

### Volumes

Because services run inside Docker containers, any data stored within the container is ephemeral and will be lost when the container is stopped or removed. To persist data beyond the lifecycle of a container, SVS uses Docker volumes (bind mounts) to map directories from the host system into the container.

To think of it simply, an SVS volume defines a mapping between a directory on the host machine and a directory inside the container. This allows data to be stored on the host system, ensuring that it remains intact even if the container is recreated or updated. Containers can both read and write data to these volumes.

```mermaid
graph LR
    A[Host System<br/>/var/svs/volumes/foo/bar] <-->|Bind Mount| B[Docker Container<br/>/container/data]
```

Volumes can be examined using the [detailed service view](#detailed-view).

---

## Generic stepts

The section below outlines the generic steps to follow when using any of the guides provided.

### Find a template

For every service, you need a template that defines how the service should be built and run. These templates are already provided or you can create your own (advanced users).

If you do not find a suitable template, contact your server administrator to import one from the [SVS Template Repository](https://github.com/kristiankunc/svs-core/tree/main/service_templates) or help you create a custom one.

Templates and services are keyed by their `IDs`. You will need to know the `ID` of the template you want to use to create a service. They are visible both in the CLI and Web.

#### Reference

All the official SVS templates have their respective documentation on the [Template Reference](../api-reference/official-templates/index.md) page.

#### CLI

Use the [`svs template list`](../cli-documentation/template.md#svs-template-list) command to list all templates available on your server.

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

#### Web

Navigate to the _Templates_ section. There you will find a list of all templates.

[![Templates section](./images/template-list.png)](./images/template-list.png)
### Create a service

Once you have identified the appropriate template for your service, you can proceed to create the service using that template.


#### CLI

Use the [`svs service create`](../cli-documentation/service.md#svs-service-create) command to create a new service based on the selected template.

```bash
sudo svs service create <your_service_name> <id_of_the_template>
```

The command allows some additional parameters, usually those do not need much tweaking since the default values from templates will usually work. Refer to the [CLI documentation](../cli-documentation/service.md#svs-service-create) for more details.

The only one you may want to use is the `--domain` option to specify the domain name for your service.
Example:

```bash
sudo svs service create my-static-site 7 --domain example.com
```

#### Web

On the _Templates_ page, locate the template you wish to use for your service. Click on the _View_ button associated with that template. This action will take you to the template's detailed view page.

On that page, click _Create Service from Template_. You will be presented with a form to fill in the necessary details for your new service, such as the service name and domain. If you are unsure about any of the fields, the default values provided should suffice for most cases. After completing the form, submit it to create your service.


### Manage your service

After creating your service, you can manage it and see its details.

#### CLI

##### Quick overview

First of all, you can list all services using the [`svs service list`](../cli-documentation/service.md#svs-service-list) command.

```bash
sudo svs service list
```

Example output:

| ID | Name  | Owner      | Status | Template            |
|----|-------|------------|--------|---------------------|
| 4  | nginx | name (1) | exited | nginx-webserver (7) |

From there, you can see a quick overview of all your services, their `IDs`, owners, current status, and the templates they are based on.

##### Detailed view

To see more details about a specific service, use the [`svs service get`](../cli-documentation/service.md#svs-service-get) command followed by the service `ID`.

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
    args=[], status=ServiceStatus.EXITED,
    git_sources=[]
)
```

From there, you can see all the details about your service, including its domain, container ID, image, exposed ports, environment variables, volumes, healthcheck configuration, and current status.

##### Control

Once you have the service `ID`, you can also start, stop, restart, delete and view logs of your service using the respective commands:

```bash
sudo svs service start <service_id>
sudo svs service stop <service_id>
sudo svs service restart <service_id>
sudo svs service delete <service_id>
sudo svs service logs <service_id>
```

#### Web

Navigate to the _Services_ section. There you will find a list of all services. On the service card, click on _View_ to see more details about the service. From there, you can start, stop, restart, or delete the service using the respective buttons.
