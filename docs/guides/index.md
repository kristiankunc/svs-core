# Guides

This section contains various guides aimed at helping you configure and deploy your projects.

**Available Guides:**

- [Static website (NGINX)](./nginx.md) - NGINX is used to deploy static (HTML, CSS, JS) websites.


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

Use the [`svs template list`](../cli.md#svs-template-list) command to list all templates available on your server.

```bash
sudo svs template list
```

Example output:

```bash
┏━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID ┃ Name            ┃ Type  ┃ Description                                              ┃
┡━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 4  │ adminer         │ image │ Adminer database management tool                         │
│ 5  │ django-app      │ build │ Django application container built on-demand from source │
│ 6  │ mysql-database  │ image │ MySQL database                                           │
│ 7  │ nginx-webserver │ image │ A minimal NGINX web server with default config           │
└────┴─────────────────┴───────┴──────────────────────────────────────────────────────────┘
```

#### Web

Navigate to the _Templates_ section. There you will find a list of all templates.

### Create a service

Once you have identified the appropriate template for your service, you can proceed to create the service using that template.


#### CLI

Use the [`svs service create`](../cli.md#svs-service-create) command to create a new service based on the selected template.

```bash
sudo svs service create <your_service_name> <id_of_the_template>
```

The command allows some additional parameters, usually those do not need much tweaking since the default values from templates will usually work. Refer to the [CLI documentation](../cli.md#svs-service-create) for more details.

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

First of all, you can list all services using the [`svs service list`](../cli.md#svs-service-list) command.

```bash
sudo svs service list
```

Example output:

```bash
┏━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ ID ┃ Name  ┃ Owner      ┃ Status ┃ Template            ┃
┡━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 4  │ nginx │ vscode (1) │ exited │ nginx-webserver (7) │
└────┴───────┴────────────┴────────┴─────────────────────┘
```

From there, you can see a quick overview of all your services, their `IDs`, owners, current status, and the templates they are based on. To see more details about a specific service, use the [`svs service get`](../cli.md#svs-service-get) command followed by the service `ID`.

```bash
sudo svs service get <service_id>
```

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
